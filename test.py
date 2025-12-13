# test_backup.py
import grpc
from protos import kvstore_pb2, kvstore_pb2_grpc

# Connect to backup server
channel = grpc.insecure_channel('localhost:50052')
stub = kvstore_pb2_grpc.KVStoreStub(channel)

# 1️⃣ Save data
response = stub.SetData(kvstore_pb2.GrpcDataRequest(
    key="foo",
    data=kvstore_pb2.GrpcData(value="bar2", version=2)
))
print("SetData:", response.success, response.message)

# 2️⃣ Get data
response = stub.GetData(kvstore_pb2.GrpcKeyRequest(key="foo"))
if response.success:
    print("GetData:", response.data.value, response.data.version)
else:
    print("GetData failed:", response.message)