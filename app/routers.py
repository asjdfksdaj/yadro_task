from fastapi import APIRouter, status
from .schemas import (
    GraphDetails, GraphIdResponse, AdjacencyResponse,
    GraphInput, ErrorResponse, ValidationErrorResponse
)
from .crud import (
    create_graph_in_db, fetch_graph, fetch_adj_list, delete_vertex
)
from .deps import SessionType  # ← Правильный импорт

router = APIRouter(prefix="/api/graph")

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="Создать граф из списка вершин и связей.",
    responses={
        201: {"model": GraphIdResponse, "description": "Граф создан"},
        400: {"model": ErrorResponse, "description": "Ошибка сохранения"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
    }
)
async def create_graph_endpoint(db: SessionType, graph_data: GraphInput):
    graph_id = await create_graph_in_db(db, graph_data)
    return {"id": graph_id}


@router.get(
    "/{graph_id}/",
    description="Получить граф по ID в виде вершин и связей.",
    responses={
        200: {"model": GraphDetails, "description": "Данные графа"},
        404: {"model": ErrorResponse, "description": "Граф не найден"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
    }
)
async def get_graph_by_id(db: SessionType, graph_id: int):
    graph_info = await fetch_graph(db, graph_id)
    return graph_info


@router.get(
    "/{graph_id}/adjacency_list",
    description="Получить список смежности графа.",
    responses={
        200: {"model": AdjacencyResponse, "description": "Список смежности"},
        404: {"model": ErrorResponse, "description": "Граф не найден"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
    }
)
async def get_adj_list(db: SessionType, graph_id: int):
    adjacency = await fetch_adj_list(db, graph_id, transpose=False)
    return {"adjacency": adjacency}


@router.get(
    "/{graph_id}/reverse_adjacency_list",
    description="Получить транспонированный список смежности.",
    responses={
        200: {"model": AdjacencyResponse, "description": "Транспонированный список"},
        404: {"model": ErrorResponse, "description": "Граф не найден"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
    }
)
async def get_rev_adj_list(db: SessionType, graph_id: int):
    adjacency = await fetch_adj_list(db, graph_id, transpose=True)
    return {"adjacency": adjacency}


@router.delete(
    "/{graph_id}/node/{vertex_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удалить вершину по имени.",
    responses={
        204: {"description": "Успешное удаление"},
        404: {"model": ErrorResponse, "description": "Граф или вершина не найдены"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации"},
    }
)
async def remove_vertex(db: SessionType, graph_id: int, vertex_name: str):
    await delete_vertex(db, graph_id, vertex_name)
    return None
