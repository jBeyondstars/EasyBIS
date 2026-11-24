"""Bundle the editor's referenced ForeverDB icons after running web_editor.py."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
from urllib.request import urlopen


EDITOR = Path(__file__).resolve().parents[1] / "docs" / "bis-editor"


def save_icon(relative_path, cache):
    if not re.fullmatch(r"icons/[0-9]+\.webp", relative_path):
        raise ValueError(f"Unexpected icon path {relative_path!r}")
    path = EDITOR / relative_path
    if path.is_file():
        image = path.read_bytes()
    elif cache and (cache / path.name).is_file():
        image = (cache / path.name).read_bytes()
    else:
        with urlopen(f"https://foreverdb.net/{relative_path}", timeout=30) as response:
            image = response.read()
    if image[:4] != b"RIFF" or image[8:12] != b"WEBP":
        raise ValueError(f"Invalid WebP for {relative_path}")
    if not path.exists():
        path.write_bytes(image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, help="Directory with previously downloaded icons")
    args = parser.parse_args()
    source = (EDITOR / "data.js").read_text(encoding="utf-8")
    data = json.loads(source.split("window.BIS_DATA=", 1)[1].strip().removesuffix(";"))
    icons = {item["icon"] for item in data["items"].values()}
    (EDITOR / "icons").mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as executor:
        list(executor.map(lambda icon: save_icon(icon, args.cache), sorted(icons)))
    print(f"{len(icons)} icons for {len(data['items'])} items")
