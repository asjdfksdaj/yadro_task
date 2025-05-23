from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from .models import Graph, Vertex, Edge
from .schemas import GraphInput, GraphIdResponse

 
def raise_validation_error(msg: str, loc: list[str] = None):
    if loc is None:
        loc = []
    raise RequestValidationError(errors=[{"loc": loc, "msg": msg, "type": "value_error"}])
 
async def create_graph_in_db(session: AsyncSession, data: GraphInput) -> int:
    adjacency_map = {}
    node_states = {}
    for vert in data.vertices:
        adjacency_map[vert.name] = []
        node_states[vert.name] = 0
 
    for link in data.links:
        if link.source not in adjacency_map:
            raise_validation_error(f"Вершина {link.source} не найдена", ["body", "links", "source"])
        if link.target not in adjacency_map:
            raise_validation_error(f"Вершина {link.target} не найдена", ["body", "links", "target"])
        adjacency_map[link.source].append(link.target)
 
    # Проверка на цикл (DFS)
    for node in adjacency_map:
        if node_states[node] == 0:
            stack = [node]
            while stack:
                current = stack[-1]
                if node_states[current] != 0:
                    node_states[current] = 1
                    stack.pop()
                    continue
                else:
                    node_states[current] = 2
                for neighbor in adjacency_map[current]:
                    if node_states[neighbor] == 2:
                        raise_validation_error("Граф содержит цикл", ["body"])
                    elif node_states[neighbor] == 0:
                        stack.append(neighbor)
 
    new_graph = Graph()
    session.add(new_graph)
    await session.flush()
 
    vertex_map = {}
    for vert in data.vertices:
        v_entity = Vertex(name=vert.name, graph_id=new_graph.id)
        session.add(v_entity)
        vertex_map[vert.name] = v_entity
    await session.flush()
 
    try:
        for link in data.links:
            e = Edge(
                source_id=vertex_map[link.source].id,
                target_id=vertex_map[link.target].id,
                graph_id=new_graph.id
            )
            session.add(e)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise_validation_error("Обнаружены дублирующиеся связи", ["body", "links"])
 
    return GraphIdResponse(id=new_graph.id)

 
async def fetch_graph(session: AsyncSession, graph_id: int):
    query = select(Graph).options(
        joinedload(Graph.vertices),
        joinedload(Graph.edges).joinedload(Edge.source_vertex),
        joinedload(Graph.edges).joinedload(Edge.target_vertex)
    ).where(Graph.id == graph_id)
 
    result = await session.execute(query)
    graph_obj = result.scalar()
    if not graph_obj:
        raise HTTPException(status_code=404, detail="Граф не найден")
    return GraphDetails(
        id=graph_obj.id,
        vertices=[Vertex(name=v.name) for v in graph_obj.vertices],
        links=[
            Link(source=e.source_vertex.name, target=e.target_vertex.name)
            for e in graph_obj.edges
        ]
    )
 
async def fetch_adj_list(session: AsyncSession, graph_id: int, transpose: bool):
    graph_info = await fetch_graph(session, graph_id)
    adj_dict = {}
    for v in graph_info.vertices:
        adj_dict[v.name] = []
 
    for e in graph_info.links:
        if not transpose:
            adj_dict[e.source].append(e.target)
        else:
            adj_dict[e.target].append(e.source)
    return adj_dict
 
async def delete_vertex(session: AsyncSession, graph_id: int, vertex_name: str):
    q_vertex = select(Vertex).where(Vertex.graph_id == graph_id, Vertex.name == vertex_name)
    res = await session.execute(q_vertex)
    vertex = res.scalar()
    if not vertex:
        raise HTTPException(status_code=404, detail="Вершина не найдена")
    await session.delete(vertex)
    await session.flush()
 
    remaining = select(exists().where(Vertex.graph_id == graph_id))
    res_check = await session.execute(remaining)
    if not res_check.scalar():
        q_graph = select(Graph).where(Graph.id == graph_id)
        graph_obj = (await session.execute(q_graph)).scalar()
        if graph_obj:
            await session.delete(graph_obj)
    await session.commit()
