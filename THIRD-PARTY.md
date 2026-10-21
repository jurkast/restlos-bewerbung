# Bibliotheken

Die Anwendung verwendet unveränderte, dynamisch geladene Drittanbieter-Bibliotheken. Die mitgelieferten Lizenztexte sind in den jeweiligen Paketverzeichnissen und `*.dist-info/licenses/` enthalten.

- PySide6 / Qt: LGPL-3.0/GPL-3.0 und weitere komponentenabhängige Lizenzen. https://www.qt.io/licensing/open-source-lgpl-obligations ; Quellcode: https://code.qt.io/ ; Version 6.12.0. Bibliotheken können im Verzeichnis lib ersetzt werden.
- ReportLab: BSD-Lizenz. https://www.reportlab.com/
- pypdf: BSD-3-Clause. https://github.com/py-pdf/pypdf
- Pillow: HPND und Abhängigkeiten. https://python-pillow.org/
- libxcb-cursor: MIT/X11. Das Ubuntu-Copyright-Dokument ist im Verzeichnis native enthalten; Quellpaket: https://launchpad.net/ubuntu/+source/xcb-util-cursor/0.1.4-1build1

Poppler wird als installiertes Systemprogramm aufgerufen und ist nicht in diesem Paket gebündelt.

- Hunspell: Systembibliothek `libhunspell-1.7-0`, MPL/GPL/LGPL je nach gewählter Lizenz. https://hunspell.github.io/
- Deutsches Hunspell-Wörterbuch: Systempaket `hunspell-de-de`; Lizenz- und Urheberhinweise in `/usr/share/doc/hunspell-de-de/copyright`. Das Wörterbuch wird nicht im Anwendungspaket gebündelt.

- python-docx: MIT. https://github.com/python-openxml/python-docx ; Lizenz in lib/python_docx-*.dist-info/licenses/.
- lxml: BSD und Lizenzen der enthaltenen libxml2/libxslt-Komponenten. https://lxml.de/ ; Lizenztexte im Paket.
- Tesseract: Apache-2.0, als Systemprogramm aufgerufen. https://github.com/tesseract-ocr/tesseract ; Sprachdaten werden über die Systempakete installiert.

## Schriften für die PDF-Vorlagen (`fonts/`)

- **Inter** – Copyright (c) 2016 The Inter Project Authors, SIL Open Font License 1.1 (`fonts/Inter-LICENSE.txt`), https://github.com/rsms/inter
- **Source Serif 4** – Copyright 2014–2023 Adobe, SIL Open Font License 1.1 (`fonts/SourceSerif4-LICENSE.md`), https://github.com/adobe-fonts/source-serif
