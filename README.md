# Examen Segundo Parcial - Pipeline de datos contenerizado

- **Materia:** Manejo Masivo de Datos (Big Data)
- **Alumno:** Alan Noé Vega Nieto
- **Matrícula:** 125053132
- **Pregunta asignada:** mi matrícula termina en 2, así que me tocó el **ticket promedio (ingreso promedio por registro) por tienda**.

## Qué hace el proyecto

Es el pipeline de DataMart con 3 contenedores que se levantan con un solo comando:

```
data/ventas_125053132.csv
        |
        v
   [ hadoop ]  MapReduce con Hadoop Streaming (mapper.py + reducer.py)
        |
        v  part-00000 (volumen "resultados")
   [ api ]  scripts/cargar_resultados.py lo inserta en la base
        |
        v
   [ db ]  PostgreSQL, tabla "resultados" (volumen "pgdata")
        ^
        |
   [ api ]  Flask: GET / POST / PUT / DELETE  ->  http://localhost:5001
```

- **hadoop**: Debian 12 + OpenJDK 17 + Python 3 + Hadoop 3.3.6 en modo standalone, con servidor SSH.
- **db**: PostgreSQL 16 con volumen nombrado y las credenciales en `.env`.
- **api**: el CRUD en Flask adaptado a la tabla `resultados`. Se conecta a la base por el nombre del servicio (`db`).

Los tres están en la red `red_datamart` que se define en el compose.

## Pasos para reproducir

Se necesita Docker Desktop abierto, Git y Python 3.

**1. Clonar el repositorio**

```bash
git clone URL_DE_TU_REPO
cd examen-p2-125053132
```

**2. Generar el dataset** (no viene en el repo porque pesa unos 340 MB). Se genera dentro de la carpeta `data/`, que es la que se monta en el contenedor:

```bash
cd data
python3 ../generar_dataset.py 125053132
cd ..
```

**3. Crear el archivo `.env`** a partir del ejemplo y cambiarle la contraseña:

```bash
cp .env.example .env
```

**4. Levantar todo**

```bash
docker compose up --build
```

La primera vez tarda porque se descarga Hadoop (unos 700 MB). Cuando ya estén los tres servicios arriba, los siguientes comandos se corren en otra pestaña de la terminal, en la misma carpeta.

**5. Correr el job de MapReduce**

```bash
docker compose exec -u hadoop hadoop bash /app/mapreduce/ejecutar_job.sh
```

Ese script borra la salida anterior y corre este comando midiendo el tiempo:

```bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -input /data/input/ventas_125053132.csv \
    -output /data/output/resultado \
    -mapper mapper.py -reducer reducer.py \
    -file mapper.py -file reducer.py
```

**6. Correr el script secuencial y comparar**

```bash
docker compose exec -u hadoop hadoop bash /app/mapreduce/comparar.sh
```

**7. Cargar los resultados a la base de datos**

```bash
docker compose exec api python scripts/cargar_resultados.py
```

**8. Consultar la API**

```bash
curl http://localhost:5001/resultados
curl http://localhost:5001/resultados/T001
```

## Evidencias

### Parte A. Infraestructura

Los tres servicios levantados con `docker compose up --build`:

![docker compose ps](evidencias/01_compose_ps.png)

`hadoop version` dentro del contenedor:

```bash
docker compose exec hadoop hadoop version
```

![hadoop version](evidencias/02_hadoop_version.png)

### Parte B. SSH sin contraseña

El usuario `hadoop` no tiene contraseña y el servidor SSH tiene desactivado el acceso con contraseña, solo se entra con llaves. Las llaves no están en el repo ni en el Dockerfile: se generan con `ssh-keygen` cuando arranca cada contenedor.

- **`ssh localhost`**: el contenedor hadoop genera su par de llaves y agrega la pública a su `authorized_keys` (como lo pide Hadoop para el modo pseudo-distribuido).
- **De api a hadoop**: el contenedor api genera su propio par. La llave privada se queda en api y solo la pública se copia a un volumen compartido (`llaves_ssh`), que el sshd de hadoop lee como otro archivo de llaves autorizadas.

```bash
docker compose exec -u hadoop hadoop ssh localhost
```

![ssh localhost](evidencias/03_ssh_localhost.png)

```bash
docker compose exec api ssh hadoop@hadoop
```

![ssh de api a hadoop](evidencias/04_ssh_api_hadoop.png)

### Parte C. MapReduce

El mapper saca `tienda <TAB> ingreso` por cada venta (ingreso = cantidad x precio_unitario). Se salta el encabezado y las líneas mal formadas (las cuenta en un contador de Hadoop en lugar de tronar). El reducer recibe todo ordenado por tienda, suma los ingresos, cuenta las ventas y saca el promedio.

Salida del job:

![job de mapreduce](evidencias/05_job_mapreduce.png)

### Comparativa de rendimiento (C2)

![comparativa](evidencias/06_comparativa_tiempos.png)

| Método | Tiempo (real) |
| --- | --- |
| Hadoop MapReduce (Streaming, standalone) | TIEMPO_MAPREDUCE |
| Script secuencial en Python (línea a línea) | TIEMPO_SECUENCIAL |

Los dos dan exactamente el mismo resultado, lo comparo con `diff` en `comparar.sh`.

