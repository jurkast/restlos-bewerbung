"""Tests for the 0.10.1 fixes. Run with:  python3 -m pytest tests
Uses isolated temporary folders via RESTLOS_DATA_DIR / RESTLOS_UPDATE_DIR."""
import importlib, json, sys, time, zipfile
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
    for name in ['storage', 'reliability', 'updates', 'studio', 'pdf_export', 'word_export', 'delivery', 'photos', 'personal']:
        sys.modules.pop(name, None)
    storage = importlib.import_module('storage')
    return storage, tmp_path


def sample(storage):
    s = storage.initial()
    p = storage.selected(s)
    p['profile'].update(name='Max Muster', email='max@example.org', phone='0123 456', address='Weg 1\n12345 Ort')
    a = s['applications'][0]
    a.update(company='Müller Logistik GmbH', position='Lagerist', motivation='Ich möchte bei Ihnen arbeiten.', evidence='Ich habe fünf Jahre Lagererfahrung.')
    return s, a


def make_pdf_file(path, pages=2):
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path))
    for i in range(pages):
        c.drawString(100, 700, 'Seite %d' % (i + 1)); c.showPage()
    c.save()
    return path


def test_save_without_pdfs_is_fast_and_skips_unchanged_attachments(env):
    storage, tmp = env
    s, a = sample(storage)
    src = make_pdf_file(tmp / 'Zeugnis.pdf')
    d = storage.document_copy(s, src, 'Zeugnisse'); a['attachments'].append(d['path'])
    storage.persist(s, a['id'], generate=False)
    ap = storage.application_dir(storage.selected(s), a)
    copy = ap / 'Anlagen' / ('01-' + Path(d['path']).name)
    assert copy.is_file()
    before = copy.stat().st_mtime_ns
    time.sleep(0.02)
    a['motivation'] += ' Neu.'
    t = time.time(); storage.persist(s, a['id'], generate=False); assert time.time() - t < 1
    assert copy.stat().st_mtime_ns == before, 'Anlage darf beim Tippen nicht neu erzeugt werden'
    assert not (ap / 'Lebenslauf' / 'Lebenslauf.pdf').exists(), 'PDFs entstehen erst im Hintergrund'
    # page edits require a new copy
    a['attachmentEdits'] = {d['path']: [{'index': 1, 'rotation': 90}]}
    storage.persist(s, a['id'], generate=False)
    from pypdf import PdfReader
    assert len(PdfReader(copy).pages) == 1


def test_background_generation_writes_pdfs_and_does_not_create_folders(env):
    storage, tmp = env
    s, a = sample(storage)
    storage.persist(s, a['id'], generate=False)
    later = storage.activate(json.loads(json.dumps(s)))  # a copy, like the state of a later message
    storage.generate_documents(later, background=True)
    ap = storage.application_dir(storage.selected(s), a)
    assert (ap / 'Anschreiben' / 'Anschreiben.pdf').is_file()
    assert (ap / '.pdf-state').read_text() == storage.pdf_digest(storage.selected(s), a)
    # An older state with another company name must not create a stray folder.
    old = json.loads(json.dumps(s)); storage.activate(old)
    old['applications'][0]['company'] = 'Alter Name'; old['applications'][0].pop('folder', None)
    a['company'] = 'Neuer Name'; storage.persist(s, a['id'], generate=False)
    storage.generate_documents(old, background=True)
    folders = list((storage.profile_dir(storage.selected(s)) / 'Bewerbungen').iterdir())
    assert len(folders) == 1 and folders[0].name.startswith('Neuer Name')


def test_load_falls_back_to_previous_copy(env):
    storage, tmp = env
    s, a = sample(storage)
    storage.persist(s, a['id'], generate=False)
    data = storage.DATA / 'data.json'
    import shutil; shutil.copy2(data, storage.DATA / 'data.previous.json')
    data.write_text('{kaputt')
    loaded = storage.load()
    assert loaded['profile']['name'] == 'Max Muster'
    assert storage.RECOVERED and list(storage.DATA.glob('data.defekt-*.json'))


def test_load_without_any_copy_gives_clear_error(env):
    storage, tmp = env
    storage.private_dir(storage.DATA); (storage.DATA / 'data.json').write_text('{kaputt')
    with pytest.raises(ValueError, match='Wiederherstellen'):
        storage.load()


def test_restore_works_when_current_data_are_broken(env):
    storage, tmp = env
    s, a = sample(storage)
    storage.persist(s, a['id'], generate=False)
    zip_path = tmp / 'sicherung.zip'; storage.backup(s, zip_path)
    (storage.DATA / 'data.json').write_text('{kaputt')
    restored = storage.restore(zip_path)
    assert restored['profile']['name'] == 'Max Muster'
    pre = list((storage.DATA / 'Sicherungen').glob('Vor-Wiederherstellung-*.zip'))
    assert pre and 'data.json' in zipfile.ZipFile(pre[0]).namelist()


