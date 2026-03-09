from pydantic import BaseModel


class SimpleDetailSchema(BaseModel):
    detail: str
