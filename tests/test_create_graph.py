from fastapi.testclient import TestClient
 
def create_graph(client: TestClient, nodes, edges):
    payload = {
        "nodes": [{"name": n} for n in nodes],
        "edges": [{"source": s, "target": t} for s, t in edges]
    }
    response = client.post("/api/graph/", json=payload)
    return response
