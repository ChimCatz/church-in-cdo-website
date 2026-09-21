#!/usr/bin/env python3
"""Rebuild the reading area of hwmr.html.

Inputs (kept in temp/HWMR/, not published):
  - Opening-text.txt                       the opening text (plain text)
  - "... Message <Word> – Prophesying Reference ....html"   one saved page per message

Output: replaces everything between <!-- HWMR:START --> and <!-- HWMR:END -->
in hwmr.html. Run from anywhere:  python tools/build_hwmr.py

To add a message (e.g. Message Eleven), save its page into temp/HWMR/ and re-run.
To change the week card's title/training/location, edit WEEK below.
"""
import glob
import html
import os
import re
import sys

from lxml import html as LH

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'temp', 'HWMR')
PAGE = os.path.join(ROOT, 'hwmr.html')

WEEK = {
    'training': 'July Summer Training 2026',
    'location': 'Anaheim, California',
}

WORDS = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
         'Ten', 'Eleven', 'Twelve']

esc = lambda t: html.escape(t, quote=False)
squash = lambda t: re.sub(r'\s+', ' ', t.replace('\xa0', ' ')).strip()


# ---------------------------------------------------------------- opening text

def opening_groups():
    raw = open(os.path.join(SRC, 'Opening-text.txt'), encoding='utf-8').read().strip()
    blocks = [b.strip() for b in re.split(r'\n\s*\n', raw)]
    heading_para = lambda b: [x.strip() for x in b.split('\n', 1)]

    groups = []

    h, p = heading_para(blocks[0])
    groups.append((h, [f'<p>{esc(p)}</p>', f'<p>{esc(blocks[1])}</p>']))

    h, p = heading_para(blocks[2])
    body, src = blocks[3].split(' Extracted from ', 1)
    groups.append((h, [f'<p>{esc(p)}</p>', f'<p>{esc(body)}</p>',
                       f'<p class="source">Extracted from {esc(src)}</p>']))

    head, intro = blocks[4].split(' – ', 1)
    intro = intro[0].upper() + intro[1:]
    parts = [f'<p>{esc(intro)}</p>']
    qs = blocks[5:]
    qs[0] = qs[0].lstrip('"')          # the five quotes were wrapped in one pair of "
    qs[-1] = qs[-1].rstrip('"')
    for q in qs:
        text, cite = q.rsplit(' (', 1)
        cite = cite.rstrip(')')
        parts.append(f'<blockquote>\n  <p>{esc(text)}</p>\n  <footer>{esc(cite)}</footer>\n</blockquote>')
    groups.append((head, parts))
    return groups


# -------------------------------------------------------------------- messages

def inner(el, unwrap_bold=False):
    """Inline HTML of el: keep <strong>, drop spans/styles."""
    out = [esc(el.text or '')]
    for ch in el:
        if ch.tag == 'strong' and not unwrap_bold:
            out.append('<strong>' + inner(ch) + '</strong>')
        else:
            out.append(inner(ch, unwrap_bold))
        out.append(esc(ch.tail or ''))
    return ''.join(out)


def clean(el, unwrap_bold=False):
    s = inner(el, unwrap_bold).replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'</strong>\s*<strong>', ' ', s) if not unwrap_bold else s


def all_bold(el):
    total = squash(el.text_content())
    bold = squash(' '.join(s.text_content() for s in el.iter('strong')))
    return bool(total) and squash(total.replace(' ', '')) == squash(bold.replace(' ', ''))


ROMAN = re.compile(r'^[IVXL]+\.\s')          # I. II. ... XV. (main points)
LETTER = re.compile(r'^[A-Z]\.\s')            # A. B. (sub-points)
NUMBER = re.compile(r'^\d+\.\s')              # 1. 2. (sub-sub-points)
DAY = re.compile(r'^Day \d+$')


def indent_of(el):
    m = re.search(r'padding-left:\s*(\d+)px', el.get('style') or '')
    return int(m.group(1)) // 40 if m else 0


