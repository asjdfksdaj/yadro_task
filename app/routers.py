from fastapi import APIRouter, status
from .schemas import GraphReadResponse, GraphCreateResponse, AdjacencyListResponse, GraphCreate, ErrorResponse, HTTPValidationError
from .crud import db_create_graph, db_get_graph, db_get_adj_list, db_delete_node
from .deps import Session
router = APIRouter(prefix="/api/graph")


@router.post("/", status_code=status.HTTP_201_CREATED, 
            description="Ручка для создания графа, принимает граф в виде списка вершин и списка ребер.",
            responses={
                201: {"model": GraphCreateResponse, "description": "Successfull response"}, # опечатка? 
                400: {"model": ErrorResponse, "description": "Failed to add graph"},
                422: {"model": HTTPValidationError, "description": "Validation Error"},
            })
async def create_graph(db: Session, new_graph: GraphCreate) -> GraphCreateResponse:
    result_graph_id = await db_create_graph(db, new_graph)

    return result_graph_id


@router.get("/{graph_id}/", 
            description="Ручка для чтения графа в виде списка вершин и списка ребер.",
            responses={
                200: {"model": GraphReadResponse, "description": "Successfull Response"},
                404: {"model": ErrorResponse, "description": "Graph entity not found"},
                422: {"model": HTTPValidationError, "description": "Validation Error"},
            })
async def read_graph(db: Session, graph_id: int) -> GraphReadResponse:
    result_graph = await db_get_graph(db, graph_id)

    return result_graph


@router.get("/{graph_id}/adjacency_list",
            description="Ручка для чтения графа в виде списка смежности.\nСписок смежности представлен в виде пар ключ - значение, где\n- ключ - имя вершины графа,\n- значение - список имен всех смежных вершин (всех потомков ключа).",
            responses={
                200: {"model": AdjacencyListResponse, "description": "Successfull Response"},
                404: {"model": ErrorResponse, "description": "Graph entity not found"},
                422: {"model": HTTPValidationError, "description": "Validation Error"},
            })
async def get_adjacency_list(db: Session, graph_id: int) -> AdjacencyListResponse:
    result_adj_list = await db_get_adj_list(db, graph_id, transpose=False)

    return result_adj_list


@router.get("/{graph_id}/reverse_adjacency_list", 
            description="Ручка для чтения транспонированного графа в виде списка смежности.\nСписок смежности представлен в виде пар ключ - значение, где\n- ключ - имя вершины графа,\n- значение - список имен всех смежных вершин (всех предков ключа в исходном графе).",
            responses={
                200: {"model": AdjacencyListResponse, "description": "Successfull Response"},
                404: {"model": ErrorResponse, "description": "Graph entity not found"},
                422: {"model": HTTPValidationError, "description": "Validation Error"},
            })
async def get_reverse_adjacency_list(db: Session, graph_id: int) -> AdjacencyListResponse:
    result_adj_list = await db_get_adj_list(db, graph_id, transpose=True)

    return result_adj_list


@router.delete("/{graph_id}/node/{node_name}", status_code=status.HTTP_204_NO_CONTENT,
               description="Ручка для удаления вершины из графа по ее имени.",
               responses={
                   204: {"description": "Successfull response"},
                   404: {"model": ErrorResponse, "description": "Graph entity not found"},
                   422: {"model": HTTPValidationError, "description": "Validation Error"},
               })
async def delete_node(db: Session, graph_id: int, node_name: str):
    await db_delete_node(db, graph_id, node_name)
    return None
