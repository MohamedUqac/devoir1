## Méthode utilisée

Un seuil fixe n'est pas une valeur relative : selon la position de la main devant la caméra, la comparaison des coordonnées à ce seuil n'est pas toujours correcte. À l'inverse, avec trois valeurs comparées entre elles (plutôt qu'à un seuil absolu), la comparaison reste valide quelle que soit l'échelle, car les trois valeurs varient ensemble, dans la même proportion.

De même, quelle que soit la rotation appliquée à la main, une comparaison basée sur un seuil fixe n'est pas toujours correcte, car son résultat dépend de l'angle de la main. Notre méthode, elle, reste invariante face à la rotation et reste correcte quel que soit l'angle.

### Filtrage temporel

Un décompte calculé image par image n'est pas utilisable tel quel. Dès que la main bouge un peu ou que MediaPipe hésite sur une image, le nombre de pouces levés passe d'une valeur à l'autre et le compteur clignote. Dans une application d'interaction humain-robot, ce clignotement serait une commande qui part toute seule.

Nous filtrons donc le décompte dans le temps avec la classe `ThumbCounter`. Elle garde les derniers décomptes bruts dans une file dont la taille est `debounce_frames`, soit trois images dans notre configuration. À chaque nouvelle image, la fonction `update` ajoute le décompte brut à cette file. Le décompte affiché ne change que si la file est pleine et que toutes ses valeurs sont identiques. Dans tous les autres cas, nous conservons la dernière valeur stable, et non zéro : une image ambiguë ne fait donc jamais clignoter l'affichage. Une valeur négative est refusée, car un nombre de pouces ne peut pas être négatif.

Ce filtre a un prix : le nouveau décompte n'apparaît qu'après `debounce_frames` images, soit environ un dixième de seconde à 30 images par seconde. Ce retard est imperceptible à l'usage, et il transforme une commande instable en une commande stable.
