# Clientes
pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto


ssh -i bit.pem ubuntu@<private-ip-of-database-instance>

# Intancias
sudo apt update  
sudo apt install python3-venv

python3 -m venv env
source env/bin/activate
deactivate

pip install --upgrade pip
pip install grpcio grpcio-tools protobuf

nano service.proto
nano db_server.py
nano proxy_server.py

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto

# Opcional db_server
touch database.csv

python3 db_server.py
python3 proxy_server.py

# Ejecución como leader
DB_ROLE=leader python3 db_server.py
DB_ROLE=leader FOLLOWERS=10.0.2.100:50051,10.0.2.164:50051 python3 db_server.py


# Conectar al db_server desde proxy
nano bit.pem
ssh -i bit.pem ubuntu@10.0.2.172


# Borrar Archivos
 rm -r service.proto service_pb2.py service_pb2_grpc.py db_server.py database.csv __pycache__
  rm -r service.proto service_pb2.py service_pb2_grpc.py proxy_server.py  __pycache__
  rm -r service.proto service_pb2.py service_pb2_grpc.py __pycache__
  rm db_server.py

  # Utiles
  cat database.csv

  # Nota
  """El Contenido de db_server.py y db_server1test.py son el mismo solo que uno esta con algunos comentarios para facilitar lectura de terminal en pruebas :)"""