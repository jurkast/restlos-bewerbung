# Restlos Bewerbung 0.13 – Bewerbungen individuell fertigstellen

Ein lokales Bewerbungsprogramm für Zorin OS 18.1 / Ubuntu 24.04 (x86_64).

## Installieren oder aktualisieren

1. Ein geöffnetes Restlos-Fenster schließen. Änderungen werden beim Schließen gespeichert.
2. `restlos-bewerbung_0.13.0_amd64.deb` per Doppelklick öffnen.
3. In der Softwareinstallation **Installieren** beziehungsweise **Aktualisieren** wählen und bei Bedarf dein Linux-Passwort eingeben.
4. Anschließend im Anwendungsmenü nach **Restlos Bewerbung** suchen.

Das Paket aktualisiert eine bereits installierte Restlos-Version. Deine Daten unter `~/Documents/Restlos Bewerbung/` bleiben erhalten. Vor dem Update ist eine ZIP-Sicherung über **Sicherung & Daten** möglich. Fehlende Systemabhängigkeiten werden bei der Installation aus den Paketquellen ergänzt.

Wenn die Datei im Archivprogramm statt in der Softwareinstallation geöffnet wird: Rechtsklick → **Mit anderer Anwendung öffnen → Softwareinstallation**. Alternativ kann im Terminal `sudo apt install /vollständiger/Pfad/restlos-bewerbung_0.13.0_amd64.deb` verwendet werden.

Ohne Installation lässt sich im vollständigen Programmordner **Restlos Bewerbung starten.sh** ausführen. Dafür werden Python 3.12, Poppler, DejaVu-Schriften, Hunspell mit deutschem Wörterbuch, Tesseract mit Deutsch/Englisch und übliche Linux-Grafikbibliotheken benötigt. Die Python- und Qt-Bibliotheken sind mitgeliefert.

## Neu in 0.13: Initiativbewerbung

Unter **Stelle** gibt es den Haken **„Initiativbewerbung – ich bewerbe mich ohne konkrete Stellenausschreibung“**:

- Position (jetzt „Wunschposition oder Bereich“), Stellenanzeige, Empfängeranschrift und Unternehmen sind optional.
- **Prüfen & Export** trennt jetzt „Bitte prüfen“ (z. B. eigener Name, E-Mail, Anschreibentext) von „Hinweise (optional)“. Fehlende Stellenangaben erscheinen bei Initiativbewerbungen nur als Hinweis; der Export ist ohne Umweg möglich.
- Betreff in Anschreiben, Word, E-Mail und Deckblatt: „Initiativbewerbung“ bzw. „Initiativbewerbung als …“. Der Standardtext der E-Mail ist angepasst.
- Die Beispielbibliothek zeigt zuerst die Vorschläge für Initiativbewerbungen; Entwurf und lokale Texthilfe funktionieren auch ohne Position.

Bestehende Bewerbungen bleiben normale Bewerbungen, bis der Haken gesetzt wird.

## Neu in 0.12: Moderne Vorlagen und mehr Hilfe im Alltag

