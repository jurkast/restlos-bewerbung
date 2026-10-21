"""Clean up the Exporte folders of the active profile (0.12).
Every export is a dated snapshot. Per application and kind the newest file always stays."""
import re
from pathlib import Path

KINDS = [('Bewerbungsmappe', 'Gesamtmappe (PDF)'), ('Bewerbung', 'E-Mail-Anhang (PDF)'), ('E-Mail-Entwurf', 'E-Mail-Entwurf'),
         ('Lebenslauf', 'Lebenslauf'), ('Anschreiben', 'Anschreiben'), ('Deckblatt', 'Deckblatt'),
         ('Texthilfe-Prompt', 'Texthilfe-Prompt')]
NAME = re.compile(r'^(' + '|'.join(re.escape(k) for k, _ in KINDS) + r')_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})?.*\.(pdf|docx|eml|txt)$')


def scan(p):
    """Per application: files, total size and what a cleanup would remove."""
    from storage import existing_application_dir
    result = []
    for a in p['applications']:
        base = existing_application_dir(p, a)
        folder = base / 'Exporte' if base else None
        if not folder or not folder.is_dir():
            continue
        groups = {}
        files = []
        for f in folder.iterdir():
            if not f.is_file() or f.is_symlink():
                continue
            m = NAME.match(f.name)
            st = f.stat()
            files.append(f)
            if m:
                groups.setdefault((m.group(1), m.group(3)), []).append((st.st_mtime, f))
        removable = []
        for items in groups.values():
            items.sort(reverse=True)
            removable += [f for _, f in items[1:]]
        result.append({'applicationId': a['id'], 'folder': str(folder), 'label': ' – '.join(x for x in (a['company'], a['position']) if x) or 'Neue Bewerbung',
                       'files': len(files), 'mb': round(sum(f.stat().st_size for f in files) / 1024 ** 2, 2),
                       'removable': sorted(f.name for f in removable),
                       'removableMb': round(sum(f.stat().st_size for f in removable) / 1024 ** 2, 2)})
    return result


def clean(p, application_ids=None):
    """Delete older exports (newest per kind stays). Paths are recomputed here, never taken from the page."""
    from storage import STORE_LOCK
    removed, freed = 0, 0
    with STORE_LOCK:
        for entry in scan(p):
            if application_ids and entry['applicationId'] not in application_ids:
                continue
            folder = Path(entry['folder'])
            for name in entry['removable']:
                f = folder / Path(name).name
                if f.is_file() and not f.is_symlink() and f.parent.resolve() == folder.resolve():
                    freed += f.stat().st_size
                    f.unlink()
                    removed += 1
    return {'removed': removed, 'mb': round(freed / 1024 ** 2, 2)}
