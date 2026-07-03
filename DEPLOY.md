# Deploy / релиз сайта Moneyrun (v2)

Инструкция по выкладке **второй версии** сайта на боевой домен **`moneyrun.tech`**.
Актуальная версия сайта — папка [`v2/`](v2/). Первая версия (файлы в корне) заморожена.

> Домен без `www` — во всём коде канонический хост `https://moneyrun.tech/`.

---

## 0. Что уже подготовлено в коде

- ✅ Все ассеты **self-contained внутри `v2/`** — деплой одной папки `v2/` ничего не ломает.
  Логотип и график лежат в [`v2/img/`](v2/img/), ссылки локальные (`img/…`, не `../art/`).
- ✅ Фавикон локальный: `favicon.svg` (+ Tilda-png как запасной для apple-touch).
- ✅ `canonical`, `og:image`, `sitemap.xml` уже используют `https://moneyrun.tech/`.
- ✅ Готовый боевой `robots.txt` лежит рядом как `v2/robots.launch.txt`.
- ✅ Скрипт открытия индексации: [`scripts/release-golive.sh`](scripts/release-golive.sh).

Осталось: настроить хостинг/домен и выполнить «флип индексации» (раздел 3).

---

## 1. Два решения, которые надо принять до релиза

**a) `www` или apex.** В коде везде `moneyrun.tech` (без `www`).
Поднять оба и **редиректить `www` → apex** (301), либо наоборот — но тогда поправить
`canonical`/`og`/`sitemap` под `www`. Проще оставить как есть (apex).

**b) Формат URL — чистый или `.html`.**
`canonical` и `sitemap.xml` указывают на **чистые** адреса:

| Страница | Файл | canonical / sitemap |
|---|---|---|
| Главная | `index.html` | `https://moneyrun.tech/` |
| Правила | `guide.html` | `https://moneyrun.tech/guide` |
| Приватность | `privacypolicy.html` | `https://moneyrun.tech/privacypolicy` |

Внутренние ссылки при этом ведут на `guide.html` / `privacypolicy.html`.
→ Нужен **rewrite на сервере**: `/guide` → `guide.html`, `/privacypolicy` → `privacypolicy.html`
(nginx `try_files $uri $uri.html $uri/ =404;` или аналог у хостинга).
Если rewrite настроить нельзя — привести `canonical` и `sitemap.xml` к `.html`.

---

## 2. Выкладка

1. **Web root = содержимое `v2/`.** В корень боевого сайта кладём всё из `v2/`:
   `index.html` (→ `/`), `guide.html`, `privacypolicy.html`, `img/`, `favicon.svg`,
   `og-moneyrun-preview.png`, `sitemap.xml`, `robots.txt`, `llms.txt`, `pricing.md`.
2. **DNS:** `moneyrun.tech` → хостинг (A/ALIAS для apex, CNAME для `www`). Дождаться распространения.
3. **HTTPS:** сертификат (Let's Encrypt / встроенный), форс-редирект `http → https`.
4. **Редирект** `www` ↔ apex к каноническому хосту (см. решение 1a).
5. **Rewrite** чистых URL (см. решение 1b), если оставляем `/guide`, `/privacypolicy`.

---

## 3. 🔴 Открыть индексацию (флип) — не забыть!

Пока сайт на staging, стоит `noindex` + `robots.txt: Disallow: /`.
В день релиза выполнить один скрипт **до сборки web root**:

```bash
bash scripts/release-golive.sh
```

Он идемпотентно:
1. убирает `<meta name="robots" content="noindex, nofollow">` из `index.html`, `guide.html`, `privacypolicy.html`;
2. активирует `v2/robots.txt` из `robots.launch.txt` (`Allow: /` + AI-боты + `Sitemap:`);
3. проставляет `<lastmod>` главной в `sitemap.xml` на сегодня.

Либо руками — то же самое в трёх действиях (строки: `index.html:6`, `guide.html:6`, `privacypolicy.html:6`).

---

## 4. Проверка после go-live (~10 мин)

- [ ] Три страницы открываются по `https`, без дубля `www`.
- [ ] `view-source`: **нет** `noindex`; `canonical` = текущему URL.
- [ ] `/robots.txt` → `Allow: /` и строка `Sitemap:`.
- [ ] `/sitemap.xml` открывается, все 3 URL отдают 200.
- [ ] `/og-moneyrun-preview.png` → 200; на `guide`/`privacypolicy` грузятся лого и график.
- [ ] OG-превью: Telegram / FB Sharing Debugger / Twitter Card Validator.
- [ ] Фавикон и apple-touch-icon видны.

---

## 5. Регистрация в поисковиках

- [ ] **Google Search Console** — подтвердить домен (DNS-TXT), отправить `sitemap.xml`.
- [ ] **Яндекс.Вебмастер** — подтвердить, отправить sitemap (критично для РФ-трафика).
- [ ] (опц.) **Bing Webmaster Tools**.
- [ ] Проверить доступность `/llms.txt` (контекст для AI-ассистентов).

## 6. Первые дни

- [ ] `site:moneyrun.tech` в Google/Яндекс — идёт ли индексация.
- [ ] В GSC/Вебмастере — нет ли ошибок покрытия / блокировки robots.
