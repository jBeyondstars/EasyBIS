"""Keep a local copy of the ForeverDB data files the generator reads.

ForeverDB publishes a manifest of its addon's data files with their SHA-256
(https://foreverdb.net/downloads/addon-manifest.json). The copy lives in
_build/cache/ForeverDB, next to ForeverDB's LICENSE.txt and NOTICE.txt.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

import fdb

SITE = "https://foreverdb.net/"
MANIFEST_URL = SITE + "downloads/addon-manifest.json"
DATA_PREFIX = "downloads/addon-data/"
USER_AGENT = "wow-addon-data-tool/0.1"  # the site refuses Python's default agent
TIMEOUT = 60
NOTICES = ("LICENSE.txt", "NOTICE.txt")
FILES = fdb.DATA_FILES + fdb.CONSUMABLE_FILES


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest() -> dict:
    """{"version": ..., "files": {file name: {"url", "sha256", "bytes"}}} for the files the generator reads."""
    manifest = json.loads(_get(MANIFEST_URL))
    files = {}
    for entry in manifest["data"]["files"]:
        name = entry["path"].rsplit("/", 1)[-1]
        if name not in FILES:
            continue
        url = urllib.parse.urljoin(SITE, entry["url"])
        parts = urllib.parse.urlsplit(url)
        if parts.scheme != "https" or parts.netloc != "foreverdb.net" or not parts.path.startswith("/" + DATA_PREFIX):
            raise ValueError(f"unexpected address for {name}: {url}")
        files[name] = {"url": url, "sha256": entry["sha256"], "bytes": entry["bytes"]}
    missing = [name for name in FILES if name not in files]
    if missing:
        raise ValueError(f"the manifest no longer lists {', '.join(missing)}")
    return {"version": manifest["data"]["version"], "files": files}


def check(cache_dir: Path, manifest: dict) -> dict[str, str]:
    """{file name: "current" | "changed" | "missing"} against the manifest."""
    status = {}
    for name, entry in manifest["files"].items():
        path = cache_dir / name
        if not path.exists():
            status[name] = "missing"
        else:
            status[name] = "current" if sha256(path) == entry["sha256"] else "changed"
    return status


def update(cache_dir: Path, manifest: dict, only=None) -> list[str]:
    """Download the files that differ from the manifest, or those of them named in `only`; returns their names."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fetched = []
    for name, state in check(cache_dir, manifest).items():
        if state == "current" or (only is not None and name not in only):
            continue
        entry = manifest["files"][name]
        data = _get(entry["url"])
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"{name}: the download does not match the manifest's SHA-256")
        (cache_dir / name).write_bytes(data)
        fetched.append(name)
    return fetched


def import_addon(addon_dir: Path, cache_dir: Path) -> list[str]:
    """Copy the data files and the licence notices from an unpacked ForeverDB addon folder."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in FILES:
        shutil.copyfile(addon_dir / "Data" / name, cache_dir / name)
        copied.append(name)
    for name in NOTICES:
        if (addon_dir / name).exists():
            shutil.copyfile(addon_dir / name, cache_dir / name)
            copied.append(name)
    return copied
