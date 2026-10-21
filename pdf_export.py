"""Local, paginated application PDFs: letter, CV (with independent sidebar flow) and cover.

0.12: modern typography (bundled Inter / Source Serif 4, DejaVu as fallback), section
titles with letter spacing, a timeline for experience/education, level bars for skills
and languages, adaptive header bands and a redesigned cover page."""
import re
import sys
import tempfile
import threading
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'lib'))
from reportlab.platypus import (SimpleDocTemplate, BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                Image, PageBreak, KeepTogether, Table, TableStyle, Flowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from pypdf import PdfReader, PdfWriter
from storage import resolve
from forms import materialize
from photos import cropped
from personal import details, signature_image
from studio import cv_profile, attachment_pdf
from letters import attachment_lines, wants_attachment_list, place_date, return_address, recipient_lines

W, H = 595.28, 841.89
MM = 72 / 25.4
INK = HexColor('#1d2b33')
MUTED = HexColor('#5d6d75')
HAIRLINE = HexColor('#dfe5e8')

# style: look of the template; display: serif for names/headings regardless of the font choice;
# heading: how section titles are drawn.
TEMPLATES = {
    'Seitenleiste': dict(side=True, accent='#167c77', style='soft', heading='line'),
    'Graphit': dict(side=True, accent='#455477', style='soft', heading='line'),
    'Sand': dict(side=True, accent='#8f6b3e', style='soft', heading='line'),
    'Nordlicht': dict(side=True, accent='#174a65', style='dark', heading='bar'),
    'Elegant': dict(side=True, accent='#5b4178', style='stripe', heading='line', display=True),
    'Kontur': dict(side=True, accent='#3d6453', style='outline', heading='bar'),
    'Studio': dict(side=True, accent='#ad4e3f', style='block', heading='bar'),
    'Klar': dict(side=False, accent='#243447', style='plain', heading='line'),
    'Modern': dict(side=False, accent='#187b79', style='line', heading='bar'),
    'Klassisch': dict(side=False, accent='#383838', style='classic', heading='line', display=True),
    'Horizont': dict(side=False, accent='#234d72', style='banner', heading='bar'),
    'Editorial': dict(side=False, accent='#954b37', style='editorial', heading='number', display=True),
}
SIDEBARS = {k: v for k, v in TEMPLATES.items() if v['side']}
LABELS = {'summary': 'Kurzprofil', 'experience': 'Berufserfahrung', 'education': 'Ausbildung & Weiterbildung',
          'projects': 'Projekte & Engagement', 'skills': 'Kenntnisse', 'languages': 'Sprachen', 'hobbies': 'Interessen'}
LOCK = threading.RLock()


# ---------------------------------------------------------------- fonts & colours

FONT_FILES = {
    'Restlos': ('Inter-Regular.ttf', 'DejaVuSans.ttf'),
    'RestlosMedium': ('Inter-Medium.ttf', 'DejaVuSans.ttf'),
    'RestlosSemi': ('Inter-SemiBold.ttf', 'DejaVuSans-Bold.ttf'),
    'RestlosBold': ('Inter-Bold.ttf', 'DejaVuSans-Bold.ttf'),
    'RestlosItalic': ('Inter-Italic.ttf', 'DejaVuSans.ttf'),
    'RestlosSerif': ('SourceSerif4-Regular.ttf', 'DejaVuSerif.ttf'),
    'RestlosSerifMedium': ('SourceSerif4-Semibold.ttf', 'DejaVuSerif.ttf'),
    'RestlosSerifSemi': ('SourceSerif4-Semibold.ttf', 'DejaVuSerif-Bold.ttf'),
    'RestlosSerifBold': ('SourceSerif4-Bold.ttf', 'DejaVuSerif-Bold.ttf'),
    'RestlosSerifItalic': ('SourceSerif4-It.ttf', 'DejaVuSerif.ttf'),
}


def fonts():
    """Register the bundled fonts; fall back to the system DejaVu fonts if a file is missing."""
    from reportlab.lib.fonts import addMapping
    registered = pdfmetrics.getRegisteredFontNames()
    for name, (bundled, fallback) in FONT_FILES.items():
        if name in registered:
            continue
        path = ROOT / 'fonts' / bundled
        if not path.is_file():
            path = Path('/usr/share/fonts/truetype/dejavu') / fallback
        pdfmetrics.registerFont(TTFont(name, str(path)))
    for base in ('Restlos', 'RestlosSerif'):
        addMapping(base, 0, 0, base)
        addMapping(base, 1, 0, base + 'Bold')
        addMapping(base, 0, 1, base + 'Italic')
        addMapping(base, 1, 1, base + 'Bold')


def mix(color, amount, other=white):
    """Blend ``color`` towards ``other`` (amount 0 = color, 1 = other)."""
    return Color(color.red + (other.red - color.red) * amount,
                 color.green + (other.green - color.green) * amount,
                 color.blue + (other.blue - color.blue) * amount)


def settings(a):
    conf = TEMPLATES.get(a['template'], TEMPLATES['Seitenleiste']).copy()
    conf['accent'] = a.get('design', {}).get('accent') or conf['accent']
    return conf


def families(a):
    d = a['design']
    serif = d['font'] == 'Serif' or a['template'] == 'Klassisch'
    body = 'RestlosSerif' if serif else 'Restlos'
    display = 'RestlosSerif' if settings(a).get('display') else body
    return body, display


def styles(a, light_text=False):
    d = a['design']
    body_font, display = families(a)
    color = HexColor(settings(a)['accent'])
    size = d['size']
    spacing = d.get('spacing', 100) / 100
    text = white if light_text else INK
    body = ParagraphStyle('body', fontName=body_font, fontSize=size, leading=size * 1.5 * spacing,
                          spaceAfter=8 * spacing, textColor=INK, splitLongWords=True)
    return {
        'body': body,
        'muted': ParagraphStyle('muted', parent=body, textColor=MUTED, spaceAfter=3 * spacing),
        'lead': ParagraphStyle('lead', parent=body, fontSize=size + 0.8, leading=(size + 0.8) * 1.55 * spacing),
        'small': ParagraphStyle('small', parent=body, fontSize=8.5, leading=12.5, spaceAfter=10, textColor=MUTED),
        'side': ParagraphStyle('side', parent=body, fontSize=8.8, leading=13, spaceAfter=7,
                               textColor=text if light_text else INK),
        'sidehead': ParagraphStyle('sidehead', parent=body, fontName=body_font + 'Semi', fontSize=9, leading=14,
                                   spaceBefore=15, spaceAfter=8, textColor=white if light_text else color,
                                   keepWithNext=True),
        'name': ParagraphStyle('name', parent=body, fontName=display + 'Bold', fontSize=29, leading=33,
                               textColor=INK, spaceAfter=4),
        'role': ParagraphStyle('role', parent=body, fontName=body_font + 'Medium', fontSize=12.5, leading=17,
                               textColor=color, spaceAfter=10),
        'section': ParagraphStyle('section', parent=body, fontName=body_font + 'Semi', fontSize=12, leading=18,
                                  textColor=color, spaceBefore=15 * spacing, spaceAfter=9 * spacing,
                                  keepWithNext=True),
        'station': ParagraphStyle('station', parent=body, fontName=body_font + 'Semi', spaceAfter=3,
                                  keepWithNext=True),
        'org': ParagraphStyle('org', parent=body, fontName=body_font + 'Medium', fontSize=size - 0.6,
                              leading=(size - 0.6) * 1.45, textColor=color, spaceAfter=4 * spacing),
        'date': ParagraphStyle('date', parent=body, fontName=body_font + 'Medium', fontSize=8.3, leading=11.5,
                               textColor=MUTED, spaceAfter=0),
        'bullet': ParagraphStyle('bullet', parent=body, leftIndent=10, bulletIndent=0, spaceAfter=2.5 * spacing),
    }


def fit_name(text, style, width, minimum=17):
    """Shrink a large name so that its longest word fits the available width."""
    words = (text or '').split() or ['']
    size = style.fontSize
    while size > minimum and max(pdfmetrics.stringWidth(w, style.fontName, size) for w in words) > width:
        size -= 1
    if size != style.fontSize:
        style.leading = style.leading * size / style.fontSize
        style.fontSize = size
    return style


def para(text, style):
    return Paragraph(escape(str(text)).replace('\n', '<br/>'), style)


def blocks(story, text, style):
    for block in text.split('\n\n'):
        if block.strip():
            story.append(para(block, style))


# ---------------------------------------------------------------- flowables

def tracked_width(text, font, size, tracking):
    return pdfmetrics.stringWidth(text, font, size) + tracking * max(len(text) - 1, 0)


class SectionTitle(Flowable):
    """Upper-case section title with letter spacing: 'line' (hairline to the right),
    'bar' (accent bar in front), 'number' (01, 02 … in front) or 'plain'."""

    def __init__(self, text, font, color, mode='line', size=8.6, tracking=1.4, line=HAIRLINE,
                 space_before=16, space_after=9, number=None, align='left'):
        super().__init__()
        self.text, self.font, self.color, self.mode = text.upper(), font, color, mode
        self.size, self.tracking, self.line, self.number, self.align = size, tracking, line, number, align
        self.space_before, self.space_after = space_before, space_after
        self.keepWithNext = 1

    def wrap(self, aw, ah):
        self.width = aw
        return aw, self.size + 4

    def getSpaceBefore(self):
        return self.space_before

    def getSpaceAfter(self):
        return self.space_after

    def _text(self, c, x, y, text, font, color):
        t = c.beginText(x, y)
        t.setFont(font, self.size)
        t.setCharSpace(self.tracking)
        t.setFillColor(color)
        t.textOut(text)
        c.drawText(t)

    def draw(self):
        c = self.canv
        y = 2
        x = 0
        tw = tracked_width(self.text, self.font, self.size, self.tracking)
        if self.align == 'center':
            x = (self.width - tw) / 2
        if self.mode == 'bar':
            c.setFillColor(self.color)
            c.roundRect(0, y - 1.5, 3, self.size + 3, 1.5, fill=1, stroke=0)
            x = 10
        elif self.mode == 'number' and self.number is not None:
            label = '%02d' % self.number
            self._text(c, 0, y, label, self.font, self.color)
            x = tracked_width(label, self.font, self.size, self.tracking) + 10
        self._text(c, x, y, self.text, self.font, INK if self.mode in ('bar', 'number') else self.color)
        if self.mode in ('line', 'number'):
            c.setStrokeColor(self.line)
            c.setLineWidth(0.7)
            mid = y + self.size * 0.35
            if self.align == 'center':
                c.line(0, mid, x - 10, mid)
            c.line(x + tw + 10, mid, self.width, mid)


LEVELS = [
    (r'muttersprach|native|mother', 1.0), (r'\bc2\b|exzellent|experte|expert', 1.0),
    (r'verhandlungssicher|fließend|fliessend|fluent', .9), (r'\bc1\b|sehr gut|sehr gute|very good', .85),
    (r'fortgeschritten|advanced|\bb2\b', .7), (r'\bgut\b|gute|good', .65), (r'\bb1\b', .55),
    (r'\ba2\b|grundkenntnis|grundlagen|basis|basic', .4), (r'\ba1\b|anfänger|beginner', .25),
]


def level_score(level):
    """Map 'B2', 'sehr gut', '4/5', '80 %' … to 0–1; None if unknown."""
    text = level.lower()
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*/\s*(\d+)', text)
    if m and float(m.group(2).replace(',', '.')):
        return max(0, min(1, float(m.group(1).replace(',', '.')) / float(m.group(2).replace(',', '.'))))
    m = re.search(r'(\d{1,3})\s*%', text)
    if m:
        return max(0, min(1, int(m.group(1)) / 100))
    for pattern, score in LEVELS:
        if re.search(pattern, text):
            return score
    return None


def split_level(line):
    for sep in (' – ', ' - ', ': ', ' — '):
        if sep in line:
            name, level = line.split(sep, 1)
            return name.strip(), level.strip()
    return line.strip(), ''


class SkillBar(Flowable):
    """Skill or language with an optional level bar."""

    def __init__(self, name, level, font, color, text=INK, muted=MUTED, track=HAIRLINE, size=8.8):
        super().__init__()
        self.name, self.level, self.score = name, level, level_score(level) if level else None
        self.font, self.color, self.text, self.muted, self.track, self.size = font, color, text, muted, track, size

    def wrap(self, aw, ah):
        self.width = aw
        self.short = bool(self.level) and pdfmetrics.stringWidth(self.level, self.font, 7.6) <= aw * 0.45
        name_width = aw - (pdfmetrics.stringWidth(self.level, self.font, 7.6) + 6 if self.short else 0)
        self.name_lines = simpleSplit(self.name, self.font + 'Medium', self.size, name_width) or ['']
        self.level_lines = [] if self.short or not self.level else simpleSplit(self.level, self.font, 7.6, aw)
        self.height = len(self.name_lines) * self.size * 1.3 + len(self.level_lines) * 10 + (7 if self.score is not None else 0) + 6
        return aw, self.height

    def draw(self):
        c = self.canv
        y = self.height - self.size
        c.setFont(self.font + 'Medium', self.size)
        c.setFillColor(self.text)
        for i, line in enumerate(self.name_lines):
            c.drawString(0, y - i * self.size * 1.3, line)
        if self.short:
            c.setFont(self.font, 7.6)
            c.setFillColor(self.muted)
            c.drawRightString(self.width, y, self.level)
        y -= (len(self.name_lines) - 1) * self.size * 1.3
        if self.score is not None:
            y -= 7
            c.setFillColor(self.track)
            c.roundRect(0, y, self.width, 3, 1.5, fill=1, stroke=0)
            c.setFillColor(self.color)
            c.roundRect(0, y, max(3, self.width * self.score), 3, 1.5, fill=1, stroke=0)
        c.setFont(self.font, 7.6)
        c.setFillColor(self.muted)
        for line in self.level_lines:
            y -= 10
            c.drawString(0, y, line)


class HeaderBlock(Flowable):
    """Coloured band behind header content; grows with the content and can bleed
    to the page edges (``bleed`` = left, right, top in points)."""

    def __init__(self, items, background, pad=(22, 20, 20, 20), bleed=(0, 0, 0), photo=None, radius=0):
        super().__init__()
        self.items, self.background, self.pad, self.bleed, self.photo, self.radius = items, background, pad, bleed, photo, radius

    def wrap(self, aw, ah):
        top, right, bottom, left = self.pad
        self.width = aw
        photo_w = self.photo[1] + 18 if self.photo else 0
        inner = aw - left - right - photo_w
        self.sizes = [item.wrap(inner, ah) for item in self.items]
        content = sum(h for _, h in self.sizes) + sum(item.getSpaceAfter() for item in self.items[:-1])
        photo_h = self.photo[2] if self.photo else 0
        self.height = top + max(content, photo_h) + bottom
        return aw, self.height

    def draw(self):
        c = self.canv
        top, right, bottom, left = self.pad
        bl, br, bt = self.bleed
        c.setFillColor(self.background)
        if self.radius:
            c.roundRect(-bl, 0, self.width + bl + br, self.height + bt, self.radius, fill=1, stroke=0)
        else:
            c.rect(-bl, 0, self.width + bl + br, self.height + bt, fill=1, stroke=0)
        y = self.height - top
        for item, (w, h) in zip(self.items, self.sizes):
            y -= h
            item.drawOn(c, left, y)
            y -= item.getSpaceAfter()
        if self.photo:
            stream, w, h = self.photo
            stream.seek(0)
            c.drawImage(ImageReader(stream), self.width - right - w, (self.height - h) / 2 + (bottom - top) / 2,
                        width=w, height=h, mask='auto')


class Rule(Flowable):
    def __init__(self, width, color, thickness=2.5, space_after=12):
        super().__init__()
        self.w, self.color, self.thickness, self.space_after = width, color, thickness, space_after

    def wrap(self, aw, ah):
        return aw, self.thickness

    def getSpaceAfter(self):
        return self.space_after

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.w, self.thickness, self.thickness / 2, fill=1, stroke=0)


