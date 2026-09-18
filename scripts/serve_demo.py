#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,sys,tempfile,uuid
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from adapters.dio import DIOAdapter
DASH=ROOT/"dashboard"; SCENARIO=ROOT/"scenarios"/"01_vesper_customer.json"
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        # Serve the UI from DASH regardless of the process working directory.
        # /static/app.css and /static/app.js map directly to dashboard/app.*
        rel=urlparse(path).path
        if rel in {"", "/"}:
            return str(DASH/"index.html")
        if rel.startswith("/static/"):
            rel=rel[len("/static/"):]
        else:
            rel=rel.lstrip("/")
        return str(DASH/rel)
    def end_headers(self):
        # Interview console assets must never be served from browser cache while iterating.
        self.send_header("Cache-Control","no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma","no-cache")
        self.send_header("Expires","0")
        super().end_headers()
    def _json(self,status,payload):
        raw=json.dumps(payload).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/api/health":
            h=DIOAdapter(os.getenv("DIO_PRESENCE_URL","http://127.0.0.1:8787")).health().as_dict()
            voice={"ready":bool(os.getenv("DIO_VESPER_VOICE_PROFILE")),"state":"configured" if os.getenv("DIO_VESPER_VOICE_PROFILE") else "profile_not_selected"}
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
            value=result.evidence[0].get("value")
            return self._json(200,value if isinstance(value,dict) else result.as_dict())
        if self.path=="/api/speak":
            text=str(payload.get("text","")).strip()
            if not text:return self._json(400,{"detail":"Text required."})
            try:
                dio=os.getenv("DIO_ROOT",str(Path.home()/"DIO-Canon-Proof"));sys.path.insert(0,dio)
                from presence_core.voice import build_voice_plan,synthesize_voice
                root=Path(dio);plan=build_voice_plan(root=root,language="English",interaction=None,requested_profile=os.getenv("DIO_VESPER_VOICE_PROFILE") or None)
                if plan.get("backend")!="pocket_tts":return self._json(503,{"detail":"Vera Pocket profile is not selected.","plan":plan})
                out=Path(tempfile.gettempdir())/("vesper-"+uuid.uuid4().hex+".wav");synthesize_voice(text=text,output_path=out,plan=plan)
                audio=out.read_bytes();out.unlink(missing_ok=True);self.send_response(200);self.send_header("Content-Type","audio/wav");self.send_header("Content-Length",str(len(audio)));self.end_headers();self.wfile.write(audio)
            except Exception as exc:return self._json(503,{"detail":f"Voice render unavailable: {exc}"})
            return
        return self._json(404,{"detail":"Not found"})
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--host",default="127.0.0.1");ap.add_argument("--port",type=int,default=8765);a=ap.parse_args()
    print(f"Elixirr demo console: http://{a.host}:{a.port}");ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
if __name__=="__main__":main()