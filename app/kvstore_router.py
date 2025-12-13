from fastapi import APIRouter, Depends
from app.schemas import *
from app.kvstore_service import kvstore_service, KVStoreService


kvstore_router = APIRouter(prefix="/kvstore")

def get_kvstore_service():
    return kvstore_service

@kvstore_router.post(
    "/getData",
    name="Get Data",
    summary="Get Data from KVStore",
    response_model=DataResponse
)
async def get_data(
    request: KeyRequest,
    kvstore_service: KVStoreService = Depends(get_kvstore_service)
) -> DataResponse:
    try: 
        success, data = await kvstore_service.getData(request.key)
        if not success:
            raise Exception(data)
        return DataResponse(success=True, message="SUCCESS", data=data)
    except Exception as e:
        return DataResponse(success=False, message=str(e), data="")


@kvstore_router.post(
    "/setData",
    name="Set Data",
    summary="Set Data in KVStore",
    response_model=BaseResponse
)
async def set_data(
    request: DataRequest,
    kvstore_service: KVStoreService = Depends(get_kvstore_service)
) -> BaseResponse:
    try:
        success, message = await kvstore_service.setData(request.key, request.data)
        if not success:
            raise Exception(message)
        return BaseResponse(success=True, message="SUCCESS")
    except Exception as e:
        return BaseResponse(success=False, message=str(e))


@kvstore_router.delete(
    "/deleteData",
    name="Delete Data",
    summary="Delete Data from KVStore",
    response_model=BaseResponse
)
async def delete_data(
    request: KeyRequest,
    kvstore_service: KVStoreService = Depends(get_kvstore_service)
) -> BaseResponse:
    try: 
        success, message = await kvstore_service.deleteData(request.key)
        if not success:
            raise Exception(message)
        return BaseResponse(success=True, message="SUCCESS")
    except Exception as e:
        return BaseResponse(success=False, message=str(e))