1. **Moderne Gestaltung aller zwölf Vorlagen:** Neue Schriften (Inter und Source Serif 4, beide frei unter der SIL Open Font License und mitgeliefert), Abschnittsüberschriften mit Sperrschrift, eine **Zeitleiste** für Berufserfahrung und Ausbildung (Zeitraum links, Position, Firma und Aufgaben rechts; Zeilen mit „-“ werden zu Aufzählungspunkten), **Balken für Kenntnisse und Sprachen** (z. B. „sehr gut“, „B2“, „4/5“, „80 %“, „Muttersprache“; unbekannte Angaben bleiben als Text), Fotos mit abgerundeten Ecken, farbige Kopfbänder bei Horizont und Studio, ein neues **Deckblatt** mit großem Farbfeld und Inhaltsangabe sowie ein überarbeiteter Briefkopf im Anschreiben. Sehr lange Namen werden automatisch kleiner gesetzt. Fehlen die mitgelieferten Schriften, verwendet Restlos DejaVu.
2. **Erinnerungen beim Start:** Fristen und Wiedervorlagen, die fällig sind oder in den nächsten drei Tagen anstehen, erscheinen beim Öffnen – über alle Profile. „Bewerbung öffnen“ springt direkt hinein.
3. **Exporte aufräumen:** Unter **Sicherung & Daten** zeigt „Exporte prüfen“, wie viel Platz die datierten Exporte belegen. Ältere Fassungen lassen sich pro Bewerbung oder gesammelt löschen; die neueste Fassung je Art bleibt immer erhalten.
4. **E-Mail-Text anpassbar:** Unter **Prüfen & Export** lassen sich Betreff und Text des E-Mail-Entwurfs ändern. Anrede, Grußformel und Name werden ergänzt.
5. **Stellenanzeige auswerten:** Unter **Stelle** übernimmt „Angaben aus der Anzeige übernehmen“ nach Prüfung Firma, Position, Ansprechperson, Anschrift, Bewerbungs-E-Mail und Frist. Alles lokal; bereits ausgefüllte Felder werden nur überschrieben, wenn du sie anhakst.
6. **Fehler behoben:** Wurden Firma oder Position in einer Sitzung mehrfach geändert, konnte ein zweiter Bewerbungsordner entstehen. Restlos findet den Ordner jetzt immer über die feste Bewerbungs-ID.

## Neu in 0.11: Briefformat, Anrede, Anlagen und Update per Klick

1. **Automatische Anrede:** Unter **Anschreiben → Anrede** ist „Automatisch“ voreingestellt. Aus der Ansprechperson unter „Stelle“ wird die passende Anrede: „Frau Dr. Anna von Berg“ ergibt „Sehr geehrte Frau Dr. von Berg,“, „Herr Max Schmidt“ ergibt „Sehr geehrter Herr Schmidt,“. Ohne Frau/Herr bleibt es bei „Sehr geehrte Damen und Herren,“. Bei frei geschriebener Empfängeranschrift wird die erste Zeile mit Frau/Herr verwendet. „Eigene Anrede“ erlaubt einen beliebigen Text. Bestehende Bewerbungen mit einer eigenen Anrede behalten diese.
2. **Anlagenverzeichnis:** Unter dem Namen im Anschreiben steht automatisch „Anlagen“ mit Lebenslauf und den Anlagen dieser Bewerbung (aus den Dateinamen, z. B. „Arbeitszeugnis Spedition Meier“). Die Liste lässt sich unter **Anschreiben → Anlagenverzeichnis** abschalten oder durch eine eigene Liste ersetzen. Gilt für PDF, Word und die Textdatei.
3. **Ort, Datum und Unterschrift unter dem Lebenslauf:** In **Gestaltung → Briefformat und Abschluss** einschaltbar. Ort und Datum kommen aus „Stelle“, die Unterschrift aus „Anschreiben → Deine Unterschrift“. In allen zwölf Vorlagen und im Word-Export.
4. **Anschreiben nach DIN 5008:** In **Gestaltung → Format des Anschreibens** „DIN 5008 (Fensterumschlag)“ wählen. Die Anschrift steht im Adressfeld nach Form B (45 mm von oben, Text bei 25 mm vom linken Rand) und passt in Fensterumschläge DIN lang und C6. Darüber steht eine kleine Absenderzeile, das Datum rechts, am linken Rand Falz- und Lochmarken. Der Bewerbungscheck warnt bei mehr als sechs Anschriftzeilen. Die Word-Ausgabe bleibt einspaltig.
5. **Update per Klick:** Ist ein Update vorbereitet, erscheint unten rechts „Jetzt neu starten und aktualisieren“ (ebenso unter **Updates & Startcheck**). Restlos speichert alles, schließt sich und startet sofort mit der neuen Version.

Alle Neuerungen kommen über das normale Programmupdate; ein neues Installationspaket ist nicht nötig. Ältere Versionen können die Daten weiterhin öffnen (die neuen Optionen werden dort nicht angewendet).

## Neu in 0.10.1: Fehlerbehebungen

