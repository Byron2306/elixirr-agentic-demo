#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,sys,uuid
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlparse
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from adapters.dio import DIOAdapter
DASH=ROOT/"dashboard"; SCENARIO=ROOT/"scenarios"/"01_vesper_customer.json"
POCKET_DEFAULT="http://127.0.0.1:8000"
def pocket_base(): return os.getenv("DIO_VESPER_POCKET_TTS_URL",POCKET_DEFAULT).rstrip("/")
def pocket_health():
    url=pocket_base()+"/health"
    try:
        with urlopen(Request(url,method="GET"),timeout=1.5) as r:
            raw=r.read(4096);ok=200<=r.status<300
            detail=raw.decode("utf-8","replace").strip()
            try: detail=json.loads(detail) if detail else None
            except json.JSONDecodeError: pass
            return {"ready":ok,"state":"ready" if ok else "unavailable","endpoint":pocket_base(),"health":detail}
    except Exception as exc:
        return {"ready":False,"state":"unavailable","endpoint":pocket_base(),"detail":str(exc)}
def encode_multipart_text(text):
    boundary="----elixirr-"+uuid.uuid4().hex
    body=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\n{text}\r\n--{boundary}--\r\n").encode("utf-8")
    return boundary,body
def pocket_synthesize(text):
    boundary,body=encode_multipart_text(text)
    req=Request(pocket_base()+"/tts",data=body,method="POST",headers={"Content-Type":f"multipart/form-data; boundary={boundary}","Accept":"audio/wav"})
    with urlopen(req,timeout=90) as r:
        audio=r.read();ctype=r.headers.get("Content-Type","audio/wav")
        if not 200<=r.status<300: raise RuntimeError(f"Pocket returned HTTP {r.status}")
        if not audio: raise RuntimeError("Pocket returned an empty audio body")
        return audio,ctype
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        rel=urlparse(path).path
        if rel in {"","/"}: return str(DASH/"index.html")
        if rel.startswith("/static/"): rel=rel[len("/static/"):]
        else: rel=rel.lstrip("/")
        return str(DASH/rel)
    def end_headers(self):
        self.send_header("Cache-Control","no-store, no-cache, must-revalidate, max-age=0");self.send_header("Pragma","no-cache");self.send_header("Expires","0");super().end_headers()
    def _json(self,status,payload):
        raw=json.dumps(payload).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/api/health":
            h=DIOAdapter(os.getenv("DIO_PRESENCE_URL","http://127.0.0.1:8787")).health().as_dict();voice=pocket_health()
            return self._json(200,{"ready":h["status"]=="ready","dio":h,"voice":voice})
        return super().do_GET()
    def do_POST(self):
        n=int(self.headers.get("Content-Length","0"));payload=json.loads(self.rfile.read(n) or b"{}")
        if self.path=="/api/message":
            secret=os.getenv("DIO_PRESENCE_PUBLIC_SHARED_SECRET","")
            if len(secret)<32:return self._json(503,{"detail":"Local Presence signing secret is not configured."})
            base=json.loads(SCENARIO.read_text());base["text"]=str(payload.get("text","")).strip();base["source_message_id"]="elixirr-live-"+uuid.uuid4().hex[:12]
            if not base["text"]:return self._json(400,{"detail":"Message text required."})
            result=DIOAdapter(os.getenv("DIO_PRESENCE_URL","http://127.0.0.1:8787")).signed_ingress(secret=secret,envelope=base)
            if not result.evidence:return self._json(502,result.as_dict())
            value=result.evidence[0].get("value");return self._json(200,value if isinstance(value,dict) else result.as_dict())
        if self.path=="/api/speak":
            text=str(payload.get("text","")).strip()
            if not text:return self._json(400,{"detail":"Text required."})
            try:
                audio,ctype=pocket_synthesize(text);self.send_response(200);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(audio)));self.end_headers();self.wfile.write(audio)
            except (HTTPError,URLError,TimeoutError,OSError,RuntimeError) as exc:return self._json(503,{"detail":f"Pocket TTS unavailable: {exc}"})
            return
        return self._json(404,{"detail":"Not found"})
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--host",default="127.0.0.1");ap.add_argument("--port",type=int,default=8765);a=ap.parse_args()
    print(f"Elixirr demo console: http://{a.host}:{a.port}");print(f"Pocket TTS: {pocket_base()}");ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
if __name__=="__main__":main()
