import queue
from fastapi.exceptions import RequestValidationError
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from . import schemas
from .models import Graph, Node, Edge

def raise_validation_error(message: str, loc: list[str] = None):
    if loc is None:
        loc = []

    errors = [
        {
            "loc": loc,
            "msg": message,
            "type": "value_error"
        }
    ]
    raise RequestValidationError(
        errors=errors
    )

async def db_create_graph(db: AsyncSession, graph: schemas.GraphCreate) -> schemas.GraphCreateResponse:
    adj_list = dict()
    nodes_status = dict()

    for node in graph.nodes:
        adj_list[node.name] = []
        nodes_status[node.name] = 0

    for edge in graph.edges:
        if edge.source not in adj_list:
            raise_validation_error(f"Node {edge.source} not found in the graph", ["body", "edges", "source"])
        if edge.target not in adj_list:
            raise_validation_error(f"Node {edge.target} not found in the graph", ["body", "edges", "target"])
        adj_list[edge.source].append(edge.target)

    for node in graph.nodes:
        node_name = node.name

        if nodes_status[node_name] == 0:
            dfs_stack = []

            dfs_stack.append(node_name)

            while (len(dfs_stack) > 0):
                v = dfs_stack[-1]

                if nodes_status[v] != 0:
                    nodes_status[v] = 1
                    dfs_stack.pop()
                    continue
                else:
                    nodes_status[v] = 2

                for v_neighbour in adj_list[v]:
                    if nodes_status[v_neighbour] == 2:
                        # raise HTTPException(422, "Graph is not DAG")
                        raise_validation_error("Graph is not DAG", ["body", "edges"])
                    elif nodes_status[v_neighbour] == 0:
                        dfs_stack.append(v_neighbour)

    graph_db = Graph()
    db.add(graph_db)

    await db.flush()

    nodes_entity = dict()

    for node in graph.nodes:
        node_db = Node(
            name=node.name,
            graph_id=graph_db.id
        )
        db.add(node_db)
        nodes_entity[node.name] = node_db

    await db.flush()

    try:
        for edge in graph.edges:
            edge_db = Edge(
                source_id=nodes_entity[edge.source].id,
                target_id=nodes_entity[edge.target].id,
                graph_id=graph_db.id
            )
            db.add(edge_db)

        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise_validation_error("There are duplicate edges in the graph", ["body", "edges"])

    return schemas.GraphCreateResponse(id=graph_db.id)


async def db_get_graph(db: AsyncSession, graph_id: int) -> schemas.GraphReadResponse:
    query = select(Graph).options(
        joinedload(Graph.nodes),
        joinedload(Graph.edges).joinedload(Edge.source_node),
        joinedload(Graph.edges).joinedload(Edge.target_node)
    ).where(Graph.id == graph_id)

    result = await db.execute(query)
    graph_db = result.scalar()

    if graph_db is None:
        raise HTTPException(404, "Graph entity not found")

    return schemas.GraphReadResponse(
        id=graph_id,
        nodes=[schemas.Node(name=node.name) for node in graph_db.nodes],
        edges=[schemas.Edge(
            source=edge.source_node.name,
            target=edge.target_node.name
        ) for edge in graph_db.edges]
    )


async def db_get_adj_list(db: AsyncSession, graph_id: int, transpose: bool = False) -> schemas.AdjacencyListResponse:
    regular_graph = await db_get_graph(db, graph_id)

    adj_list = dict()

    for node in regular_graph.nodes:
        adj_list[node.name] = []

    for edge in regular_graph.edges:
        if not transpose:
            adj_list[edge.source].append(edge.target)
        else:
            adj_list[edge.target].append(edge.source)

    return schemas.AdjacencyListResponse(
        adjacency_list=adj_list
    )


async def db_delete_node(db: AsyncSession, graph_id: int, node_name: str):
    query = select(Node).where(Node.graph_id == graph_id,
                               Node.name == node_name)

    result = await db.execute(query)
    node_db = result.scalar()

    if node_db is None:
        raise HTTPException(404, "Graph entity not found")


    await db.delete(node_db)

    await db.flush()

    query = select(exists().where(Node.graph_id == graph_id))
    result = await db.execute(query)

    if not result.scalar():
        query = select(Graph).where(Graph.id == graph_id)
        result = await db.execute(query)
        await db.delete(result.scalar())

    await db.commit()

    return None
