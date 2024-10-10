import grpc
from concurrent import futures
import time
import service_pb2
import service_pb2_grpc

class ProxyService(service_pb2_grpc.DatabaseServiceServicer):
    def __init__(self):
        self.followers = []  # Lista de followers dinámicos
        self.possible_follower_addresses = ['localhost:50051', 'localhost:50052', 'localhost:50053']  # Ejemplo de direcciones

    def check_followers(self):
        """Verificar qué instancias son followers activos."""
        # Este método puede enviar un "ping" a cada instancia conocida y actualizar la lista de followers.
        # Por simplicidad, puedes almacenar las direcciones IP o puertos de las instancias.
        active_followers = []
        for address in self.possible_follower_addresses:
            try:
                with grpc.insecure_channel(f'{address}') as channel:
                    stub = service_pb2_grpc.DatabaseServiceStub(channel)
                    # Enviar un ping para comprobar la actividad
                    response = stub.Ping(service_pb2.PingRequest())
                    if response.status == "alive":
                        active_followers.append(address)
            except Exception as e:
                print(f"Follower {address} no responde.")
        
        # Actualizar la lista de followers dinámicamente
        self.followers = active_followers
        return self.followers

    def send_followers_to_leader(self, leader_address):
        """Notificar al líder la lista actualizada de followers."""
        with grpc.insecure_channel(leader_address) as channel:
            stub = service_pb2_grpc.DatabaseServiceStub(channel)
            request = service_pb2.FollowersUpdateRequest(followers=self.followers)
            response = stub.UpdateFollowers(request)

    def Ping(self, request, context):
        """Responder al ping desde el proxy."""
        return service_pb2.PingResponse(status="alive")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(ProxyService(), server)
    server.add_insecure_port('[::]:50050')
    server.start()
    print("Proxy corriendo en el puerto 50050...")
    try:
        while True:
            time.sleep(86400)  # Mantener el servidor en ejecución
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()