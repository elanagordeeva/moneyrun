#!/usr/bin/env python3
"""
Генератор изображений через OpenAI Images API (gpt-image-1).

Использование:
    python3 scripts/gen-image.py "prompt текстом" --out art/some-name.png
    python3 scripts/gen-image.py "prompt" --out art/x.png --size 1024x1024 --quality high

Параметры:
    --out      путь файла (обязательный)
    --size     1024x1024 | 1024x1536 | 1536x1024  (default: 1024x1024)
    --quality  low | medium | high  (default: medium)
    --bg       transparent | opaque  (default: opaque)

Ключ читается из .env (OPENAI_API_KEY=sk-...).
.env лежит в корне проекта и в git не попадает.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def load_env() -> dict:
    """Минимальный парсер .env без зависимостей."""
    env = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def generate(prompt: str, out: Path, size: str, quality: str, bg: str) -> None:
    env = load_env()
    api_key = env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.startswith("sk-"):
        print("ERROR: OPENAI_API_KEY не найден в .env или окружении.", file=sys.stderr)
        print(f"       Создай {ENV_FILE} (см. .env.example).", file=sys.stderr)
        sys.exit(1)

    body = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
        "background": bg,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    print(f"→ Generating ({size}, {quality}, bg={bg})...")
    print(f"  Prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)

    b64 = data["data"][0].get("b64_json")
    if not b64:
        print("ERROR: response had no b64_json:", file=sys.stderr)
        print(json.dumps(data)[:400], file=sys.stderr)
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    print(f"✓ Saved → {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


def main():
    ap = argparse.ArgumentParser(description="OpenAI image generator")
    ap.add_argument("prompt", help="Text prompt for the image")
    ap.add_argument("--out", required=True, type=Path, help="Output file path")
    ap.add_argument("--size", default="1024x1024",
                    choices=["1024x1024", "1024x1536", "1536x1024"])
    ap.add_argument("--quality", default="medium",
                    choices=["low", "medium", "high"])
    ap.add_argument("--bg", default="opaque",
                    choices=["transparent", "opaque"])
    args = ap.parse_args()

    out = args.out
    if not out.is_absolute():
        out = ROOT / out
    generate(args.prompt, out, args.size, args.quality, args.bg)


if __name__ == "__main__":
    main()
