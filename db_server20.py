import csv
import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import sys

# Definir el nombre del archivo CSV (Base de datos básica)
DB_FILE = 'database.csv'

# Lista de direcciones de los followers (IPs privadas de las instancias followers)
FOLLOWERS = ['10.0.2.173:50051', '10.0.2.174:50051']  # Actualiza estas direcciones

class DatabaseService(service_pb2_grpc.DatabaseServiceServicer):
    def __init__(self, role):
        self.role = role  # "leader" o "follower"

    def ReadData(self, request, context):
        query = request.query
        with open(DB_FILE, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            rows = [','.join(row) for row in reader]
            result = "\n".join(rows)

        return service_pb2.ReadResponse(result=result)

    def WriteData(self, request, context):
        data = request.data.split(',')
        new_id = data[0]  # El ID a verificar

        # Verificar si el ID ya existe
        with open(DB_FILE, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if row[0] == new_id:
                    return service_pb2.WriteResponse(status="ERROR: ID ya existente")

        # Si el ID no existe, agregar al CSV
        with open(DB_FILE, mode='a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data)

        # Solo si es líder, replicar la escritura en los followers
        if self.role == "leader":
            self.replicate_to_followers(data)

        return service_pb2.WriteResponse(status="SUCCESS")

    def replicate_to_followers(self, data):
        """Enviar actualización a los followers para replicar el cambio."""
        for follower_address in FOLLOWERS:
            try:
                # Conectar con el follower
                with grpc.insecure_channel(follower_address) as channel:
                    stub = service_pb2_grpc.DatabaseServiceStub(channel)
                    # Enviar la solicitud de replicación
                    request = service_pb2.WriteRequest(data=",".join(data))
                    response = stub.WriteData(request)
                    print(f"Replication to {follower_address}: {response.status}")
            except Exception as e:
                print(f"Failed to replicate to {follower_address}: {e}")

def serve(role):
    # Crear y configurar el servidor gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseService(role), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    
    if role == "leader":
        print("Leader server started on port 50051.")
    else:
        print("Follower server started on port 50051.")
    
    server.wait_for_termination()

if __name__ == '__main__':
    # Pasar el rol como argumento al ejecutar el script
    if len(sys.argv) != 2 or sys.argv[1] not in ["leader", "follower"]:
        print("Usage: python db_server.py [leader|follower]")
        sys.exit(1)

    # Obtener el rol (líder o follower)
    role = sys.argv[1]

    # Ejecutar el servidor con el rol especificado
    serve(role)

# Para iniciar el leader
# python db_server.py leader

# PAra iniciar un follower
# python db_server.py follower