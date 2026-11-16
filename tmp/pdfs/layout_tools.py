from functools import lru_cache
from xml.sax.saxutils import escape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

LEADING = {}
CHANGES = []

@lru_cache(None)
def rules_for(original, n):
    p = original.pages[n-1]
    vertical = [e for e in p.lines if abs(e['x0']-e['x1']) < .1]
    return [e for e in p.lines
            if abs(e['y0']-e['y1']) < .1 and e['x1']-e['x0'] > 20
            and 35 < e['top'] < 805
            and not any(e['x0']-.8 <= v['x0'] <= e['x1']+.8
                        and v['top']-.8 <= e['top'] <= v['bottom']+.8
                        for v in vertical)]

def clear_above(original, n, e, size):
    return not any(ch['text'].strip() and ch['x0'] < e['x1']-2
                   and ch['x1'] > e['x0']+2
                   and ch['top'] < e['top']-1.5
                   and ch['bottom'] > e['top']-size-2
                   for ch in original.pages[n-1].chars)

def paragraph(text, size, width, leading):
    p = Paragraph(escape(text).replace('\n', '<br/>'),
                  ParagraphStyle('layout', fontName='Helvetica', fontSize=size, leading=leading))
    _, height = p.wrap(width, 1000)
    return p, height

def fit_rule(original, n, anchor, text, size, x, h, mode):
    rules = rules_for(original, n)
    same = [e for e in rules if abs(e['top']-anchor['b']) < 3
            and e['x0'] >= anchor['r']+1]
    if same:
        e = min(same, key=lambda e: abs(x-e['x0']))
    elif mode == 'after':
        below = [e for e in rules if anchor['b']+2 <= e['top'] <= anchor['b']+h+19
                 and clear_above(original, n, e, min(size, 8.5))]
        if not below:
            return None
        e = min(below, key=lambda e:e['top'])
    else:
        return None
    if not clear_above(original, n, e, min(size, 8.5)):
        return None
    xx = e['x0']+3
    width = min(e['x1'], 552.8)-xx-3
    yy = e['top']-size-4
    following = sorted([z for z in rules if abs(z['x0']-e['x0'])<1
                        and abs(z['x1']-e['x1'])<1
                        and e['top']+10 < z['top'] <= e['top']+29
                        and clear_above(original,n,z,size)],key=lambda z:z['top'])
    lead = following[0]['top']-e['top'] if following else size*1.25
    p, ph = paragraph(text,size,width,lead)
    # Preserve room for a wrapped answer between this row and the next printed text.
    next_chars = [ch['top'] for ch in original.pages[n-1].chars
                  if ch['text'].strip() and ch['top'] > e['top']+1
                  and ch['x0'] < min(e['x1'],552.8) and ch['x1'] > xx]
    limit = min(next_chars, default=805)-2
    while yy+ph > limit and size > 7.6:
        size -= .2
        yy = e['top']-size-4
        lead = following[0]['top']-e['top'] if following else size*1.25
        p, ph = paragraph(text,size,width,lead)
    if yy+ph > limit:
        return None
    LEADING[(n,xx,yy,text)] = lead
    CHANGES.append((n, mode, text))
    return xx,yy,width,ph+.2,text,size,False,False

def on_rule(n, x0, y, x1, text, size=8.5):
    x=x0+3; yy=y-size-4; w=x1-x0-6
    p, ph=paragraph(text,size,w,size*1.2)
    assert len(p.blPara.lines)==1,(n,text,w)
    return x,yy,w,ph+.2,text,size,False,False
