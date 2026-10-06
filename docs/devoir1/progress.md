# Progress — Devoir 1

> Historique du dépôt `devoir1` (commits du Devoir 1, dates fournies pour cette mise à jour).

| Commit | Date | Message |
|---|---|---|
| 80f87ec | 2026-09-30 | feat: ajouter le code Devoir1 (detection pouce leve) sans toucher a Lab1 |
| 8bb8b77 | 2026-09-30 | feat : implémenter is_thumb_extended |
| dcf4cb6 | 2026-09-30 | Merge pull request #1 from MohamedUqac/mdiarra5/dev |
| 6e5632a | 2026-09-30 | docs: ajouter section methode du rapport (echelle et rotation) |
| 91beaa4 | 2026-10-06 | docs: ajouter spec, plan, progress et audit du devoir 1 |
| 694b0dc | 2026-10-06 | Merge pull request #2 from MohamedUqac/mdiarra5/dev |

## Résultat des tests

Commande : `.venv\Scripts\python.exe -m pytest test\devoir1 -q --tb=no`

| Résultat | Détail |
|---|---|
| 37 passed | — |
| 5 failed | tous dans `test/devoir1/test_thumb_counter.py` |

Échecs :
- `test_valeur_repetee_window_fois_est_publiee`
- `test_valeur_repetee_moins_que_window_fois_nest_pas_publiee`
- `test_valeurs_alternees_ne_publient_jamais`
- `test_reset_remet_le_decompte_stable_a_zero`
- `test_les_premieres_maj_ne_publient_quau_dernier_tour_de_la_fenetre`

## Statut des tâches

| Tâche | Statut | Preuve |
|---|---|---|
| Dépôt `devoir1` créé, branche `mdiarra5/dev` | fait | commits `80f87ec`, `8bb8b77` et merges `dcf4cb6`, `694b0dc` |
| `is_thumb_extended` | fait | commit `8bb8b77` ; tests de `test_thumb_detector.py` inclus dans les 37 passed |
| `rapport/methode.md` (seuil fixe vs relatif, rotation) | fait | commit `6e5632a` |
| `ThumbCounter.update` | à faire | 5 échecs dans `test/devoir1/test_thumb_counter.py` |
| Paragraphe filtrage temporel | à faire | non prouvé par les commits listés |
| Autres sections du rapport | à faire | non prouvé par les commits listés |
| PR #1 et #2 de mdiarra5/dev fusionnées ; branches Merello16 et sokhona26 non examinées | fait | commits `dcf4cb6` et `694b0dc` |
