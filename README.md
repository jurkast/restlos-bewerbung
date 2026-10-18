# Restlos Bewerbung 0.6 – Automatische Updates

Ein lokales Bewerbungsprogramm für Zorin OS 18.1 / Ubuntu 24.04 (x86_64).

## Installieren oder aktualisieren

1. Ein geöffnetes Restlos-Fenster schließen. Änderungen werden beim Schließen gespeichert.
2. `restlos-bewerbung_0.6.0_amd64.deb` per Doppelklick öffnen.
3. In der Softwareinstallation **Installieren** beziehungsweise **Aktualisieren** wählen und bei Bedarf dein Linux-Passwort eingeben.
4. Anschließend im Anwendungsmenü nach **Restlos Bewerbung** suchen.

Das Paket aktualisiert eine bereits installierte Restlos-Version. Deine Daten unter `~/Documents/Restlos Bewerbung/` bleiben erhalten. Vor dem Update ist eine ZIP-Sicherung über **Sicherung & Daten** möglich. Fehlende Systemabhängigkeiten werden bei der Installation aus den Paketquellen ergänzt.

Wenn die Datei im Archivprogramm statt in der Softwareinstallation geöffnet wird: Rechtsklick → **Mit anderer Anwendung öffnen → Softwareinstallation**. Alternativ kann im Terminal `sudo apt install /vollständiger/Pfad/restlos-bewerbung_0.6.0_amd64.deb` verwendet werden.

Ohne Installation lässt sich im vollständigen Programmordner **Restlos Bewerbung starten.sh** ausführen. Dafür werden Python 3.12, Poppler, DejaVu-Schriften, Hunspell mit deutschem Wörterbuch, Tesseract mit Deutsch/Englisch und übliche Linux-Grafikbibliotheken benötigt. Die Python- und Qt-Bibliotheken sind mitgeliefert.

## Automatische Updates ab Version 0.6

Für den Wechsel von 0.5 oder älter muss dieses DEB-Paket **einmalig** installiert werden. Danach ist die Updateprüfung standardmäßig aktiv. Unter **Updates & Startcheck** kannst du sie ausschalten oder eine Prüfung anstoßen.

Restlos lädt ausschließlich Programmupdates aus den öffentlichen Releases von https://github.com/jurkast/restlos-bewerbung. Beim Start und alle sechs Stunden prüft es auf eine neuere Version. Signatur, Prüfsumme, Dateigröße, Programmkennung und Plattform müssen passen. Ein vollständiges Update wird im Benutzerverzeichnis vorbereitet und beim nächsten normalen Start aktiviert. Die laufende Arbeit wird nicht durch einen Neustart unterbrochen.

- Bewerbungsdaten bleiben unter `~/Documents/Restlos Bewerbung/`.
- Vor der Aktivierung entsteht dort unter **Sicherungen** eine vollständige lokale ZIP-Sicherung. Scheitert die Sicherung, wird das Update nicht aktiviert. Die Sicherungen werden nicht automatisch gelöscht.
- Programmupdates liegen getrennt unter `~/.local/share/restlos-bewerbung-updates/` und benötigen zusätzlich etwa 1 GB pro vorbereiteter Version. Für die Vorbereitung werden mindestens 3 GB freier Speicher verlangt.
- Für normale Programmupdates ist kein Administratorpasswort erforderlich. Neue Systemabhängigkeiten können später dennoch ein neues DEB-Paket erfordern; die App zeigt dies dann an.
- Eine neue Version, die beim ersten Start die Oberfläche nicht erreicht, wird beim nächsten Start zurückgenommen. Unter **Updates & Startcheck** kannst du auch selbst zur vorherigen Programmversion wechseln. Dabei werden automatische Updates vorerst ausgeschaltet. Deine Daten werden dadurch nicht auf einen alten Stand zurückgesetzt.
- Ohne Internet oder bei einer ungültigen Aktualisierung bleibt die vorhandene Version nutzbar.

**Es gibt keinen Upload deiner Bewerbungsdaten.** GitHub erhält beim Abruf der öffentlichen Update-Dateien die üblichen Verbindungsdaten, etwa IP-Adresse und Zeitpunkt. Profile, Anhänge und lokale Sicherungen werden nicht an GitHub gesendet. Eine zusätzliche Sicherung auf einem zweiten Datenträger bleibt sinnvoll.

