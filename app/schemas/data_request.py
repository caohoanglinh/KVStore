from app.schemas.key_request import KeyRequest

class DataRequest(KeyRequest):
    key: str
    value: str