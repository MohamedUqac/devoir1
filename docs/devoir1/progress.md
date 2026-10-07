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

## Mise en place

- [x] Dépôt `devoir1` créé, branche `mdiarra5/dev` — commits `80f87ec`, `8bb8b77` et merges `dcf4cb6`, `694b0dc`
- [x] PR #1, #2, #4, #5, #6, #7 et #8 fusionnées dans master
- Note: sokhona26 fusionnée (PR #5) ; Merello16 n'a aucun commit en avance sur master

## is_thumb_extended

- [x] `is_thumb_extended` implémenté — commit `8bb8b77`
- Note: tests de `test_thumb_detector.py` inclus dans les 42 passed

## ThumbCounter

- [x] `ThumbCounter.update` implémenté avec aider — commit `4010d82`
- Note: 42 passed dans `test/devoir1/`

## Rapport

- [x] `rapport/methode.md` (seuil fixe vs relatif, rotation) — commit `6e5632a`
- [ ] Paragraphe filtrage temporel
- [ ] Autres sections du rapport
- [x] test caméra en direct réussi le 2026-10-06
- [ ] test caméra à refaire avec vidéo pour le rapport

## Audit

- [x] audit.md à jour (PR #6 et #8) : 42 passed, relecture du code sans défaut constaté