Quellcodeänderungen werden erst ausgeliefert, wenn daraus eine signierte Version erstellt und als GitHub Release veröffentlicht wurde. Der private Signierschlüssel gehört weder ins Repository noch in die veröffentlichten Pakete.

## Startcheck und sicheres Schließen

**Updates & Startcheck** prüft PDF-Vorschau, Texterkennung, deutsches Wörterbuch sowie Name und E-Mail im aktiven Profil. Die Angaben selbst werden dafür nicht online übertragen.

Beim Schließen wird der aktuelle Stand gespeichert. Tritt dabei ein Fehler auf, bleibt das Fenster mit einer Meldung offen, damit du reagieren und deine Arbeit sichern kannst.

## Einfach ausfüllen – Restlos übernimmt die Positionierung

Unter **Mein Profil** gibt es sechs Bereiche:

- **Kontakt & Foto:** Name, Beruf, E-Mail, Telefon und getrennte Adressfelder.
- **Berufserfahrung:** Für jede Station Zeitraum, Position, Unternehmen, Ort und Aufgaben ausfüllen. „Aktuell / bis heute“ ersetzt das Enddatum. Einträge lassen sich hinzufügen, entfernen und mit Pfeilen sortieren.
- **Ausbildung:** Zeitraum, Abschluss, Einrichtung, Ort und Schwerpunkte pro Eintrag.
- **Kenntnisse:** Jeweils ein Feld für Kenntnis und Niveau/Beschreibung.
- **Sprachen:** Jeweils ein Feld für Sprache und Kenntnisstand.
- **Weitere Angaben:** Optionales Kurzprofil, Projekte/Engagement und Interessen.

Die Angaben erscheinen automatisch im richtigen Lebenslaufabschnitt. Rechts wird eine echte PDF-Vorschau erzeugt. Die Reihenfolge der Stationen bestimmst du selbst, beispielsweise neueste Station zuerst. Leere Bereiche werden nicht ausgegeben.

Bestehende Freitexte bleiben beim Update erhalten. Mit **In ausfüllbare Einträge übernehmen** werden sie in Formular-Einträge übertragen. Unklare Texte bleiben dabei im Aufgabenfeld stehen und können anschließend auf die richtigen Felder verteilt werden. Vorherige Originaltexte bleiben zusätzlich in den Formulardaten hinterlegt. Ein Import alter Unterlagen schaltet die betroffenen Bereiche wieder auf Freitext, damit importierte Inhalte nicht von alten Formularzeilen überschrieben werden.

## Bewerbungsfoto

Unter **Mein Profil → Kontakt & Foto → Foto auswählen** ein JPG-, PNG- oder WebP-Bild hinzufügen. Das Original wird automatisch in den Unterordner **Fotos** des Profils kopiert. Es bleibt auf deinem Rechner.

- Die Seitenleisten-Vorlagen zeigen das Foto **links über den Kontaktdaten**.
- Zur Auswahl stehen Hochformat, Quadrat oder Kreis.
- Über Vergrößerung und horizontale/vertikale Position kannst du den Ausschnitt verändern.
- In **Gestaltung** kann das Foto pro Bewerbung aus- oder eingeblendet werden.
- **Foto entfernen** entfernt die Zuordnung zum Profil; das gespeicherte Original bleibt in der Ablage.

Das PDF verwendet nur den zugeschnittenen Bildinhalt. Zulässig sind Bilder bis 20 MB und 30 Megapixel. Einspaltige Vorlagen zeigen das Foto oberhalb der Namens- und Kontaktangaben.

## Anschreiben als Formular

Unter **Stelle** werden Unternehmen, Position, Empfängeradresse, Ort und Datum erfasst. Absender, Empfängerblock, Betreff und Datum werden automatisch gesetzt.

Unter **Anschreiben → Formular ausfüllen** stehen die Abschnitte in der passenden Reihenfolge:

1. Einstieg und Motivation.
2. Passende Erfahrung.
3. Bezug zum Unternehmen (optional).
4. Verfügbarkeit (optional).
5. Abschluss.

