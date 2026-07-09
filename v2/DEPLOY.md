# Перенос сайта на moneyrun.tech — чек-лист

Сайт (папка `v2/`) полностью заточен под боевой домен **moneyrun.tech** (без `www`).
Все мета-теги, canonical, sitemap, llms.txt и структурированные данные уже указывают на этот
домен. Ресурсы (`img/…`, `favicon.*`) подключены относительными путями и заработают, как только
`v2/` станет корнем домена.

Ниже — что сделать в момент переноса и что проверить после.

---

## 📋 В момент переноса

### 1. Снять заглушку индексации
Убрать строку со всех трёх страниц (`index.html`, `guide.html`, `privacypolicy.html`):
```html
<meta name="robots" content="noindex, nofollow">
```

### 2. Включить боевой robots.txt
Заменить активный `robots.txt` содержимым `robots.launch.txt`
(в нём `Allow: /`, разрешения AI-ботам и строка `Sitemap:`).
Сейчас активный `robots.txt` = `Disallow: /` — это полный запрет индексации, он для превью.

### 3. `v2/` — корень домена + чистые URL и редиректы
Canonical, `sitemap.xml` и `llms.txt` используют **чистые URL без `.html`**
(`/`, `/guide`, `/privacypolicy`), а внутренние ссылки в вёрстке ведут на `guide.html` /
`privacypolicy.html`. Чтобы не было дублей и 404, сервер должен:
- отдавать `/guide` → `guide.html`, `/privacypolicy` → `privacypolicy.html`;
- редиректить `*.html` → чистый URL (301).

Пример для nginx (корень указывает на папку `v2/`):
```nginx
server {
    server_name moneyrun.tech;
    root /var/www/moneyrun/v2;
    index index.html;

    # /guide, /privacypolicy → отдаём соответствующий .html
    location = /guide          { try_files /guide.html =404; }
    location = /privacypolicy  { try_files /privacypolicy.html =404; }

    # 301 со старых .html на чистые URL (убираем дубли)
    location = /index.html         { return 301 /; }
    location = /guide.html         { return 301 /guide; }
    location = /privacypolicy.html { return 301 /privacypolicy; }

    # всё остальное — как есть (ассеты, robots.txt, sitemap.xml, llms.txt, og-картинка)
    location / { try_files $uri $uri/ =404; }
}
```

### 4. Домен, HTTPS, www
- Основной домен — `moneyrun.tech` **без** `www`.
- Настроить редиректы `www → без www` и `http → https`.
- Если сайт остаётся на **GitHub Pages** — добавить в репозиторий файл `CNAME` с одной строкой
  `moneyrun.tech`. Если переезд на свой сервер — `CNAME` не нужен.

---

## 🔍 После переноса — проверить

- [ ] `https://moneyrun.tech/og-moneyrun-preview.png` отдаёт **200**
      (пока домен пустой — 404, из-за этого превью не цеплялось в Telegram).
- [ ] Превью ссылки и сброс кэша OG:
      Telegram (`@WebpageBot`), [Facebook Debugger](https://developers.facebook.com/tools/debug/),
      Twitter Card Validator.
- [ ] Чистые URL `/guide`, `/privacypolicy` → **200**; `*.html` → **301** на чистые.
- [ ] `robots.txt` отдаёт боевую версию (не `Disallow: /`).
- [ ] `sitemap.xml` и `llms.txt` доступны из корня домена.
- [ ] Отправить `sitemap.xml` в **Яндекс.Вебмастер** и **Google Search Console**, запросить переобход.
- [ ] Favicon и `theme-color` подхватились; HTTPS-сертификат валиден.
- [ ] Мелочь: обновить `lastmod` у `/guide` в `sitemap.xml` (стоит `2026-02-16`, страница правилась позже).

---

## ⚠️ Что НЕ трогать

- **Моки** (`fetchTodaySnapshot()`, `fetchTrainingRecord()`) — данные для виджета
  «Сегодня в движении» и карточек тренировок. Они отключатся сами, когда с бэка пойдут
  реальные данные: при интеграции меняется только тело `fetchX()`, моки не удалять.
- **Подложка карты** мини-карточек на Главной (`img/tcard-map-placeholder.png`) — это
  статическая картинка, а не данные. С бэка не приходит, остаётся закостыленной.
  С бэка идёт только трек (`polyline`), он рисуется поверх этой подложки.