def test_previous_copy_is_not_overwritten_on_every_save(env):
    storage, tmp = env
    s, a = sample(storage)
    storage.persist(s, a['id'], generate=False)
    a['motivation'] = 'Erste Fassung'; storage.persist(s, a['id'], generate=False)
    prev = storage.DATA / 'data.previous.json'
    first = prev.read_text()
    for text in ('Zweite', 'Dritte'):
        a['motivation'] = text; storage.persist(s, a['id'], generate=False)
    assert prev.read_text() == first
    assert list((storage.DATA / 'Sicherungen' / 'Täglich').glob('data-*.json'))


def test_word_export_survives_extra_blank_lines(env):
    storage, tmp = env
    s, a = sample(storage)
    p = s['profile']
    storage.persist(s, a['id'], generate=False)
    p['form']['experience']['mode'] = 'text'
    p['experience'] = '01/2020 – heute · Lager\nAufgaben\n\n\n\nZweite Station\nMehr'
    from word_export import make_docx
    make_docx(s, a, tmp / 'cv.docx', 'cv')
    from pdf_export import make_pdf
    make_pdf(s, a, tmp / 'cv.pdf', 'cv', False)
    assert (tmp / 'cv.docx').stat().st_size > 0 and (tmp / 'cv.pdf').stat().st_size > 0


def test_text_advice_has_no_false_dass_or_article_hits(env):
    from studio import text_advice
    assert text_advice('Ich hoffe das Beste.') == []
    assert text_advice('Aufgaben, die die Abteilung hat.') == []
    hit = text_advice('Ich hoffe das Sie mich einladen.')
    assert hit and hit[0]['replacement'] == 'Ich hoffe, dass'
    assert text_advice('Ich ich bin hier.')[0]['replacement'] == 'Ich'


def test_application_check_labels_and_company_match(env):
    storage, tmp = env
    s, a = sample(storage)
    storage.persist(s, a['id'], generate=False)
    a['form']['recipientMode'] = 'text'; a['recipient'] = 'Müller GmbH\nPersonalabteilung\n12345 Ort'
    a['form']['letterMode'] = 'text'; a['letter'] = 'Text mit [Platzhalter].'
    from studio import application_check
    msgs = [i['message'] for i in application_check(s, a, check_size=False)['issues']]
    assert not any('nicht überein' in m for m in msgs)
    assert any('„Anschreiben“' in m for m in msgs)
    a['recipient'] = 'Schmidt AG\n12345 Ort'
    msgs = [i['message'] for i in application_check(s, a, check_size=False)['issues']]
    assert any('nicht überein' in m for m in msgs)


def test_same_photo_twice_is_stored_once(env):
    storage, tmp = env
    s, a = sample(storage)
    from PIL import Image
    img = tmp / 'foto.png'; Image.new('RGB', (40, 50), 'white').save(img)
    d1 = storage.document_copy(s, img, 'Fotos'); d2 = storage.document_copy(s, img, 'Fotos')
    assert d1 is d2 and len(storage.selected(s)['documents']) == 1


def test_mail_subject_and_attachment_name(env):
    storage, tmp = env
    s, a = sample(storage)
    a['position'] = ''
    pdf = make_pdf_file(tmp / 'b.pdf', 1)
    from delivery import mail_draft
    mail_draft(tmp / 'm.eml', pdf, s, a)
    raw = (tmp / 'm.eml').read_text(errors='replace')
    assert 'Subject: Bewerbung\r\n' in raw or 'Subject: Bewerbung\n' in raw
    assert 'Bewerbung_Max_Muster.pdf' in raw and 'als .' not in raw


def test_old_update_versions_and_backups_are_pruned(env, monkeypatch):
    storage, tmp = env
    import updates
    versions = tmp / 'updates' / 'versions'
    for v in ('0.8.0', '0.9.0', '0.9.1', '0.10.0'):
        (versions / v).mkdir(parents=True); (versions / v / 'app.py').write_text('')
    (tmp / 'updates' / 'current.json').write_text(json.dumps({'version': '0.10.0', 'previous': '0.9.1'}))
    removed = updates.prune_versions()
    assert sorted(removed) == ['0.8.0', '0.9.0']
    assert (versions / '0.9.1').is_dir() and (versions / '0.10.0').is_dir()

    s, a = sample(storage)
    storage.persist(s, a['id'], generate=False)
    import reliability
    folder = storage.private_dir(storage.DATA / 'Sicherungen')
    for i in range(7):
        (folder / ('Vor-Update-2026-01-0%d_00-00-00-aaaaaa.zip' % (i + 1))).write_bytes(b'x')
    reliability.snapshot_before_update()
    left = sorted(folder.glob('Vor-Update-*.zip'))
    assert len(left) == reliability.KEEP_UPDATE_BACKUPS and left[-1].name.startswith('Vor-Update-20')
