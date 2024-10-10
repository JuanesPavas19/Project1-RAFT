import csv
import service_pb2
import service_pb2_grpc
import grpc
from concurrent import futures

# Archivo CSV para simular la base de datos
DB_FILE = 'database.csv'

class DatabaseService(service_pb2_grpc.DatabaseServiceServicer):

    def ReadData(self, request, context):
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
        
        return service_pb2.WriteResponse(status="SUCCESS")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Database server started on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()