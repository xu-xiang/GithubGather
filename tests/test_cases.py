from fastapi.testclient import TestClient
from githubgather.main import app

client = TestClient(app)


def test_normal_api_call():
    response = client.get("/users/octocat/repos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_error_handling():
    response = client.get("/repos/octocat/unknown")
    assert response.status_code == 404


def test_deep_fetch():
    response = client.get("/users/octocat/repos?deep_fetch=true&per_page=10")
    assert response.status_code == 200
    assert len(response.json()) > 10


def test_field_filtering():
    response = client.get("/users/octocat/repos?fields=name,description")
    assert response.status_code == 200
    for repo in response.json():
        assert "name" in repo and "description" in repo and "id" not in repo


def test_linked_requests():
    response = client.get("/users/octocat/repos?linked_readme=/repos/{full_name}/readme")
    assert response.status_code == 200
    for repo in response.json():
        assert "linked_readme" in repo

# 更多测试用例 ...
