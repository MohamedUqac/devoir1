# Plan — Devoir 1

Équipe de 3. Chaque membre travaille sur sa branche et fusionne via PR vers `master` (dépôt `devoir1`).

## Tâches
1. [x] Mise en place du dépôt (remotes `origin`/`devoir1`, branches personnelles).
2. [x] `is_thumb_extended` — critère MCP < IP < TIP. Vérifier : `pytest test/devoir1/test_thumb_detector.py`.
3. [x] `ThumbCounter.update` — filtre temporel (collègue). Vérifier : `pytest test/devoir1/test_thumb_counter.py`. Fait, commit 4010d82, PR #5.
4. [x] La suite test/devoir1 passe entièrement. Fait, 42 passed le 2026-10-07.
5. [~] Rapport : Méthode (partiel, paragraphe filtrage temporel à ajouter) ; Bibliothèques, Introduction, Schéma bloc, Explications du code, Conclusion, Références à écrire.
6. [x] Audit final (`audit.md`) puis PR vers `master`. Fait, PR #6.

## Règles
- Un seul changement par commit, message clair.
- Tests lancés avant chaque push.
