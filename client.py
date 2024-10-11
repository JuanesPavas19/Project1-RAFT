import service_pb2
import service_pb2_grpc
import grpc

PROXY_HOST = '18.214.36.227'  #IP pública del proxy
PROXY_PORT = '50052'

def run():
    with grpc.insecure_channel(f'{PROXY_HOST}:{PROXY_PORT}') as channel:
        stub = service_pb2_grpc.DatabaseServiceStub(channel)

        # Preguntar al usuario si quiere leer o escribir
        action = input("¿Quires hacer read o write? (read/write): ").strip().lower()

        if action == "read":
            # Solicitud de lectura
            read_request = service_pb2.ReadRequest(query="SELECT *")
            read_response = stub.ReadData(read_request)
            print(f'Read Response:\n{read_response.result}')

        elif action == "write":
            # Solicitud de escritura
            new_id = input("Ingrese ID: ").strip()
            name = input("Ingrese un NOmbre: ").strip()
            email = input("Ingrese un correo: ").strip()

            # Crear solicitud de escritura
            write_request = service_pb2.WriteRequest(data=f"{new_id},{name},{email}")
            write_response = stub.WriteData(write_request)
            print(f'Write Response: {write_response.status}')

        else:
            print("Invalid action. Please enter 'read' or 'write'.")

if __name__ == '__main__':
    run()