- **Flüssigeres Tippen:** Beim automatischen Speichern werden nur noch geänderte Dateien geschrieben. Anlagenkopien entstehen nur neu, wenn sich Anlagen, Seitenbearbeitung oder Originaldatei ändern. Anschreiben-, Lebenslauf- und Deckblatt-PDFs im Bewerbungsordner werden im Hintergrund erzeugt; beim Schließen wird alles vollständig gespeichert.
- **Word-Export:** Kein Abbruch mehr, wenn in Berufserfahrung oder Ausbildung mehrere Leerzeilen hintereinander stehen (auch im PDF entstehen dadurch keine leeren Überschriften mehr).
- **Datenrettung:** Ist `data.json` beschädigt, lädt Restlos automatisch `data.previous.json` oder die neueste Tageskopie unter `Sicherungen/Täglich/` und behält die beschädigte Datei als `data.defekt-….json`. `data.previous.json` enthält jetzt einen mindestens 15 Minuten älteren Stand; zusätzlich gibt es eine Tageskopie der Formulardaten (14 Tage).
- **Wiederherstellen** funktioniert auch, wenn die aktuellen Daten beschädigt sind. Die Sicherung vor der Wiederherstellung liegt jetzt unter `Sicherungen/`.
- **Sicheres Schließen:** Antwortet die Oberfläche nicht, fragt Restlos nach 8 Sekunden, ob das Fenster trotzdem geschlossen werden soll.
- **Textprüfung:** Keine falschen Vorschläge mehr bei „Ich hoffe das Beste“ oder „…, die die Abteilung“.
- **Bewerbungscheck:** Verständliche Abschnittsnamen statt interner Feldnamen. Der Firmenabgleich ignoriert Rechtsformen wie GmbH oder AG („Müller GmbH“ passt zu „Müller Logistik GmbH“).
- **Betreff ohne Position:** „Bewerbung“ statt „Bewerbung als “. Der E-Mail-Anhang heißt `Bewerbung_Vorname_Nachname.pdf`.
- **Speicherplatz:** Von den Sicherungen vor Updates bleiben die fünf neuesten erhalten. Vorbereitete Programmversionen werden auf die laufende, aktive und vorherige Version begrenzt (je etwa 1 GB). Wird dieselbe Datei (z. B. Foto oder Unterschrift) erneut ausgewählt, verwendet Restlos die vorhandene Kopie statt eines Duplikats.
- Automatische Tests unter `tests/` (`python3 -m pytest tests`).

## Neu in 0.10: Sechs Bereiche für die fertige Bewerbung

1. **Eigener Lebenslauf:** Unter „Bewerbung bearbeiten → Lebenslauf“ eine eigene Fassung aktivieren. Berufliche Inhalte werden aus dem Profil übernommen und danach unabhängig bearbeitet. Kontakt, persönliche Angaben, Foto und Unterschrift bleiben gemeinsame Profildaten. Eigene Stationen werden als Text mit Leerzeilen zwischen den Stationen bearbeitet. Beim Ausschalten bleibt die eigene Fassung für eine spätere Aktivierung gespeichert. „Neu aus Profil übernehmen“ ersetzt sie nach Bestätigung.
2. **Anlagen bearbeiten:** Anlagen per Ziehen oder Pfeilen sortieren. „Seiten bearbeiten“ öffnet Originalseiten als Vorschau; Seiten lassen sich drehen, entfernen und sortieren. Änderungen werden erst mit „Änderungen übernehmen“ gespeichert und gelten pro Bewerbung. „Zurücksetzen“ stellt alle Originalseiten wieder her. Es muss mindestens eine Seite erhalten bleiben; maximal 300 Seiten pro bearbeiteter Anlage. Die Original-PDF bleibt erhalten. Im Bewerbungsordner liegen nummerierte, bearbeitete Anlagenkopien.
3. **Bewerbungscheck:** Vor PDF-, Word- oder E-Mail-Export werden Pflichtangaben, mögliche Platzhalter, erkannte Zeiträume und Hinweise auf andere Firmennamen geprüft. Die tatsächliche Gesamtmappe wird erzeugt, ihre Seitenzahl und Dateigröße angezeigt; ab 5 MB erscheint ein Hinweis. „Zum Abschnitt“ führt zurück zur Eingabe. Du entscheidest nach der Prüfung über den Export. Der Firmenabgleich erkennt bekannte Namen aus anderen Bewerbungen und Abweichungen zur Empfängeranschrift, nicht beliebige falsche Namen.
4. **Dateiablage reparieren:** In „Dokumentablage → Fehlende Dateien suchen“ fehlende Originale aller Profile auflisten. „Datei wieder zuordnen“ kopiert eine von dir ausgewählte Datei desselben Typs an den hinterlegten Ort. Vorhandene Dateien werden nicht überschrieben. Speichern und Öffnen bleiben bei fehlenden Anlagen möglich; unvollständige Sicherungen/Updates werden weiterhin verhindert.
5. **Textprüfung:** Lokale Regeln finden doppelte Wörter/Sätze, überlange Sätze, allgemeine Formulierungen, mehrfache Leerzeichen und ausgewählte häufige Sprachfehler. Vorschläge einzeln übernehmen; die vorherige Fassung wird gesichert. Bei einer Übernahme wechselt das Anschreiben zur freien Textbearbeitung. Dies ist **keine vollständige Grammatikprüfung**; die bestehende Rechtschreibprüfung bleibt zusätzlich aktiv.
6. **Layout:** In „Gestaltung“ Textabstände (75–130 %), Fotogröße (50–100 %) und Seitenumbrüche vor Hauptabschnitten des Lebenslaufs einstellen. Die ausgewählte Vorlage und Farbe gelten für Anschreiben, Lebenslauf und Deckblatt. Word übernimmt Inhalte, Foto, Abstände und Seitenumbrüche in seiner einspaltigen Fassung.

