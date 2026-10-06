# Spec — Devoir 1 : détection du pouce levé (MediaPipe Hands)

## Objectif
À partir d'une image de caméra, détecter les mains avec MediaPipe Hands (21 repères par main) et afficher le nombre de pouces levés, de façon stable dans le temps.

## Entrées / sorties
- Entrée : images vidéo (webcam) ; repères de la main fournis par MediaPipe.
- Sortie : nombre de pouces levés (entier >= 0), affiché dans le HUD.

## Fonctions à implémenter (`code/thumb_detector.py`)
1. `is_thumb_extended(metrics)` : retourne True si, selon la distance au poignet, MCP < IP < TIP (pouce déployé). Comparaison relative des 3 valeurs, sans seuil fixe (invariance à l'échelle et à la rotation).
2. `ThumbCounter.update(raw_count)` : filtre temporel. Ajoute `raw_count` à un historique (deque de taille `debounce_frames`) ; la valeur stable ne change que lorsque l'historique est plein et que toutes ses valeurs sont identiques ; retourne la valeur stable. Rejette une valeur négative.

## Contraintes
- Ne pas modifier le code fourni (`detect_thumbs.py`, `emotion_detector.py`).
- Les tests de `test/devoir1/` doivent passer.
- Rapport : `rapport/methode.md` et autres sections selon l'énoncé.

## Critère de réussite
Tous les tests de `test/devoir1/` passent ; la démo détecte correctement 0, 1 ou 2 pouces sans clignotement.
