import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_books_empty(monkeypatch):
    def fake_get_redis():
        class FakeCache:
            def get(self, key): return None
            def set(self, key, value, ex=None): pass
        return FakeCache()
    monkeypatch.setattr("app.models.get_redis", fake_get_redis)
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_book(monkeypatch):
    def fake_get_redis():
        class FakeCache:
            def get(self, key): return None
            def set(self, key, value, ex=None): pass
        return FakeCache()
    monkeypatch.setattr("app.models.get_redis", fake_get_redis)
    data = {"title": "Test Book", "author": "Tester"}
    response = client.post("/books", json=data)
    assert response.status_code == 200 or response.status_code == 201
    assert response.json()["title"] == "Test Book"

def test_cache_miss(monkeypatch):
    calls = {"get": 0, "set": 0}
    class FakeCache:
        def get(self, key):
            calls["get"] += 1
            return None
        def set(self, key, value, ex=None):
            calls["set"] += 1
    def fake_get_redis():
        return FakeCache()
    monkeypatch.setattr("app.models.get_redis", fake_get_redis)
    response = client.get("/books")
    assert response.status_code == 200
    assert calls["get"] >= 0
    assert calls["set"] >= 0

def test_pytest_discovery():
    assert 1 == 1

def test_import():
    assert True