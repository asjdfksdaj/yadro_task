from fastapi.testclient import TestClient
from tests.test_get_graph import create_test_graph
 
def test_delete_node_success(client: TestClient):
    nodes = ["x", "y", "z"]
    edges = [("x", "y"), ("y", "z")]
    g_id = create_test_graph(client, nodes, edges)
 
    resp = client.delete(f"/api/graph/{g_id}/node/z")
    assert resp.status_code == 204
 
    resp_get = client.get(f"/api/graph/{g_id}")
    data = resp_get.json()
    node_names = [n["name"] for n in data["nodes"]]
    assert sorted(node_names) == ["x", "y"]
    edges_list = [(e["source"], e["target"]) for e in data["edges"]]
    assert len(edges_list) == 1
 
def test_delete_nonexistent_node(client: TestClient):
    nodes = ["a", "b"]
    edges = [("a", "b")]
    g_id = create_test_graph(client, nodes, edges)
 
    resp = client.delete(f"/api/graph/{g_id}/node/unknown")
    assert resp.status_code == 404
 
def test_delete_node_from_nonexistent_graph(client: TestClient):
    resp = client.delete("/api/graph/9999/node/x")
    assert resp.status_code == 404
 
def test_delete_last_node(client: TestClient):
    nodes = ["solo"]
    edges = []
    g_id = create_test_graph(client, nodes, edges)
 
    resp = client.delete(f"/api/graph/{g_id}/node/solo")
    assert resp.status_code == 204
 
    resp_get = client.get(f"/api/graph/{g_id}")
    assert resp_get.status_code == 404
