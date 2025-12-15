from concurrent import futures
import grpc
from protos import kvstore_pb2, kvstore_pb2_grpc
import os
DATA_PATH = "data/prime.txt"
os.makedirs("data", exist_ok=True)


store = {}
backup_channel = grpc.insecure_channel('localhost:50052')
stub = kvstore_pb2_grpc.KVStoreStub(backup_channel)

class PrimeService(kvstore_pb2_grpc.KVStoreServicer):

    def SetData(self, request, context):
        response = stub.SetData(kvstore_pb2.GrpcDataRequest(
            key=request.key,
            data=kvstore_pb2.GrpcData(value=request.data.value, version=request.data.version)
        ))
        if response.success:
            store[request.key] = {
                "value": request.data.value,
                "version": request.data.version
            }
            with open(DATA_PATH, "a", encoding="utf-8") as f:
                f.write(f"SET {request.key} {request.data.value} {request.data.version}\n")
       
            return kvstore_pb2.GrpcStatusResponse(
                success=True,
                message="Stored successfully"
            )       
        else:
            return kvstore_pb2.GrpcStatusResponse(
                success=False,
                message="Backup store failed to store data"
        )
   
    def GetData(self, request, context):
        backup_response = stub.GetData(kvstore_pb2.GrpcDataRequest(key=request.key))
        if backup_response.success:
            data = {
                "value": backup_response.data.value,
                "version": backup_response.data.version
            }

            store[request.key] = data

            with open(DATA_PATH, "a", encoding="utf-8") as f:
                f.write(
                    f"GET {request.key} {data['value']} {data['version']}\n"
                )

            return kvstore_pb2.GrpcDataResponse(
                success=True,
                message="Found",
                data=kvstore_pb2.GrpcData(
                    value=data["value"],
                    version=data["version"]
                )
            )
        
        return kvstore_pb2.GrpcDataResponse(
            success=False,
            message="Key not found"
        )

    def DeleteData(self, request, context):
        if request.key in store:
            with open(DATA_PATH, "a", encoding="utf-8") as f:
                    f.write(f"DELETE {request.key}\n")
            del store[request.key]            
            return kvstore_pb2.GrpcStatusResponse(success=True, message="Deleted")
        return kvstore_pb2.GrpcStatusResponse(success=False, message="Key not found")

    def HealthCheck(self, request, context):
        return kvstore_pb2.GrpcHealthCheckResponse(status=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kvstore_pb2_grpc.add_KVStoreServicer_to_server(PrimeService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("KVStore gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()