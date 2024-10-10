import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import random

# IPs de las instancias de base de datos
DB_SERVERS = [
    {'host': '10.0.2.172', 'port': '50051', 'role': 'leader'},   # Leader Test
    {'host': '10.0.2.100', 'port': '50051', 'role': 'follower'}, # Follower1
    {'host': '10.0.2.164', 'port': '50051', 'role': 'follower'}  # Follower2
]

# Redes Ip Elasticas?
#10.0.2.172 10.0.2.173 10.0.2.174

class ProxyService(service_pb2_grpc.DatabaseServiceServicer):

    def __init__(self):
        # Crear canales gRPC para cada servidor de base de datos
        self.db_channels = {}
        for server in DB_SERVERS:
            channel = grpc.insecure_channel(f'{server["host"]}:{server["port"]}')
            stub = service_pb2_grpc.DatabaseServiceStub(channel)
            self.db_channels[server['role']] = stub

    def ReadData(self, request, context):
        # Seleccionar un follower aleatorio para redirigir la lectura
        followers = [stub for role, stub in self.db_channels.items() if role == 'follower']
        follower_stub = random.choice(followers)
        response = follower_stub.ReadData(request)
        return response

    def WriteData(self, request, context):
        # Redirigir la escritura al líder
        leader_stub = self.db_channels['leader']
        response = leader_stub.WriteData(request)
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(ProxyService(), server)
    server.add_insecure_port('[::]:50052')  # Puerto del proxy
    server.start()
    print("Proxy server started on port 50052.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()