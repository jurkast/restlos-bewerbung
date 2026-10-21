"""Suggestions from a pasted job advertisement (0.12). Local, rule based, never applied
without confirmation: company, position, contact person, address, e-mail and deadline."""
import re
from datetime import date

LEGAL = r'(?:GmbH(?:\s*&\s*Co\.?\s*KG)?|gGmbH|AG|SE|KGaA|KG|OHG|GbR|UG(?:\s*\(haftungsbeschränkt\))?|e\.\s?V\.|eG|mbH|Ltd\.?|Inc\.?)'
GENDER = r'\((?:m|w|d|f|x|div|i)(?:\s*[/|,]\s*(?:m|w|d|f|x|div|i))+\)|\(all genders?\)|\(gn\)|\*in\b|/-?in\b'
MONTHS = {'januar': 1, 'februar': 2, 'märz': 3, 'maerz': 3, 'april': 4, 'mai': 5, 'juni': 6, 'juli': 7,
          'august': 8, 'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12}


def _lines(text):
    return [re.sub(r'\s+', ' ', x).strip(' \t•·-–*|') for x in text.splitlines() if x.strip()]


def clean_title(text):
    text = re.sub(r'^.*?\b(?:such(?:t|en)|gesucht)\b', '', text, flags=re.I) if re.search(r'\b(?:such(?:t|en))\b', text, re.I) else text
    text = re.sub(r'^(?:\s*(?:wir|ab sofort|zum nächstmöglichen zeitpunkt|zur verstärkung( unseres teams)?|ab dem [\d.]+|in (?:voll|teil)zeit|für unseren standort \w+))+', '', text, flags=re.I)
    text = re.sub(r'^\s*(?:eine[nrs]?|einen|ein)\s+', '', text, flags=re.I)
    text = re.sub(r'^(?:stellenangebot|stellenanzeige|job)\s*:\s*', '', text, flags=re.I)
    text = re.sub(r'\s*(?:in|ab|zum|für)\s+(?:vollzeit|teilzeit|sofort|\d).*$', '', text, flags=re.I)
    return text.strip(' ,.:!–-')


def find_position(lines):
    """Job title: the text in front of a gender note like (m/w/d), or after 'suchen …'."""
    for line in lines[:40]:
        m = re.search(GENDER, line, re.I)
        if m:
            title = clean_title(line[:m.start()])
            if 2 <= len(title) <= 90:
                return title
    for line in lines[:40]:
        if re.search(r'\b(?:suchen|sucht)\b', line, re.I):
            title = clean_title(re.split(r'[.!]', line)[0])
            if 3 <= len(title) <= 80:
                return title
    return ''


def find_company(lines, text):
    m = re.search(r'([A-ZÄÖÜ][\w&.\-ÄÖÜäöüß]*(?:\s+[A-ZÄÖÜ&][\w&.\-ÄÖÜäöüß]*){0,5}\s+' + LEGAL + r')(?![\w])', text)
    if m:
        return re.sub(r'^(?:Die|Der|Das)\s+', '', m.group(1).strip())
    for line in lines[:15]:
        m = re.match(r'^(?:die|der|das)?\s*(.+?)\s+(?:sucht|ist ein|ist eine|steht für)\b', line, re.I)
        if m and len(m.group(1)) <= 60:
            return m.group(1).strip()
    return ''


def find_contact(lines, text):
    m = re.search(r'(?:Ansprechpartner(?:in)?|Ansprechperson|Kontakt(?:person)?|Ihr(?:e)?\s+Ansprechpartner(?:in)?(?:\s+ist)?)\s*[:\-]?\s*'
                  r'((?:Frau|Herrn?)[ \t]+(?:(?:Prof\.|Dr\.)[ \t]+)*[A-ZÄÖÜ][\wäöüß\-]+(?:[ \t]+(?:(?:von|van|de|zu)[ \t]+)?[A-ZÄÖÜ][\wäöüß\-]+){0,2})', text)
    if m:
        return m.group(1).strip()
    m = re.search(r'\b((?:Frau|Herrn?)[ \t]+(?:(?:Prof\.|Dr\.)[ \t]+)*[A-ZÄÖÜ][\wäöüß\-]+(?:[ \t]+[A-ZÄÖÜ][\wäöüß\-]+)?)', text)
    return m.group(1).strip() if m else ''


def find_address(lines):
    for i, line in enumerate(lines):
        m = re.search(r'\b(\d{5})\s+([A-ZÄÖÜ][\wäöüß\-]+(?:\s+(?:a\.\s?d\.|am|an der|im|in)?\s*[A-ZÄÖÜ][\wäöüß\-]+)?)', line)
        if not m:
            continue
        street = ''
        same = re.search(r'([A-ZÄÖÜ][\wäöüß.\- ]*?(?:straße|strasse|str\.|weg|allee|platz|ring|gasse|damm|ufer|chaussee|markt)\s*\d+\s*[a-z]?)', line, re.I)
        if same:
            street = same.group(1).strip()
        elif i and re.search(r'\d+\s*[a-z]?\s*$', lines[i - 1]) and len(lines[i - 1]) <= 60:
            street = re.sub(r'^.*?,\s*', '', lines[i - 1]).strip()
        return {'street': street, 'postcode': m.group(1), 'city': m.group(2).strip()}
    return {}


def find_email(text):
    m = re.search(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}', text)
    return m.group(0) if m else ''


def find_deadline(text, today=None):
    today = today or date.today()
    m = re.search(r'(?:bis(?:\s+zum)?|spätestens(?:\s+(?:am|zum|bis))?|bewerbungsschluss|bewerbungsfrist)\s*:?\s*'
                  r'(\d{1,2})\.\s*(\d{1,2}\.|' + '|'.join(MONTHS) + r')\s*(\d{4})?', text, re.I)
    if not m:
        return ''
    day = int(m.group(1))
    month = m.group(2).rstrip('.')
    month = int(month) if month.isdigit() else MONTHS[month.lower()]
    year = int(m.group(3)) if m.group(3) else today.year + (1 if (month, day) < (today.month, today.day) else 0)
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return ''


def suggest(text, today=None):
    lines = _lines(text or '')
    fields = {
        'position': find_position(lines),
        'company': find_company(lines, text or ''),
        'contact': find_contact(lines, text or ''),
        'recipientEmail': find_email(text or ''),
        'deadline': find_deadline(text or '', today),
    }
    fields.update(find_address(lines))
    return {k: v for k, v in fields.items() if v}
