#!/usr/bin/env python3
"""Локальный dev-сервер Moneyrun с live-reload.

Запускается через launchd (LaunchAgent tech.moneyrun.devserver),
поэтому переживает засыпание ноутбука и автоматически
перезапускается при падении.

Ручной запуск:  python3 scripts/serve.py
"""
from pathlib import Path
from livereload import Server

ROOT = Path(__file__).resolve().parent.parent

server = Server()
server.watch(str(ROOT / "index.html"))
server.watch(str(ROOT / "art"))
server.watch(str(ROOT / "*.html"))
server.watch(str(ROOT / "*.css"))
server.watch(str(ROOT / "*.js"))
server.serve(port=8000, host="localhost", root=str(ROOT), open_url_delay=None)
