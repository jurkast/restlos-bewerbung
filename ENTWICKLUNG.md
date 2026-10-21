# Quellcode und Veröffentlichung

Dieses Repository enthält nur Programmcode. Nutzerdaten, private Signierschlüssel und lokal erzeugte Bewerbungen gehören nicht hinein.

## Lokal entwickeln

Python 3.12 und die im DEB-Paket aufgeführten Systemabhängigkeiten werden benötigt. Die Python-Bibliotheken stehen in `requirements.txt`. Für eine Entwicklungsumgebung:

```sh
python3 -m venv .venv
.venv/bin/pip install --target lib -r requirements.txt
mkdir -p native
./'Restlos Bewerbung starten.sh'
```

`native/` kann leer bleiben, wenn die Grafikbibliotheken über das System installiert sind. Im ausgelieferten Runtime-Paket enthält es libxcb-cursor und dessen Lizenzhinweis. Das Programm lädt die Python-Bibliotheken aus `lib/`.

## Eine Änderung als Update veröffentlichen

1. Änderung implementieren und testen (`python3 -m pytest tests`; die Tests verwenden eigene temporäre Datenordner). `VERSION` erhöhen, beispielsweise von `0.6.0` auf `0.6.1`.
2. UI-Versionsanzeige, Dokumentation und Versionsstandardwerte ebenfalls aktualisieren. Neue Systemabhängigkeiten erfordern gegebenenfalls einen höheren `minimum_base`-Wert im Release-Skript und ein neues DEB-Paket.
3. Mit dem bestehenden privaten Signierschlüssel außerhalb des Repositorys bauen:

```sh
python3 tools/build_release.py --runtime . --key /sicherer/Pfad/private.pem --output dist
```

4. Quellcode committen und ins Repository pushen. Die vier erzeugten Dateien als Assets eines normalen, veröffentlichten GitHub Release hochladen:
   - `restlos-bewerbung_VERSION.zip`
   - `restlos-bewerbung_VERSION_amd64.deb`
   - `restlos-update.json`
   - `restlos-update.sig`

Beispiel für den Upload nach Prüfung der Dateien:

```sh
gh release create v0.6.1 dist/restlos-bewerbung-0.6.1.zip dist/restlos-bewerbung_0.6.1_amd64.deb dist/restlos-update.json dist/restlos-update.sig --repo jurkast/restlos-bewerbung --title 'Restlos Bewerbung 0.6.1' --notes-file RELEASE-NOTES.md
```

Erst ein veröffentlichtes Release wird vom Updater angeboten. Ein Commit alleine ist kein Programmupdate. Entwürfe und Vorabversionen werden über den verwendeten Latest-Endpunkt nicht ausgeliefert.

Der private Schlüssel darf niemals mit hochgeladen oder durch einen neu generierten ersetzt werden: bestehende Installationen vertrauen dem ausgelieferten öffentlichen Schlüssel. Den privaten Schlüssel separat sichern. Ohne ihn können bestehende Installationen keine neuen Updates akzeptieren.

## Daten und Rollback

Das Programm speichert persönliche Dateien getrennt unter `~/Documents/Restlos Bewerbung/`. Tests verwenden `RESTLOS_DATA_DIR`, `RESTLOS_LEGACY_DIR` und `RESTLOS_UPDATE_DIR` mit isolierten Testverzeichnissen. Neue Versionen müssen Daten weiterhin kompatibel lesen und schreiben; ein Programm-Rollback ersetzt keine Datenmigration rückwärts. Vor Updates erstellt der Updater eine lokale ZIP-Sicherung.

`lib/`, `native/`, `dist/`, `.venv/`, Testdaten, private Schlüssel und Konfigurationen werden nicht in Git aufgenommen. Das Build-Skript verwendet eine explizite Liste erlaubter Programmdateien und die beiden angegebenen Runtime-Verzeichnisse.
