from concurrent import futures
import grpc
from protos import kvstore_pb2, kvstore_pb2_grpc

store = {}
prime_channel = grpc.insecure_channel('localhost:50051')
stub = kvstore_pb2_grpc.KVStoreStub(prime_channel)

class BackupService(kvstore_pb2_grpc.KVStoreServicer):

    def SetData(self, request, context):
        store[request.key] = {
            "value": request.data.value,
            "version": request.data.version
        }
        return kvstore_pb2.GrpcStatusResponse(
            success=True,
            message="Stored successfully"
        )
    
    def GetData(self, request, context):
        if request.key in store:
            data = store[request.key]
            return kvstore_pb2.GrpcDataResponse(
                success=True,
                message="Found",
                data=kvstore_pb2.GrpcData(
                    value=data["value"],
                    version=data["version"]
                )
            )
        else:
            return kvstore_pb2.GrpcDataResponse(
                success=False,
                message="Key not found"
            )
        
    def DeleteData(self, request, context):
        if request.key in store:
            del store[request.key]
            return kvstore_pb2.GrpcStatusResponse(success=True, message="Deleted")
        return kvstore_pb2.GrpcStatusResponse(success=False, message="Key not found")

    def HealthCheck(self, request, context):
        return kvstore_pb2.GrpcHealthCheckResponse(status=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kvstore_pb2_grpc.add_KVStoreServicer_to_server(BackupService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("KVStore gRPC server started on port 50052")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()