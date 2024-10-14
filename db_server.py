import csv
import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import os
import time
import random
from threading import Thread
import socket # para leer ip propia

"""El Contenido de db_server.py y db_server1test.py son el mismo solo que uno esta con algunos comentarios para facilitar lectura de terminal en pruebas :)"""

FIRST_RUN = True
DB_FILE = 'database.csv'

# Verificar si el archivo ya existe
if os.path.exists(DB_FILE):
    print(f"El archivo '{DB_FILE}' ya existe. Se eliminará para crear uno nuevo.")
    os.remove(DB_FILE)  # Eliminar el archivo si existe
else:
    print(f"El archivo '{DB_FILE}' no existe. Creando uno nuevo.")

# Crear un nuevo archivo CSV con la estructura especificada
with open(DB_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Escribir la cabecera (estructura)
    writer.writerow(['id', 'name', 'email'])

print(f"Archivo '{DB_FILE}' creado con la estructura: id, name, email.")

# Obtener la IP privada del servidor
def get_private_ip():
    return socket.gethostbyname(socket.gethostname())

ROLE = 'follower'
CURRENT_TERM = 0
VOTED_FOR = None
LEADER_ID = None
TIMEOUT = random.uniform(8.0, 10.0) if FIRST_RUN else random.uniform(1.5, 3.0)
LAST_HEARTBEAT = time.time()

#OTHER_DB_NODES = ['10.0.2.100', '10.0.2.164'] #Example
# Establecer la IP del servidor
SERVER_IP = get_private_ip()

# Lista de nodos, incluyendo la IP del servidor
ALL_DB_NODES = [
    '10.0.2.172',
    '10.0.2.100',
    '10.0.2.164'
]

# Filtrar nodos que no sean la IP del servidor
OTHER_DB_NODES = [ip for ip in ALL_DB_NODES if ip != SERVER_IP]
print(OTHER_DB_NODES)


class DatabaseService(service_pb2_grpc.DatabaseServiceServicer):

    def ReadData(self, request, context):
        global ROLE
        print(f"[{ROLE}] - Read operation requested")
        
        with open(DB_FILE, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            rows = [','.join(row) for row in reader]
            result = "\n".join(rows)
        
        print(f"[{ROLE}] - Read operation completed")
        return service_pb2.ReadResponse(result=result)

    def WriteData(self, request, context):
        global ROLE
        if ROLE == 'leader':
            print(f"[{ROLE}] - Write operation requested")
            data = request.data.split(',')
            new_id = data[0]

            # Verificar si el ID ya existe
            with open(DB_FILE, mode='r') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    if row[0] == new_id:
                        print(f"[{ROLE}] - Write operation failed: ID already exists")
                        return service_pb2.WriteResponse(status="ERROR: ID ya existente")

            # Si el ID no existe, agregar al CSV
            with open(DB_FILE, mode='a') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(data)
            
            print(f"[{ROLE}] - Write operation completed")

            # Replicar los datos a los seguidores
            self.replicate_to_followers(data)

            return service_pb2.WriteResponse(status="SUCCESS")
        else:
            print(f"[{ROLE}] - Write operation attempted on follower - Redirect to leader required")
            return service_pb2.WriteResponse(status="ERROR: Cannot write to follower")

    def ReplicateData(self, request, context):
        print(f"[{ROLE}] - Replication request received")
        data = request.data.split(',')
        print(f"[{ROLE}] - Data to replicate: {data}")

        try:
            with open(DB_FILE, mode='a') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(data)
            print(f"[{ROLE}] - Replication completed successfully")
            return service_pb2.WriteResponse(status="SUCCESS")
        except Exception as e:
            print(f"[{ROLE}] - Replication failed: {e}")
            return service_pb2.WriteResponse(status=f"ERROR: {e}")

    def replicate_to_followers(self, data):
        for follower_ip in OTHER_DB_NODES:
            try:
                channel = grpc.insecure_channel(f'{follower_ip}:50051')
                stub = service_pb2_grpc.DatabaseServiceStub(channel)
                replicate_request = service_pb2.WriteRequest(data=','.join(data))
                response = stub.ReplicateData(replicate_request)
                if response.status == "SUCCESS":
                    print(f"[{ROLE}] - Data successfully replicated to {follower_ip}")
                else:
                    print(f"[{ROLE}] - Replication to {follower_ip} failed: {response.status}")
            except Exception as e:
                print(f"[{ROLE}] - Error replicating to {follower_ip}: {e}")
    
    def RequestVote(self, request, context):
        global CURRENT_TERM, VOTED_FOR
        term = request.term
        candidate_id = request.candidate_id

        try:
            # Votar si el termino del candidato es mayor al actual y aun no ha votado en este termino
            if term > CURRENT_TERM or (term == CURRENT_TERM and VOTED_FOR is None):
                VOTED_FOR = candidate_id
                CURRENT_TERM = term
                print(f"[{ROLE}] - Voted for {candidate_id} in term {term}")
                return service_pb2.VoteResponse(granted=True)
            
            print(f"[{ROLE}] - Vote denied to {candidate_id} in term {term}")
            return service_pb2.VoteResponse(granted=False)
        except grpc.RpcError as e:
            # Manejar el error de conexión y mostrar un mensaje simplificado
            print(f"[{ROLE}] - Error al contactar candidato {candidate_id}: {e.code()}")
            return service_pb2.VoteResponse(granted=False)

    def AppendEntries(self, request, context):
        global ROLE, LEADER_ID, TIMEOUT, LAST_HEARTBEAT, FIRST_RUN
        LEADER_ID = request.leader_id
        LAST_HEARTBEAT = time.time()  # Actualizar el tiempo del ultimo heartbeat recibido
        TIMEOUT = random.uniform(1.5, 3.0)  # Restablecer el timeout aleatorio
        
        if FIRST_RUN:
            FIRST_RUN = False
            TIMEOUT = random.uniform(1.5, 3.0)
        
        #print
        print(f"[{ROLE}] - Received heartbeat from leader {LEADER_ID}")
        return service_pb2.AppendEntriesResponse(success=True)
    
    def Ping(self, request, context):
        global ROLE
        # Devolver el role (follower, leader, etc.) y el estado (activo)
        return service_pb2.PingResponse(role=ROLE, state="active")
    
    #Degradar un líder a follower
    def DegradeToFollower(self, request, context):
        global ROLE
        print(f"[{ROLE}] - Degrading to follower by request.")
        ROLE = 'follower'
        return service_pb2.DegradeResponse(status="SUCCESS")
    
    # Metodods para hablar con el Proxy-------------------------------------------------
    
    def UpdateActiveNodes(self, request, context):
        global OTHER_DB_NODES
        print(f"[{ROLE}] - Received active node list: {request.active_nodes}")

        # Actualizar la lista de nodos activos
        ACTIVE_DB_NODES = list(request.active_nodes)
        OTHER_DB_NODES = [ip for ip in ACTIVE_DB_NODES if ip != SERVER_IP]
        print(f"[{ROLE}] - Active node list was updated: {OTHER_DB_NODES}")

        return service_pb2.UpdateResponse(status="SUCCESS")
    
    def request_active_nodes_from_proxy(proxy_ip):
        try:
            channel = grpc.insecure_channel(f'{proxy_ip}:50051')  # Conectar al proxy
            stub = service_pb2_grpc.DatabaseServiceStub(channel)
            request = service_pb2.PingRequest()
            response = stub.Ping(request)
            print(f"Received active nodes from proxy: {response.active_nodes}")
            ACTIVE_DB_NODES = list(response.active_nodes)  # Convertirlo a lista
            OTHER_DB_NODES = [ip for ip in ACTIVE_DB_NODES if ip != SERVER_IP]
            return OTHER_DB_NODES 
        except Exception as e:
            print(f"Error fetching active nodes from proxy: {e}")
            return []
        
    # Funciones para Actualizar el Database.csv
        
    def RequestDatabase(self, request, context):
        try:
            with open(DB_FILE, mode='r') as csv_file:
                reader = csv.reader(csv_file)
                rows = [','.join(row) for row in reader]
                result = "\n".join(rows)
            return service_pb2.DatabaseResponse(database=result)
        except Exception as e:
            print(f"Error al leer el archivo CSV: {e}")
            return service_pb2.DatabaseResponse(database="")
        

def start_election():
    global ROLE, CURRENT_TERM, VOTED_FOR, LEADER_ID, LAST_HEARTBEAT

    while True:
        time.sleep(0.1)  # El lider sigue activo?

        # Mirar si el tiempo desde el ultimo heartbeat supera el timeout
        if ROLE == 'follower' and (time.time() - LAST_HEARTBEAT) > TIMEOUT:
            print(f"[{ROLE}] - Timeout expired, starting election")
            ROLE = 'candidate'
            CURRENT_TERM += 1
            VOTED_FOR = None
            LEADER_ID = None

            # Pedir votos a los otros nodos y votarse a si mismo
            vote_count = 1
            for node_ip in OTHER_DB_NODES:
                try:
                    channel = grpc.insecure_channel(f'{node_ip}:50051')
                    stub = service_pb2_grpc.DatabaseServiceStub(channel)
                    vote_request = service_pb2.VoteRequest(term=CURRENT_TERM, candidate_id='self')
                    vote_response = stub.RequestVote(vote_request)
                    if vote_response.granted:
                        vote_count += 1
                except Exception as e:
                    #print(f"[{ROLE}] - Error contacting node {node_ip}: {e}")
                    print(f"[{ROLE}] - Error contacting node {node_ip}")

            # Si consigue la mayoria de votos se convierte en lider
            if vote_count > (len(OTHER_DB_NODES) + 1) // 2:
                print(f"[{ROLE}] - Became leader for term {CURRENT_TERM}")
                ROLE = 'leader'
                LEADER_ID = 'self'
                start_heartbeats()
            else:
                print(f"[{ROLE}] - Did not receive enough votes, remaining as follower")
                ROLE = 'follower'
                LAST_HEARTBEAT = time.time()

def start_heartbeats():
    global LEADER_ID, ROLE

    while ROLE == 'leader':
        #print
        print(f"[{ROLE}] - Sending heartbeats to followers")
        for node_ip in OTHER_DB_NODES:
            try:
                channel = grpc.insecure_channel(f'{node_ip}:50051')
                stub = service_pb2_grpc.DatabaseServiceStub(channel)
                heartbeat_request = service_pb2.AppendEntriesRequest(leader_id='self')
                stub.AppendEntries(heartbeat_request)
                #print
                print(f"[{ROLE}] - Heartbeat successfully sent to node {node_ip}")
            except grpc.RpcError as e:
                print(f"[{ROLE}] - Error sending heartbeat to node {node_ip}")
                status_code = e.code()
                if status_code == grpc.StatusCode.UNAVAILABLE:
                    print(f"[{ROLE}] - Node {node_ip} is unreachable (Status: UNAVAILABLE)")
                elif status_code == grpc.StatusCode.CANCELLED:
                    print(f"[{ROLE}] - Heartbeat to node {node_ip} was cancelled (Status: CANCELLED)")
                else:
                    print(f"[{ROLE}] - Unexpected error sending heartbeat to node {node_ip}")
        
        time.sleep(1)
        
def fetch_leader_and_sync():
    global ROLE, LEADER_ID

    # Hacer ping a cada nodo para determinar quién es el líder
    for node_ip in OTHER_DB_NODES:
        try:
            channel = grpc.insecure_channel(f'{node_ip}:50051')
            stub = service_pb2_grpc.DatabaseServiceStub(channel)
            ping_request = service_pb2.PingRequest()  # Crear una solicitud de ping
            response = stub.Ping(ping_request)  # Llamar al método Ping

            # Verificar si el nodo es el líder
            if response.role == 'leader':
                LEADER_ID = node_ip
                print(f"[{ROLE}] - Found leader: {LEADER_ID}")
                break  # Salir si encontramos al líder

        except grpc.RpcError as e:
            print(f"[{ROLE}] - Error contacting node {node_ip}")

    if LEADER_ID is not None:
        # Si encontramos al líder, se puede sincronizar el CSV si es necesario
        sync_with_leader(LEADER_ID)

def sync_with_leader(leader_ip):
    """Sincronizar con el líder para obtener datos actualizados."""
    try:
        channel = grpc.insecure_channel(f'{leader_ip}:50051')
        stub = service_pb2_grpc.DatabaseServiceStub(channel)
        request = service_pb2.DatabaseRequest()  # Solicitud para obtener la base de datos
        response = stub.RequestDatabase(request)  # Llamar al método RequestDatabase

        # Procesar la respuesta del líder
        if response.database:
            with open(DB_FILE, mode='w') as csv_file:
                csv_file.write(response.database)  # Escribir los datos del líder en el archivo
            print(f"[{ROLE}] - Database synchronized with leader {leader_ip}")

    except grpc.RpcError as e:
        print(f"[{ROLE}] - Error syncing with leader {leader_ip}")

def serve():
    global ROLE, CURRENT_TERM, VOTED_FOR, LEADER_ID
    ROLE = 'follower'
    CURRENT_TERM = 0
    VOTED_FOR = None
    LEADER_ID = None

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f"Database server ({ROLE}) started on port 50051.")
    
    # Sincronizar la base de datos del líder
    fetch_leader_and_sync()
    
    Thread(target=start_election).start()

    server.wait_for_termination()

if __name__ == '__main__':
    serve()