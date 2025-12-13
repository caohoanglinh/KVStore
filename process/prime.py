import grpc
from protos import kvstore_pb2 
from protos import kvstore_pb2_grpc

from concurrent import futures
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


AOF_PATH = "data/prime.aof"
BACKUP_ADDRESS = "localhost:50052"

class PrimeKVStore(kvstore_pb2_grpc.KVStoreServicer):
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()
        self._load_aof()

        # gRPC stub to Backup
        self.backup_channel = grpc.insecure_channel(BACKUP_ADDRESS)
        self.backup_stub = kvstore_pb2_grpc.KVStoreStub(self.backup_channel)

    # ---------- Persistence ----------

    def _load_aof(self):
        if not os.path.exists(AOF_PATH):
            return

        with open(AOF_PATH, "r") as f:
            for line in f:
                parts = line.strip().split(" ", 2)
                if parts[0] == "SET":
                    self.store[parts[1]] = parts[2]
                elif parts[0] == "DEL":
                    self.store.pop(parts[1], None)

    def _append_aof(self, line: str):
        with open(AOF_PATH, "a") as f:
            f.write(line + "\n")

    # ---------- gRPC APIs ----------

    def GetData(self, request, context):
        with self.lock:
            if request.key in self.store:
                return kvstore_pb2.DataResponse(
                    success=True,
                    message="FOUND",
                    data=self.store[request.key]
                )
            return kvstore_pb2.DataResponse(
                success=False,
                message="NOT_FOUND",
                data=""
            )

    def SetData(self, request, context):
        with self.lock:
            self.store[request.key] = request.value
            self._append_aof(f"SET {request.key} {request.value}")

            # Replicate to backup
            try:
                self.backup_stub.SetData(request)
            except Exception:
                pass  # Backup failure tolerated

        return kvstore_pb2.BaseResponse(success=True, message="OK")

    def DeleteData(self, request, context):
        with self.lock:
            self.store.pop(request.key, None)
            self._append_aof(f"DEL {request.key}")

            try:
                self.backup_stub.DeleteData(request)
            except Exception:
                pass

        return kvstore_pb2.BaseResponse(success=True, message="OK")

    def Heartbeat(self, request, context):
        return kvstore_pb2.BaseResponse(success=True, message="PRIME_ALIVE")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    kvstore_pb2_grpc.add_KVStoreServicer_to_server(
        PrimeKVStore(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Prime running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