Die Absätze erscheinen sofort im Dokument. Grußformel und Name werden automatisch ergänzt. Beispielantworten für verschiedene Berufsbereiche helfen beim Einstieg; Platzhalter müssen durch eigene, wahrheitsgemäße Angaben ersetzt werden.

Mit **Text frei bearbeiten** lässt sich der zusammengestellte Text frei ändern. Beim Wechsel eines vorhandenen Freitexts zurück ins Formular wird nach Bestätigung der gesamte Text im ersten Abschnitt erhalten. Er kann anschließend auf die Abschnitte verteilt werden. Bestehende Texte werden nicht unbemerkt ersetzt.

## Zwölf eigene Vorlagen und Gestaltung

**Seitenleiste, Graphit, Sand, Nordlicht, Elegant, Kontur, Studio, Klar, Modern, Klassisch, Horizont und Editorial.**

Die Vorlagen unterscheiden sich durch Seitenleisten, dunkle Flächen, Konturen, Randlinien, Kopfbänder oder eine einspaltige Gestaltung. Akzentfarbe, Sans-/Serifenschrift und Textgröße lassen sich anpassen. Anschreiben und optionales Deckblatt verwenden dieselbe Farbauswahl. Die Reihenfolge der Lebenslaufabschnitte ist einstellbar; in Seitenleisten-Vorlagen bleiben Kenntnisse und Sprachen links.

Das **optionale Deckblatt** verwendet Position, Firma, Name, Kontakte und Foto automatisch. Es kann angesehen, einzeln exportiert oder der Mappe vorangestellt werden. Ohne aktivierte Option bleibt es aus der Gesamtmappe heraus.

## Profile, Ordner, Dokumente und Export

Jedes Profil hat eigene Daten, Originaldokumente und Bewerbungen. Der lokale Hauptordner ist `~/Documents/Restlos Bewerbung/`.

```text
Profile / Profilname_ID /
  Profil.json
  Fotos /
  Lebenslauf /
  Anschreiben /
  Zeugnisse /
  Zertifikate /
  Sonstiges /
  Bewerbungen / Firma - Position_ID /
    Bewerbung.json
    Anschreiben / Anschreiben.txt + Anschreiben.pdf
    Lebenslauf / Lebenslauf.txt + Lebenslauf.pdf
    Deckblatt / Deckblatt.pdf (wenn aktiviert)
    Anlagen /
    Exporte / datierte PDF-, DOCX- und EML-Dateien
```

Bearbeitbare Formulardaten und automatisch erzeugte PDFs werden gespeichert. **Prüfen & Export** speichert zusätzliche Momentaufnahmen im Exportordner. Die Gesamtmappe enthält optional Deckblatt, Anschreiben, Lebenslauf und zugeordnete PDF-Anlagen. Die Vorschau ist auf die ersten zwölf Seiten begrenzt; exportiert werden alle Seiten.

PDF-/TXT-Dateien im Dateimanager sind Ausgaben, keine direkt synchronisierten Eingaben. Änderungen daran werden nur über die Importfunktion übernommen. Ein gemeinsames Profil liefert die Lebenslaufdaten seiner Bewerbungen; exportierte Momentaufnahmen bleiben unverändert. Die App blockiert einen gleichzeitigen zweiten Zugriff auf denselben Datenbestand.

## Neu in 0.5: Überblick und Texthilfe

### Bewerbungen planen

Unter **Stelle → Fristen & nächste Schritte** speicherst du Bewerbungsfrist, Wiedervorlage, Versanddatum und Notizen. Die Übersicht lässt sich nach Firma/Position, Status und fälligen Terminen filtern. Eine Bewerbungsfrist wird nur bei Entwürfen als fällig angezeigt; Wiedervorlagen gelten auch nach dem Versand. Zusagen und Absagen werden nicht als fällig markiert. Die Anzeige verwendet das Datum deines Rechners. Es gibt keine Benachrichtigungen bei geschlossenem Programm.

### Optionale lokale KI

Unter **Anschreiben → Lokale Modelle prüfen** sucht Restlos nach Ollama auf diesem Rechner. Ollama und ein lokales GGUF-Textmodell sind separat erforderlich und nicht im Paket enthalten. Ohne Modell bleiben alle bisherigen Funktionen nutzbar.

