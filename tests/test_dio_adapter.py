import json
from unittest.mock import patch
from adapters.dio import DIOAdapter

class DummyResponse:
    def __init__(self,payload): self.payload=payload
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self): return json.dumps(self.payload).encode()

def test_health_normalizes_live_vesper():
    payload={"ok":True,"presence_identity":"Vesper","automatic_external_actions":False,"attachment_mode":"quarantine_only","public_status":"verified_binding_only"}
    with patch("adapters.dio.request.urlopen",return_value=DummyResponse(payload)):
        out=DIOAdapter().health().as_dict()
    assert out["act"]=="vesper"
    assert out["mode"]=="live"
    assert out["status"]=="ready"
    assert out["details"]["automatic_external_actions"] is False

def test_health_fails_closed_when_unavailable():
    with patch("adapters.dio.request.urlopen",side_effect=OSError("offline")):
        out=DIOAdapter().health().as_dict()
    assert out["mode"]=="unavailable"
    assert out["status"]=="fail"

def test_signed_ingress_preserves_source_authority():
    payload={"decision":{"intent":"product_request","product":"homs","confidence":0.99},"needs_you_id":"NY-1"}
    with patch("adapters.dio.request.urlopen",return_value=DummyResponse(payload)):
        out=DIOAdapter().signed_ingress(secret="demo-secret",envelope={"channel":"webchat","external_user_id":"u","text":"marking"}).as_dict()
    assert out["status"]=="needs_you"
    assert out["authority"]=="source_system_only"
    assert out["details"]["external_authority_created"] is False
