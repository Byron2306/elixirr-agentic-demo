#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from adapters.dio import DIOAdapter

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description="Act One: live Vesper/DIO demonstration")
    ap.add_argument("--base-url", default=os.getenv("DIO_PRESENCE_URL","http://127.0.0.1:8787"))
    ap.add_argument("--send", action="store_true", help="Send the bounded signed customer scenario after health check.")
    ap.add_argument("--scenario", default=str(ROOT/"scenarios"/"01_vesper_customer.json"))
    args=ap.parse_args()
    adapter=DIOAdapter(args.base_url)
    health=adapter.health()
    print(json.dumps(health.as_dict(),indent=2))
    if not args.send:
        return 0 if health.status=="ready" else 2
    secret=os.getenv("DIO_PRESENCE_PUBLIC_SHARED_SECRET","")
    if not secret:
        print(json.dumps({"act":"vesper","mode":"unavailable","status":"fail","summary":"--send requested but DIO_PRESENCE_PUBLIC_SHARED_SECRET is not set."},indent=2))
        return 3
    envelope=json.loads(Path(args.scenario).read_text(encoding="utf-8"))
    result=adapter.signed_ingress(secret=secret,envelope=envelope)
    print(json.dumps(result.as_dict(),indent=2))
    return 0 if result.status in {"pass","needs_you","refuse"} else 4

if __name__=="__main__":
    raise SystemExit(main())
