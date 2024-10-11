import csv
import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import os
import time
import random
from threading import Thread

DB_FILE = 'database.csv'


ROLE = 'follower'
CURRENT_TERM = 0
VOTED_FOR = None
LEADER_ID = None
TIMEOUT = random.uniform(1.5, 3.0) 
LAST_HEARTBEAT = time.time()



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
            return service_pb2.WriteResponse(status="SUCCESS")
        else:
            print(f"[{ROLE}] - Write operation attempted on follower - Redirect to leader required")
            return service_pb2.WriteResponse(status="ERROR: Cannot write to follower")

    def RequestVote(self, request, context):
        global CURRENT_TERM, VOTED_FOR
        term = request.term
        candidate_id = request.candidate_id

        # Votar si el termino del candidato es mayor al actual y aun no ha votado en este termino
        if term > CURRENT_TERM or (term == CURRENT_TERM and VOTED_FOR is None):
            VOTED_FOR = candidate_id
            CURRENT_TERM = term
            print(f"[{ROLE}] - Voted for {candidate_id} in term {term}")
            return service_pb2.VoteResponse(granted=True)
        
        print(f"[{ROLE}] - Vote denied to {candidate_id} in term {term}")
        return service_pb2.VoteResponse(granted=False)

    def AppendEntries(self, request, context):
        global ROLE, LEADER_ID, TIMEOUT, LAST_HEARTBEAT
        LEADER_ID = request.leader_id
        LAST_HEARTBEAT = time.time()  # Actualizar el tiempo del ultimo heartbeat recibido
        TIMEOUT = random.uniform(1.5, 3.0)  # Restablecer el timeout aleatorio
        print(f"[{ROLE}] - Received heartbeat from leader {LEADER_ID}")
        return service_pb2.AppendEntriesResponse(success=True)
    
    def Ping(self, request, context):
        global ROLE
        # Devolver el role (follower, leader, etc.) y el estado (activo)
        return service_pb2.PingResponse(role=ROLE, state="active")
    
    # Metodods para hablar con el Proxy-------------------------------------------------
    
    def UpdateActiveNodes(self, request, context):
        global OTHER_DB_NODES
        print(f"[{ROLE}] - Received active node list: {request.active_nodes}")

        # Actualizar la lista de nodos activos
        OTHER_DB_NODES = list(request.active_nodes)

        return service_pb2.UpdateResponse(status="SUCCESS")
    
    def request_active_nodes_from_proxy(proxy_ip):
        try:
            channel = grpc.insecure_channel(f'{proxy_ip}:50051')  # Conectar al proxy
            stub = service_pb2_grpc.DatabaseServiceStub(channel)
            request = service_pb2.PingRequest()  # O algún otro tipo de request que tu proxy pueda manejar
            response = stub.Ping(request)  # O el método que maneje el proxy para enviar nodos activos
            print(f"Received active nodes from proxy: {response.active_nodes}")
            return list(response.active_nodes)  # Convertirlo a lista
        except Exception as e:
            print(f"Error fetching active nodes from proxy: {e}")
            return []
        

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
                    print(f"[{ROLE}] - Error contacting node {node_ip}: {e}")

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
        print(f"[{ROLE}] - Sending heartbeats to followers")
        for node_ip in OTHER_DB_NODES:
            try:
                channel = grpc.insecure_channel(f'{node_ip}:50051')
                stub = service_pb2_grpc.DatabaseServiceStub(channel)
                heartbeat_request = service_pb2.AppendEntriesRequest(leader_id='self')
                stub.AppendEntries(heartbeat_request)
                print(f"[{ROLE}] - Heartbeat successfully sent to node {node_ip}")
            except grpc.RpcError as e:
                status_code = e.code()
                if status_code == grpc.StatusCode.UNAVAILABLE:
                    print(f"[{ROLE}] - Node {node_ip} is unreachable (Status: UNAVAILABLE)")
                elif status_code == grpc.StatusCode.CANCELLED:
                    print(f"[{ROLE}] - Heartbeat to node {node_ip} was cancelled (Status: CANCELLED)")
                else:
                    print(f"[{ROLE}] - Unexpected error sending heartbeat to node {node_ip}: {e}")
        
        time.sleep(1)

def serve():
    global ROLE, CURRENT_TERM, VOTED_FOR, LEADER_ID, OTHER_DB_NODES
    ROLE = 'follower'
    CURRENT_TERM = 0
    VOTED_FOR = None
    LEADER_ID = None
    
    # Solicitar la lista de nodos activos al proxy
    proxy_ip = '3.227.12.220'  # La IP del proxy
    OTHER_DB_NODES = DatabaseService.request_active_nodes_from_proxy(proxy_ip)
    
    if OTHER_DB_NODES:
        print(f"Initial active nodes received from proxy: {OTHER_DB_NODES}")
    else:
        print("Failed to retrieve active nodes from proxy. Starting with an empty list.")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f"Database server ({ROLE}) started on port 50051.")
    
    Thread(target=start_election).start()

    server.wait_for_termination()

if __name__ == '__main__':
    serve()
