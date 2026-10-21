"""Tests for 0.12: modern templates, job-ad suggestions, export cleanup, e-mail text and
the application folder lookup. Run with:  python3 -m pytest tests/test_v012.py"""
import importlib, json, os, sys
from datetime import date
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if (ROOT / 'lib').is_dir():
    sys.path.insert(0, str(ROOT / 'lib'))


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv('RESTLOS_DATA_DIR', str(tmp_path / 'data'))
    monkeypatch.setenv('RESTLOS_UPDATE_DIR', str(tmp_path / 'updates'))
    monkeypatch.setenv('RESTLOS_LEGACY_DIR', str(tmp_path / 'legacy'))
    for name in ['storage', 'studio', 'pdf_export', 'word_export', 'letters', 'forms', 'photos', 'personal', 'housekeeping', 'delivery']:
        sys.modules.pop(name, None)
    return importlib.import_module('storage'), tmp_path


def sample(storage, tmp):
    from PIL import Image
    s = storage.initial(); p = storage.selected(s); pr = p['profile']
    pr.update(name='Max Muster', email='max@example.org', phone='0171 234', title='Lagerist', birthDate='1994-03-14')
    pr['form'].update(street='Lindenweg 4', postcode='59755', city='Arnsberg')
    pr['form']['experience']['rows'] = [dict(start='2021-04', end='', current=True, title='Fachkraft Lager', organization='Spedition Meier', city='Arnsberg', details='- Wareneingang\n- Inventur')]
    pr['form']['skills']['rows'] = [dict(name='SAP', level='sehr gut'), dict(name='Stapler', level='vorhanden')]
    pr['form']['languages']['rows'] = [dict(name='Englisch', level='B2')]
    Image.new('RGB', (400, 500), 'gray').save(tmp / 'foto.jpg')
    pr['photo'] = storage.document_copy(s, tmp / 'foto.jpg', 'Fotos')['path']
    a = s['applications'][0]
    a.update(company='Müller GmbH', position='Lagerist', location='Arnsberg', date='21.10.2026', motivation='Ich will.', evidence='Ich kann.')
    storage.persist(s, a['id'], generate=False)
    return s, a


def text(path):
    from pypdf import PdfReader
    return '\n'.join(p.extract_text() for p in PdfReader(path).pages)


def test_bundled_fonts_are_used(env):
    storage, tmp = env
    s, a = sample(storage, tmp)
    from pdf_export import make_pdf
    make_pdf(s, a, tmp / 'cv.pdf', 'cv', False)
    from pypdf import PdfReader
    fonts = set()
    for page in PdfReader(tmp / 'cv.pdf').pages:
        for f in (page['/Resources'].get('/Font') or {}).values():
            fonts.add(str(f.get_object()['/BaseFont']))
    assert any('Inter' in f for f in fonts), fonts


@pytest.mark.parametrize('template', ['Seitenleiste', 'Graphit', 'Sand', 'Nordlicht', 'Elegant', 'Kontur', 'Studio',
                                      'Klar', 'Modern', 'Klassisch', 'Horizont', 'Editorial'])
def test_all_templates_render_content(env, template):
    storage, tmp = env
    s, a = sample(storage, tmp)
    from pdf_export import make_pdf
    a['template'] = template; a['design']['cover'] = True
    make_pdf(s, a, tmp / 'all.pdf', 'all', False)
    t = text(tmp / 'all.pdf')
    for needle in ('Max Muster', 'Fachkraft Lager', 'Spedition Meier', 'Wareneingang', 'SAP', 'Englisch', '14.03.1994',
                   'Bewerbung als Lagerist', 'Müller GmbH'):
        assert needle in t, (template, needle)


def test_level_scores():
    from pdf_export import level_score
    assert level_score('Muttersprache') == 1.0 and level_score('B2') == .7 and level_score('4/5') == .8
    assert level_score('80 %') == .8 and level_score('Grundkenntnisse') == .4 and level_score('vorhanden') is None


def test_letter_still_has_only_the_signature_image(env):
    storage, tmp = env
    s, a = sample(storage, tmp)
    from pdf_export import make_pdf
    from pypdf import PdfReader
    for template in ('Horizont', 'Seitenleiste'):
        a['template'] = template
        make_pdf(s, a, tmp / 'l.pdf', 'letter', False)
        assert sum(len(p.images) for p in PdfReader(tmp / 'l.pdf').pages) == 0


