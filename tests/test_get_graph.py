from fastapi.testclient import TestClient
from tests.test_create_graph import post_graph


def create_test_graph(test_client: TestClient, nodes: list[str], edges: list[tuple[str, str]]) -> int:
    response = post_graph(test_client, nodes, edges)
    assert response.status_code == 201
    return response.json()["id"]


def test_get_graph(test_client: TestClient):
    nodes = ["a", "b", "c"]
    response_edges = [("a", "b"), ("b", "c")]
    graph_id = create_test_graph(test_client, nodes, response_edges)

    response = test_client.get(f"/api/graph/{graph_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == graph_id

    response_nodes = [node["name"] for node in data["nodes"]]
    assert sorted(response_nodes) == ["a", "b", "c"]

    response_edges = [(edge["source"], edge["target"])
                      for edge in data["edges"]]
    assert ("a", "b") in response_edges
    assert ("b", "c") in response_edges


def test_get_adjacency_list(test_client: TestClient):
    nodes = ["a", "b", "c", "d"]
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    graph_id = create_test_graph(test_client, nodes, edges)

    response = test_client.get(f"/api/graph/{graph_id}/adjacency_list")

    assert response.status_code == 200
    data = response.json()
    adj_list = data["adjacency_list"]

    assert sorted(adj_list.keys()) == ["a", "b", "c", "d"]
    assert sorted(adj_list["a"]) == ["b", "c"]
    assert sorted(adj_list["b"]) == ["d"]
    assert sorted(adj_list["c"]) == ["d"]
    assert adj_list["d"] == []


def test_get_reverse_adjacency_list(test_client: TestClient):
    nodes = ["a", "b", "c", "d"]
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    graph_id = create_test_graph(test_client, nodes, edges)

    response = test_client.get(f"/api/graph/{graph_id}/reverse_adjacency_list")

    assert response.status_code == 200
    data = response.json()
    rev_adj_list = data["adjacency_list"]

    assert sorted(rev_adj_list.keys()) == ["a", "b", "c", "d"]
    assert sorted(rev_adj_list["a"]) == []
    assert sorted(rev_adj_list["b"]) == ["a"]
    assert sorted(rev_adj_list["c"]) == ["a"]
    assert sorted(rev_adj_list["d"]) == ["b", "c"]


def test_get_nonexistent_graph(test_client: TestClient):
    response = test_client.get("/api/graph/9999")

    assert response.status_code == 404
    assert response.json() == {"message": "Graph entity not found"}


def test_get_graph_with_no_edges(test_client: TestClient):
    nodes = ["a", "b", "c", "d"]
    edges = []
    graph_id = create_test_graph(test_client, nodes, edges)

    response = test_client.get(f"/api/graph/{graph_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == graph_id
    assert len(data["nodes"]) == 4
    assert len(data["edges"]) == 0

    response = test_client.get(f"/api/graph/{graph_id}/adjacency_list")
    assert response.status_code == 200
    data = response.json()
    adj_list = data["adjacency_list"]

    for node in ["a", "b", "c", "d"]:
        assert adj_list[node] == []