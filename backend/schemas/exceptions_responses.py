from pydantic import BaseModel


class SimpleDetailSchema(BaseModel):
    """
    Schema used for frequent status codes except for 500.
    """

    detail: str


class DetailSchema(BaseModel):
    """
    Schema used for 500 status code.
    """

    message: str
    error_type: str


class InternalServerErrorResponseSchema(BaseModel):
    detail: DetailSchema
