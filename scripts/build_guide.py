#!/usr/bin/env python3
"""Сборка guide.html (Правила сервиса) из /tmp/guide.txt в дизайне нового сайта.
Текст 1-в-1, таблицы переносятся структурно."""
import re, html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
lines = Path('/tmp/guide.txt').read_text(encoding='utf-8').split('\n')

# --- отрезаем верх (nav) и низ ---
# первый осмысленный контент начинается со строки про "Платформа Moneyrun"
start = next(i for i,l in enumerate(lines) if l.startswith('Платформа Moneyrun'))
lines = lines[start:]
# убираем хвост 'Наверх'
lines = [l for l in lines if l.strip() != 'Наверх']

H2 = {
 'Игровой модуль (ИМ)','Матрица Грейдов','ИМ.Experience (XP) детализация',
 'ИМ.XP. Пульсовые данные','ИМ.XP. Тренировочная нагрузка','ИМ.XP. Лимиты нагрузки',
 'ИМ.XP. Любительская результативность','Таблица Running Level','ИМ.XP начисление','ИМ.XP дополнительные условия',
 'Финансирование','Философия','Run, Earn, Enjoy!','Актуальная версия',
}
H3 = {
 'Регистрация','Инфо Профиля','Подписка в Telegram','Running Level','Experience, XP',
 'Монетизация, ₽','Пульсовые данные','Верхние зоны (HPZ)','Беговые часы',
 'Минимальный темп, мин/км','Создание Клуба','Роль Забота в Клубе','Финвайт',
 'Определение RL-интервала для Грейдов','Пример действующего распределения:',
}
SKIP = {'Button','Условия перехода','Доп. условия монетизации','Дополнительные возможности',
        'Мужчины','Женщины','Мужчины Женщины'}

# --- Матрица Грейдов (захардкожена 1-в-1) ---
GRADES = ['F','D','D1','D2','C','C+','B','B+','A','A+','Next']
MATRIX = {
 'Условия перехода': [
   ('Регистрация',         ['+','+','+','+','+','+','+','+','+','+','+']),
   ('Инфо профиля',        ['—','+','+','+','+','+','+','+','+','+','+']),
   ('Подписка в Telegram', ['—','—','—','+','+','+','+','+','+','+','+']),
   ('Running Level',       ['—','—','—','0','1—9','10—23','24—38','39—52','53—63','64—75','76—118']),
   ('Experience, XP',      ['—','0','200','700','1 500','3 500','7 000','11 200','16 240','22 288','22 289—∞']),
   ('Монетизация, ₽',      ['—','1','2','3','4','7','10','13','16','19','22—∞']),
 ],
 'Доп. условия монетизации': [
   ('Пульсовые данные',        ['20 мин','20 мин','+','+','+','+','+','+','+','+','+']),
   ('Верхние зоны (HPZ)',      ['—','—','—','+','+','+','+','+','+','+','+']),
   ('Беговые часы',            ['—','—','—','+','+','+','+','+','+','+','+']),
   ('Минимальный темп, мин/км',['10:00','10:00','8:00','8:00','8:00','8:00','8:00','8:00','8:00','8:00','8:00']),
 ],
 'Дополнительные возможности': [
   ('Создание Клуба',     ['—','—','—','—','+','+','+','+','+','+','+']),
   ('Роль Забота в Клубе',['—','—','—','—','+','+','+','+','+','+','+']),
   ('Финвайт',            ['—','—','—','—','—','+','+','+','+','+','+']),
 ],
}
def matrix_html():
    out=['<div class="g-tablewrap"><table class="g-matrix">']
    out.append('<thead><tr><th>Грейды</th>'+''.join(f'<th>{g}</th>' for g in GRADES)+'</tr></thead>')
    for sub, rows in MATRIX.items():
        out.append(f'<tbody><tr class="g-sub"><td colspan="{len(GRADES)+1}">{sub}</td></tr>')
        for label, vals in rows:
            cells=''.join(f'<td>{"" if v=="—" else v}{"—" if v=="—" else ""}</td>' for v in vals)
            out.append(f'<tr><th class="g-rowh">{label}</th>'+cells+'</tr>')
        out.append('</tbody>')
    out.append('</table></div>')
    return '\n'.join(out)

