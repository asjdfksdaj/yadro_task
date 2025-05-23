from fastapi.testclient import TestClient
from tests.test_create_graph import create_graph
 
def test_get_graph_by_id(client: TestClient):
    nodes = ["A", "B"]
    edges = [("A", "B")]
    g_id = create_graph(client, nodes, edges)
 
    resp = client.get(f"/api/graph/{g_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == g_id
    node_names = [n["name"] for n in data["nodes"]]
    assert sorted(node_names) == ["A", "B"]
    edge_list = [(e["source"], e["target"]) for e in data["edges"]]
    assert ("A", "B") in edge_list
 
def test_get_nonexistent_graph(client: TestClient):
    resp = client.get("/api/graph/9999")
    assert resp.status_code == 404
    assert resp.json() == {"message": "Граф не найден"}
 
def test_graph_with_no_edges(client: TestClient):
    nodes = ["X", "Y"]
    edges = []
    g_id = create_graph(client, nodes, edges)
 
    resp = client.get(f"/api/graph/{g_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["edges"]) == 0
