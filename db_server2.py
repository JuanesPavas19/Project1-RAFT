import grpc
from concurrent import futures
import time
import service_pb2
import service_pb2_grpc

class DatabaseService(service_pb2_grpc.DatabaseServiceServicer):
    def __init__(self):
        self.data = []
        self.followers = []  # Lista de followers dinámicos

    def WriteData(self, request, context):
        """Escribir datos y replicar a los followers."""
        self.data.append(request.data)
        print(f"Datos escritos: {self.data}")
        self.replicate_to_followers(request.data)
        return service_pb2.WriteResponse(status="Data written")

    def replicate_to_followers(self, data):
        """Enviar actualización a los followers dinámicos."""
        for follower_address in self.followers:
            try:
                with grpc.insecure_channel(follower_address) as channel:
                    stub = service_pb2_grpc.DatabaseServiceStub(channel)
                    request = service_pb2.WriteRequest(data=",".join(data))
                    response = stub.WriteData(request)
                    print(f"Replication to {follower_address}: {response.status}")
            except Exception as e:
                print(f"Failed to replicate to {follower_address}: {e}")

    def UpdateFollowers(self, request, context):
        """Actualizar la lista de followers desde el proxy."""
        self.followers = request.followers
        print(f"Followers actualizados: {self.followers}")
        return service_pb2.FollowersUpdateResponse(status="Followers updated")

    def Ping(self, request, context):
        """Responder al ping desde el proxy."""
        return service_pb2.PingResponse(status="alive")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseService(), server)
    server.add_insecure_port('[::]:50051')  # Cambiar el puerto según la instancia
    server.start()
    print("DB Server corriendo en el puerto 50051...")
    try:
        while True:
            time.sleep(86400)  # Mantener el servidor en ejecución
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()