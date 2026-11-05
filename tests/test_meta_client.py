"""Tests for the Meta API code path, using a mock opener (no key, no network)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from meta_client import interpret, call_meta_model, local_fallback  # noqa: E402

SCENE = {"count": 12, "groups": 3, "spread": "wide", "mode": "sample",
         "note": "synthetic demo scene"}


def test_fallback_without_key():
    os.environ.pop("META_MODEL_API_KEY", None)
    out = interpret(SCENE)
    assert out["source"].startswith("LOCAL FALLBACK"), out
    assert "12" in out["happening"]


def test_real_path_with_mock_opener():
    os.environ["META_MODEL_API_KEY"] = "TEST-KEY-NEVER-REAL"
    seen = {}

    def fake_opener(url, data, headers):
        seen["url"] = url
        seen["auth"] = headers["Authorization"]
        assert "api.meta.ai" in url
        assert headers["Authorization"].startswith("Bearer ")
        body = json.dumps({
            "choices": [{"message": {"content": "Mock: a lively, attentive crowd."}}]
        })
        return 200, body

    out, err = call_meta_model(SCENE, opener=fake_opener)
    assert err is None, err
    assert out["source"].startswith("META MODEL API")
    assert "lively" in out["happening"]
    assert "TEST-KEY" not in json.dumps(out)  # key never echoed back
    os.environ.pop("META_MODEL_API_KEY", None)


def test_fallback_labels_are_honest():
    out = local_fallback({"count": 0, "groups": 0, "spread": "none"})
    assert "No audience" in out["mood"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
    print("ALL META CLIENT TESTS PASS")