En mi caso el script secuencial fue mucho más rápido. Hadoop en modo standalone corre todo en una sola JVM y en una sola máquina, entonces no hay paralelismo real y solo queda el costo extra: arrancar la JVM, partir el CSV en splits, pasar cada línea por una tubería a un proceso de Python (así trabaja Streaming), escribir a disco los 5 millones de pares clave-valor, ordenarlos y luego pasarlos al reducer. El secuencial solo lee el archivo una vez y va sumando en un diccionario que tiene una llave por tienda, eso cabe sin problema en memoria. Con un archivo de este tamaño ese trabajo extra de MapReduce pesa más que lo que ayuda. Empezaría a convenir con datos que ya no caben en una sola máquina y con un clúster de varios nodos donde los maps sí corren en paralelo.

### Parte D. Integración

Carga de `part-00000` a la tabla `resultados`:

![carga a la base](evidencias/07_carga_bd.png)

Endpoints de lectura:

```bash
curl http://localhost:5001/resultados
curl http://localhost:5001/resultados/T001
```

![api get](evidencias/08_api_get.png)

Endpoints de escritura (el CRUD completo sobre la tabla nueva):

```bash
curl -X POST http://localhost:5001/resultados \
     -H "Content-Type: application/json" \
     -d '{"tienda": "T099", "ticket_promedio": 1234.50, "num_ventas": 10}'

curl -X PUT http://localhost:5001/resultados/T099 \
     -H "Content-Type: application/json" \
     -d '{"ticket_promedio": 2000}'

curl -X DELETE http://localhost:5001/resultados/T099
```

![api escritura](evidencias/09_api_escritura.png)

Persistencia: después de `docker compose down` y `docker compose up -d` los datos siguen en la base porque están en el volumen nombrado `pgdata`.

![persistencia](evidencias/10_persistencia.png)

## Parte E. Teoría

**1. Modos de Hadoop.**
En *standalone* todo corre en un solo proceso de Java en la máquina local, no se levanta ningún demonio y se usa el sistema de archivos normal del sistema operativo. Sirve para probar y depurar, es el que uso en este examen. En *pseudo-distribuido* sigue siendo una sola máquina, pero cada demonio (NameNode, DataNode, ResourceManager, NodeManager) corre en su propio proceso y se comunican como si fueran un clúster, por eso pide SSH a localhost. En *totalmente distribuido* los demonios están repartidos en varias máquinas y ya hay replicación y tolerancia a fallos de verdad. HDFS se usa en el pseudo-distribuido y en el totalmente distribuido, en standalone no.

**2. Por qué el dataset va como volumen y no con `COPY`.**
Primero, porque la imagen pesaría 340 MB más y cada vez que cambiara el CSV habría que reconstruirla. Segundo, porque los datos no son parte de la aplicación: con volumen la misma imagen sirve para el dataset de cualquier matrícula. Además así el CSV no queda guardado dentro de la imagen (si se publica la imagen se irían los datos con ella) y montarlo en solo lectura protege el archivo original.

**3. `docker compose down` contra `down -v`.**
Con `docker compose down` se detienen y se borran los contenedores y la red, pero los volúmenes nombrados se quedan. Como los datos de PostgreSQL están en el volumen `pgdata`, al volver a levantar siguen ahí. Con `docker compose down -v` también se borran los volúmenes, entonces la base se pierde: al levantar otra vez PostgreSQL arranca vacío y hay que volver a cargar los resultados.

**4. Por qué MapReduce no siempre es más rápido.**
Porque tiene un costo fijo: arrancar la JVM, dividir el archivo, lanzar las tareas, escribir resultados intermedios a disco y ordenarlos en el shuffle. Con 400 MB, que caben en la memoria de una laptop, ese costo es más grande que el trabajo en sí, y en standalone ni siquiera hay varias máquinas para repartirlo. Conviene cuando los datos ya no caben en una sola máquina (cientos de GB o TB), cuando hay un clúster con varios nodos para paralelizar y cuando se necesita tolerancia a fallos.

**5. `CMD` vs `ENTRYPOINT` y `COPY` vs `ADD`.**
`CMD` es el comando por defecto del contenedor y se reemplaza fácil escribiendo otro al final de `docker run`. `ENTRYPOINT` es el ejecutable fijo: lo que se escriba al final de `docker run` (o lo que diga `CMD`) le llega como argumentos. En mi Dockerfile de hadoop el `ENTRYPOINT` es el script que prepara las llaves y el `CMD` es el servidor SSH. `COPY` solo copia archivos del contexto de build a la imagen. `ADD` hace lo mismo pero además puede descargar desde una URL y descomprime solo los `.tar` locales. Se recomienda usar `COPY` a menos que se necesite eso extra.

## Estructura del repositorio

```
examen-p2-125053132/
├── README.md
├── .gitignore               # incluye *.csv y .env
├── .env.example
├── docker-compose.yml
├── generar_dataset.py       # script del examen para generar el CSV
├── data/                    # aquí va el CSV (no se sube)
├── hadoop/
│   ├── Dockerfile
│   └── entrypoint.sh        # genera las llaves SSH al arrancar
├── mapreduce/
│   ├── mapper.py
│   ├── reducer.py
│   ├── secuencial.py
│   ├── ejecutar_job.sh      # corre el job con Hadoop Streaming y mide el tiempo
│   └── comparar.sh          # corre el secuencial y compara resultados
├── api/
│   ├── Dockerfile
│   ├── entrypoint.sh        # genera la llave de la api y comparte la pública
│   ├── requirements.txt
│   └── app.py
├── scripts/
│   └── cargar_resultados.py
└── evidencias/              # capturas
```

## Errores comunes

- `env file .env not found`: falta el paso 3 (`cp .env.example .env`).
- `No encuentro /data/input/ventas_125053132.csv`: el CSV no está en la carpeta `data/`.
- El puerto 5001 está ocupado: cambiar `API_PORT` en `.env` y volver a correr `docker compose up -d`.