**Komplette Mappe ansehen:** Unter „Anlagen“ oder „Prüfen & Export“ alle Seiten einschließlich bearbeiteter Anlagen einzeln durchblättern. Die Anzeige rendert jeweils eine Seite und hat dadurch nicht die Zwölf-Seiten-Grenze der normalen Editorvorschau.

Alle neuen Funktionen arbeiten lokal. Die eigene Lebenslauffassung und Anlagenbearbeitungen werden von älteren Restlos-Versionen nicht angewendet; für diese Funktionen bitte Version 0.10 oder neuer verwenden.

## Neu in 0.9.1: Größe der Unterschrift

Unter **Anschreiben → Deine Unterschrift** lässt sich die Größe je Bewerbung zwischen **25 und 150 %** einstellen. **Kompakt · 65 %** verkleinert sie mit einem Klick. Die PDF-Vorschau und der PDF-/Word-Export verwenden dieselbe proportionale Skalierung. Bestehende Bewerbungen behalten zunächst ihre bisherige Größe (100 %). Die Originalbilddatei bleibt unverändert.

## Seit 0.9: Drei Wege zur Unterschrift

Unter **Anschreiben → Deine Unterschrift → Unterschrift hinzufügen/ersetzen** öffnet sich die Auswahl:

- **Eintippen:** Namen eingeben, zwischen drei mitgelieferten Schriftarten wählen und eine Farbe festlegen. Die Vorschau wird sofort angepasst.
- **Zeichnen:** Mit Maus, Trackpad oder Finger auf der weißen Fläche unterschreiben. Einzelne Striche zurücknehmen oder die Fläche leeren. Farbauswahl ebenfalls verfügbar.
- **Hochladen:** Ein eigenes PNG-, JPG- oder WebP-Bild auswählen und übernehmen.

Eingetippte und gezeichnete Unterschriften werden erst mit **Unterschrift einfügen** als PNG in der lokalen Profilablage gespeichert. Abbrechen erhält die vorhandene Unterschrift. Beim Upload übernimmt die erfolgreiche Dateiauswahl das Bild. Die erzeugten Bilder erscheinen genauso wie hochgeladene Unterschriften in PDF und Word. Die Schriftarten werden lokal mitgeliefert; ihre Lizenzen stehen in `SIGNATURE-FONT-LICENSES.md`.

## Seit 0.8: Persönliche Angaben und Unterschrift

