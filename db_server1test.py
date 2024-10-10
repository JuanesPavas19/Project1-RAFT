import csv
import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures
import os

# Archivo CSV para simular la base de datos
DB_FILE = 'database.csv'

# Variable para identificar si la instancia es líder o follower
ROLE = os.getenv('DB_ROLE', 'follower')  # Se ssigna 'follower' por defecto, pero puede cambiarse a 'leader'

# Lista de direcciones IP de los followers
FOLLOWERS = os.getenv('FOLLOWERS', '').split(',')

class DatabaseService(service_pb2_grpc.DatabaseServiceServicer):

    def ReadData(self, request, context):
        print(f"[{ROLE}] - Read operation requested")
        
        with open(DB_FILE, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            rows = [','.join(row) for row in reader]
            result = "\n".join(rows)
        
        print(f"[{ROLE}] - Read operation completed")
        return service_pb2.ReadResponse(result=result)

    def WriteData(self, request, context):
        if ROLE == 'leader':
            print(f"[{ROLE}] - Write operation requested")
            data = request.data.split(',')
            new_id = data[0]  # El ID a verificar

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

            # Replicar datos en los followers
            self.replicate_to_followers(data)

            return service_pb2.WriteResponse(status="SUCCESS")
        else:
            print(f"[{ROLE}] - Write operation attempted on follower - Redirect to leader required")
            return service_pb2.WriteResponse(status="ERROR: Cannot write to follower")

    # def ReplicateData(self, request, context):
    #     print(f"[{ROLE}] - Replication request received")
    #     data = request.data.split(',')
    #     with open(DB_FILE, mode='a') as csv_file:
    #         writer = csv.writer(csv_file)
    #         writer.writerow(data)
    #     print(f"[{ROLE}] - Replication completed")
    #     return service_pb2.WriteResponse(status="SUCCESS")
    
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
            return service_pb2.WriteResponse(status="ERROR: {e}")

    def replicate_to_followers(self, data):
        for follower in FOLLOWERS:
            try:
                channel = grpc.insecure_channel(follower)
                stub = service_pb2_grpc.DatabaseServiceStub(channel)
                request = service_pb2.WriteRequest(data=",".join(data))
                response = stub.ReplicateData(request)
                print(f"Replication to {follower} completed with status: {response.status}")
            except Exception as e:
                print(f"Failed to replicate to {follower}: {e}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f"Database server ({ROLE}) started on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()