def semi_cells(l):
    return [c.strip() for c in l.replace(';|;',';').split(';')]

def is_semirow(l):
    return len([c for c in semi_cells(l) if c])>=2

def is_code(l):
    s=l.strip()
    if not s or re.search(r'[А-Яа-яЁё]',s): return False
    return bool(re.search(r'(min\(|max\(|iif\(|^\)$|^,\s*ChT$|Ch72|ChT)',s))

def semi_table(rows):
    # rows: list of raw lines containing ';'
    parsed=[[c.strip() for c in r.replace(';|;',';').split(';')] for r in rows]
    ncol=max(len(r) for r in parsed)
    out=['<div class="g-tablewrap"><table class="g-tbl">']
    for i,r in enumerate(parsed):
        r=r+['']*(ncol-len(r))
        tag='th' if i==0 else 'td'
        out.append('<tr>'+''.join(f'<{tag}>{c}</{tag}>' for c in r)+'</tr>')
    out.append('</table></div>')
    return '\n'.join(out)

def rl_table(rows, head):
    # head like "RL (M) 5 км 10 км 21 км 42 км Грейд"
    heads=['RL','5 км','10 км','21 км','42 км','Грейд']
    out=['<div class="g-tablewrap g-rl"><table class="g-tbl">']
    out.append('<thead><tr>'+''.join(f'<th>{h}</th>' for h in heads)+'</tr></thead><tbody>')
    for r in rows:
        parts=r.split()
        times=[p for p in parts if re.match(r'^\d+:\d',p)]
        grade=parts[-1]
        if not times:
            # особая строка без результатов (напр. RL=0): описание на ширину дистанций
            rl=parts[0]
            desc=' '.join(parts[1:-1])
            out.append(f'<tr><td>{rl}</td><td colspan="4">{desc}</td><td>{grade}</td></tr>')
            continue
        rl=' '.join(parts[:len(parts)-len(times)-1])
        cells=[rl]+times+[grade]
        out.append('<tr>'+''.join(f'<td>{c}</td>' for c in cells)+'</tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)

# --- инлайн-выделение 1-в-1 из исходного HTML (жирный/курсив/цвет) ---
# Парсим /tmp/guide.html и для каждого абзаца переносим реальное оформление:
#   <strong>/font-weight>=600 -> <b>; <em>/font-style:italic -> <i>;
#   ссылка <a> или color rgb(255,133,98) -> <span class="g-term"> (цвет акцента)
from html.parser import HTMLParser
class _Rich(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.stack=[]; s.cells=[]
    def _st(s):
        b=i=c=False
        for el in s.stack:
            tag=el['tag']; style=el['style']
            if tag in ('b','strong'): b=True
            if tag in ('i','em'): i=True
            if tag=='a': c=True
            mw=re.search(r'font-weight:\s*(\d+)',style)
            if mw and int(mw.group(1))>=600: b=True
            if re.search(r'font-style:\s*italic',style): i=True
            m=re.search(r'color:\s*([^;"]+)',style)
            if m and '255, 133, 98' in m.group(1): c=True
        return b,i,c
    def handle_starttag(s,tag,attrs):
        d=dict(attrs); s.stack.append({'tag':tag,'style':d.get('style') or ''})
    def handle_startendtag(s,tag,attrs): pass
    def handle_endtag(s,tag):
        for k in range(len(s.stack)-1,-1,-1):
            if s.stack[k]['tag']==tag: del s.stack[k]; break
    def handle_data(s,data):
        b,i,c=s._st()
        for ch in data.replace('\xa0',' '):
            s.cells.append((ch,b,i,c))

CELLS=[]; NPLAIN=''; NIDX=[]
try:
    _src=Path('/tmp/guide.html').read_text(encoding='utf-8')
    _a=_src.find('Платформа'); _a=_src.rfind('<div',0,_a) if _a>0 else 0
    _b=_src.find('uc-footer'); _b=_b if _b>0 else len(_src)
    _p=_Rich(); _p.feed(_src[_a:_b]); CELLS=_p.cells
    _np=[];
    for _j,(_ch,_x,_y,_z) in enumerate(CELLS):
        if not _ch.isspace(): _np.append(_ch); NIDX.append(_j)
    NPLAIN=''.join(_np)
except FileNotFoundError:
    pass

_cursor=0
def _render(a,bnd):
    out=[]; buf=''; cb=ci=cc=None; prev=False
    def flush():
        nonlocal buf
        if not buf: return
        t=H.escape(buf,quote=False)
        if cc: t=f'<span class="g-term">{t}</span>'
        if ci: t=f'<i>{t}</i>'
        if cb: t=f'<b>{t}</b>'
        out.append(t); buf=''
    for k in range(a,bnd+1):
        ch,b,i,c=CELLS[k]
        if ch.isspace():
            ch=' '
            if prev: continue
            prev=True
        else:
            prev=False
        if (b,i,c)!=(cb,ci,cc):
            flush(); cb,ci,cc=b,i,c
        buf+=ch
    flush()
    return ''.join(out).strip()

def style(text):
    """Возвращает абзац с инлайн-оформлением, взятым 1-в-1 из исходного HTML."""
    global _cursor
    if not NPLAIN: return H.escape(text,quote=False)
    key=''.join(c for c in text if not c.isspace())
    if not key: return H.escape(text,quote=False)
    pos=NPLAIN.find(key,_cursor)
    if pos<0: pos=NPLAIN.find(key)
    if pos<0: return H.escape(text,quote=False)
    _cursor=pos+len(key)
    return _render(NIDX[pos], NIDX[pos+len(key)-1])

# --- основной проход ---
body=[]
i=0
n=len(lines)
def esc(s): return s  # текст уже из источника; <b> сохраняем
while i<n:
    ln=lines[i].strip()
    if not ln: i+=1; continue
    if ln in SKIP: i+=1; continue
    if re.fullmatch(r'[1-4]', ln): i+=1; continue  # шаговые маркеры
    # убрали вводный абзац по просьбе (в исходнике вокруг тире — неразрывные пробелы)
    if 'это социально-благотворительный проект по развитию' in ln.replace('\xa0',' '):
        i+=1; continue
    # «Состоит из двух основных элементов» -> подзаголовок + нумерованные карточки
    if ln.startswith('Состоит из двух основных элементов'):
        body.append('<p class="g-lead">'+style(ln)+'</p>')
        items=[]; j=i+1
        while j<n and len(items)<2:
            s=lines[j].strip()
            if s: items.append(s)
            j+=1
        lis=''
        for idx,it in enumerate(items, start=1):
            lis+=(f'<li><span class="g-num g-num-{idx}">{idx}</span>'
                  f'<span class="g-el-text">{style(it.rstrip(" ;"))}</span></li>')
        body.append('<ol class="g-elements">'+lis+'</ol>')
        i=j; continue
    # Матрица: вставляем после h2 и проглатываем строки до 'Регистрация' (первое определение)
    if ln=='Матрица Грейдов':
        body.append('<h2>Матрица Грейдов</h2>')
        body.append(matrix_html())
        i+=1
        # пропустить строки матрицы (заглавные таблицы) до первого определения 'Регистрация'
        while i<n and lines[i].strip()!='Регистрация':
            i+=1
        continue
    # RL таблица: заголовок "Таблица Running Level"
    if ln=='Таблица Running Level':
        body.append('<h2>Таблица Running Level</h2>')
        body.append('<div class="g-tabs"><button class="g-tab on" data-t="m">Мужчины</button><button class="g-tab" data-t="w">Женщины</button></div>')
        # собрать мужские строки: после "RL (M) ..." до "RL (Ж) ..."
        # найти заголовки
        j=i+1
        while j<n and not lines[j].startswith('RL (M)'): j+=1
        mhead=lines[j]; j+=1
        mrows=[]
        while j<n and not lines[j].startswith('RL (Ж)'):
            if re.match(r'^(NL Rus|\d+) ', lines[j]): mrows.append(lines[j])
            j+=1
        whead=lines[j]; j+=1
        wrows=[]
        while j<n and lines[j].strip() not in H2:
            if re.match(r'^(NL Rus|\d+) ', lines[j]): wrows.append(lines[j])
            j+=1
        body.append('<div class="g-rlpane" data-pane="m">'+rl_table(mrows,mhead)+'</div>')
        body.append('<div class="g-rlpane" data-pane="w" hidden>'+rl_table(wrows,whead)+'</div>')
        i=j
        continue
    # многострочный формульный блок (min( ... )) — моноширинно, целиком
    if is_code(ln):
        block=[]
        while i<n and is_code(lines[i]):
            block.append(lines[i].rstrip()); i+=1
        body.append('<pre class="g-formula">'+H.escape('\n'.join(block))+'</pre>')
        continue
    # таблица с разделителем ';' (минимум 2 непустые ячейки)
    if is_semirow(ln):
        block=[]
        while i<n and is_semirow(lines[i]):
            block.append(lines[i].strip()); i+=1
        body.append(semi_table(block))
        continue
    if ln in H2:
        body.append(f'<h2>{ln}</h2>'); i+=1; continue
    if ln in H3:
        body.append(f'<h3>{ln}</h3>'); i+=1; continue
    # одиночная строка-формула
    if re.fullmatch(r'[\w().,<>=\-∞ ]{1,40}', ln) and re.match(r'^(min|max|iif)\(', ln):
        body.append(f'<pre class="g-formula">{ln}</pre>'); i+=1; continue
    # абзац; убираем висячую разделительную ';' из исходной вёрстки + выделяем термины
    body.append(f'<p>{style(ln.rstrip(" ;"))}</p>'); i+=1

content='\n    '.join(body)

CSS = """
    :root{--bg:#eef2ec;--bg2:#f4f7f3;--surface:#ffffff;--ink:#0e120e;--ink2:#1b1b21;--muted:#6b7068;--muted2:#9aa097;--border:#e6eae3;--border2:#dadfd6;--lime:#d0f85d;--lime2:#d5ffa8;--lime-deep:#bee14b;--lime-ink:#1f2a05;--c-blue:#bcdcff;--c-blue-ink:#143b6b;--c-tomato:#f0563f;--fd:'Manrope',system-ui,sans-serif;--fb:'Inter',system-ui,sans-serif;--fm:'JetBrains Mono',ui-monospace,monospace;--fw:'Roboto Flex','Roboto',system-ui,sans-serif;--maxw:1240px;--sh-sm:0 2px 6px rgba(15,20,15,.05),0 1px 2px rgba(15,20,15,.04);--sh-md:0 14px 30px -10px rgba(15,30,12,.10),0 8px 18px -6px rgba(15,30,12,.06);--r-sm:12px;--r-md:18px;--r-lg:24px}
    *{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}
    body{background:var(--bg);color:var(--ink);font-family:var(--fb);line-height:1.65;-webkit-font-smoothing:antialiased}
    ::selection{background:var(--lime);color:var(--lime-ink)}img{max-width:100%;display:block}a{color:inherit}
    #navbar{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(238,242,236,.82);backdrop-filter:blur(18px) saturate(160%);-webkit-backdrop-filter:blur(18px) saturate(160%);border-bottom:1px solid var(--border)}
    #navbar .nav-inner{max-width:var(--maxw);margin:0 auto;display:flex;align-items:center;justify-content:space-between;padding:.85rem clamp(1.25rem,5vw,4rem)}
    .nav-logo{display:flex;align-items:center;gap:.55rem;text-decoration:none;color:var(--ink)}
    .nav-logo img{height:28px;width:auto;display:block}
    .nav-logo .wordmark{font-family:var(--fw);font-weight:800;font-style:italic;font-variation-settings:'slnt' -10;font-size:22px;line-height:1;color:var(--ink)}
    .nav-links{display:flex;gap:.05rem;list-style:none;align-items:center}
    .nav-links a{color:var(--muted);text-decoration:none;font-size:.92rem;font-weight:500;padding:.55rem .85rem;border-radius:999px}
    .nav-links a:hover{color:var(--ink);background:rgba(15,20,15,.04)}
    .nav-cta{display:none;align-items:center;gap:.35rem;background:var(--ink);color:#fff;font-family:var(--fd);font-weight:700;font-size:.92rem;padding:.6rem 1.1rem;border-radius:999px;text-decoration:none}
    @media(min-width:1100px){.nav-cta{display:inline-flex}}
    @media(max-width:1080px){.nav-links{display:none}}
    .legal{max-width:var(--maxw);margin:0 auto;padding:7.5rem clamp(1.25rem,5vw,4rem) 4rem}
    .legal-wrap{max-width:860px;margin:0 auto}
    .legal-back{display:inline-flex;gap:.4rem;font-size:.9rem;color:var(--muted);text-decoration:none;margin-bottom:1.2rem}
    .legal-back:hover{color:var(--ink)}
    /* hero-блок страницы */
    .g-hero{position:relative;overflow:hidden;border-radius:var(--r-lg);background:#deeafd;box-shadow:var(--sh-md);margin:0 0 2.8rem;display:grid;grid-template-columns:1fr minmax(240px,46%);gap:1rem;align-items:center;isolation:isolate}
    .g-hero::before{content:'';position:absolute;inset:0;z-index:0;background:url('art/electric-2-sky.svg') center/cover no-repeat}
    .g-hero::after{content:'';position:absolute;inset:0;z-index:0;background:linear-gradient(105deg,rgba(252,253,254,.92) 0%,rgba(252,253,254,.55) 46%,rgba(252,253,254,0) 72%)}
    .g-hero-text{position:relative;z-index:2;padding:clamp(1.8rem,4vw,2.8rem) clamp(1.4rem,4vw,2.6rem)}
    .g-hero-eyebrow{display:inline-block;font-family:var(--fm);font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:var(--c-blue-ink);background:#fff;border:1px solid var(--c-blue);border-radius:999px;padding:.34rem .8rem;margin-bottom:1.1rem}
    .g-hero h1{font-family:var(--fd);font-weight:800;font-size:clamp(2rem,4.6vw,3.1rem);letter-spacing:-.03em;line-height:1.04;margin:0 0 .9rem;color:var(--ink)}
    .g-hero-sub{color:#2c466f;font-size:clamp(1rem,1.4vw,1.12rem);line-height:1.6;max-width:34ch;margin:0}
    .g-hero-art{position:relative;z-index:1;align-self:center;justify-self:center;padding:clamp(1.2rem,3vw,2rem) clamp(1rem,2.5vw,1.6rem)}
    .g-hero-art img{display:block;width:100%;max-width:400px;height:auto;border-radius:22px;box-shadow:0 26px 50px -20px rgba(20,45,90,.4),0 8px 18px -10px rgba(20,45,90,.22);transform:rotate(-1.5deg)}
    @media(max-width:680px){
      .g-hero{grid-template-columns:1fr}
      .g-hero::after{background:linear-gradient(180deg,rgba(252,253,254,.92) 0%,rgba(252,253,254,.55) 62%,rgba(252,253,254,.35) 100%)}
      .g-hero-art{justify-self:center;padding-top:0;max-width:300px;margin:0 auto}
    }
    .legal h2{font-family:var(--fd);font-weight:800;font-size:clamp(1.3rem,2.4vw,1.7rem);letter-spacing:-.02em;line-height:1.2;margin:2.8rem 0 1rem;padding-top:.4rem}
    .legal h3{font-family:var(--fd);font-weight:700;font-size:1.1rem;letter-spacing:-.01em;margin:1.8rem 0 .5rem;color:var(--ink)}
    .legal p{color:var(--ink2);line-height:1.72;margin-bottom:.9rem;font-size:1rem}
    .legal b{font-weight:600;color:var(--ink)}
    .legal .g-term{color:var(--c-tomato);font-weight:600}
    .g-lead{font-family:var(--fd);font-weight:700;font-size:clamp(1.05rem,1.6vw,1.2rem);color:var(--ink);margin:.4rem 0 1.1rem}
    .g-elements{list-style:none;margin:.2rem 0 2.4rem;padding:0;display:grid;gap:1rem}
    .g-elements li{display:flex;gap:1.1rem;align-items:flex-start;background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:1.2rem 1.4rem;box-shadow:var(--sh-sm)}
    .g-num{flex:0 0 auto;width:36px;height:36px;border-radius:11px;font-family:var(--fd);font-weight:800;font-size:1.1rem;display:flex;align-items:center;justify-content:center}
    .g-num-1{background:var(--c-blue);color:var(--c-blue-ink)}
    .g-num-2{background:var(--lime);color:var(--lime-ink)}
    .g-el-text{color:var(--ink2);line-height:1.65;font-size:1rem;align-self:center}
    .g-formula{font-family:var(--fm);background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:.5rem .8rem;margin:.3rem 0;font-size:.9rem;color:var(--ink);display:inline-block}
    .g-tablewrap{overflow-x:auto;margin:1.2rem 0 1.6rem;border:1px solid var(--border);border-radius:var(--r-md);background:var(--surface);box-shadow:var(--sh-sm)}
    table.g-tbl,table.g-matrix{border-collapse:collapse;width:100%;font-size:.86rem}
    table.g-tbl th,table.g-tbl td,table.g-matrix th,table.g-matrix td{padding:.6rem .75rem;text-align:left;border-bottom:1px solid var(--border);white-space:nowrap}
    table.g-tbl thead th,table.g-tbl tr:first-child th{background:var(--bg2);font-family:var(--fd);font-weight:700;color:var(--ink);position:sticky;top:0}
    .g-matrix th{background:var(--bg2);font-family:var(--fd);font-weight:700}
    .g-matrix .g-rowh{text-align:left;font-family:var(--fb);font-weight:600;color:var(--ink);background:var(--surface);position:sticky;left:0;min-width:200px}
    .g-matrix td{text-align:center;color:var(--ink2)}
    .g-matrix tr.g-sub td{background:var(--lime2);color:var(--lime-ink);font-family:var(--fd);font-weight:800;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;text-align:left}
    .g-rl table{font-size:.82rem}
    .g-rl{max-height:560px;overflow:auto}
    .g-tabs{display:flex;gap:.4rem;margin:1.2rem 0 .2rem}
    .g-tab{font-family:var(--fd);font-weight:700;font-size:.9rem;padding:.5rem 1.1rem;border-radius:999px;border:1px solid var(--border);background:var(--surface);color:var(--muted);cursor:pointer}
    .g-tab.on{background:var(--ink);color:#fff;border-color:var(--ink)}
    footer{padding:4rem 0 2rem;margin-top:3rem;background:var(--surface);border-top:1px solid var(--border)}
    .foot-inner{max-width:var(--maxw);margin:0 auto;padding:0 clamp(1.25rem,5vw,4rem);display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:2rem}
    .foot-c{display:flex;flex-direction:column;gap:.6rem}
    .foot-c .label{font-family:var(--fm);font-size:.66rem;letter-spacing:.24em;color:var(--muted);text-transform:uppercase;margin-bottom:.5rem}
    .foot-c a{color:var(--ink);text-decoration:none;font-size:.95rem}.foot-c a:hover{color:var(--lime-ink)}
    .foot-c .tagline{color:var(--muted);font-size:.92rem;line-height:1.6;max-width:340px}
    .foot-bottom{max-width:var(--maxw);margin:2.5rem auto 0;padding:1.5rem clamp(1.25rem,5vw,4rem) 0;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;color:var(--muted);font-size:.85rem;font-family:var(--fm)}
    .foot-bottom a{color:var(--muted);text-decoration:none}.foot-bottom a:hover{color:var(--ink)}
    @media(max-width:880px){.foot-inner{grid-template-columns:1fr;gap:2rem}}
"""

NAV = """<nav id="navbar"><div class="nav-inner">
  <a href="index.html" class="nav-logo" aria-label="Moneyrun"><img class="logo-mark" src="art/logo-mark.png" alt="Moneyrun mark" width="120" height="120"><span class="wordmark">Moneyrun</span></a>
  <div class="nav-right" style="display:flex;align-items:center;gap:.65rem">
    <ul class="nav-links"><li><a href="index.html#howto">Как работает</a></li><li><a href="index.html#rules">Правила</a></li><li><a href="index.html#clubs">Клубы</a></li><li><a href="index.html#principles">Принципы</a></li></ul>
    <a href="index.html#download" class="nav-cta">Скачать →</a>
  </div></div></nav>"""

FOOT = """<footer><div class="foot-inner">
  <div class="foot-c"><a href="index.html" class="nav-logo" style="margin-bottom:.4rem"><img class="logo-mark" src="art/logo-mark.png" alt="Moneyrun" width="120" height="120"><span class="wordmark">Moneyrun</span></a><p class="tagline">Социально-благотворительный проект по развитию бегового движения.</p></div>
  <div class="foot-c"><span class="label">Сервис</span><a href="index.html#howto">Как работает</a><a href="index.html#rules">Правила</a><a href="index.html#clubs">Клубы</a><a href="index.html#principles">Принципы</a></div>
  <div class="foot-c"><span class="label">Связаться</span><a href="https://t.me/moneyrun" target="_blank" rel="noopener">Telegram · @moneyrun</a><a href="index.html#contact">Сотрудничество</a></div>
</div><div class="foot-bottom"><span>© 2023 — 2026 Moneyrun</span><span style="display:flex;gap:1.5rem;flex-wrap:wrap"><a href="guide.html">Правила сервиса</a><a href="privacypolicy.html">Политика конфиденциальности</a></span></div></footer>"""

JS = """<script>document.querySelectorAll('.g-tab').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.g-tab').forEach(x=>x.classList.remove('on'));b.classList.add('on');const t=b.dataset.t;document.querySelectorAll('.g-rlpane').forEach(p=>{p.hidden=(p.dataset.pane!==t)});}));</script>"""

doc=f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Правила сервиса — Moneyrun</title>
  <meta name="description" content="Правила сервиса Moneyrun: игровой Грейдовый модуль, начисление XP, монетизация и финансирование.">
  <meta name="theme-color" content="#eef2ec">
  <link rel="icon" type="image/png" href="https://static.tildacdn.com/tild6335-6462-4965-b561-643434616164/Logo_32x32.png">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,slnt,wght@8..144,-10..0,400..1000&family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
{NAV}
<main class="legal"><div class="legal-wrap">
    <a href="index.html" class="legal-back">← На главную</a>
    <header class="g-hero">
      <div class="g-hero-text">
        <span class="g-hero-eyebrow">Документация</span>
        <h1>Правила сервиса</h1>
        <p class="g-hero-sub">Платформа Moneyrun — социально-благотворительный проект по развитию бегового движения.</p>
      </div>
      <div class="g-hero-art" aria-hidden="true">
        <img src="art/guide-hero.svg" alt="Прогресс по Грейдам" loading="eager">
      </div>
    </header>
    {content}
</div></main>
{FOOT}
{JS}
</body>
</html>
"""
Path(ROOT/'guide.html').write_text(doc, encoding='utf-8')
print('guide.html written,', len(doc), 'bytes; body blocks:', len(body))
