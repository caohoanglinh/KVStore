from pydantic import BaseModel

class KeyRequest(BaseModel):
    key: str