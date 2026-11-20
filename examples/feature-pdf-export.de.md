# PDF-Export der Monatsberichte für das Controlling

<!-- canvas-meta: branch=feature/pdf-export; lang=de; phase=final; created=2026-11-20; updated=2026-11-20 -->

## Maßnahme
- PDF-Export der Monatsberichte

## Beschreibung
- Button „Als PDF exportieren“ auf der Berichtsseite
- PDF serverseitig aus der vorhandenen Vorlage erzeugen
- Ziel: Controlling kann Berichte ohne Screenshots archivieren

## Hintergrund
- Das Controlling macht heute Screenshots für das Prüfarchiv
- Screenshots sind unvollständig und kosten ca. 30 Minuten pro Monat

## Mehrwert
- Spart ca. 30 Minuten pro Monat im Controlling

## Stakeholder
- Beteiligt: Controlling, Datenschutz
- Betroffen: alle Berichtsnutzer

## IT
- Node.js-Backend (package.json)

## Kritische Erfolgsfaktoren
- PDF entspricht der Bildschirmansicht

## Ressourcen
- 3 Personentage Entwicklung

## Umsetzung
- Zeitlicher Horizont: 2/5 – ein Sprint
- Komplexität: 2/5 – Vorlage wird wiederverwendet
- Kosten: 1/5 – keine neuen Lizenzen
- Risiko: 2/5 – Renderunterschiede zwischen Umgebungen

## Erforderliche Aktivitäten zur Umsetzung
- [x] Export-Endpunkt umsetzen — AI — nächster Schritt
- [ ] Review — Anna (Controlling) — vor dem Merge

## Offene Punkte
- 
