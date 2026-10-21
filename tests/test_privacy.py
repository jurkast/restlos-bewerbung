"""Privacy guard: nothing that looks like personal application data may be part of the
repository or of a release. Run with:  python3 -m pytest tests/test_privacy.py"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {'.pdf', '.docx', '.doc', '.odt', '.eml', '.zip', '.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff',
                      '.xlsx', '.key'}
FORBIDDEN_DIRS = {'Profile', 'Sicherungen', 'Exporte', 'Bewerbungen'}


def tracked():
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files'], capture_output=True, text=True, check=True).stdout
    return [ROOT / x for x in out.splitlines()]


def test_no_personal_files_in_repository():
    bad = []
    for path in tracked():
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or FORBIDDEN_DIRS & set(rel.parts):
            bad.append(str(rel))
        elif path.suffix == '.pem' and path.name != 'update-public.pem':
            bad.append(str(rel))
        elif re.fullmatch(r'(data|Profil|Bewerbung)(\.previous)?\.json', path.name):
            bad.append(str(rel))
    assert not bad, 'Persönliche Dateien im Repository: %s' % bad


def test_no_private_key_or_saved_state_in_text_files():
    bad = []
    for path in tracked():
        if path.suffix.lower() in ('.ttf',) or not path.is_file():
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        if re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----', text):
            bad.append(path.name)
        if re.search(r'"selectedProfile"\s*:\s*"[0-9a-f-]{36}"', text):
            bad.append(path.name)
    assert not bad, bad


def test_build_skips_untracked_files(tmp_path):
    """A personal file lying in the program folder must not be packaged."""
    source = (ROOT / 'tools' / 'build_release.py').read_text(encoding='utf-8')
    assert "git','-C',str(root),'ls-files'" in source and 'privacy_check(app)' in source
