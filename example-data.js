// Eigene Formulierungsvorschläge von Restlos. Alle Daten bleiben lokal.
const answerExamples = [
  {
    "id": "ex001",
    "field": "motivation",
    "category": "Büro & Verwaltung",
    "situation": "Alle Situationen",
    "title": "Organisation im Alltag",
    "text": "Mich reizt es, Informationen zu ordnen und dafür zu sorgen, dass Termine und Absprachen zuverlässig zusammenpassen. Bei [Unternehmen] möchte ich diese Stärke besonders für [Aufgabe aus der Stellenanzeige] einsetzen."
  },
  {
    "id": "ex002",
    "field": "evidence",
    "category": "Büro & Verwaltung",
    "situation": "Alle Situationen",
    "title": "Anfragen sorgfältig bearbeiten",
    "text": "Bei [Arbeitgeber oder Projekt] habe ich [Art der Anfragen oder Vorgänge] bearbeitet. Ich habe die notwendigen Informationen mit [Beteiligte] abgestimmt und [konkreter eigener Beitrag]."
  },
  {
    "id": "ex003",
    "field": "motivation",
    "category": "Handwerk & Montage",
    "situation": "Alle Situationen",
    "title": "Sichtbare Ergebnisse",
    "text": "Ich arbeite gerne praktisch und sehe am Ende des Tages, was ich geschaffen habe. An der Stelle als [Beruf / Position] interessiert mich besonders [Arbeitsbereich oder Material]."
  },
  {
    "id": "ex004",
    "field": "evidence",
    "category": "Handwerk & Montage",
    "situation": "Alle Situationen",
    "title": "Sorgfalt am Werkstück",
    "text": "Bei [Betrieb oder Projekt] habe ich [handwerkliche Aufgabe] ausgeführt. Dabei habe ich [konkrete Maßnahme für Genauigkeit oder Sicherheit] beachtet. Das Ergebnis war [tatsächliches Ergebnis]."
  },
  {
    "id": "ex005",
    "field": "motivation",
    "category": "Pflege & Betreuung",
    "situation": "Alle Situationen",
    "title": "Menschen begleiten",
    "text": "Ich möchte Menschen bei [konkreter Unterstützungsbedarf] begleiten und dabei auf ihre individuellen Bedürfnisse eingehen. An Ihrer Einrichtung spricht mich [konkreter Bezug zur Einrichtung] an."
  },
  {
    "id": "ex006",
    "field": "evidence",
    "category": "Pflege & Betreuung",
    "situation": "Alle Situationen",
    "title": "Verantwortungsbewusst unterstützen",
    "text": "In [Einrichtung oder Tätigkeit] habe ich [Aufgabe im eigenen Verantwortungsbereich] übernommen. In einer Situation mit [konkrete Herausforderung] habe ich [eigenes Vorgehen] und dabei [wichtige Abstimmung] berücksichtigt."
  },
  {
    "id": "ex007",
    "field": "motivation",
    "category": "Verkauf & Einzelhandel",
    "situation": "Alle Situationen",
    "title": "Kunden verständlich beraten",
    "text": "Im Verkauf gefällt mir der direkte Kontakt zu Menschen. Ich möchte Kunden dabei helfen, [konkretes Anliegen der Kundschaft] zu lösen. Ihr Sortiment im Bereich [Sortiment] interessiert mich besonders."
  },
  {
    "id": "ex008",
    "field": "evidence",
    "category": "Verkauf & Einzelhandel",
    "situation": "Alle Situationen",
    "title": "Bedarf erkennen",
    "text": "Bei [Arbeitgeber oder Praktikum] habe ich Kunden zu [Produkt oder Anliegen] beraten. Ich habe zunächst [Vorgehen zur Bedarfsermittlung] und anschließend [passende Lösung] vorgeschlagen."
  },
  {
    "id": "ex009",
    "field": "motivation",
    "category": "Lager & Logistik",
    "situation": "Alle Situationen",
    "title": "Abläufe zuverlässig unterstützen",
    "text": "Mich interessiert, wie Waren durch gute Planung zur richtigen Zeit am richtigen Ort ankommen. Als [Beruf / Position] möchte ich bei [Unternehmen] besonders im Bereich [Aufgabenbereich] mitarbeiten."
  },
  {
    "id": "ex010",
    "field": "evidence",
    "category": "Lager & Logistik",
    "situation": "Alle Situationen",
    "title": "Waren sorgfältig bearbeiten",
    "text": "Bei [Betrieb oder Praktikum] habe ich [Lageraufgabe] übernommen. Mit [tatsächlich verwendetes Hilfsmittel oder System] habe ich [konkretes Vorgehen] und so [belegbarer Beitrag] erreicht."
  },
  {
    "id": "ex011",
    "field": "motivation",
    "category": "IT & Software",
    "situation": "Alle Situationen",
    "title": "Nützliche Lösungen entwickeln",
    "text": "Ich möchte technische Lösungen entwickeln, die [konkretes Problem der Nutzer] vereinfachen. Die Aufgabe bei [Unternehmen] interessiert mich, weil sie [Technologie oder Aufgabenfeld] mit [fachlicher Bezug] verbindet."
  },
  {
    "id": "ex012",
    "field": "evidence",
    "category": "IT & Software",
    "situation": "Alle Situationen",
    "title": "Eigenen Projektbeitrag zeigen",
    "text": "Für [Projekt] habe ich mit [tatsächlich eingesetzte Technologie] eine Lösung für [Problem] umgesetzt. Mein eigener Beitrag war [eigener Anteil]. Überprüft habe ich die Lösung durch [Test oder Rückmeldung]."
  },
  {
    "id": "ex013",
    "field": "motivation",
    "category": "Gastronomie & Hotel",
    "situation": "Alle Situationen",
    "title": "Gastfreundschaft im Alltag",
    "text": "Mir gefällt es, Gästen durch aufmerksamen Service einen angenehmen Aufenthalt zu ermöglichen. An Ihrem Haus interessiert mich besonders [Angebot oder Arbeitsbereich]."
  },
  {
    "id": "ex014",
    "field": "evidence",
    "category": "Gastronomie & Hotel",
    "situation": "Alle Situationen",
    "title": "Bei viel Betrieb den Überblick behalten",
    "text": "Bei [Betrieb oder Veranstaltung] war ich für [konkrete Aufgabe] zuständig. Auch bei [Situation mit hohem Arbeitsaufkommen] habe ich [eigenes Vorgehen] und mich mit [Team oder zuständige Person] abgestimmt."
  },
  {
    "id": "ex015",
    "field": "motivation",
    "category": "Reinigung & Hauswirtschaft",
    "situation": "Alle Situationen",
    "title": "Sorgfalt und Wohlbefinden",
    "text": "Ich arbeite gerne sorgfältig und möchte dazu beitragen, dass sich Menschen in gepflegten Räumen wohlfühlen. Die Tätigkeit im Bereich [Einsatzbereich] bei [Unternehmen] spricht mich deshalb an."
  },
  {
    "id": "ex016",
    "field": "evidence",
    "category": "Reinigung & Hauswirtschaft",
    "situation": "Alle Situationen",
    "title": "Nachvollziehbare Arbeitsabläufe",
    "text": "Bei [Arbeitgeber oder Tätigkeit] habe ich [konkrete Reinigungs- oder Versorgungsaufgabe] erledigt. Dabei habe ich [angewandter Ablauf oder Vorgabe] eingehalten und [konkretes Beispiel für Sorgfalt]."
  },
  {
    "id": "ex017",
    "field": "motivation",
    "category": "Produktion & Fertigung",
    "situation": "Alle Situationen",
    "title": "Interesse an der Herstellung",
    "text": "Mich interessiert die Herstellung von [Produkt oder Produktgruppe]. Besonders gerne möchte ich bei [Unternehmen] an [konkreter Fertigungsaufgabe] mitarbeiten und mich in die Abläufe einarbeiten."
  },
  {
    "id": "ex018",
    "field": "evidence",
    "category": "Produktion & Fertigung",
    "situation": "Alle Situationen",
    "title": "Qualität im eigenen Arbeitsschritt",
    "text": "Bei [Betrieb oder Praktikum] habe ich [Fertigungsschritt] durchgeführt. Ich habe [konkrete Qualitätskontrolle] vorgenommen und bei [Abweichung oder Rückfrage] mit [zuständige Person] Rücksprache gehalten."
  },
  {
    "id": "ex019",
    "field": "motivation",
    "category": "Erziehung & Soziales",
    "situation": "Alle Situationen",
    "title": "Entwicklung begleiten",
    "text": "Ich möchte Menschen dabei unterstützen, [konkretes pädagogisches oder soziales Ziel] zu erreichen. Ihr Ansatz zu [tatsächlich bekanntes Konzept] interessiert mich, weil [persönlicher fachlicher Bezug]."
  },
  {
    "id": "ex020",
    "field": "evidence",
    "category": "Erziehung & Soziales",
    "situation": "Alle Situationen",
    "title": "Bedürfnisse berücksichtigen",
    "text": "Im Rahmen von [Tätigkeit oder Praktikum] habe ich [Angebot oder Aufgabe] begleitet. Dabei habe ich [eigenes Vorgehen] an [Bedürfnisse der Zielgruppe] angepasst und mich mit [Team oder Fachkraft] abgestimmt."
  },
  {
    "id": "ex021",
    "field": "motivation",
    "category": "Technik & Elektronik",
    "situation": "Alle Situationen",
    "title": "Technische Zusammenhänge verstehen",
    "text": "Mich begeistert, technische Zusammenhänge zu verstehen und Fehler systematisch einzugrenzen. Bei der Stelle als [Beruf / Position] interessiert mich besonders [Anlage, System oder Aufgabenfeld]."
  },
  {
    "id": "ex022",
    "field": "evidence",
    "category": "Technik & Elektronik",
    "situation": "Alle Situationen",
    "title": "Systematisch vorgehen",
    "text": "Bei [Projekt oder Betrieb] habe ich [technische Aufgabe im eigenen Verantwortungsbereich] bearbeitet. Ich bin dabei mit [Methode oder Werkzeug] vorgegangen und habe [tatsächliches Ergebnis] dokumentiert."
  },
  {
    "id": "ex023",
    "field": "motivation",
    "category": "Fahrdienst & Transport",
    "situation": "Alle Situationen",
    "title": "Verlässlich unterwegs",
    "text": "An der Tätigkeit als [Beruf / Position] gefällt mir die Verbindung aus selbstständigem Arbeiten und verlässlichem Service. Besonders interessiert mich [Art der Fahrten oder Transporte] bei [Unternehmen]."
  },
  {
    "id": "ex024",
    "field": "evidence",
    "category": "Fahrdienst & Transport",
    "situation": "Alle Situationen",
    "title": "Planung und Abstimmung",
    "text": "In [bisherige Tätigkeit] habe ich [Transport- oder Planungsaufgabe] übernommen. Bei [konkrete Herausforderung] habe ich [eigenes Vorgehen] und [relevante Abstimmung] berücksichtigt."
  },
  {
    "id": "ex025",
    "field": "motivation",
    "category": "Marketing & Gestaltung",
    "situation": "Alle Situationen",
    "title": "Zielgruppen erreichen",
    "text": "Ich möchte Inhalte gestalten, die [Zielgruppe] verständlich erreichen. An [Unternehmen] interessiert mich besonders [Produkt oder Kommunikationsaufgabe], weil [konkreter eigener Bezug]."
  },
  {
    "id": "ex026",
    "field": "evidence",
    "category": "Marketing & Gestaltung",
    "situation": "Alle Situationen",
    "title": "Arbeit anhand von Feedback verbessern",
    "text": "Für [Projekt oder Auftrag] habe ich [Inhalt oder Gestaltung] entwickelt. Mein Anteil umfasste [eigene Aufgaben]. Auf Grundlage von [Feedback oder tatsächliche Auswertung] habe ich [konkrete Verbesserung] vorgenommen."
  },
  {
    "id": "ex027",
    "field": "motivation",
    "category": "Buchhaltung & Finanzen",
    "situation": "Alle Situationen",
    "title": "Genauigkeit mit Zahlen",
    "text": "Mir liegt es, Zahlen sorgfältig zu prüfen und Zusammenhänge nachvollziehbar darzustellen. Bei [Unternehmen] möchte ich diese Arbeitsweise für [konkrete Aufgabe] einsetzen."
  },
  {
    "id": "ex028",
    "field": "evidence",
    "category": "Buchhaltung & Finanzen",
    "situation": "Alle Situationen",
    "title": "Unstimmigkeiten klären",
    "text": "Bei [Arbeitgeber oder Ausbildung] habe ich [konkrete kaufmännische Aufgabe] mit [tatsächlich verwendetes Programm] bearbeitet. Unstimmigkeiten habe ich durch [eigenes Vorgehen] geklärt und [Ergebnis] dokumentiert."
  },
  {
    "id": "ex029",
    "field": "motivation",
    "category": "Kundenservice & Empfang",
    "situation": "Alle Situationen",
    "title": "Anliegen verständlich klären",
    "text": "Ich möchte Menschen bei ihren Anliegen weiterhelfen und Informationen verständlich vermitteln. Die Aufgabe bei [Unternehmen] interessiert mich besonders wegen [konkreter Aufgabenbereich]."
  },
  {
    "id": "ex030",
    "field": "evidence",
    "category": "Kundenservice & Empfang",
    "situation": "Alle Situationen",
    "title": "Eine konkrete Kundensituation",
    "text": "Bei [Arbeitgeber oder Tätigkeit] habe ich [Art der Kundenanfragen] bearbeitet. In einer Situation mit [konkretes Anliegen] habe ich [eigenes Vorgehen] und dadurch [tatsächliches Ergebnis] erreicht."
  },
  {
    "id": "ex031",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Ausbildung & Berufseinstieg",
    "title": "Passender Einstieg: Ausbildung & Berufseinstieg",
    "text": "Ich möchte eine Ausbildung als [Beruf / Position] beginnen, weil mich [konkrete Tätigkeit] interessiert. Bei [Einblick in den Beruf] habe ich erlebt, wie [persönliche Beobachtung]. Das hat meinen Berufswunsch bestärkt."
  },
  {
    "id": "ex032",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Ausbildung & Berufseinstieg",
    "title": "Erfahrung zeigen: Ausbildung & Berufseinstieg",
    "text": "In [Schulprojekt oder Praktikum] habe ich [Aufgabe] übernommen. Dabei habe ich gelernt, [konkret erlernte Fähigkeit]. Diese Erfahrung möchte ich in der Ausbildung weiter ausbauen."
  },
  {
    "id": "ex033",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Praktikum",
    "title": "Passender Einstieg: Praktikum",
    "text": "Mit einem Praktikum im Bereich [Bereich] möchte ich herausfinden, wie [konkrete berufliche Aufgabe] im Alltag umgesetzt wird. Bei [Unternehmen] interessiert mich dafür besonders [Aufgabe oder Abteilung]."
  },
  {
    "id": "ex034",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Praktikum",
    "title": "Erfahrung zeigen: Praktikum",
    "text": "Aus [Studium, Schule oder eigenem Projekt] kenne ich bereits [Grundkenntnis]. Angewendet habe ich sie bei [konkretes Beispiel]. Im Praktikum möchte ich darauf aufbauen."
  },
  {
    "id": "ex035",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Quereinstieg",
    "title": "Passender Einstieg: Quereinstieg",
    "text": "Ich möchte mich beruflich in Richtung [neuer Bereich] verändern. Ausschlaggebend dafür ist [konkreter Beweggrund]. Die Stelle als [Beruf / Position] verbindet mein Interesse an [Aufgabe] mit meiner Erfahrung in [übertragbarer Bereich]."
  },
  {
    "id": "ex036",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Quereinstieg",
    "title": "Erfahrung zeigen: Quereinstieg",
    "text": "Aus meiner bisherigen Tätigkeit in [Bereich] bringe ich [übertragbare Fähigkeit] mit. Bei [konkrete Situation] habe ich [eigener Beitrag]. Für den neuen Aufgabenbereich habe ich mich durch [tatsächliche Vorbereitung] vorbereitet."
  },
  {
    "id": "ex037",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Wiedereinstieg",
    "title": "Passender Einstieg: Wiedereinstieg",
    "text": "Nach einer beruflichen Pause möchte ich wieder im Bereich [Bereich] arbeiten. Besonders ansprechend finde ich an Ihrer Stelle [konkrete Aufgabe]. Dabei möchte ich an meine Erfahrung in [bisheriger Schwerpunkt] anknüpfen."
  },
  {
    "id": "ex038",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Wiedereinstieg",
    "title": "Erfahrung zeigen: Wiedereinstieg",
    "text": "Vor meiner beruflichen Pause habe ich [relevante Aufgabe] übernommen. Meine Kenntnisse in [Bereich] habe ich inzwischen durch [tatsächliche Auffrischung oder Weiterbildung] aktualisiert."
  },
  {
    "id": "ex039",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Ohne Berufserfahrung",
    "title": "Passender Einstieg: Ohne Berufserfahrung",
    "text": "Ich möchte in den Bereich [Bereich] einsteigen, weil [konkretes Interesse]. Erste Anknüpfungspunkte bietet mir [Schule, privates Projekt oder Ehrenamt]. Bei Ihnen interessiert mich besonders [Aufgabe aus der Anzeige]."
  },
  {
    "id": "ex040",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Ohne Berufserfahrung",
    "title": "Erfahrung zeigen: Ohne Berufserfahrung",
    "text": "Auch ohne bisherige Berufserfahrung konnte ich bei [Projekt, Schule oder Ehrenamt] zeigen, dass ich [passende Fähigkeit]. Konkret habe ich [eigener Beitrag]."
  },
  {
    "id": "ex041",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Initiativbewerbung",
    "title": "Passender Einstieg: Initiativbewerbung",
    "text": "Ich möchte Ihr Team im Bereich [Bereich] unterstützen. Auf [Unternehmen] bin ich durch [tatsächlicher Kontaktpunkt] aufmerksam geworden. Besonders interessiert mich [konkrete Tätigkeit oder Angebot]."
  },
  {
    "id": "ex042",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Initiativbewerbung",
    "title": "Erfahrung zeigen: Initiativbewerbung",
    "text": "Für eine Mitarbeit im Bereich [Bereich] bringe ich Erfahrung mit [relevante Aufgabe] mit. Ein Beispiel ist [Projekt oder Tätigkeit], bei dem ich [eigener Beitrag]."
  },
  {
    "id": "ex043",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Teilzeit & Minijob",
    "title": "Passender Einstieg: Teilzeit & Minijob",
    "text": "Ich suche eine Tätigkeit in Teilzeit im Bereich [Bereich]. Ihre Aufgabe als [Beruf / Position] interessiert mich besonders, weil [inhaltlicher Bezug zur Tätigkeit]."
  },
  {
    "id": "ex044",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Teilzeit & Minijob",
    "title": "Erfahrung zeigen: Teilzeit & Minijob",
    "text": "Bei [bisherige Tätigkeit oder Projekt] habe ich [passende Aufgabe] übernommen. Dabei konnte ich meine Stärke in [Fähigkeit] einsetzen, indem ich [konkretes Beispiel]."
  },
  {
    "id": "ex045",
    "field": "motivation",
    "category": "Alle Berufe",
    "situation": "Mit Berufserfahrung",
    "title": "Passender Einstieg: Mit Berufserfahrung",
    "text": "In meiner bisherigen Tätigkeit habe ich meinen Schwerpunkt auf [Schwerpunkt] gelegt. Nun möchte ich meine Erfahrung für [gewünschte Aufgabe] einsetzen. Genau diese Möglichkeit sehe ich in Ihrer Ausschreibung."
  },
  {
    "id": "ex046",
    "field": "evidence",
    "category": "Alle Berufe",
    "situation": "Mit Berufserfahrung",
    "title": "Erfahrung zeigen: Mit Berufserfahrung",
    "text": "Bei [Arbeitgeber] war ich für [Verantwortungsbereich] zuständig. Für [konkrete Herausforderung] habe ich [eigene Maßnahme] umgesetzt. Dies führte zu [nachweisbares Ergebnis ohne erfundene Kennzahl]."
  },
  {
    "id": "ex047",
    "field": "fit",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Aufgabe aus der Anzeige",
    "text": "An Ihrer Ausschreibung spricht mich besonders [konkrete Aufgabe] an. Meine Erfahrung mit [passende Erfahrung] möchte ich dafür einsetzen, [realistischer eigener Beitrag]."
  },
  {
    "id": "ex048",
    "field": "fit",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Produkt oder Leistung",
    "text": "Ihr Angebot im Bereich [Produkt oder Leistung] interessiert mich, weil [konkreter persönlicher oder fachlicher Bezug]. Als [Beruf / Position] möchte ich dazu beitragen, [passender Beitrag zur ausgeschriebenen Aufgabe]."
  },
  {
    "id": "ex049",
    "field": "fit",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Arbeitsweise",
    "text": "Auf [Informationsquelle] beschreiben Sie [konkrete Arbeitsweise des Unternehmens]. Das passt zu meiner Erfahrung mit [eigene Arbeitsweise mit Beispiel]."
  },
  {
    "id": "ex050",
    "field": "fit",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Persönlicher Kontakt",
    "text": "Im Gespräch mit [Ansprechperson] am [Datum oder Anlass] habe ich mehr über [Aufgabe oder Team] erfahren. Besonders [konkreter Gesprächsinhalt] hat mein Interesse an einer Mitarbeit bestärkt."
  },
  {
    "id": "ex051",
    "field": "fit",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Regionaler Bezug",
    "text": "Durch [konkreter Kontakt oder Beobachtung vor Ort] bin ich auf Ihr Unternehmen aufmerksam geworden. Besonders interessiert mich Ihre Tätigkeit im Bereich [Bereich], zu der ich [passende Erfahrung oder Interesse] mitbringe."
  },
  {
    "id": "ex052",
    "field": "fit",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Lernmöglichkeiten",
    "text": "Die in Ihrer Anzeige genannte Möglichkeit, [konkretes Lern- oder Aufgabenfeld] kennenzulernen, spricht mich besonders an. Erste Grundlagen bringe ich durch [tatsächliche Vorkenntnisse] mit."
  },
  {
    "id": "ex053",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Fester Starttermin",
    "text": "Ein Einstieg ist mir ab dem [möglicher Starttermin] möglich."
  },
  {
    "id": "ex054",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Kündigungsfrist",
    "text": "Meine Kündigungsfrist beträgt [tatsächliche Kündigungsfrist]. Den möglichen Eintrittstermin stimme ich gerne mit Ihnen ab."
  },
  {
    "id": "ex055",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Start nach Absprache",
    "text": "Den Eintrittstermin vereinbare ich gerne mit Ihnen im persönlichen Gespräch."
  },
  {
    "id": "ex056",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Teilzeitumfang",
    "text": "Ich möchte mit [gewünschte Wochenstunden] Wochenstunden arbeiten. An [mögliche Arbeitstage oder Zeiträume] bin ich verfügbar."
  },
  {
    "id": "ex057",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Praktikumszeitraum",
    "text": "Für das Praktikum stehe ich Ihnen vom [Beginn] bis zum [Ende] zur Verfügung."
  },
  {
    "id": "ex058",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Ausbildungsbeginn",
    "text": "Für den von Ihnen genannten Ausbildungsbeginn am [Ausbildungsbeginn] stehe ich zur Verfügung."
  },
  {
    "id": "ex059",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Gehaltswunsch – nur wenn verlangt",
    "text": "Meine Gehaltsvorstellung liegt bei [Betrag] Euro brutto jährlich bei [Wochenstunden] Wochenstunden."
  },
  {
    "id": "ex060",
    "field": "availability",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Stundenlohn – nur wenn verlangt",
    "text": "Meine Vorstellung liegt bei einem Stundenlohn von [Betrag] Euro brutto."
  },
  {
    "id": "ex061",
    "field": "closing",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Kurz und freundlich",
    "text": "Ich freue mich darauf, Sie in einem persönlichen Gespräch kennenzulernen."
  },
  {
    "id": "ex062",
    "field": "closing",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Beitrag besprechen",
    "text": "Gerne erläutere ich Ihnen im Gespräch, wie ich Ihr Team bei [konkrete Aufgabe] unterstützen kann."
  },
  {
    "id": "ex063",
    "field": "closing",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Erfahrung vertiefen",
    "text": "Über meine Erfahrungen mit [relevanter Bereich] und die Aufgaben in Ihrem Team spreche ich gerne persönlich mit Ihnen."
  },
  {
    "id": "ex064",
    "field": "closing",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Ausbildung",
    "text": "Ich freue mich über die Gelegenheit, Ihnen meine Motivation für die Ausbildung persönlich vorzustellen."
  },
  {
    "id": "ex065",
    "field": "closing",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Offene Fragen klären",
    "text": "Gerne beantworte ich Ihre Fragen zu meinem Werdegang in einem persönlichen Gespräch."
  },
  {
    "id": "ex066",
    "field": "closing",
    "category": "Alle Berufe",
    "situation": "Alle Situationen",
    "title": "Initiativbewerbung",
    "text": "Ich freue mich über ein Gespräch zu möglichen Einsatzbereichen in Ihrem Team."
  }
];
