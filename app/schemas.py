from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator

MAX_NAME_LEN = 255
name_pattern = r'^[a-zA-Z]+$'

class Vertex(BaseModel):
    name: str = Field(max_length=MAX_NAME_LEN, pattern=name_pattern)

class Link(BaseModel):
    source: str = Field(max_length=MAX_NAME_LEN, pattern=name_pattern)
    target: str = Field(max_length=MAX_NAME_LEN, pattern=name_pattern)

class GraphInput(BaseModel):
    vertices: list[Vertex]
    links: list[Link]

    @field_validator('vertices')
    def check_vertices(cls, v):
        if not v:
            raise RequestValidationError(
                errors=[{
                    "loc": ["body", "vertices"],
                    "msg": "Vertices list must not be empty",
                    "type": "value_error"
                }]
            )
        return v

class GraphIdResponse(BaseModel):
    id: int

class GraphDetails(BaseModel):
    id: int
    vertices: list[Vertex]
    links: list[Link]

class AdjacencyResponse(BaseModel):
    adjacency: dict[str, list[str]]

class ErrorResponse(BaseModel):
    message: str

class ValidationErrorItem(BaseModel):
    loc: list[str]
    msg: str
    type: str

class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorItem] = None

