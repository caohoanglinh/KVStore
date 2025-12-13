from concurrent import futures
import grpc
from protos import kvstore_pb2
from protos import kvstore_pb2_grpc

store = {}
backup_channel = grpc.insecure_channel('localhost:50052')
stub = kvstore_pb2_grpc.KVStoreStub(backup_channel)

class PrimeService(kvstore_pb2_grpc.KVStoreServicer):

    def SetData(self, request, context):
        store[request.key] = {
            "value": request.data.value,
            "version": request.data.version
        }
        response = stub.SetData(kvstore_pb2.GrpcDataRequest(
            key="foo",
            data=kvstore_pb2.GrpcData(value="bar", version=1)
        ))
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
    kvstore_pb2_grpc.add_KVStoreServicer_to_server(kvstore_pb2_grpc.KVStoreServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("KVStore gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()