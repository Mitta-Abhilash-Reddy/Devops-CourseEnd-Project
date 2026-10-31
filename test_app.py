import app as app_module


def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DB_PATH", str(tmp_path / "t.db"))
    return app_module.app.test_client()


def test_health(tmp_path, monkeypatch):
    assert client(tmp_path, monkeypatch).get("/health").json == {"status": "ok"}


def test_add_search_return(tmp_path, monkeypatch):
    c = client(tmp_path, monkeypatch)
    c.post("/add", data={"book": "Clean Code", "student": "21IT001"})
    assert b"Clean Code" in c.get("/?q=clean").data
    assert b"Clean Code" not in c.get("/?q=zzz").data
    c.post("/return/1")
    assert c.get("/api/issues").json[0]["returned"] == 1
