## Méthode utilisée

Un seuil fixe n'est pas une valeur relative : selon la position de la main devant la caméra, la comparaison des coordonnées à ce seuil n'est pas toujours correcte. À l'inverse, avec trois valeurs comparées entre elles (plutôt qu'à un seuil absolu), la comparaison reste valide quelle que soit l'échelle, car les trois valeurs varient ensemble, dans la même proportion.

De même, quelle que soit la rotation appliquée à la main, une comparaison basée sur un seuil fixe n'est pas toujours correcte, car son résultat dépend de l'angle de la main. Notre méthode, elle, reste invariante face à la rotation et reste correcte quel que soit l'angle.

<!-- TODO: paragraphe filtrage temporel (ThumbCounter) -->
