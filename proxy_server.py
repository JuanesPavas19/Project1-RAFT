import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import random

DB_SERVERS = [
    {'host': '10.0.2.250', 'port': '50051'},   
    {'host': '10.0.2.234', 'port': '50051'},   
    {'host': '10.0.2.167', 'port': '50051'}    
]

class ProxyService(service_pb2_grpc.DatabaseServiceServicer):

    def __init__(self):
        self.db_channels = {}
        for server in DB_SERVERS:
            channel = grpc.insecure_channel(f'{server["host"]}:{server["port"]}')
            stub = service_pb2_grpc.DatabaseServiceStub(channel)
            self.db_channels[server["host"]] = stub

        self.current_leader = None

    def find_leader(self):
        """ Método para identificar cuál nodo es el líder """
        for ip, stub in self.db_channels.items():
            try:
                # Solicitar un heartbeat para verificar si el nodo es el lider
                response = stub.AppendEntries(service_pb2.AppendEntriesRequest(leader_id=''))
                if response.success:
                    self.current_leader = ip
                    print(f"Leader identified: {self.current_leader}")
                    return
            except Exception as e:
                print(f"Error contacting node {ip}: {e}")

        print("No leader found.")
        self.current_leader = None

    def ReadData(self, request, context):
        if self.current_leader is None:
            self.find_leader()

        # Seleccionar un follower aleatorio si hay un lider identificado
        followers = [ip for ip in self.db_channels.keys() if ip != self.current_leader]
        if followers:
            follower_stub = random.choice([self.db_channels[ip] for ip in followers])
            response = follower_stub.ReadData(request)
            return response
        else:
            return service_pb2.ReadResponse(result="ERROR: No followers available.")

    def WriteData(self, request, context):
        if self.current_leader is None:
            self.find_leader()

        if self.current_leader:
            leader_stub = self.db_channels[self.current_leader]
            response = leader_stub.WriteData(request)
            return response
        else:
            return service_pb2.WriteResponse(status="ERROR: No leader available for writing.")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(ProxyService(), server)
    server.add_insecure_port('[::]:50052')  # Puerto del proxy
    server.start()
    print("Proxy server started on port 50052.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