# ---------------------------------------------------------------- building blocks

def photo_data(p, a, width):
    if not p.get('photo') or not a['design']['photo'] or not resolve(p['photo']).is_file():
        return None
    width *= a['design'].get('photoScale', 100) / 100
    shape = p['photoSettings']['shape']
    return cropped(p, 0 if shape == 'round' else 0.06), width, width * (1.25 if shape == 'portrait' else 1)


def photo(p, a, width=130, align='LEFT'):
    data = photo_data(p, a, width)
    if not data:
        return []
    image = Image(data[0], width=data[1], height=data[2])
    image.hAlign = align
    return [image, Spacer(1, 14)]


DATE_RE = re.compile(r'(\d{4}|heute|seit|bis|aktuell|present)', re.I)


def station(block, st, width, conf, date_col=74):
    """One experience/education entry as a small timeline table (splits between rows)."""
    lines = [x for x in block.strip('\n').split('\n')]
    head = lines[0].strip()
    parts = [x.strip() for x in head.split(' · ') if x.strip()]
    date = ''
    if len(parts) > 1 and DATE_RE.search(parts[0]) and len(parts[0]) <= 32:
        date, parts = parts[0], parts[1:]
    title = parts[0] if parts else head
    org = ' · '.join(parts[1:])
    accent = HexColor(conf['accent'])
    rows = [[para(date.replace(' – ', ' –\n') if len(date) > 14 else date, st['date']), para(title, st['station'])]]
    if org:
        rows.append(['', para(org, st['org'])])
    for line in lines[1:]:
        text = line.strip()
        if not text:
            continue
        bullet = re.match(r'^[-•*–]\s+(.*)$', text)
        if bullet:
            rows.append(['', Paragraph(escape(bullet.group(1)), st['bullet'], bulletText='•')])
        else:
            rows.append(['', para(text, st['muted'])])
    if not date:
        date_col = 0
    style = [('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
             ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
             ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]
    if date_col:
        # The (often two-line) date spans the first rows so it does not stretch the title row.
        span = min(len(rows), 3) - 1
        for i in range(1, span + 1):
            rows[i][0] = ''
        if span:
            style.append(('SPAN', (0, 0), (0, span)))
        style += [('LEFTPADDING', (1, 0), (1, -1), 12),
                  ('LINEBEFORE', (1, 0), (1, -1), 0.9, mix(accent, 0.7)),
                  ('TOPPADDING', (0, 0), (0, 0), 1.6)]
    # Head (date, title, company) stays with the section title; the details may flow onto the next page.
    head_rows = (min(len(rows), 3) - 1 if date_col else 1) + 1
    head = Table(rows[:head_rows], colWidths=[date_col, width - date_col], hAlign='LEFT')
    head.setStyle(TableStyle(style))
    out = [head]
    if rows[head_rows:]:
        rest_style = [s for s in style if s[0] != 'SPAN' and not (s[1] == (0, 0) and s[2] == (0, 0))]
        rest = Table(rows[head_rows:], colWidths=[date_col, width - date_col], hAlign='LEFT', splitByRow=1)
        rest.setStyle(TableStyle(rest_style))
        out.append(rest)
    return out + [Spacer(1, 11 * st['body'].leading / (st['body'].fontSize * 1.5))]


def skill_flowables(text, st, conf, light=False, columns=1, width=None):
    accent = HexColor(conf['accent'])
    font = st['body'].fontName
    rows = [split_level(x) for x in text.splitlines() if x.strip()]
    if light:
        bars = [SkillBar(n, l, font, white, text=white, muted=mix(accent, 0.55), track=mix(accent, 0.35, white)) for n, l in rows]
    else:
        bars = [SkillBar(n, l, font, accent, track=mix(accent, 0.86)) for n, l in rows]
    if columns == 1 or len(bars) < 2:
        return bars
    gap = 22
    col = (width - gap) / 2
    grid = [bars[i:i + 2] + ([''] if len(bars[i:i + 2]) == 1 else []) for i in range(0, len(bars), 2)]
    table = Table(grid, colWidths=[col, col], hAlign='LEFT', splitByRow=1)
    table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                               ('RIGHTPADDING', (0, 0), (0, -1), gap), ('RIGHTPADDING', (1, 0), (1, -1), 0),
                               ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    return [table]


def section_title(text, st, conf, number=None, light=False, align='left'):
    accent = HexColor(conf['accent'])
    spacing = st['body'].leading / (st['body'].fontSize * 1.5)
    return SectionTitle(text, st['body'].fontName + 'Semi', white if light else accent, conf['heading'],
                        line=mix(accent, 0.45) if light else HAIRLINE, number=number,
                        space_before=17 * spacing, space_after=10 * spacing, align=align)


def sections(story, p, a, st, keys, conf=None, width=470, skill_columns=2):
    conf = conf or settings(a)
    align = 'center' if conf.get('style') == 'classic' else 'left'
    number = 0
    for key in keys:
        if not p.get(key, '').strip():
            continue
        if key in a['design'].get('breakBefore', []):
            story.append(PageBreak())
        number += 1
        story.append(section_title(LABELS[key], st, conf, number, align=align))
        if key in ('experience', 'education'):
            for block in p[key].split('\n\n'):
                if block.strip('\n').split('\n')[0].strip():
                    story.extend(station(block, st, width, conf))
        elif key in ('skills', 'languages'):
            story.extend(skill_flowables(p[key], st, conf, columns=skill_columns, width=width))
        elif key == 'summary':
            blocks(story, p[key], st['lead'])
        else:
            blocks(story, p[key], st['body'])


def contact_rows(p):
    rows = [('E-Mail', p['email']), ('Telefon', p['phone']), ('Adresse', p['address'])]
    for line in details(p).splitlines():
        label, _, value = line.partition(': ')
        rows.append((label, value))
    return [(k, v) for k, v in rows if v.strip()]


def labelled(rows, st, light=False, accent=None):
    """Small upper-case label above each value (sidebar contact and personal details)."""
    out = []
    label = ParagraphStyle('label', parent=st['side'], fontName=st['body'].fontName + 'Semi', fontSize=6.8,
                           leading=9, spaceAfter=1.5, textColor=mix(accent, 0.45) if light else MUTED)
    for key, value in rows:
        out.append(Paragraph('<font>%s</font>' % escape(key.upper()), label))
        out.append(para(value, st['side']))
    return out


def page_footer(c, doc, p, color, x0=48, x1=W - 48, label='Lebenslauf', light=False):
    c.saveState()
    c.setFont('Restlos', 7.3)
    c.setFillColor(MUTED)
    name = (p.get('name') or '').strip()
    if name and label:
        c.drawString(x0, 24, name + '  ·  ' + label)
    c.drawRightString(x1, 24, 'Seite %d' % doc.page)
    c.restoreState()


# ---------------------------------------------------------------- letter

def letter_ending(p, a, st, documents):
    """Closing, optional signature image, name and – since 0.11 – the list of enclosures."""
    ending = [para('Mit freundlichen Grüßen', st['body']), Spacer(1, 8)]
    if p.get('signature') and a['design'].get('signature', True) and resolve(p['signature']).is_file():
        stream, w, h = signature_image(p, a)
        im = Image(stream, width=w, height=h)
        im.hAlign = 'LEFT'
        ending.extend([im, Spacer(1, 5)])
    ending.append(para(p['name'], st['body']))
    story = [KeepTogether(ending)]
    if wants_attachment_list(a):
        lines = attachment_lines(documents, a)
        if lines:
            story.append(KeepTogether([Spacer(1, 16), para('Anlagen', st['station']), para('\n'.join(lines), st['small'])]))
    return story


def subject(a):
    return 'Bewerbung als ' + a['position'].strip() if a['position'].strip() else 'Bewerbung'


def letter_head(p, a, st, conf, width):
    """Name, profession and contact details at the top of the letter."""
    accent = HexColor(conf['accent'])
    style = conf['style']
    contact = [x for x in [p['email'], p['phone']] + [l.strip() for l in p['address'].splitlines()] if x.strip()]
    right = ParagraphStyle('contact', parent=st['small'], alignment=TA_RIGHT, leading=12, spaceAfter=0)
    name_style = ParagraphStyle('lname', parent=st['name'], fontSize=24, leading=28, spaceAfter=2)
    role_style = ParagraphStyle('lrole', parent=st['role'], fontSize=11, leading=15, spaceAfter=0)
    if style == 'banner':
        name_style.textColor = white
        role_style.textColor = mix(accent, 0.7)
        right.textColor = mix(accent, 0.75)
    left = [para(p['name'] or 'Dein Name', fit_name(p['name'], name_style, width * 0.58))]
    if p.get('title', '').strip():
        left.append(para(p['title'], role_style))
    table = Table([[left, para('\n'.join(contact), right)]], colWidths=[width * 0.58, width * 0.42], hAlign='LEFT')
    table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'BOTTOM'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                               ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    if style == 'banner':
        return [HeaderBlock([table], accent, pad=(30, 0, 22, 0), bleed=(60, 60, 52)), Spacer(1, 26)]
    rule_color = HAIRLINE if style in ('plain', 'classic') else accent
    return [table, Spacer(1, 12), Rule(width if style in ('plain', 'classic') else 46, rule_color,
                                       0.8 if style in ('plain', 'classic') else 3, 26)]


def letter_background(conf, p):
    accent = HexColor(conf['accent'])
    style = conf['style']

    def draw(c, d):
        c.saveState()
        if style in ('soft', 'dark', 'stripe', 'outline', 'block'):
            c.setFillColor(accent)
            c.rect(0, 0, 8 if style != 'soft' else 6, H, fill=1, stroke=0)
        elif style == 'editorial':
            c.setFillColor(accent)
            c.rect(30, 48, 2.5, H - 96, fill=1, stroke=0)
        elif style == 'line':
            c.setFillColor(accent)
            c.rect(0, H - 8, W, 8, fill=1, stroke=0)
        c.restoreState()
        page_footer(c, d, p, accent, 54, W - 54, label='Anschreiben')
    return draw


def letter_pdf(p, a, path, documents=()):
    if a['design'].get('letterLayout') == 'din5008':
        return letter_din5008(p, a, path, documents)
    st = styles(a)
    conf = settings(a)
    width = W - 108 - 12
    story = letter_head(p, a, st, conf, width)
    recipient = ParagraphStyle('recipient', parent=st['body'], spaceAfter=0)
    dated = ParagraphStyle('dated', parent=st['body'], alignment=TA_RIGHT, textColor=MUTED, spaceAfter=0)
    story.append(para(a['recipient'] or a['company'], recipient))
    story += [Spacer(1, 18), para(', '.join(filter(None, [a['location'], a['date']])), dated), Spacer(1, 22)]
    story.append(para(subject(a), ParagraphStyle('subject', parent=st['station'], fontSize=st['body'].fontSize + 2.5,
                                                 leading=(st['body'].fontSize + 2.5) * 1.35, spaceAfter=14)))
    blocks(story, a['salutation'], st['body'])
    blocks(story, a['letter'], st['body'])
    story += letter_ending(p, a, st, documents)
    background = letter_background(conf, p)
    SimpleDocTemplate(str(path), pagesize=(W, H), leftMargin=54, rightMargin=54, topMargin=46,
                      bottomMargin=52).build(story, onFirstPage=background, onLaterPages=background)


def letter_din5008(p, a, path, documents=()):
    """Letter following DIN 5008 form B: address field 45 mm from the top and 20 mm from the
    left edge (fits DL/C6 window envelopes), fold marks at 105/210 mm, punch mark at 148.5 mm."""
    st = styles(a)
    conf = settings(a)
    left = 25 * MM
    right = 20 * MM
    font = st['body'].fontName
    _, display = families(a)
    accent = HexColor(conf['accent'])
    dated = ParagraphStyle('dated', parent=st['body'], alignment=TA_RIGHT, spaceAfter=0)
    # Body starts below the address field and the information line (≈ 98 mm from the top).
    story = [Spacer(1, (98.4 - 20) * MM - 6), para(', '.join(filter(None, [a['location'], a['date']])), dated),
             Spacer(1, 16), para(subject(a), st['station']), Spacer(1, 10)]
    blocks(story, a['salutation'], st['body'])
    blocks(story, a['letter'], st['body'])
    story += letter_ending(p, a, st, documents)
    contact = [x for x in [' · '.join(filter(None, [p['phone'], p['email']]))] if x]

    def first(c, d):
        c.saveState()
        c.setFillColor(INK if conf['style'] in ('plain', 'classic') else accent)
        c.setFont(display + 'Bold', 19)
        c.drawString(left, H - 20 * MM, p['name'] or 'Dein Name')
        c.setFillColor(MUTED)
        c.setFont(font, 8.5)
        y = H - 26 * MM
        for line in [' · '.join(x.strip() for x in p['address'].splitlines() if x.strip())] + contact:
            if line:
                c.drawString(left, y, line)
                y -= 11
        c.setStrokeColor(HAIRLINE if conf['style'] in ('plain', 'classic') else accent)
        c.setLineWidth(0.8 if conf['style'] in ('plain', 'classic') else 1.5)
        c.line(left, H - 38 * MM, W - right, H - 38 * MM)
        # Address field (form B): 17.7 mm Zusatz-/Vermerkzone + 27.3 mm Anschriftzone, 85 mm wide.
        sender = return_address(p)
        if sender:
            c.setFont(font, 6.5)
            c.setFillColor(MUTED)
            lines = simpleSplit(sender, font, 6.5, 80 * MM)[:2]
            for i, line in enumerate(lines):
                c.drawString(left, H - (45 + 17.7) * MM + 3 + (len(lines) - 1 - i) * 8, line)
        c.setFillColor(INK)
        c.setFont(font, 10)
        y = H - (45 + 17.7) * MM - 12
        for line in recipient_lines(a)[:6]:
            for part in simpleSplit(line, font, 10, 80 * MM)[:1]:
                c.drawString(left, y, part)
            y -= 12.2
        # Fold and punch marks on the left edge.
        c.setStrokeColor(HexColor('#9aa7ad'))
        c.setLineWidth(0.5)
        for mm, length in ((105, 5), (210, 5), (148.5, 8)):
            c.line(3.5 * MM, H - mm * MM, (3.5 + length) * MM, H - mm * MM)
        c.restoreState()
        page_footer(c, d, p, accent, left, W - right, label='Anschreiben')

    def later(c, d):
        page_footer(c, d, p, accent, left, W - right, label='Anschreiben')

    SimpleDocTemplate(str(path), pagesize=(W, H), leftMargin=left - 6, rightMargin=right - 6, topMargin=20 * MM - 6,
                      bottomMargin=48).build(story, onFirstPage=first, onLaterPages=later)


# ---------------------------------------------------------------- CV

def cv_closing(p, a, st):
    """Optional place, date, signature and name at the end of the CV (0.11)."""
    if not a['design'].get('cvSignature'):
        return []
    out = [Spacer(1, 22)]
    line = place_date(p, a)
    if line:
        out.append(para(line, st['body']))
    if p.get('signature') and resolve(p['signature']).is_file():
        stream, w, h = signature_image(p, a)
        im = Image(stream, width=w, height=h)
        im.hAlign = 'LEFT'
        out.extend([Spacer(1, 4), im])
    out.append(para(p['name'], st['body']))
    return [KeepTogether(out)]


def cv_single(p, a, path, conf, st):
    """One-column templates: Klar, Modern, Klassisch, Horizont, Editorial."""
    accent = HexColor(conf['accent'])
    style = conf['style']
    margin = 50
    width = W - 2 * margin - 12
    centered = style == 'classic'
    eyebrow = SectionTitle('Lebenslauf', st['body'].fontName + 'Semi', accent, 'plain', size=7.8, tracking=1.8,
                           space_before=0, space_after=8, align='center' if centered else 'left')
    name = ParagraphStyle('n', parent=st['name'], alignment=TA_CENTER if centered else 0)
    role = ParagraphStyle('r', parent=st['role'], alignment=TA_CENTER if centered else 0)
    contact_style = ParagraphStyle('c', parent=st['small'], alignment=TA_CENTER if centered else 0, spaceAfter=0,
                                   leading=13)
    if style == 'banner':
        name.textColor = white
        role.textColor = mix(accent, 0.72)
        contact_style.textColor = mix(accent, 0.78)
        eyebrow.color = mix(accent, 0.6)
    contact = '   ·   '.join(x for x in [p['email'], p['phone'], ', '.join(l.strip() for l in p['address'].splitlines() if l.strip())] if x.strip())
    personal = '   ·   '.join(details(p).splitlines())
    text_width = width - ((photo_data(p, a, 92) or (0, 0))[1] + 34 if style != 'classic' else 0)
    head = [eyebrow, para(p['name'] or 'Dein Name', fit_name(p['name'], name, text_width))]
    if p['title']:
        head.append(para(p['title'], role))
    head.append(para(contact, contact_style))
    if personal:
        head.append(para(personal, contact_style))
    pic = photo_data(p, a, 92)
    story = []
    if style == 'banner':
        story.append(HeaderBlock(head, accent, pad=(34, 0, 28, 0), bleed=(margin + 6, margin + 6, 46), photo=pic))
        story.append(Spacer(1, 6))
    else:
        if pic and not centered:
            image = Image(pic[0], width=pic[1], height=pic[2])
            table = Table([[head, image]], colWidths=[width - pic[1] - 16, pic[1] + 16], hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                                       ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                       ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
            story.append(table)
        else:
            if pic:
                story += photo(p, a, 92, 'CENTER')
            story += head
        story.append(Spacer(1, 6))
        if style in ('plain', 'classic'):
            story.append(Rule(width, HAIRLINE, 0.8, 4))
    sections(story, p, a, st, a['design']['order'], conf, width)
    story += cv_closing(p, a, st)

    def bg(c, d):
        c.saveState()
        if style == 'editorial':
            c.setFillColor(accent)
            c.rect(26, 48, 3, H - 96, fill=1, stroke=0)
        elif style == 'line':
            c.setFillColor(accent)
            c.rect(0, H - 8, W, 8, fill=1, stroke=0)
        elif style == 'banner' and d.page > 1:
            c.setFillColor(accent)
            c.rect(0, H - 8, W, 8, fill=1, stroke=0)
        c.restoreState()
        page_footer(c, d, p, accent, margin, W - margin)

    top = 0 if style == 'banner' else 44
    doc = BaseDocTemplate(str(path), pagesize=(W, H))
    first = Frame(margin, 50, W - 2 * margin, H - 50 - top, leftPadding=6, rightPadding=6, topPadding=0 if style == 'banner' else 6, bottomPadding=6)
    later = Frame(margin, 50, W - 2 * margin, H - 50 - 44, leftPadding=6, rightPadding=6, topPadding=6, bottomPadding=6)
    doc.addPageTemplates([PageTemplate(id='first', frames=[first], onPage=bg, autoNextPageTemplate='later'),
                          PageTemplate(id='later', frames=[later], onPage=bg)])
    doc.build(story)


def cv_pdf(p, a, path):
    conf = settings(a)
    if not conf['side']:
        return cv_single(p, a, path, conf, styles(a))
    style = conf['style']
    dark = style == 'dark'
    st = styles(a, dark)
    accent = HexColor(conf['accent'])
    light = mix(accent, 0.92)
    panel = 196
    side_x, side_w = 24, panel - 36
    main_x, main_w = panel + 18, W - panel - 18 - 30
    inner_main = main_w - 12

    # Sidebar: photo, contact/personal details, skills and languages with level bars.
    left = photo(p, a, 130, 'CENTER')
    rows = contact_rows(p)
    head = lambda text: section_title(text, st, dict(conf, heading='plain'), light=dark)
    if rows:
        left += [head('Kontakt')] + labelled(rows, st, dark, accent)
    for key in ('skills', 'languages'):
        if p[key].strip():
            left.append(head(LABELS[key]))
            left += skill_flowables(p[key], st, conf, light=dark)
    if not left:
        left = [head('Kontakt')]

    # Main column: header, then the remaining sections.
    eyebrow = SectionTitle('Lebenslauf', st['body'].fontName + 'Semi', accent, 'plain', size=7.8, tracking=1.8,
                           space_before=0, space_after=8)
    name = ParagraphStyle('n', parent=st['name'])
    role = ParagraphStyle('r', parent=st['role'])
    if style == 'block':
        name.textColor = white
        role.textColor = mix(accent, 0.72)
        eyebrow.color = mix(accent, 0.6)
    header = [eyebrow, para(p['name'] or 'Dein Name', fit_name(p['name'], name, inner_main - (44 if style == 'block' else 0)))]
    if p['title']:
        header.append(para(p['title'], role))
    if style == 'block':
        main = [HeaderBlock(header, accent, pad=(30, 22, 24, 22), bleed=(main_x + 6 - panel, W - main_x - main_w + 6, 50)), Spacer(1, 4)]
    else:
        main = header + [Rule(42, accent, 3, 6)]
    main_st = styles(a) if dark else st
    sections(main, p, a, main_st, [k for k in a['design']['order'] if k not in ('skills', 'languages')], conf, inner_main)
    main += cv_closing(p, a, main_st)

    def bg(c, d):
        c.saveState()
        if dark:
            c.setFillColor(accent)
            c.rect(0, 0, panel, H, fill=1, stroke=0)
        elif style == 'outline':
            c.setStrokeColor(mix(accent, 0.55))
            c.setLineWidth(1)
            c.roundRect(14, 40, panel - 22, H - 80, 12, fill=0, stroke=1)
        else:
            c.setFillColor(light)
            c.rect(0, 0, panel, H, fill=1, stroke=0)
            if style == 'stripe':
                c.setFillColor(accent)
                c.rect(0, 0, 7, H, fill=1, stroke=0)
            elif style == 'soft':
                c.setFillColor(accent)
                c.rect(0, H - 7, panel, 7, fill=1, stroke=0)
        c.restoreState()
        page_footer(c, d, p, accent, main_x + 6, main_x + main_w - 6)

    top = 46 if style != 'block' else 0
    with tempfile.TemporaryDirectory() as td:
        for name_, story, x, width, fn, top_ in [('left', left, side_x, side_w, bg, 46),
                                                  ('right', main, main_x, main_w, lambda c, d: None, top)]:
            doc = BaseDocTemplate(str(Path(td) / (name_ + '.pdf')), pagesize=(W, H))
            first = Frame(x, 50, width, H - 50 - top_, leftPadding=6, rightPadding=6,
                          topPadding=6 if top_ else 0, bottomPadding=6)
            later = Frame(x, 50, width, H - 50 - 46, leftPadding=6, rightPadding=6, topPadding=6, bottomPadding=6)
            doc.addPageTemplates([PageTemplate(id='first', frames=[first], onPage=fn, autoNextPageTemplate='later'),
                                  PageTemplate(id='later', frames=[later], onPage=fn)])
            doc.build(story)
        l = PdfReader(Path(td) / 'left.pdf')
        r = PdfReader(Path(td) / 'right.pdf')
        w = PdfWriter()
        for i in range(max(len(l.pages), len(r.pages))):
            if i < len(l.pages):
                page = l.pages[i]
            else:
                buf = BytesIO()
                c = pdfcanvas.Canvas(buf, pagesize=(W, H))
                bg(c, type('Page', (), {'page': i + 1})())
                c.save()
                buf.seek(0)
                page = PdfReader(buf).pages[0]
            if i < len(r.pages):
                page.merge_page(r.pages[i])
            w.add_page(page)
        w.write(str(path))
        w.close()


# ---------------------------------------------------------------- cover

def cover_pdf(p, a, path):
    st = styles(a)
    conf = settings(a)
    accent = HexColor(conf['accent'])
    _, display = families(a)
    margin = 56
    width = W - 2 * margin - 12
    eyebrow = SectionTitle('Bewerbung als', st['body'].fontName + 'Semi', mix(accent, 0.6), 'plain', size=8.5,
                           tracking=2, space_before=0, space_after=12)
    position = ParagraphStyle('pos', parent=st['name'], fontName=display + 'Bold', fontSize=34, leading=39,
                              textColor=white, spaceAfter=10)
    company = ParagraphStyle('comp', parent=st['role'], fontSize=14, leading=19, textColor=mix(accent, 0.75))
    band = [eyebrow, para(a['position'] or 'Deine Position', position)]
    if a['company'].strip():
        band.append(para(a['company'], company))
    story = [HeaderBlock(band, accent, pad=(150, 0, 70, 0), bleed=(margin + 6, margin + 6, 40)), Spacer(1, 34)]
    pic = photo_data(p, a, 132)
    name = ParagraphStyle('cname', parent=st['name'], fontSize=26, leading=30)
    info = []
    info.append(para(p['name'] or 'Dein Name', fit_name(p['name'], name, width - 200)))
    if p['title']:
        info.append(para(p['title'], st['role']))
    info.append(Spacer(1, 6))
    info += labelled([(k, v) for k, v in contact_rows(p) if k in ('E-Mail', 'Telefon', 'Adresse')], st)
    if pic:
        image = Image(pic[0], width=pic[1], height=pic[2])
        table = Table([[image, info]], colWidths=[pic[1] + 28, width - pic[1] - 28], hAlign='LEFT')
        table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                   ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 0),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
        story.append(table)
    else:
        story += info
    contents = a.get('_contents') or ['Anschreiben', 'Lebenslauf']
    story += [Spacer(1, 30), section_title('Inhalt', st, dict(conf, heading='line'))]
    story.append(para('\n'.join(contents), st['body']))

    def bg(c, d):
        c.saveState()
        c.setFillColor(mix(accent, 0.94))
        c.rect(0, 0, W, 34, fill=1, stroke=0)
        c.restoreState()

    doc = BaseDocTemplate(str(path), pagesize=(W, H))
    doc.addPageTemplates([PageTemplate(id='cover', frames=[Frame(margin, 50, W - 2 * margin, H - 50, leftPadding=6,
                                                                 rightPadding=6, topPadding=0, bottomPadding=6)], onPage=bg)])
    doc.build(story)


def cover_contents(documents, a):
    lines = ['Anschreiben', 'Lebenslauf']
    if a.get('attachments'):
        lines += attachment_lines(documents, dict(a, form=dict(a.get('form', {}), attachmentText='')))[1:]
    return lines


# ---------------------------------------------------------------- assembly

def make_pdf(s, a, path, kind='all', attachments=True):
    if kind not in ('all', 'letter', 'cv', 'cover'):
        raise ValueError('Unbekanntes Dokumentformat.')
    with LOCK:
        p = s['profile']
        materialize(p, a)
        fonts()
        owner = next((x for x in s.get('profiles', []) if x.get('id') == s.get('selectedProfile')), None)
        documents = owner['documents'] if owner else []
        with tempfile.TemporaryDirectory() as td:
            files = []
            # Cover is optional; it precedes the letter, CV and attachments.
            for key, include in [('cover', kind == 'cover' or kind == 'all' and a['design']['cover']),
                                 ('letter', kind in ('all', 'letter')), ('cv', kind in ('all', 'cv'))]:
                if not include:
                    continue
                file = Path(td) / (key + '.pdf')
                if key == 'letter':
                    letter_pdf(p, a, file, documents)
                elif key == 'cv':
                    cv_pdf(cv_profile(p, a), a, file)
                else:
                    cover_pdf(p, dict(a, _contents=cover_contents(documents, a)), file)
                files.append(file)
            if kind == 'all' and attachments:
                for i, rel in enumerate(a['attachments']):
                    file = Path(td) / ('attachment-' + str(i) + '.pdf')
                    attachment_pdf(a, rel, file)
                    files.append(file)
            writer = PdfWriter()
            for f in files:
                writer.append(str(f))
            writer.add_metadata({'/Title': ('Lebenslauf' if kind == 'cv' else 'Bewerbung') + ' – ' + p['name'],
                                 '/Author': p['name']})
            writer.write(str(path))
            writer.close()
