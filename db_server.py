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


OTHER_DB_NODES = ['10.0.2.162', '10.0.2.234']

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
            except Exception as e:
                print(f"[{ROLE}] - Error sending heartbeat to node {node_ip}: {e}")
        time.sleep(1) 

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
    
    Thread(target=start_election).start()

    server.wait_for_termination()

if __name__ == '__main__':
    serve()
