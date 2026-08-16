# -*- coding: utf-8 -*-
"""Parse a 行测真题 .docx into ordered blocks: paragraphs (text+images) and tables."""
import zipfile
import re
import sys
import os
import json
import xml.etree.ElementTree as ET

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
VML_NS = 'urn:schemas-microsoft-com:vml'


def w(tag):
    return '{%s}%s' % (W_NS, tag)


def rattr(el, name):
    return el.get('{%s}%s' % (R_NS, name))


def load_docx(path):
    z = zipfile.ZipFile(path)
    doc = ET.fromstring(z.read('word/document.xml'))
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    media = {}
    for rel in rels:
        target = rel.get('Target') or ''
        m = re.search(r'media/([^/]+)$', target)
        if m:
            media[rel.get('Id')] = m.group(1)
    return doc, media


def para_tokens(p, media):
    """Return ordered tokens of a paragraph: ('t', text) and ('img', mediafile)."""
    tokens = []
    for el in p.iter():
        tag = el.tag
        if tag == w('t') and el.text:
            tokens.append(('t', el.text))
        elif tag == '{%s}blip' % A_NS:
            rid = rattr(el, 'embed')
            if rid and rid in media:
                tokens.append(('img', media[rid]))
        elif tag == '{%s}imagedata' % VML_NS:
            rid = rattr(el, 'id')
            if rid and rid in media:
                tokens.append(('img', media[rid]))
    # merge consecutive duplicate images (drawing + vml fallback both present)
    merged = []
    for tok in tokens:
        if merged and tok == merged[-1]:
            continue
        merged.append(tok)
    return merged


def parse_para(p, media):
    return ('p', para_tokens(p, media))


def parse_table(tbl, media):
    rows = []
    for tr in tbl.findall(w('tr')):
        cells = []
        for tc in tr.findall(w('tc')):
            cell_blocks = []
            for child in tc:
                if child.tag == w('p'):
                    cell_blocks.append(parse_para(child, media))
                elif child.tag == w('tbl'):
                    cell_blocks.append(parse_table(child, media))
            cells.append(cell_blocks)
        rows.append(cells)
    return ('tbl', rows)


def parse_blocks(path):
    doc, media = load_docx(path)
    body = doc.find(w('body'))
    blocks = []
    for child in body:
        if child.tag == w('p'):
            blocks.append(parse_para(child, media))
        elif child.tag == w('tbl'):
            blocks.append(parse_table(child, media))
    return blocks


def block_text(block):
    """Plain text of a block (paragraph or flattened table)."""
    kind, data = block
    if kind == 'p':
        return ''.join(t for k, t in data if k == 't')
    out = []
    for row in data:
        for cell in row:
            for b in cell:
                out.append(block_text(b))
            out.append(' | ')
        out.append('\n')
    return ''.join(out)


def block_imgs(block):
    kind, data = block
    if kind == 'p':
        return [t for k, t in data if k == 'img']
    out = []
    for row in data:
        for cell in row:
            for b in cell:
                out.extend(block_imgs(b))
    return out


def main():
    path = sys.argv[1]
    blocks = parse_blocks(path)
    print('total blocks:', len(blocks))
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    for i, b in enumerate(blocks):
        if i >= limit:
            break
        txt = block_text(b).strip()
        imgs = block_imgs(b)
        if txt or imgs:
            line = '[IMG:%s] ' % ','.join(imgs) if imgs else ''
            print(i, line + txt[:120])


if __name__ == '__main__':
    main()
