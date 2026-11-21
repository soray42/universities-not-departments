"""Fetch the public inputs listed in data/sources.csv into data/raw/ and data/orcid/.

    python scripts/download_data.py                  download every 'fetch' row, extract every 'extract' row, and
                                                     verify md5s where the source is fixed ('fixed' = yes)
    python scripts/download_data.py --check-urls     HEAD request for every URL, nothing downloaded
    python scripts/download_data.py --from-local RAW [--orcid-local ORCID]
                                                     symlink each listed file from an existing data/raw (and ORCID)
                                                     directory instead of downloading (for testing)

Rows of kind 'manual' cannot be fetched by a script (terms of use); the script prints what to do and where to put
the file. Rows of kind 'script' are fetched by the analysis script named in their notes when it runs. No data file is
redistributed with the repository.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = DATA / "sources.csv"
UA = {"User-Agent": "academic-replication-download/1.0"}


def rows():
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def ok(r, p: Path) -> bool:
    """file present and, for a fixed source with a recorded md5, byte-identical to the file used in the paper"""
    if not p.exists():
        return False
    if p.is_dir():
        return any(p.iterdir())
    return not (r["fixed"] == "yes" and r["md5"]) or md5(p) == r["md5"]


def fetch(url: str, dest: Path, tries: int = 4) -> str | None:
    """download to a temporary file, then rename (never writes through an existing symlink); returns an error
    message or None. The Internet Archive drops bursts of connections, so its requests are spaced and retried."""
    import time
    import requests
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    slow = "web.archive.org" in url
    err = None
    for attempt in range(tries):
        if slow or attempt:
            time.sleep(8 * attempt + (3 if slow else 0))
        try:
            with requests.get(url, headers=UA, stream=True, timeout=300) as resp:
                resp.raise_for_status()
                with open(tmp, "wb") as fh:
                    for chunk in resp.iter_content(1 << 20):
                        fh.write(chunk)
            tmp.replace(dest)
            return None
        except Exception as exc:                                   # noqa: BLE001 (network)
            err = f"{type(exc).__name__}: {exc}"
    tmp.unlink(missing_ok=True)
    return err


def extract(r, dest: Path):
    arc = DATA / r["archive"]
    member = r["member"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if arc.suffix == ".7z":
        import py7zr
        with py7zr.SevenZipFile(arc) as z:
            names = [n for n in z.getnames() if n.startswith(member) and n.endswith(".parquet")]
        tmpdir = dest.parent / (dest.name + ".tmp")
        with py7zr.SevenZipFile(arc) as z:
            z.extract(path=tmpdir, targets=names)
        if dest.is_symlink():
            dest.unlink()
        elif dest.exists():
            shutil.rmtree(dest)
        (tmpdir / member.rstrip("/")).rename(dest)
        shutil.rmtree(tmpdir, ignore_errors=True)
        return
    tmp = dest.with_name(dest.name + ".part")
    with zipfile.ZipFile(arc) as z, z.open(member) as src, open(tmp, "wb") as out:
        shutil.copyfileobj(src, out, 1 << 22)
    tmp.replace(dest)


def download():
    R = rows()
    missing_manual, bad = [], []
    for r in R:
        p = DATA / r["path"]
        if ok(r, p):
            continue
        if r["kind"] == "fetch":
            print(f"fetch   {r['path']}", flush=True)
            err = fetch(r["url"], p)
            if err:
                bad.append((r["path"], f"download failed ({err}); run make data again"))
                continue
        elif r["kind"] == "extract":
            if not (DATA / r["archive"]).exists():
                bad.append((r["path"], f"archive {r['archive']} missing"))
                continue
            print(f"extract {r['path']}", flush=True)
            extract(r, p)
        elif r["kind"] == "bundled":
            print(f"copy    {r['path']} (bundled with the repository)", flush=True)
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / r["url"], p)
        elif r["kind"] == "script":
            print(f"later   {r['path']} (written by the analysis at run time)")
            continue
        else:
            missing_manual.append(r)
            continue
        if p.is_file() and r["md5"] and md5(p) != r["md5"]:
            if r["fixed"] == "yes":
                bad.append((r["path"], "md5 differs from the file used in the paper"))
            else:
                print(f"  note: {r['path']} is a live source; its md5 differs from the copy used in the paper")
    report(missing_manual, bad)


def report(missing_manual, bad):
    if missing_manual:
        print("\nManual step needed for these files (put each at the path shown):")
        for r in missing_manual:
            print(f"  data/{r['path']}\n      {r['notes']}\n      {r['url']}  (terms: {r['licence']})")
    for p, why in bad:
        print(f"PROBLEM: data/{p}: {why}")
    if not missing_manual and not bad:
        print("all inputs present")
    sys.exit(1 if bad or missing_manual else 0)


def check_urls():
    """HEAD request for every URL. Servers that refuse HEAD (403/404/405/501) get a 1-byte ranged GET instead;
    requests to the Internet Archive are spaced and retried, because it drops bursts of connections."""
    import time
    import requests
    seen = set()
    fails = 0
    for r in rows():
        u = r["url"]
        if r["kind"] == "extract" or not u or u in seen:
            continue
        seen.add(u)
        slow = "web.archive.org" in u
        code, size, how = "?", "?", "HEAD"
        for attempt in range(4 if slow else 2):
            try:
                if slow:
                    time.sleep(1.5 * (attempt + 1))
                resp = requests.head(u, headers=UA, allow_redirects=True, timeout=60)
                code, size = resp.status_code, resp.headers.get("Content-Length", "?")
                if code in (403, 404, 405, 501):
                    how = "GET 1 byte"
                    with requests.get(u, headers={**UA, "Range": "bytes=0-0"}, stream=True, timeout=60) as g:
                        code = g.status_code
                        size = g.headers.get("Content-Range", "?").split("/")[-1]
                break
            except Exception as exc:                               # noqa: BLE001 (network)
                code, size = type(exc).__name__, "?"
        good = code in (200, 206)
        fails += not good
        print(f"{'ok ' if good else '!! '}{code} {size:>12} {how:10s} {r['kind']:7s} {r['path']}  {u}", flush=True)
    print(f"{len(seen)} URLs checked, {fails} not reachable")


def from_local(raw: Path, orcid: Path | None):
    raw = raw.resolve()
    linked, absent = 0, []
    for r in rows():
        rel = Path(r["path"])
        base, sub = (raw, Path(*rel.parts[1:])) if rel.parts[0] == "raw" else (orcid, Path(*rel.parts[1:]))
        if base is None:
            absent.append(r["path"])
            continue
        src, dest = base / sub, DATA / rel
        if not src.exists():
            absent.append(r["path"])
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_symlink() or dest.exists():
            if dest.is_symlink() and Path(os.readlink(dest)) == src:
                linked += 1
                continue
            raise SystemExit(f"{dest} exists; remove it first")
        dest.symlink_to(src, target_is_directory=src.is_dir())
        linked += 1
    print(f"linked {linked} files from {raw}" + (f" and {orcid}" if orcid else ""))
    if absent:
        print(f"{len(absent)} listed files not found locally:")
        for a in absent:
            print("  data/" + a)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check-urls", action="store_true")
    ap.add_argument("--from-local", type=Path)
    ap.add_argument("--orcid-local", type=Path)
    a = ap.parse_args()
    if a.check_urls:
        check_urls()
    elif a.from_local:
        orcid = a.orcid_local.resolve() if a.orcid_local and a.orcid_local.exists() else None
        from_local(a.from_local, orcid)
    else:
        download()


if __name__ == "__main__":
    main()
