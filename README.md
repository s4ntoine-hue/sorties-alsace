# Sorties en Alsace

Agenda des sorties en Alsace et dans les villes frontalières (Bâle, Lörrach, Fribourg-en-Brisgau), réuni depuis plus de 20 agendas en ligne.

Site : https://s4ntoine-hue.github.io/sorties-alsace/

- `index.html` : la page (charge `events.json`).
- `sources/*.json` : un fichier par agenda source.
- `merge.py` : fusionne les sources, retire les doublons et écrit `events.json`.
- `traductions.json` : titres allemands/anglais traduits en français.
- `IMPORT.md` : procédure de mise à jour quotidienne.
