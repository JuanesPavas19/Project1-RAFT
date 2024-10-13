# Proyecto N1: Implementación de Algoritmo de Consenso para Elección de Líder

## Descripción del Proyecto

Este proyecto implementa un sistema distribuido utilizando un algoritmo de consenso para la elección de un líder. El objetivo es coordinar la consistencia de datos entre nodos que interactúan en una base de datos relacional distribuida. El sistema es capaz de tolerar fallos, como la caída del líder, y asegura la disponibilidad continua mediante la elección automática de un nuevo líder utilizando el algoritmo Raft. 

El sistema consta de cinco procesos:

- **Proceso 1**: Cliente que realiza consultas de lectura (read) y escritura (write).
- **Proceso 2**: Proxy que intercepta las solicitudes del cliente y las redirige al líder para operaciones de escritura o a un seguidor (follower) para lecturas.
- **Proceso 3**: El líder del sistema, que coordina las operaciones de escritura y asegura la replicación de los datos a los followers.
- **Procesos 4 y 5**: followers que mantienen réplicas del estado de la base de datos y responden a las solicitudes de lectura.

El sistema utiliza el algoritmo de consenso Raft para garantizar que siempre exista un único líder. Si el líder falla, los followers eligen un nuevo líder. El sistema también maneja casos en los que un nodo vuelve a unirse a la red, asegurándose de que reciba la versión más actualizada de la base de datos.

## Estructura del Proyecto

Los archivos principales son los siguientes:

- **`proxy_server.py`**: Implementa el proxy que intercepta las solicitudes del cliente y dirige las operaciones al líder o a los followers según sea necesario.
- **`db_server.py`**: Implementa los nodos de base de datos, que pueden actuar como líderes o followers, manejar las operaciones de escritura/lectura y replicar los datos.
- **`service.proto`**: Archivo que define los servicios gRPC utilizados para la comunicación entre los nodos del sistema.
- **`client.py`**: Cliente que realiza solicitudes de lectura y escritura a través del proxy.

## Procesos

1. **Cliente (Proceso 1)**:
   - El cliente interactúa con el sistema realizando solicitudes de lectura y escritura.
   - Si la solicitud es de lectura (`read`), el proxy redirige la consulta a un follower para obtener los datos.
   - Si la solicitud es de escritura (`write`), el proxy dirige la solicitud al líder, quien actualiza la base de datos y replica los cambios en los followers.

2. **Proxy (Proceso 2)**:
   - El proxy actúa como intermediario entre el cliente y los nodos de la base de datos.
   - Redirige las solicitudes de escritura al líder y las solicitudes de lectura a los Followers.


3. **Líder (Proceso 3)**:
   - El líder es responsable de coordinar las operaciones de escritura.
   - Garantiza la consistencia de los datos replicándolos a los Followers.
   - Si el líder falla, los Followers realizan una votación utilizando el algoritmo Raft para elegir un nuevo líder.

4. **Follower (Procesos 4 y 5)**:
   - Mantienen una réplica de la base de datos y responden a las solicitudes de lectura.
   - Reciben actualizaciones del líder para garantizar la consistencia de los datos.
   - Si un foloower se desconecta y vuelve a conectarse, el líder replica la base de datos más reciente en el nodo reconectado.

## Características del Sistema

- **Tolerancia a Fallos**: El sistema detecta la falla del líder y ejecuta el algoritmo Raft para elegir un nuevo líder. Si un follower se cae, no afecta la disponibilidad del sistema, y al reconectarse, recibe la base de datos actualizada.
- **Replicación de Datos**: Todas las operaciones de escritura se realizan en el líder, y los cambios se replican automáticamente en los followeres cuanod se hace el `write`.
- **Manejo de Líderes Duplicados**: Si por alguna razón ocurren dos elecciones simultáneas y se designan dos líderes, el sistema degrada automáticamente uno de ellos a follower para asegurar que solo haya un líder en todo momento.
- **Sincronización de Nuevos Nodos**: Si un  follower se desconecta y luego se reconecta, el líder replica los datos más recientes en ese nodo para asegurar que esté sincronizado con el estado actual del sistema.

## Instalación y Configuración

### Requisitos

- Python 3.8+
- gRPC y Protocol Buffers




### Generar los Archivos gRPC

Si modificaste el archivo `service.proto`, necesitarás regenerar los archivos de código gRPC. Para hacerlo, ejecuta el siguiente comando:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto
```


### Crear el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Conexion a Base de datos
Debido a que las BD son privadas, no se puede entrar directaemnte a ella desde una instancia. por lo que con este comando podras.

```bash
chmod 400 'keyRaft.pem'
ssh -i 'keyRaft.pem' ubuntu@'10.0.2.250'
```

```bash
`keyRaft.pem` es el nombre de tu archivo key.pem
`10.0.2.250` es la IP privada de la BD
```


### Ejecución del Sistema

1. **Iniciar el Proxy**:
   - El proxy se encarga de manejar las solicitudes del cliente y coordinar la comunicación entre los nodos.
   ```bash
   python proxy_server.py
   ```

2. **Iniciar los Nodos de Base de Datos**:
   - Cada nodo de la base de datos debe ejecutarse como un proceso independiente.
   - Se puede iniciar varios procesos de base de datos para simular los followers y el líder.
   ```bash
   python db_server.py
   ```

3. **Ejecutar el Cliente**:
   - El cliente realiza solicitudes de lectura o escritura a través del proxy.
     ```bash
     python client.py
     ```


## Instrucciones de Uso

- **Lecturas**: El cliente envía una solicitud de lectura (`read`) al proxy, quien redirige la solicitud a uno de los followers para obtener la información solicitada.
- **Escrituras**: El cliente envía una solicitud de escritura (`write`) al proxy, quien redirige la solicitud al líder para realizar la actualización y luego replicar los cambios en los followers.

## Manejo de Fallos (ESTAN MAS EXPLICITOS Y CON EVIDENCIAS EN EL INFORME FINAL .DOCX)

- Si el líder falla, el proxy detectará la falla y los followers iniciarán una elección para seleccionar un nuevo líder utilizando el algoritmo Raft.
- Si un follower se desconecta y luego se reconecta, recibirá la base de datos más actualizada desde el líder.
- Si se detectan dos líderes simultáneamente, uno de ellos será degradado automáticamente a follower para asegurar que solo haya un líder en todo momento.
