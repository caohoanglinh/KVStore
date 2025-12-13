from fastapi import APIRouter
from app.schemas import *
from protos import kvstore_pb2_grpc
from protos import kvstore_pb2
import grpc

PRIME_ADDRESS = "localhost:50051"
BACKUP_ADDRESS = "localhost:50052"

prime_channel = grpc.insecure_channel(PRIME_ADDRESS)
backup_channel = grpc.insecure_channel(BACKUP_ADDRESS)

prime_stub = kvstore_pb2_grpc.KVStoreStub(prime_channel)
backup_stub = kvstore_pb2_grpc.KVStoreStub(backup_channel)

def is_alive(stub) -> bool:
    try:
        stub.Heartbeat(kvstore_pb2.BaseResponse(success=True))
        return True
    except Exception:
        return False
    
def get_active_stub():
    if is_alive(prime_stub):
        return prime_stub
    if is_alive(backup_stub):
        return backup_stub
    raise Exception("No KVStore server available")

kvstore_router = APIRouter(prefix="/kvstore")

@kvstore_router.post(
    "/getData",
    response_model=DataResponse
)
async def get_data(request: KeyRequest) -> DataResponse:
    try:
        stub = get_active_stub()   # <-- HEARTBEAT CHECK HERE

        grpc_req = kvstore_pb2.KeyRequest(key=request.key)
        grpc_res = stub.GetData(grpc_req)

        return DataResponse(
            success=grpc_res.success,
            message=grpc_res.message,
            data=grpc_res.data
        )

    except Exception as e:
        return DataResponse(
            success=False,
            message=str(e),
            data=""
        )


@kvstore_router.post(
    "/setData",
    response_model=BaseResponse
)
async def set_data(request: DataRequest) -> BaseResponse:
    try:
        if is_alive(prime_stub):
            stub = prime_stub
        else:
            stub = backup_stub

        grpc_req = kvstore_pb2.DataRequest(
            key=request.key,
            value=request.value
        )

        grpc_res = stub.SetData(grpc_req)

        return BaseResponse(
            success=grpc_res.success,
            message=grpc_res.message
        )

    except Exception as e:
        return BaseResponse(
            success=False,
            message=str(e)
        )

@kvstore_router.delete(
    "/deleteData",
    response_model=BaseResponse
)
async def delete_data(request: KeyRequest) -> BaseResponse:
    try:
        if is_alive(prime_stub):
            stub = prime_stub
        else:
            stub = backup_stub

        grpc_req = kvstore_pb2.KeyRequest(key=request.key)
        grpc_res = stub.DeleteData(grpc_req)

        return BaseResponse(
            success=grpc_res.success,
            message=grpc_res.message
        )

    except Exception as e:
        return BaseResponse(
            success=False,
            message=str(e)
        )
