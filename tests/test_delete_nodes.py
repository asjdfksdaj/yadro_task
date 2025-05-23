from fastapi.testclient import TestClient
from tests.test_get_graph import create_test_graph


def test_delete_node_success(test_client: TestClient):
    nodes = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "c")]
    graph_id = create_test_graph(test_client, nodes, edges)

    response = test_client.delete(f"/api/graph/{graph_id}/node/c")

    assert response.status_code == 204
    assert response.content == b''

    response = test_client.get(f"/api/graph/{graph_id}")
    assert response.status_code == 200
    data = response.json()

    response_nodes = [node["name"] for node in data["nodes"]]
    assert sorted(response_nodes) == ["a", "b"]

    response_edges = [(edge["source"], edge["target"])
                      for edge in data["edges"]]
    assert len(response_edges) == 1


def test_delete_node_with_multiple_connections(test_client: TestClient):
    nodes = ["a", "b", "c", "d"]
    edges = [("a", "b"), ("b", "c"), ("b", "d"), ("a", "d")]
    graph_id = create_test_graph(test_client, nodes, edges)

    response = test_client.delete(f"/api/graph/{graph_id}/node/b")

    assert response.status_code == 204

    response = test_client.get(f"/api/graph/{graph_id}")
    data = response.json()

    response_nodes = [node["name"] for node in data["nodes"]]
    assert sorted(response_nodes) == ["a", "c", "d"]

    response_edges = [(edge["source"], edge["target"])
                      for edge in data["edges"]]
    assert len(response_edges) == 1
    assert ("a", "d") in response_edges

    response = test_client.get(f"/api/graph/{graph_id}/adjacency_list")
    data = response.json()
    adj_list = data["adjacency_list"]

    assert sorted(adj_list.keys()) == ["a", "c", "d"]
    assert sorted(adj_list["a"]) == ["d"]
    assert adj_list["c"] == []
    assert adj_list["d"] == []


def test_delete_node_nonexistent_node(test_client: TestClient):
    nodes = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "c")]
    graph_id = create_test_graph(test_client, nodes, edges)

    response = test_client.delete(f"/api/graph/{graph_id}/node/z")

    assert response.status_code == 404
    assert response.json() == {"message": "Graph entity not found"}

    response = test_client.get(f"/api/graph/{graph_id}")
    data = response.json()
    response_nodes = [node["name"] for node in data["nodes"]]
    assert sorted(response_nodes) == ["a", "b", "c"]


def test_delete_node_nonexistent_graph(test_client: TestClient):
    response = test_client.delete("/api/graph/9999/node/a")

    assert response.status_code == 404
    assert response.json() == {"message": "Graph entity not found"}

def test_delete_last_node(test_client: TestClient):
    nodes = ["a"]
    edges = []
    graph_id = create_test_graph(test_client, nodes, edges)

    response = test_client.delete(f"/api/graph/{graph_id}/node/a")

    assert response.status_code == 204
    
    response = test_client.get(f"/api/graph/{graph_id}")

    assert response.status_code == 404
    assert response.json() == {"message": "Graph entity not found"}