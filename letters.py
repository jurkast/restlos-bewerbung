"""Letter details added in 0.11: automatic salutation, list of enclosures,
place/date line for the CV and DIN 5008 helpers. Pure functions, no I/O."""
import re
from pathlib import Path

DEFAULT_SALUTATION = 'Sehr geehrte Damen und Herren,'
PARTICLES = {'von', 'van', 'de', 'der', 'den', 'zu', 'vom', 'zur', 'ten', 'ter', 'di', 'da', 'del', 'le', 'la'}
LAYOUTS = ('standard', 'din5008')


def contact_person(a):
    """Contact line used for the salutation: the form field, or in free-text mode
    the first recipient line that starts with Frau/Herr."""
    form = a.get('form', {})
    if form.get('recipientMode') == 'form':
        return form.get('contact', '')
    for line in a.get('recipient', '').splitlines():
        if re.match(r'^\s*(Frau|Herrn?)\b', line):
            return line
    return ''


def salutation_for(contact):
    """'Frau Dr. Anna von Berg' -> 'Sehr geehrte Frau Dr. von Berg,'.
    Without Frau/Herr the neutral salutation is used. Keep in sync with letter-tools.js."""
    m = re.match(r'^\s*(Frau|Herrn?)\s+(.+?)\s*,?\s*$', contact or '')
    if not m:
        return DEFAULT_SALUTATION
    tokens = m.group(2).split()
    titles = [t for t in tokens if re.match(r'^(Prof|Professor|Dr)\b', t)]
    names = [t for t in tokens if not t.endswith('.') and t not in titles]
    if not names:
        return DEFAULT_SALUTATION
    start = next((i for i, t in enumerate(names) if t.lower() in PARTICLES and i < len(names) - 1), len(names) - 1)
    surname = ' '.join(names[start:])
    greeting = 'Sehr geehrte Frau ' if m.group(1) == 'Frau' else 'Sehr geehrter Herr '
    return greeting + ' '.join(titles + [surname]) + ','


def document_label(name):
    """'Arbeitszeugnis_Firma-AG.pdf' -> 'Arbeitszeugnis Firma-AG'."""
    stem = Path(name).stem
    stem = re.sub(r'_[0-9a-f]{6}$', '', stem)  # copy suffix added by Restlos
    return re.sub(r'\s+', ' ', stem.replace('_', ' ')).strip() or name


def attachment_lines(documents, a):
    """Enclosure list for the letter. An own text replaces the automatic list."""
    own = a.get('form', {}).get('attachmentText', '')
    if own.strip():
        return [x.strip() for x in own.splitlines() if x.strip()]
    names = {d['path']: d['name'] for d in documents}
    lines = ['Lebenslauf']
    for rel in a.get('attachments', []):
        label = document_label(names.get(rel, Path(rel).name))
        if label not in lines:
            lines.append(label)
    return lines


def wants_attachment_list(a):
    return bool(a.get('design', {}).get('attachmentList', True))


def place_date(p, a):
    """'Arnsberg, 21.10.2026' for the end of the CV."""
    place = a.get('location', '').strip() or p.get('form', {}).get('city', '').strip()
    return ', '.join(x for x in (place, a.get('date', '').strip()) if x)


def return_address(p):
    """Single sender line above the recipient in the DIN 5008 address field."""
    parts = [p.get('name', '').strip()] + [x.strip() for x in p.get('address', '').splitlines() if x.strip()]
    return ' · '.join(x for x in parts if x)


def recipient_lines(a):
    return [x.strip() for x in (a.get('recipient') or a.get('company', '')).splitlines() if x.strip()]
