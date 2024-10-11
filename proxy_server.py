import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import random
import time, threading

DB_SERVERS = [
    {'host': '10.0.2.172', 'port': '50051'},   
    {'host': '10.0.2.100', 'port': '50051'},   
    {'host': '10.0.2.164', 'port': '50051'}    
]

class ProxyService(service_pb2_grpc.DatabaseServiceServicer):

    def __init__(self):
        self.db_channels = {}
        for server in DB_SERVERS:
            # Crear el canal con timeout para mantener la conexión viva
            channel = grpc.insecure_channel(f'{server["host"]}:{server["port"]}', options=[
                ('grpc.keepalive_timeout_ms', 1000)  # Timeout de 1 segundo
            ])
            stub = service_pb2_grpc.DatabaseServiceStub(channel)
            self.db_channels[server["host"]] = stub

        self.current_leader = None
        self.server_status = {server["host"]: {"role": "unknown", "state": "inactive"} for server in DB_SERVERS}

        # Iniciar el ciclo de pings
        self.start_ping_loop()

    def start_ping_loop(self):
        """Inicia un ciclo que realiza pings periódicos a los db_servers."""
        def ping_servers():
            while True:
                for ip, stub in self.db_channels.items():
                    try:
                        # Enviar el ping y recibir el estado
                        response = stub.Ping(service_pb2.PingRequest(message="ping"))
                        if self.server_status[ip]["state"] != "active" or self.server_status[ip]["role"] != response.role:
                            # Solo mostrar si hay un cambio en el estado o rol del nodo
                            print(f"Node {ip} is now active with role {response.role}")
                        self.server_status[ip] = {"role": response.role, "state": response.state}
                    
                        # Si encontramos un nuevo líder, actualizar
                        if response.role == "leader":
                            if self.current_leader != ip:
                                self.current_leader = ip
                                print(f"\n New leader identified: {self.current_leader}")
                                self.send_active_list_to_all()  # Enviar lista de nodos activos

                    except grpc.RpcError as e:
                        if self.server_status[ip]["state"] != "inactive":
                            # Solo mostrar el error si el nodo no estaba ya marcado como inactivo
                            if e.code() == grpc.StatusCode.UNAVAILABLE:
                                print(f"Node {ip} is unavailable (Connection refused)")
                            else:
                                print(f"Error contacting node {ip}: {e.details() if e.details() else 'Unknown error'}")
                            # Si falla el ping, marcar como inactivo
                            self.server_status[ip] = {"role": "unknown", "state": "inactive"}
                    
                # Imprimir el estado actual de los servidores solo si hubo cambios
                print("\nEstado actual de los servidores:")
                for ip, status in self.server_status.items():
                    print(f"Servidor {ip} - Rol: {status['role']}, Estado: {status['state']}")
            
                # Enviar la lista de nodos activos al final de cada ciclo de ping
                self.send_active_list_to_all()

                # Esperar X segundos antes del próximo ping
                time.sleep(5)

        # Ejecutar el ping en un hilo separado
        ping_thread = threading.Thread(target=ping_servers)
        ping_thread.daemon = True  # El hilo se cerrará cuando el programa principal termine
        ping_thread.start()

    # def send_active_list_to_all(self):
    #     """Envía la lista de instancias activas a todos los nodos."""
    #     active_instances = [ip for ip, status in self.server_status.items() if status["state"] == "active"]
        
    #     for ip, stub in self.db_channels.items():
    #         try:
    #             stub.UpdateActiveInstances(service_pb2.UpdateRequest(active_instances=active_instances))
    #             print(f"Active instances list sent to {ip}: {active_instances}")
    #         except grpc.RpcError as e:
    #             print(f"Failed to send active instances list to {ip}: {e}")
    
    def send_active_list_to_all(self):
        """Envía la lista de instancias activas a todos los nodos activos."""
        active_instances = [ip for ip, status in self.server_status.items() if status["state"] == "active"]

        for ip, stub in self.db_channels.items():
            # Verificamos si el nodo está activo antes de enviar la lista
            if self.server_status[ip]["state"] == "active":
                try:
                    # Enviamos la lista de instancias activas
                    request = service_pb2.UpdateRequest(active_nodes=active_instances)
                    stub.UpdateActiveNodes(request)
                    print(f"Sent active node list to {ip}: {active_instances}")
                except grpc.RpcError as e:
                    # Capturamos el error solo si no es repetido
                    print(f"Error sending active node list to {ip}: {e.details() if e.details() else 'Unknown error'}")
                    # Marcar como inactivo en caso de error
                    self.server_status[ip]["state"] = "inactive"

    def find_leader(self):
        """Encuentra y asigna el líder actual."""
        for ip, status in self.server_status.items():
            if status["role"] == "leader" and status["state"] == "active":
                self.current_leader = ip
                print(f"Líder encontrado: {self.current_leader}")
                return

        print("No se encontró líder activo.")
        self.current_leader = None

    def ReadData(self, request, context):
        if self.current_leader is None:
            self.find_leader()

        followers = [ip for ip, status in self.server_status.items() if status["role"] == "follower" and status["state"] == "active"]
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