# Audit — Devoir 1

> État au 2026-10-06. À refaire après fusion des branches.

## Tests
- `test_thumb_detector.py` : 19/19 réussis.
- `test_thumb_counter.py` : non réussis, `ThumbCounter.update` pas encore implémenté.
- `test_emotion_detector.py`, `test_hud.py` : à relancer après fusion (non vérifiés ici).

## Conformité à la spec
- Code fourni non modifié : à confirmer avec `git diff master -- code/detect_thumbs.py code/emotion_detector.py`.
- `is_thumb_extended` : conforme (comparaison relative, sans seuil).
- `ThumbCounter.update` : non conforme tant que le stub existe.

## Risques
- Dépendance au travail du collègue pour le filtre temporel.
- Rapport incomplet (sections listées dans plan.md).

## Décision
Pas prêt à la remise. Relancer `pytest test/devoir1` après fusion et mettre à jour ce fichier.