def test_long_cv_flows_over_pages(env):
    storage, tmp = env
    s, a = sample(storage, tmp)
    f = s['profile']['form']
    f['experience']['rows'] = [dict(start='2010-01', end='2012-01', current=False, title='Station %d' % i, organization='Firma', city='',
                                    details='\n'.join('- Aufgabe %d' % j for j in range(45 if i == 0 else 4))) for i in range(5)]
    s['profile']['name'] = 'Alexandra-Maximiliane von Hohenberg-Lüdenscheidt'
    storage.persist(s, a['id'], generate=False)
    from pdf_export import make_pdf
    from pypdf import PdfReader
    for template in ('Seitenleiste', 'Klar'):
        a['template'] = template
        make_pdf(s, a, tmp / 'cv.pdf', 'cv', False)
        pages = PdfReader(tmp / 'cv.pdf').pages
        # the experience section starts on page 1 instead of leaving it empty
        assert 'Station 0' in pages[0].extract_text() and len(pages) >= 2
        assert 'Hohenberg-Lüdenscheidt' in pages[0].extract_text().replace('\n', ' ')


AD = """Müller Logistik GmbH
Wir suchen zum nächstmöglichen Zeitpunkt eine
Fachkraft für Lagerlogistik (m/w/d) in Vollzeit
Bewerbungen bitte bis zum 15.11.2026 an:
Ihre Ansprechpartnerin: Frau Dr. Anna von Berg
Industriestraße 12
59821 Arnsberg
bewerbung@mueller-logistik.de"""


def test_job_ad_suggestions():
    from jobad import suggest
    got = suggest(AD, today=date(2026, 10, 21))
    assert got == {'position': 'Fachkraft für Lagerlogistik', 'company': 'Müller Logistik GmbH', 'contact': 'Frau Dr. Anna von Berg',
                   'recipientEmail': 'bewerbung@mueller-logistik.de', 'deadline': '2026-11-15', 'street': 'Industriestraße 12',
                   'postcode': '59821', 'city': 'Arnsberg'}
    other = suggest('Die Stadtwerke Arnsberg AG sucht ab sofort einen Elektroniker für Betriebstechnik (w/m/d).\n'
                    'Kontakt: Herr Klaus Weber\nAm Markt 5, 59755 Arnsberg\nBewerbungsschluss: 30. November', today=date(2026, 10, 21))
    assert other['position'] == 'Elektroniker für Betriebstechnik' and other['company'] == 'Stadtwerke Arnsberg AG'
    assert other['contact'] == 'Herr Klaus Weber' and other['deadline'] == '2026-11-30' and other['street'] == 'Am Markt 5'
    assert suggest('') == {}


def test_export_cleanup_keeps_newest_per_kind(env):
    storage, tmp = env
    s, a = sample(storage, tmp)
    ex = storage.application_dir(storage.selected(s), a) / 'Exporte'
    for i in range(3):
        for kind, ext in (('Bewerbungsmappe', 'pdf'), ('Lebenslauf', 'docx')):
            f = ex / f'{kind}_2026-10-0{i + 1}_10-00-00_a{i}.{ext}'; f.write_bytes(b'x' * 1000); os.utime(f, (1e9 + i, 1e9 + i))
    (ex / 'eigene-notiz.txt').write_text('bleibt')
    import housekeeping
    entry = housekeeping.scan(storage.selected(s))[0]
    assert len(entry['removable']) == 4
    result = housekeeping.clean(storage.selected(s))
    assert result['removed'] == 4
    left = sorted(f.name for f in ex.iterdir())
    assert left == ['Bewerbungsmappe_2026-10-03_10-00-00_a2.pdf', 'Lebenslauf_2026-10-03_10-00-00_a2.docx', 'eigene-notiz.txt']


def test_mail_subject_and_text_can_be_customised(env):
    storage, tmp = env
    s, a = sample(storage, tmp)
    from delivery import mail_draft
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(tmp / 'b.pdf')); c.drawString(10, 10, 'x'); c.save()
    mail_draft(tmp / 'std.eml', tmp / 'b.pdf', s, a)
    raw = (tmp / 'std.eml').read_text(errors='replace')
    assert 'Subject: Bewerbung als Lagerist' in raw and 'anbei erhalten Sie' in raw
    a['form']['mailSubject'] = 'Initiativbewerbung'; a['form']['mailText'] = 'Mein eigener Text.'
    mail_draft(tmp / 'own.eml', tmp / 'b.pdf', s, a)
    raw = (tmp / 'own.eml').read_text(errors='replace')
    assert 'Subject: Initiativbewerbung' in raw and 'Mein eigener Text.' in raw and 'anbei' not in raw
    assert 'Mit freundlichen Gr' in raw


def test_folder_survives_two_renames_in_one_session(env):
    """Bug fixed in 0.12: the page keeps the first folder name, a second rename created a second folder."""
    storage, tmp = env
    s, a = sample(storage, tmp)
    page_state = json.loads(json.dumps(s))           # what the page still knows
    for company in ('Erste Firma', 'Zweite Firma'):
        state = json.loads(json.dumps(page_state)); storage.activate(state)
        state['applications'][0]['company'] = company
        storage.persist(state, generate=False)
    folders = [d.name for d in (storage.profile_dir(storage.selected(s)) / 'Bewerbungen').iterdir()]
    assert len(folders) == 1 and folders[0].startswith('Zweite Firma')
