"""Fetch the exact public register versions; refuse silent source drift."""
from pathlib import Path
import hashlib,json,urllib.request
from analyze import ROOT

if __name__=='__main__':
    manifest=json.loads((ROOT/'data/sources.json').read_text())
    out=ROOT/'sources';out.mkdir(exist_ok=True)
    for r in manifest:
        if r['id'] not in {'aiib_cofinance_2024','aiib_cofinance_2025'}:continue
        data=urllib.request.urlopen(r['url'],timeout=60).read()
        digest=hashlib.sha256(data).hexdigest()
        if digest!=r['sha256']:
            raise RuntimeError(f"Source drift for {r['id']}: expected {r['sha256']}, got {digest}. Use released CSVs or obtain the archived study version.")
        (out/r['file']).write_bytes(data)
        print(r['id'],digest)