1. Ollama nach der offiziellen Anleitung installieren: https://docs.ollama.com/linux
2. Ein zum Rechner passendes lokales Textmodell über Ollama herunterladen. Das Modell benötigt zusätzlichen Speicherplatz. Mit `ollama list` lassen sich vorhandene Modelle anzeigen.
3. Den lokalen Ollama-Dienst starten (bei manueller Ausführung: `ollama serve`).
4. In Restlos **Lokale Modelle prüfen**, Modell auswählen, eigene Angaben ausfüllen und **Text vorschlagen** drücken.

Restlos nutzt ausschließlich `http://127.0.0.1:11434`. HTTP-Proxys und Weiterleitungen werden nicht verwendet. Als Cloud-Einträge erkennbare Modelle werden abgelehnt. Die Anbindung setzt einen vertrauenswürdigen lokalen Ollama-Dienst voraus; seine Konfiguration wird durch Restlos nicht verändert.

Übergeben werden berufliche Angaben, Position, Unternehmen, die eingefügte Stellenanzeige, Motivation, Erfahrungsbelege und bisheriger Anschreibentext. Kontaktfelder, Profilfoto und Originalanhänge werden nicht automatisch angehängt. Persönliche Informationen, die du selbst in Freitexte geschrieben hast, sind natürlich Teil dieser Texte. Restlos sendet nichts automatisch an einen Onlinedienst.

Vorschläge erscheinen zunächst in einem bearbeitbaren Prüfungsdialog. Fehlende Angaben kann das Modell als Rückfragen nennen. Auch eine lokale KI kann Aussagen erfinden: Erfahrung, Abschlüsse, Zahlen und Firmenbezug vor der Übernahme selbst prüfen. Änderungen der Ausgangsdaten seit der Erstellung werden beim Öffnen des Vorschlags angezeigt. Ein Profilwechsel ordnet den Vorschlag weiterhin der ursprünglichen Bewerbung zu.

Bei **Geprüften Text übernehmen** wird die bisherige Fassung gespeichert. Über **Frühere Texte ansehen** lassen sich bis zu zehn Fassungen vor KI-Übernahmen/Wiederherstellungen zurückholen. Dies ist kein Verlauf sämtlicher Tastatureingaben. Vorschläge und Textfassungen werden mit den Profildaten gesichert.

Über **Prompt als Textdatei speichern** erhältst du die vorbereitete Anfrage mit deinen beruflichen Angaben im Exportordner – auch ohne Ollama. Die Datei wird nicht automatisch weitergegeben.

Die Anbindung und Bedienung wurden mit einem lokalen Testserver geprüft. Auf dem Entwicklungsrechner ist noch kein echtes Sprachmodell eingerichtet; dessen Textqualität, Geschwindigkeit und Speicherbedarf sind deshalb nicht verifiziert. Ein Generierungsaufruf kann nach etwa einer Minute ohne Antwort abbrechen.

API-Referenzen: https://docs.ollama.com/api/generate und https://docs.ollama.com/api/tags

## Funktionen aus 0.4

- **Kopieren** auf der Startseite erstellt eine eigenständige Bewerbung mit eigenem Ordner, Anschreiben, Gestaltung und Anlagenzuordnung. Die gemeinsamen Profildaten bleiben gemeinsam. Firma und Empfänger der Kopie anschließend anpassen. Termine, Versanddatum, Notizen und KI-Vorschläge werden in der Kopie zurückgesetzt.
- **Prüfen & Export → Bearbeitbare Word-Dateien:** Lebenslauf, Anschreiben und Deckblatt als DOCX. Diese Ausgabe ist einspaltig und in LibreOffice/Word bearbeitbar; die zwölf gestalteten Vorlagen stehen als PDF zur Verfügung. Änderungen an Word-Dateien werden nicht automatisch zurück ins Programm übertragen.
- **E-Mail-Datei mit PDF-Anhang speichern:** Erstellt einen lokalen EML-Entwurf mit Betreff, Nachricht und vollständiger Bewerbungsmappe. Eine Empfängeradresse kann eingegeben werden. Die Datei in einem geeigneten Mailprogramm öffnen und dort prüfen und versenden. Restlos selbst sendet nichts; das Öffnen als bearbeitbarer Entwurf hängt vom Mailprogramm ab.
- **PDF-Prüfbericht:** Zeigt Seitenzahl, Dateigröße und Seiten mit auslesbarem Text. Er weist auf fehlende Basisangaben, mögliche Platzhalter und Dateien über 5 MB hin. Die 5-MB-Grenze ist ein Hinweis; maßgeblich sind die Vorgaben des Arbeitgebers.

