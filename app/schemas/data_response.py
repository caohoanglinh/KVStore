from app.schemas.base_response import BaseResponse

class DataResponse(BaseResponse):
    success: bool
    message: str
    data: str