Unter **Mein Profil → Kontakt & Foto** lassen sich Geburtsdatum, Geburtsort, Familienstand und Staatsangehörigkeit freiwillig ergänzen. Nur ausgefüllte Angaben erscheinen im Lebenslauf – bei Seitenleisten unter **Persönliches**, bei einspaltigen Vorlagen bei den Kontaktdaten. Das gilt auch für den Word-Export. Anschreiben und Deckblatt übernehmen diese zusätzlichen Angaben nicht.

Unter **Anschreiben → Deine Unterschrift** kannst du ein Bild deiner Unterschrift (PNG, JPG oder WebP) hinzufügen. Verwende ein möglichst eng zugeschnittenes Bild mit transparentem oder weißem Hintergrund. Restlos kopiert das Original in die lokale Profilablage **Sonstiges**. Im Anschreiben erscheint es zwischen Grußformel und Name, auch im Word-Export und in der Gesamtmappe. Die Unterschrift lässt sich pro Bewerbung ausschalten. Beim Ersetzen oder Entfernen aus dem Profil bleibt das Original in der Ablage erhalten.

## Beispielbibliothek und Ausfüllhilfe

Unter **Anschreiben** öffnet **Passende Beispielantwort finden** die lokale Bibliothek mit 66 eigenständigen Vorschlägen für alle fünf Textabschnitte. Enthalten sind 15 Berufsfelder und acht Bewerbungssituationen, darunter Quereinstieg, Ausbildung, Praktikum und Wiedereinstieg. Suche und Filter lassen sich kombinieren; allgemeine Vorschläge bleiben dabei verfügbar.

Nach der Auswahl füllst du die benötigten Angaben in einzelnen Feldern aus. Unternehmen und Position werden, soweit vorhanden, vorausgefüllt. Der fertige Absatz bleibt frei bearbeitbar. Änderungen an den Angaben erzeugen den Absatz erneut. Unausgefüllte Platzhalter verhindern die Übernahme.

Vorhandene Texte werden standardmäßig ergänzt. Ersetzen ist ausdrücklich auswählbar und erfordert eine Bestätigung. Im Freitextmodus betrifft Ersetzen den gesamten Anschreibentext. Unter **Frühere Texte ansehen** bleiben bis zu zehn vorherige Fassungen verfügbar. Die Beispiele, Eingaben und der Verlauf werden lokal verarbeitet; es ist kein KI-Modell nötig.

## Automatische Updates ab Version 0.6

Für den Wechsel von 0.5 oder älter muss dieses DEB-Paket **einmalig** installiert werden. Danach ist die Updateprüfung standardmäßig aktiv. Unter **Updates & Startcheck** kannst du sie ausschalten oder eine Prüfung anstoßen.

Restlos lädt ausschließlich Programmupdates aus den öffentlichen Releases von https://github.com/jurkast/restlos-bewerbung. Beim Start und danach stündlich prüft es auf eine neuere Version. Signatur, Prüfsumme, Dateigröße, Programmkennung und Plattform müssen passen. Ein vollständiges Update wird im Benutzerverzeichnis vorbereitet und beim nächsten normalen Start aktiviert. Die laufende Arbeit wird nicht durch einen Neustart unterbrochen.

- Bewerbungsdaten bleiben unter `~/Documents/Restlos Bewerbung/`.
- Vor der Aktivierung entsteht dort unter **Sicherungen** eine vollständige lokale ZIP-Sicherung. Scheitert die Sicherung, wird das Update nicht aktiviert. Die fünf neuesten Sicherungen vor Updates bleiben erhalten; ältere werden automatisch entfernt.
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

## Lizenz

Restlos Bewerbung steht unter der **MIT-Lizenz** (siehe `LICENSE`): Nutzung, Veränderung und Weitergabe sind erlaubt, solange der Copyright- und Lizenzhinweis erhalten bleibt. Das Programm wird ohne Gewährleistung bereitgestellt. Die mitgelieferten Bibliotheken und Schriftarten behalten ihre eigenen Lizenzen: `THIRD-PARTY.md`, `SIGNATURE-FONT-LICENSES.md` und `lib/*dist-info/`.

Quellcode liegt im Programmordner.
