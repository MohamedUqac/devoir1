# Audit — Devoir 1

> État vérifié le 2026-10-06.

## Tests
- [x] `pytest test/devoir1` : 37 passed et 5 failed, tous les échecs localisés dans `test_thumb_counter.py` (`NotImplementedError` sur `ThumbCounter.update`).
- [ ] `test_emotion_detector.py`, `test_hud.py` : non vérifiés dans la passe du 2026-10-06.

## Conformité à la spec
- [x] `is_thumb_extended` : implémenté (commit 8bb8b77), comparaison relative sans seuil.
- [x] Code fourni (`detect_thumbs.py`, `emotion_detector.py`) : non modifié par aucun commit après 80f87ec.
- [!] `ThumbCounter.update` : non implémenté, le stub lève `NotImplementedError`.

## Risques
- [!] Branches `Merello16` et `sokhona26` : non examinées.
- [!] Rapport incomplet : sections listées dans `plan.md` absentes ou incomplètes.

## Décision
- [!] Pas prêt à la remise tant que `ThumbCounter.update` n'est pas implémenté et que le rapport est incomplet.
