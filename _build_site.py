#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将《万古云海》全部 .md 文件转换为 HTML 网站。
生成 site/ 目录，包含 index.html 及各卷/楔子/附录页面。
运行方式：python3 _build_site.py
"""

import os, re, glob, html as html_mod

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, 'site')
os.makedirs(SITE, exist_ok=True)

# ── 卷排序 ──
VOL_ORDER = {
    '楔子': 0,
    '第一卷': 1, '第二卷': 2, '第三卷': 3, '第四卷': 4,
    '第五卷': 5, '第六卷': 6, '第七卷': 7, '第八卷': 8,
    '第九卷': 9, '第十卷': 10, '第十一卷': 11, '第十二卷': 12,
    '附录': 13,
}

def sort_key(fname):
    base = os.path.splitext(fname)[0]
    for k, v in VOL_ORDER.items():
        if base.startswith(k) or base == k:
            return v
    return 99

# ── 极简 Markdown → HTML 转换器 ──
def md_to_html(text):
    """将 Markdown 文本转为 HTML 片段（支持标题、表格、粗体、引用、段落、分隔线）。"""
    lines = text.split('\n')
    out = []
    in_table = False
    in_blockquote = False
    in_ul = False
    para_buf = []

    def flush_para():
        if para_buf:
            p = '<br>\n'.join(para_buf)
            out.append(f'<p>{p}</p>')
            para_buf.clear()

    def flush_ul():
        nonlocal in_ul
        if in_ul:
            out.append('</ul>')
            in_ul = False

    def flush_bq():
        nonlocal in_blockquote
        if in_blockquote:
            out.append('</blockquote>')
            in_blockquote = False

    def inline(s):
        s = html_mod.escape(s)
        # bold **...**
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        # inline code `...`
        s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
        return s

    for raw_line in lines:
        line = raw_line.rstrip()

        # ── 分隔线 ──
        if re.match(r'^---+\s*$', line):
            flush_para(); flush_ul(); flush_bq()
            if in_table:
                out.append('</table>')
                in_table = False
            out.append('<hr>')
            continue

        # ── 表格 ──
        if '|' in line and re.match(r'^\s*\|', line):
            flush_para(); flush_ul(); flush_bq()
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            # 分隔行 (---|---|---)
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue
            if not in_table:
                out.append('<table>')
                in_table = True
                # 第一行当表头
                out.append('<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr>')
            else:
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
            continue
        else:
            if in_table:
                out.append('</table>')
                in_table = False

        # ── 标题 ──
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            flush_para(); flush_ul(); flush_bq()
            level = len(m.group(1))
            title = inline(m.group(2))
            slug = re.sub(r'\s+', '-', m.group(2).strip())
            out.append(f'<h{level} id="{html_mod.escape(slug)}">{title}</h{level}>')
            continue

        # ── 引用 ──
        if line.startswith('>'):
            flush_para(); flush_ul()
            content = inline(line.lstrip('>').strip())
            if not in_blockquote:
                out.append('<blockquote>')
                in_blockquote = True
            out.append(f'<p>{content}</p>')
            continue
        else:
            flush_bq()

        # ── 无序列表 ──
        m = re.match(r'^[-*]\s+(.+)$', line)
        if m:
            flush_para(); flush_bq()
            if not in_ul:
                out.append('<ul>')
                in_ul = True
            out.append(f'<li>{inline(m.group(1))}</li>')
            continue
        else:
            flush_ul()

        # ── 空行 ──
        if not line.strip():
            flush_para()
            continue

        # ── 普通段落 ──
        para_buf.append(inline(line))

    flush_para(); flush_ul(); flush_bq()
    if in_table:
        out.append('</table>')
    return '\n'.join(out)


# ── CSS 样式 ──
CSS = '''
:root {
    --bg: #0e0e12;
    --card-bg: #16161d;
    --text: #d4d4dc;
    --text-dim: #8a8a9a;
    --accent: #6c9bff;
    --accent2: #a78bfa;
    --gold: #f0c674;
    --border: #2a2a3a;
    --hover: #1e1e2a;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: "Noto Serif SC", "Source Han Serif CN", "Songti SC", serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.9;
    min-height: 100vh;
}
.container { max-width: 900px; margin: 0 auto; padding: 40px 24px 80px; }
h1 {
    text-align: center; font-size: 2.2em; color: var(--gold);
    margin-bottom: 8px; letter-spacing: 0.15em;
}
.subtitle { text-align: center; color: var(--text-dim); margin-bottom: 40px; font-size: 0.95em; }
h2 {
    font-size: 1.5em; color: var(--accent); margin: 48px 0 16px;
    padding-bottom: 8px; border-bottom: 1px solid var(--border);
}
h3 { font-size: 1.2em; color: var(--accent2); margin: 32px 0 12px; }
h4, h5, h6 { color: var(--gold); margin: 24px 0 8px; }
p { margin: 12px 0; text-indent: 2em; text-align: justify; }
blockquote {
    border-left: 3px solid var(--accent2); margin: 16px 0;
    padding: 8px 20px; background: rgba(167,139,250,0.06);
    border-radius: 0 6px 6px 0;
}
blockquote p { text-indent: 0; color: var(--text-dim); font-style: italic; }
ul { margin: 12px 0 12px 2em; }
li { margin: 4px 0; }
hr { border: none; border-top: 1px solid var(--border); margin: 36px 0; }
table {
    width: 100%; border-collapse: collapse; margin: 16px 0;
    font-size: 0.92em;
}
th, td {
    border: 1px solid var(--border); padding: 8px 12px; text-align: left;
}
th { background: rgba(108,155,255,0.1); color: var(--accent); font-weight: 600; }
td { background: var(--card-bg); }
strong { color: var(--gold); }
code { background: rgba(108,155,255,0.12); padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
a { color: var(--accent); text-decoration: none; transition: color 0.2s; }
a:hover { color: var(--gold); }

/* 首页专用 */
.hero { text-align: center; padding: 60px 0 20px; }
.hero h1 { font-size: 3em; margin-bottom: 12px; }
.hero .stats { color: var(--text-dim); font-size: 1.05em; margin-bottom: 48px; }
.vol-grid { display: grid; grid-template-columns: 1fr; gap: 16px; margin-bottom: 40px; }
.vol-card {
    background: var(--card-bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px 24px; transition: all 0.25s;
    cursor: pointer; text-decoration: none; display: block;
}
.vol-card:hover { border-color: var(--accent); background: var(--hover); transform: translateY(-2px); }
.vol-card .vol-title { font-size: 1.2em; color: var(--gold); margin-bottom: 6px; }
.vol-card .vol-meta { color: var(--text-dim); font-size: 0.88em; }
.vol-card .vol-chapters {
    margin-top: 10px; font-size: 0.85em; color: var(--text-dim);
    max-height: 0; overflow: hidden; transition: max-height 0.35s ease;
}
.vol-card:hover .vol-chapters { max-height: 600px; }
.vol-card .vol-chapters span { display: inline-block; margin: 2px 8px 2px 0; }
.vol-card .vol-chapters a { color: var(--accent); }
.vol-card .vol-chapters a:hover { color: var(--gold); }

/* 导航 */
.nav {
    position: sticky; top: 0; background: rgba(14,14,18,0.92);
    backdrop-filter: blur(8px); border-bottom: 1px solid var(--border);
    padding: 10px 24px; z-index: 100; display: flex; align-items: center;
    gap: 16px; font-size: 0.9em;
}
.nav a { color: var(--text-dim); }
.nav a:hover { color: var(--gold); }
.nav .sep { color: var(--border); }

/* 返回顶部 */
.back-top {
    position: fixed; bottom: 32px; right: 32px;
    width: 44px; height: 44px; border-radius: 50%;
    background: var(--card-bg); border: 1px solid var(--border);
    color: var(--accent); font-size: 1.3em; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    opacity: 0; transition: opacity 0.3s;
}
.back-top.show { opacity: 1; }

@media (max-width: 640px) {
    .container { padding: 20px 16px 60px; }
    h1 { font-size: 1.6em; }
    h2 { font-size: 1.25em; }
    .hero h1 { font-size: 2em; }
    table { font-size: 0.82em; }
    th, td { padding: 5px 8px; }
}
'''

BACK_TOP_JS = '''
<button class="back-top" id="backTop" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
window.addEventListener('scroll', function(){
    document.getElementById('backTop').classList.toggle('show', window.scrollY > 400);
});
</script>
'''


def page_html(title, body, nav_html=''):
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_mod.escape(title)} - 万古云海</title>
<style>{CSS}</style>
</head>
<body>
{nav_html}
<div class="container">
{body}
</div>
{BACK_TOP_JS}
</body>
</html>'''


def nav_bar(current_label, prev_link=None, next_link=None):
    parts = ['<div class="nav">']
    parts.append('<a href="index.html">首页</a>')
    parts.append('<span class="sep">›</span>')
    parts.append(f'<span style="color:var(--gold)">{html_mod.escape(current_label)}</span>')
    parts.append('<span style="flex:1"></span>')
    if prev_link:
        parts.append(f'<a href="{prev_link[1]}">← {html_mod.escape(prev_link[0])}</a>')
    if prev_link and next_link:
        parts.append('<span class="sep">|</span>')
    if next_link:
        parts.append(f'<a href="{next_link[1]}">{html_mod.escape(next_link[0])} →</a>')
    parts.append('</div>')
    return '\n'.join(parts)


# ── 收集所有 md 文件 ──
md_files = sorted(glob.glob(os.path.join(BASE, '*.md')), key=lambda f: sort_key(os.path.basename(f)))
# 排除总纲
md_files = [f for f in md_files if '创作总纲' not in f]

entries = []  # (label, html_filename, md_path, chapters[], nws)
for fp in md_files:
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()
    basename = os.path.splitext(os.path.basename(fp))[0]
    html_name = basename + '.html'
    nws = len(re.sub(r'\s', '', text))

    # 提取章节列表
    chapters = []
    for m in re.finditer(r'## (第.+?章\s*.+)', text):
        ch_title = m.group(1).strip()
        slug = re.sub(r'\s+', '-', ch_title)
        chapters.append((ch_title, slug))

    # 推导显示标签
    if basename == '楔子':
        label = '楔子'
    elif basename == '附录':
        label = '附录'
    else:
        # e.g. 第一卷_初入修途 -> 第一卷 · 初入修途
        parts = basename.split('_', 1)
        label = ' · '.join(parts) if len(parts) == 2 else basename

    entries.append((label, html_name, fp, chapters, nws))

# ── 生成各页面 HTML ──
for i, (label, html_name, fp, chapters, nws) in enumerate(entries):
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read()

    body_html = md_to_html(text)

    prev_link = (entries[i-1][0], entries[i-1][1]) if i > 0 else None
    next_link = (entries[i+1][0], entries[i+1][1]) if i < len(entries)-1 else None
    nav = nav_bar(label, prev_link, next_link)

    full_html = page_html(label, body_html, nav)
    out_path = os.path.join(SITE, html_name)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f'  ✓ {html_name} ({nws}字, {len(chapters)}章)')

# ── 生成 index.html ──
total_nws = sum(e[4] for e in entries)
total_chs = sum(len(e[3]) for e in entries)

cards = []
for label, html_name, fp, chapters, nws in entries:
    ch_info = f'{len(chapters)}章 · ' if chapters else ''
    ch_spans = ''
    if chapters:
        ch_links = []
        for ch_title, slug in chapters:
            ch_links.append(f'<a href="{html_name}#{html_mod.escape(slug)}">{html_mod.escape(ch_title)}</a>')
        ch_spans = '<br>'.join(ch_links)

    cards.append(f'''<a class="vol-card" href="{html_name}">
  <div class="vol-title">{html_mod.escape(label)}</div>
  <div class="vol-meta">{ch_info}{nws}字</div>
  {"<div class='vol-chapters'>" + ch_spans + "</div>" if ch_spans else ""}
</a>''')

index_body = f'''
<div class="hero">
  <h1>万古云海</h1>
  <p class="subtitle">玄幻修真长篇小说 · 辰东风格</p>
  <p class="stats">全书 {total_chs} 章 · {total_nws} 字（{total_nws/10000:.1f}万字）</p>
</div>
<div class="vol-grid">
{"".join(cards)}
</div>
'''

index_html = page_html('万古云海', index_body)
with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
print(f'\n  ✓ index.html (首页)')
print(f'\n完成！共 {len(entries)+1} 个 HTML 文件 → site/')
print(f'预览：python3 -m http.server 8000 -d "{SITE}"')
