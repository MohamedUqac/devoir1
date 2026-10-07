# Audit — Devoir 1

> État vérifié le 2026-10-06.

## Tests
- [x] `pytest test/devoir1` : 42 passed, 0 failed.
- [x] `test_emotion_detector.py`, `test_hud.py` et `test_thumb_detector.py` : réussis (inclus dans les 42 passed).

## Conformité à la spec
- [x] `is_thumb_extended` : implémenté (commit 8bb8b77), comparaison relative sans seuil.
- [x] Code fourni (`detect_thumbs.py`, `emotion_detector.py`) : non modifié par aucun commit après 80f87ec.
- [x] `ThumbCounter.update` : implémenté (commit 4010d82), conforme au contrat (historique, fenêtre pleine, valeurs identiques).

## Risques
- [!] Branche `Merello16` : aucun commit en avance sur master.
- [!] Rapport incomplet : sections listées dans `plan.md` absentes ou incomplètes.

## Décision
- [x] Le code est complet et les tests passent. Il reste le rapport à finir avant la remise.

## Relecture du code

aucun défaut constaté
