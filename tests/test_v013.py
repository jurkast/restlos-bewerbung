"""Tests for 0.13: unsolicited applications (Initiativbewerbung).
Run with:  python3 -m pytest tests/test_v013.py"""
import importlib, json, sys
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
    for name in ['storage', 'studio', 'pdf_export', 'word_export', 'letters', 'forms', 'delivery', 'assistant_local']:
        sys.modules.pop(name, None)
    return importlib.import_module('storage'), tmp_path


def sample(storage, initiative=True, position=''):
    s = storage.initial()
    s['profile'].update(name='Max Muster', email='max@example.org', phone='0171', address='Weg 1\n12345 Ort')
    a = s['applications'][0]
    a.update(company='Müller GmbH', position=position, motivation='Ich möchte Ihr Team unterstützen.', evidence='Fünf Jahre Lager.', initiative=initiative)
    a['form']['recipientMode'] = 'text'; a['recipient'] = ''
    storage.persist(s, a['id'], generate=False)
    return s, a


def test_existing_applications_are_not_initiative(env):
    storage, tmp = env
    s, a = sample(storage)
    raw = json.loads(json.dumps(s))
    raw['profiles'][0]['applications'][0].pop('initiative')
    assert storage.validate(raw)['applications'][0]['initiative'] is False
    raw['profiles'][0]['applications'][0]['initiative'] = 'ja'
    with pytest.raises(ValueError):
        storage.validate(raw)


def test_subject_lines():
    from letters import subject_line
    assert subject_line({'position': '', 'initiative': True}) == 'Initiativbewerbung'
    assert subject_line({'position': 'Lagerist', 'initiative': True}) == 'Initiativbewerbung als Lagerist'
    assert subject_line({'position': 'Lagerist'}) == 'Bewerbung als Lagerist'


def test_check_turns_missing_job_details_into_hints(env):
    storage, tmp = env
    s, a = sample(storage)
    from studio import application_check
    issues = application_check(s, a, check_size=False)['issues']
    by_field = {i['field']: i for i in issues if i['step'] == 'stelle'}
    assert by_field['position']['level'] == 'hint' and by_field['recipient']['level'] == 'hint'
    assert not any(i['level'] == 'must' and i['field'] in ('position', 'recipient', 'company') for i in issues)
    # without the tick the same gaps are required again
    a['initiative'] = False
    issues = application_check(s, a, check_size=False)['issues']
    assert {i['field'] for i in issues if i['level'] == 'must'} >= {'position', 'recipient'}
    # required profile data stay required for unsolicited applications as well
    a['initiative'] = True; s['profile']['email'] = ''
    assert any(i['field'] == 'email' and i['level'] == 'must' for i in application_check(s, a, check_size=False)['issues'])


def test_pdf_word_mail_and_report(env):
    storage, tmp = env
    s, a = sample(storage)
    from pdf_export import make_pdf
    from pypdf import PdfReader
    a['design']['cover'] = True
    make_pdf(s, a, tmp / 'all.pdf', 'all', False)
    text = '\n'.join(p.extract_text() for p in PdfReader(tmp / 'all.pdf').pages)
    assert 'Initiativbewerbung' in text and 'Bewerbung als' not in text and 'Deine Position' not in text
    from word_export import make_docx
    from docx import Document
    make_docx(s, a, tmp / 'l.docx', 'letter')
    assert any(p.text == 'Initiativbewerbung' for p in Document(tmp / 'l.docx').paragraphs)
    from delivery import mail_draft, pdf_report
    mail_draft(tmp / 'm.eml', tmp / 'all.pdf', s, a)
    raw = (tmp / 'm.eml').read_text(errors='replace')
    assert 'Subject: Initiativbewerbung' in raw and 'meine Initiativbewerbung' in raw
    assert not any('Position fehlt' in w for w in pdf_report(tmp / 'all.pdf', s, a)['warnings'])


def test_ai_prompt_knows_the_kind_of_application(env):
    storage, tmp = env
    s, a = sample(storage)
    from assistant_local import inputs
    assert inputs(s, a)['Art'].startswith('Initiativbewerbung')
