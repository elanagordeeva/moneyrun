#!/usr/bin/env bash
#
# Moneyrun v2 — открытие индексации в день релиза.
#
# Что делает (идемпотентно, можно запускать повторно):
#   1) убирает <meta name="robots" content="noindex, nofollow"> со всех страниц v2/
#   2) активирует robots.txt из robots.launch.txt (Allow: / + AI-боты + Sitemap)
#   3) проставляет <lastmod> главной в sitemap.xml на сегодняшнюю дату
#
# Запуск из любого места:  bash scripts/release-golive.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
V2="$ROOT/v2"
TODAY="$(date +%F)"

echo "▸ Moneyrun go-live flip"
echo "  корень: $ROOT"
echo

# 1) снять noindex со всех страниц
for f in index.html guide.html privacypolicy.html; do
  p="$V2/$f"
  if grep -q 'name="robots"[^>]*noindex' "$p"; then
    tmp="$(mktemp)"
    grep -v 'name="robots"[^>]*noindex' "$p" > "$tmp" && mv "$tmp" "$p"
    echo "  ✓ noindex убран: v2/$f"
  else
    echo "  • noindex уже отсутствует: v2/$f"
  fi
done
echo

# 2) активировать launch-robots (без верхнего блока-инструкции: всё до первого User-agent отбрасываем)
if [ -f "$V2/robots.launch.txt" ]; then
  awk 'seen || /^User-agent/ { seen=1; print }' "$V2/robots.launch.txt" > "$V2/robots.txt"
  echo "  ✓ robots.txt ← robots.launch.txt (Allow: / + AI-боты + Sitemap)"
else
  echo "  ! robots.launch.txt не найден — robots.txt не тронут" >&2
fi
echo

# 3) обновить lastmod главной в sitemap на сегодня
if [ -f "$V2/sitemap.xml" ]; then
  perl -0pi -e "s{(<loc>https://moneyrun\.tech/</loc>\s*<lastmod>)[0-9-]+}{\${1}$TODAY}" "$V2/sitemap.xml"
  echo "  ✓ sitemap.xml: lastmod главной → $TODAY"
fi
echo

echo "Готово. Быстрая проверка перед деплоем:"
echo "  grep -R noindex v2/*.html    # должно быть пусто"
echo "  head -2 v2/robots.txt         # User-agent: *  →  Allow: /"
echo
echo "После деплоя — отправить sitemap в Google Search Console и Яндекс.Вебмастер."