def load_message(path):
    raw = open(path, 'rb').read()
    doc = LH.fromstring(raw)
    c = doc.xpath('//div[contains(@class,"czr-wp-the-content")]')[0]
    kids = [k for k in c if isinstance(k.tag, str)]
    m = re.search(rb'url:\s*(https?://\S+)', raw[:600])
    url = m.group(1).decode() if m else ''

    series, num, title = (squash(k.text_content()) for k in kids[:3])
    body, state, in_verse = [], None, False
    stats = {}

    def add(cls, html_, tag='p'):
        stats[cls] = stats.get(cls, 0) + 1
        attr = f' class="{cls}"' if cls else ''
        body.append(f'<{tag}{attr}>{html_}</{tag}>')

    for k in kids[3:]:
        text = squash(k.text_content())
        if not text or re.fullmatch(r'[—–\-\s]+', text):
            continue                                   # blank line / divider rule
        centered = 'text-align:center' in (k.get('style') or '').replace(' ', '')
        if k.tag in ('h3', 'h4') or (centered and text.isupper()):
            up = text.upper()
            state = ('outline' if 'EXTRACT' in up else 'opening' if 'OPENING' in up
                     else 'concluding' if 'CONCLUDING' in up else 'topics')
            in_verse = False
            stats['h5'] = stats.get('h5', 0) + 1
            body.append(f'<h5>{clean(k, True)}</h5>')
            continue

        bold = all_bold(k)
        if state == 'outline':
            if text.lower().startswith('scripture reading'):
                in_verse = True
                add('label', clean(k, True))
            elif ROMAN.match(text):
                in_verse = False
                add('op-main', clean(k, True))
            elif indent_of(k) >= 2 or NUMBER.match(text):
                add('op-sub2', clean(k))
            elif indent_of(k) == 1 or LETTER.match(text):
                add('op-sub', clean(k))
            elif in_verse:
                add('verse', clean(k))
            else:
                add('', clean(k))
        elif state == 'topics':
            if DAY.match(text):
                add('label day', clean(k, True))
            elif text.startswith('('):          # a few notes lack the closing )
                add('topic-note', clean(k))
            else:
                add('topic', clean(k))
        else:  # opening / concluding word
            if bold and len(text) < 90:
                add('label', clean(k, True))
            else:
                add('', clean(k))

    return {'series': series, 'num': num, 'title': title, 'url': url,
            'body': body, 'stats': stats, 'text': squash(' '.join(
                squash(k.text_content()) for k in kids))}


def find_messages():
    found = {}
    for i, w in enumerate(WORDS, 1):
        hits = glob.glob(os.path.join(SRC, f'* Message {w} *.html'))
        if hits:
            found[i] = load_message(hits[0])
    return found


# ------------------------------------------------------------------------ html

def group(title, parts, open_=False):
    body = '\n\n'.join(parts)
    body = '\n'.join('      ' + ln if ln else ln for ln in body.split('\n'))
    return (f'    <details class="group"{" open" if open_ else ""}>\n'
            f'      <summary><h2>{esc(title)}</h2></summary>\n'
            f'      <div class="group-body">\n{body}\n      </div>\n'
            f'    </details>')


def weekly(msgs):
    series = {m['series'] for m in msgs.values()}
    assert len(series) == 1, f'messages disagree on the series title: {series}'
    series = series.pop()

    tiles, panels = [], []
    for n in range(1, len(WORDS) + 1):
        m = msgs.get(n)
        if not m:
            tiles.append(f'          <button type="button" class="msg-tile" disabled>'
                         f'<span class="msg-num">M{n}</span>'
                         f'<span class="msg-title">Coming soon</span></button>')
            continue
        tiles.append(f'          <button type="button" class="msg-tile" aria-expanded="false" '
                     f'aria-controls="msg-{n}"><span class="msg-num">M{n}</span>'
                     f'<span class="msg-title">{esc(m["title"])}</span></button>')
        src = (f'<p class="msg-source">Source: <a href="{esc(m["url"])}" target="_blank" '
               f'rel="noopener">Prophesying Reference</a></p>') if m['url'] else ''
        inner_ = '\n'.join('          ' + b for b in m['body'])
        panels.append(
            f'        <section class="msg-panel" id="msg-{n}" aria-labelledby="msg-{n}-title">\n'
            f'          <header class="msg-head">\n'
            f'            <p class="msg-eyebrow">{esc(m["num"])}</p>\n'
            f'            <h4 id="msg-{n}-title">{esc(m["title"])}</h4>\n'
            f'          </header>\n'
            f'          <div class="msg-body">\n{inner_}\n          </div>\n'
            f'          {src}\n'
            f'        </section>')

    card = (
        '    <div class="week-card">\n'
        '      <header class="week-head">\n'
        f'        <h3>{esc(series)}</h3>\n'
        f'        <p class="week-meta"><span>{esc(WEEK["training"])}</span>'
        f'<span>{esc(WEEK["location"])}</span></p>\n'
        '      </header>\n'
        '      <div class="msg-tiles" role="group" aria-label="Messages">\n'
        + '\n'.join(tiles) + '\n      </div>\n'
        '      <div class="msg-panels">\n' + '\n'.join(panels) + '\n      </div>\n'
        '    </div>')
    return card


def build():
    msgs = find_messages()
    parts = [group(t, p) for t, p in opening_groups()]
    parts.append(group('Weekly Messages', [weekly(msgs)], open_=True))
    block = '<!-- HWMR:START (generated by tools/build_hwmr.py — edit that, not this) -->\n' \
            + '\n'.join(parts) + '\n    <!-- HWMR:END -->'

    page = open(PAGE, encoding='utf-8').read()
    if 'HWMR:START' in page:
        page = re.sub(r'<!-- HWMR:START.*?<!-- HWMR:END -->', lambda m: block, page, flags=re.S)
    else:
        page = re.sub(r'(<article class="prose">).*?(</article>)',
                      lambda m: m.group(1) + '\n    ' + block + '\n    ' + m.group(2),
                      page, flags=re.S)
    open(PAGE, 'w', encoding='utf-8', newline='\n').write(page)
    return msgs


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    msgs = build()
    for n, m in sorted(msgs.items()):
        print(f'M{n:<2} {m["title"][:60]:<60} {m["stats"]}')
    missing = [n for n in range(1, 13) if n not in msgs]
    print('missing:', missing or 'none')