## Import, Rechtschreibung und Sicherungen

Die Dokumentablage unterstützt die bestätigte Datenübernahme aus PDFs mit Text, DOCX, ODT und TXT. Erkannte Angaben können falsch zugeordnet sein und müssen geprüft werden. Bei mehreren Dateien wird zunächst die erste analysiert, weitere einzeln über **Daten übernehmen**. Scans und Bilder werden automatisch mit lokalem Tesseract erkannt (Deutsch und Englisch). Unterstützt werden PNG, JPG, WebP und TIFF sowie bildbasierte PDF-Seiten. Pro PDF sind bis zu 100 Seiten und davon höchstens 20 OCR-Seiten möglich; bei Überschreitung erscheint eine Meldung. Die Importdatei darf höchstens 40 MB groß sein. Die Originaldatei bleibt gespeichert. OCR kann Buchstaben, Zahlen und die Lesereihenfolge verwechseln; prüfe die vorgeschlagenen Angaben vor der Übernahme.

Deutsche Rechtschreibung wird lokal nach einer kurzen Eingabepause geprüft. Vorschläge lassen sich anklicken; Eigennamen und Fachbegriffe können ins Profilwörterbuch aufgenommen werden. Das ist keine Grammatik- oder Faktenprüfung.

**Sicherung & Daten** erstellt eine ZIP-Datei mit allen Profilen, Originalen, Fotos, Formulardaten und Exporten. Vor dem Wiederherstellen wird der aktuelle Bestand automatisch gesichert. Sicherungen sind nicht verschlüsselt. Vorhandene Daten der ersten Bewerbungsatelier-Version werden beim ersten Start übernommen, sofern noch kein Restlos-Datenbestand vorhanden ist.

## Funktionsumfang und Referenz

Die Funktionsideen wurden unter anderem mit den öffentlichen Produktbeschreibungen von Bewerbung2Go verglichen: ausfüllbare Felder, automatische Formatierung, passende Dokumentdesigns und Beispieltexte. Die Restlos-Vorlagen und Formulierungen sind eigenständig. Eine vollständige Funktionsgleichheit oder Überlegenheit wird nicht behauptet.

Restlos arbeitet ohne Onlinekonto und überträgt keine Bewerbungsdaten an einen KI-Anbieter. Die lokale KI-Anbindung benötigt einen separat eingerichteten Ollama-Dienst mit Modell. Nicht enthalten sind eine integrierte Stellenbörse und direkter E-Mail-Versand. Die vorhandenen Textbeispiele bleiben vorgefertigte Formulierungshilfen. Ein Bewerbungserfolg oder eine universelle ATS-Kompatibilität wird nicht garantiert.

Getestet mit Beispieldaten: signierte Updatevorbereitung, lokale Sicherung, Startbestätigung, Rückkehr bei Startfehler, abgelehnte Signatur/Prüfsumme/Pfade, Verhalten bei fehlender Verbindung sowie Speichern beim Schließen; Planung und Suchfilter, lokale KI-Schnittstelle mit Testserver, Modellfilter, Fehlerantworten, Vorschau/Übernahme/Wiederherstellung von Texten; OCR aus Bild und Scan-PDF, drei DOCX-Ausgaben einschließlich visueller Prüfung, EML-PDF-Anhang, Kopierfunktion und Exportbericht im Desktop-Fenster; zwölf Layouts mit Foto, Fotoausschnitte, Formulardaten und automatische Platzierung, lange mehrseitige Lebensläufe, Deckblatt und Gesamtmappe, Desktop-Bedienung, Rechtschreibkorrekturen, Migration älterer Texte, Speicherung und ZIP-Wiederherstellung.

Quellcode liegt im Programmordner. Bibliothekslizenzen: `THIRD-PARTY.md` und `lib/*dist-info/`.
