from fastapi import APIRouter
from app.schemas import *


kvstore_router = APIRouter(prefix="/kvstore")

@kvstore_router.post(
    "/getData",
    name="Get Data",
    summary="Get Data from KVStore",
    response_model=DataResponse
)
async def get_data(key: str) -> DataResponse:
    try: 
        # TODO: Implement the logic
        data = "sample_data"  # Placeholder for actual data retrieval logic
        return DataResponse(success=True, message="SUCCESS", data=data)
    except Exception as e:
        return DataResponse(success=False, message="FAILED", data="")


@kvstore_router.post(
    "/setData",
    name="Set Data",
    summary="Set Data in KVStore",
    response_model=BaseResponse
)
async def set_data(request: DataRequest) -> BaseResponse:
    try:
        # TODO: Implement the logic
        return BaseResponse(success=True, message="SUCCESS")
    except Exception as e:
        return BaseResponse(success=False, message="FAILED")


@kvstore_router.delete(
    "/deleteData",
    name="Delete Data",
    summary="Delete Data from KVStore",
    response_model=BaseResponse
)
async def delete_data(key: str) -> BaseResponse:
    try: 
        # TODO: Implement the logic
        return BaseResponse(success=True, message="SUCCESS")
    except Exception as e:
        return BaseResponse(success=False, message="FAILED")