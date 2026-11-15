# Import quotidien des événements

Procédure suivie chaque matin par la tâche planifiée « Import agenda Alsace ».

## Sources

| id (`sources/<id>.json`) | Site | Pages à lire | Remarques |
|---|---|---|---|
| `visit-alsace` | Visit Alsace | https://www.visit.alsace/agenda-sorties-evenements/ puis `/page/2/`, `/page/3/` | La liste donne titre, catégorie, commune ; la date est celle de l'en-tête du groupe. |
| `coze` | Coze | https://www.coze.fr/agenda/ puis `?paged=2` (+ bloc « Les expositions du moment ») | Donne horaire, lieu, prix, gratuit. |
| `pass-alsace` | Pass'Alsace | https://www.pass-alsace.com/agenda-des-evenements puis `/page/2`, `/page/3`, `/page/4` | Donne dates, horaire, lieu complet. |
| `tourisme-colmar` | Office de tourisme de Colmar | https://www.tourisme-colmar.com/fr/loisirs-fr/evenements/agenda puis `?product_codes=&item_template=carte2&brpa=2` | Une ligne par jour : fusionner les lignes d'une même fiche en plage de dates. |
| `saintlouis-tourisme` | Saint-Louis Tourisme | https://www.saintlouis-tourisme.fr/sortir/agenda/ puis `/page/2/`, `/page/3/` | Une ligne par occurrence (`/occ/N/`) : fusionner en plage de dates. Pays FR. |
| `bs-ch` | Canton de Bâle-Ville | https://www.bs.ch/veranstaltungen puis `?page=1` | Pays CH. Écarter les réunions administratives et ventes aux enchères. |
| `localcities-bale` | Localcities (Bâle) | https://www.localcities.ch/de/veranstaltungen/basel/3681 | Événements du jour seulement. Pays CH. |
| `visit-freiburg` | Visit Freiburg | https://visit.freiburg.de/fr/evenements/top-10-des-evenements | Calendrier complet masqué par les cookies. Pays DE. |
| `weil-am-rhein` | Ville de Weil am Rhein | https://www.weil-am-rhein.de/start/kultur/veranstaltungskalender | Pays DE. |
| `bs-ch-grands` | Bâle – grands événements | https://www.bs.ch/fr/schwerpunkte/portrait/evenements-bale | Pays CH. |
| `myswitzerland-bale` | MySwitzerland (Bâle) | https://www.myswitzerland.com/fr-fr/decouvrir/manifestations/manifestations-rechercher/-/bale/ (puis `?p=2`) | Pays CH. Écarter les expositions permanentes. |
| `swissactivities-bale` | Swiss Activities (Bâle) | https://www.swissactivities.com/fr-fr/ville-de-b-le/evenements/ | 20 premiers seulement. Pays CH. |
| `baselland-tourismus` | Baselland Tourismus | https://www.baselland-tourismus.ch/fr/calendrier-des-evenements | Page 1 seulement. Pays CH. |
| `meer-bale` | Meer (expositions à Bâle) | https://www.meer.com/fr/calendar?country_id=50&locality_id=365660 | Expositions en cours. Pays CH. |
| `denkmal-bale` | Denkmal (concerts et soirées) | https://denkmal.org/fr/basel/AAAA-MM-JJ, aujourd'hui + 6 jours | Pays CH, sauf le lieu « Burghof » qui est à Lörrach (commune Lörrach, pays DE). |
| `oazis-lorrach` | Oazis (Lörrach) | https://oazis.app/sorties/lorrach | Garder seulement Lörrach et ses quartiers. Pays DE. |
| `dreilaendermuseum` | Dreiländermuseum Lörrach | https://www.dreilaendermuseum.eu/de/anschauen/veranstaltungen/ | Pays DE. |
| `songkick-lorrach` | Songkick (Marktplatz Lörrach) | https://www.songkick.com/fr/venues/886706-marktplatz-lorrach | Pays DE. |
| `oazis-freiburg` | Oazis (Fribourg) | https://oazis.app/sorties/freiburg-im-breisgau | Pas de lien par événement. Pays DE. Écarter les cours de langue. |
| `foretnoire-magique` | Forêt-Noire magique | https://www.foretnoire-magique.fr/lexperience/evenements | Pays DE. Garder le sud de la Forêt-Noire (Fribourg, Hochschwarzwald, Bad Dürrheim). Années parfois absentes. |
| `fever-freiburg` | Fever (Fribourg) | https://feverup.com/fr/freiburg-im-breisgau | Garder les concerts (Fribourg, Colmar) et spectacles proches ; écarter excursions, billets de musée, jeux de piste. `pays` par événement. |
| `fred-info` | FRED (transfrontalier) | https://fred.info/fr/evenements/ | Premier bloc seulement. Écarter permanences, webinaires et réunions administratives. |
| `made-in-alsace` | Made in Alsace | https://www.madeinalsace.com/les-evenements-en-alsace/mulhouse/ et `/colmar/` | Liste chargée en JavaScript : laisser `events: []` tant qu'aucune donnée n'est lisible. |

## Format d'un fichier source

```json
{"source":"coze","nom":"Coze","pays":"FR","lu_le":"AAAA-MM-JJ","pages":["…"],"note":"…",
 "events":[{"titre":"…","date_debut":"AAAA-MM-JJ","date_fin":null,"horaires":null,"lieu":null,
            "commune":"…","categorie":"…","prix":null,"url":"https://…",
            "description":"une phrase reprise de la page, ou null"}]}
```

`description` est affichée dans la fiche détaillée de l'appli ; sans elle, la fiche montre un résumé automatique.

Ne rien inventer : un champ absent de la page reste `null`. Si une source ne répond pas, garder l'ancien fichier (et donc son `lu_le`).

## Étapes

1. Lire chaque source (agent web-fetch : les sites sont bloqués en accès direct depuis le conteneur).
2. Réécrire `sources/<id>.json` pour chaque source lue.
3. Traduire : pour chaque nouveau titre qui n'est pas en français (sources CH et DE surtout), ajouter dans `traductions.json` → `titres` la ligne « titre original exact » : « titre en français ». Garder tels quels les noms propres (groupes, artistes, lieux). Pour les mots de catégorie, compléter `mots`. La page affiche le titre français et garde le titre original dans la fiche (et dans la recherche).
4. `python3 merge.py` : écarte les événements terminés, fusionne les doublons (même commune, titres proches, dates qui se recouvrent), garde toutes les sources de chaque événement, écrit `events.json`.
5. Copier `events.json` dans le dossier de publication et republier `agenda-alsace.html` avec `events.json` (même URL : https://claude.ai/artifact/25j8WAnKKJosAPWqn4cfZn).
6. Ajouter dans la table `GEO` de la page les coordonnées des nouvelles communes, sinon le rayon les ignore.

Testés et non retenus (15/11/2026) : basel.com et tempslibre.ch (refusés), infomaniak.events (le lien du 15/11 vise Fribourg en Suisse) et visit-bw.com et le calendrier de visit.freiburg.de (liste chargée en JavaScript ou derrière les cookies), basellife.com (vérification anti-robot), bandsintown (interdit aux robots), infoconcert (refusé), eventbrite (pas de dates, villes mélangées), loerrach.de (JavaScript). Breisach : aucun agenda trouvé.
Piste : oazis.app a aussi des pages /sorties/<ville> pour d'autres villes.
