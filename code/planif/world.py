"""
planif.world - Grille de planification, geometrie de cellule et occupation des obstacles.

Palier 0 des trois planificateurs (docs/superpowers/plans/6mig841-ameliorations/plan06.md) :
astar, thetastar, dstarlite, compare et app lisent tous la grille, la taille de cellule, le
depart, le but et les obstacles ici. Aucune valeur numerique n'est ecrite en dur ailleurs
(workflow.md R7).

Le fichier lu est `planif_config.json`, cherche dans cet ordre :
  1. le chemin donne par la variable d'environnement PLANIF_CONFIG,
  2. `planif_config.json` a cote du paquet `planif`.

Ce module est volontairement independant de `ihr_ros` : l'application matplotlib du Lab 1
(spec.md, "Le substitut tkinter et l'application matplotlib du Lab 1 restent separes") ne
depend que de matplotlib et numpy, jamais de la configuration du robot ni de son fichier
`ihr_config.json`.

Une cle absente ou une cellule invalide leve une erreur explicite qui nomme la cle ou la
cellule, jamais un repli silencieux (R3, R8).
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

Cellule = tuple[int, int]  # (colonne, ligne)

_ENV_VAR = "PLANIF_CONFIG"
_FILENAME = "planif_config.json"

_cache: dict[str, Any] | None = None
_cache_path: Path | None = None

# Ordre fixe des huit deplacements : garantit un ordre de visite deterministe (R19), donc
# un depart-egalite deterministe pour A*, Theta* et D*-Lite.
_DEPLACEMENTS_8: tuple[tuple[int, int], ...] = (
    (1, 0), (1, 1), (0, 1), (-1, 1),
    (-1, 0), (-1, -1), (0, -1), (1, -1),
)


class ConfigError(RuntimeError):
    """Configuration de planification absente, illisible, ou cle manquante."""


class CelluleInvalideError(ValueError):
    """Cellule hors grille, ou pas de cellule nul/negatif rendant une conversion infinie."""


def config_path() -> Path:
    """
    --------------------------------------------------------------------------
    Purpose:
        Resoudre le chemin du fichier de configuration de planification, sans le lire.

    Inputs:
        aucun (lit la variable d'environnement PLANIF_CONFIG si elle existe)

    Outputs:
        path (Path): chemin absolu du fichier de configuration
    --------------------------------------------------------------------------
    """
    override = os.environ.get(_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    return (Path(__file__).resolve().parent.parent / _FILENAME).resolve()


def load_config(force_reload: bool = False) -> dict[str, Any]:
    """
    --------------------------------------------------------------------------
    Purpose:
        Charger planif_config.json une seule fois par processus.

    Inputs:
        force_reload (bool): relire le fichier meme s'il est deja en cache

    Outputs:
        config (dict): contenu integral de planif_config.json
    --------------------------------------------------------------------------
    """
    global _cache, _cache_path
    path = config_path()
    if _cache is not None and not force_reload and _cache_path == path:
        return _cache

    if not path.is_file():
        raise ConfigError(
            f"Configuration de planification introuvable : {path}. "
            f"Definir {_ENV_VAR} ou replacer {_FILENAME} a cote du paquet planif."
        )
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Configuration de planification illisible ({path}) : {exc}") from exc

    _cache = data
    _cache_path = path
    return data


def config_section(name: str) -> dict[str, Any]:
    """
    --------------------------------------------------------------------------
    Purpose:
        Retourner une section de premier niveau (grille, depart, but...).

    Inputs:
        name (str): nom de la section

    Outputs:
        section (dict): contenu de la section
    --------------------------------------------------------------------------
    """
    data = load_config()
    if name not in data:
        raise ConfigError(
            f"Section '{name}' absente de {config_path()}. "
            f"Sections presentes : {sorted(k for k in data if not k.startswith('_'))}."
        )
    return data[name]


def config_value(section_name: str, key: str) -> Any:
    """
    --------------------------------------------------------------------------
    Purpose:
        Lire une valeur de configuration, en echouant explicitement si absente.

    Inputs:
        section_name (str): nom de la section
        key (str): nom de la cle dans cette section

    Outputs:
        value (Any): valeur lue
    --------------------------------------------------------------------------
    """
    data = config_section(section_name)
    if key not in data:
        raise ConfigError(
            f"Cle '{key}' absente de la section '{section_name}' dans {config_path()}. "
            f"Cles presentes : {sorted(data)}."
        )
    return data[key]


def rectangle_vers_cellules(rectangle: dict[str, int]) -> set[Cellule]:
    """
    --------------------------------------------------------------------------
    Purpose:
        Deplier un rectangle de configuration en l'ensemble de ses cellules.

    Inputs:
        rectangle (dict): cles colonne_min, colonne_max, ligne_min, ligne_max (incluses)

    Outputs:
        cellules (set[Cellule]): toutes les cellules du rectangle
    --------------------------------------------------------------------------
    """
    cellules: set[Cellule] = set()
    for colonne in range(rectangle["colonne_min"], rectangle["colonne_max"] + 1):
        for ligne in range(rectangle["ligne_min"], rectangle["ligne_max"] + 1):
            cellules.add((colonne, ligne))
    return cellules


class World:
    """
    Grille rectangulaire de cellules carrees, avec une occupation d'obstacle mutable.

    Toutes les valeurs geometriques viennent de planif_config.json (R7). Une instance peut
    aussi etre construite depuis un dictionnaire fourni par un appelant (un test, par
    exemple), pour les scenarios limites (arrivee enfermee, cellule hors grille, pas de
    cellule nul) sans toucher au fichier reel.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        donnees = config if config is not None else load_config()

        grille = donnees.get("grille")
        if grille is None:
            raise ConfigError("Section 'grille' absente de la configuration de planification.")
        for cle in ("largeur_cellules", "hauteur_cellules", "taille_cellule"):
            if cle not in grille:
                raise ConfigError(f"Cle '{cle}' absente de la section 'grille'.")

        self.largeur_cellules: int = grille["largeur_cellules"]
        self.hauteur_cellules: int = grille["hauteur_cellules"]
        self.taille_cellule: float = grille["taille_cellule"]
        self.origine_x: float = grille.get("origine_x", 0.0)
        self.origine_y: float = grille.get("origine_y", 0.0)

        if not self.taille_cellule or self.taille_cellule <= 0:
            raise CelluleInvalideError(
                f"Le pas de cellule (taille_cellule={self.taille_cellule!r}) ne peut pas "
                "etre nul ou negatif : toute conversion grille <-> unites deviendrait infinie."
            )

        self._occupees: set[Cellule] = set()
        obstacle_initial = donnees.get("obstacle_initial")
        if obstacle_initial:
            self._occupees |= rectangle_vers_cellules(obstacle_initial)

        depart = donnees.get("depart")
        but = donnees.get("but")
        self.depart: Cellule | None = (depart["colonne"], depart["ligne"]) if depart else None
        self.but: Cellule | None = (but["colonne"], but["ligne"]) if but else None

    def est_dans_la_grille(self, cellule: Cellule) -> bool:
        """Vrai si `cellule` tombe dans les bornes de la grille."""
        colonne, ligne = cellule
        return 0 <= colonne < self.largeur_cellules and 0 <= ligne < self.hauteur_cellules

    def _verifier_dans_la_grille(self, cellule: Cellule) -> None:
        if not self.est_dans_la_grille(cellule):
            raise CelluleInvalideError(
                f"Cellule {cellule} hors grille (largeur={self.largeur_cellules}, "
                f"hauteur={self.hauteur_cellules})."
            )

    def est_occupee(self, cellule: Cellule) -> bool:
        """Vrai si `cellule` porte un obstacle. Leve CelluleInvalideError si hors grille."""
        self._verifier_dans_la_grille(cellule)
        return cellule in self._occupees

    def vers_unites(self, cellule: Cellule) -> tuple[float, float]:
        """Convertit une cellule de grille vers les coordonnees de son centre, en unites."""
        self._verifier_dans_la_grille(cellule)
        colonne, ligne = cellule
        x = self.origine_x + (colonne + 0.5) * self.taille_cellule
        y = self.origine_y + (ligne + 0.5) * self.taille_cellule
        return (x, y)

    def vers_cellule(self, point: tuple[float, float]) -> Cellule:
        """Convertit un point en unites vers la cellule de grille qui le contient."""
        x, y = point
        colonne = math.floor((x - self.origine_x) / self.taille_cellule)
        ligne = math.floor((y - self.origine_y) / self.taille_cellule)
        cellule = (colonne, ligne)
        self._verifier_dans_la_grille(cellule)
        return cellule

    def definir_occupation(self, cellules: Iterable[Cellule], occupee: bool) -> list[Cellule]:
        """
        Marque `cellules` comme occupees ou libres. Rend la liste des cellules dont
        l'occupation a reellement change, pour que D*-Lite sache lesquelles reexaminer.
        """
        changees: list[Cellule] = []
        for cellule in cellules:
            self._verifier_dans_la_grille(cellule)
            deja_occupee = cellule in self._occupees
            if occupee and not deja_occupee:
                self._occupees.add(cellule)
                changees.append(cellule)
            elif not occupee and deja_occupee:
                self._occupees.discard(cellule)
                changees.append(cellule)
        return changees

    def voisins(self, cellule: Cellule) -> list[Cellule]:
        """
        Rend les cellules voisines (8-connexite) dans la grille, ni occupees ni hors
        grille, dans un ordre fixe (R19). Refuse une diagonale qui couperait un coin
        entre deux cellules occupees adjacentes.
        """
        self._verifier_dans_la_grille(cellule)
        colonne, ligne = cellule
        resultat: list[Cellule] = []
        for dc, dl in _DEPLACEMENTS_8:
            voisine = (colonne + dc, ligne + dl)
            if not self.est_dans_la_grille(voisine) or voisine in self._occupees:
                continue
            if dc != 0 and dl != 0:
                cote_a = (colonne + dc, ligne)
                cote_b = (colonne, ligne + dl)
                if cote_a in self._occupees and cote_b in self._occupees:
                    continue
            resultat.append(voisine)
        return resultat

    def voisins_potentiels(self, cellule: Cellule) -> list[Cellule]:
        """
        Cellules geometriquement adjacentes (8-connexite), sans filtrer l'occupation.
        Sert a D*-Lite pour retrouver, apres un changement d'occupation sur `cellule`,
        toutes les cellules dont le cout de deplacement vers `cellule` a pu changer.
        """
        self._verifier_dans_la_grille(cellule)
        colonne, ligne = cellule
        return [
            (colonne + dc, ligne + dl)
            for dc, dl in _DEPLACEMENTS_8
            if self.est_dans_la_grille((colonne + dc, ligne + dl))
        ]

    def cout_deplacement(self, a: Cellule, b: Cellule) -> float:
        """Distance euclidienne entre deux cellules, en unites (pas necessairement adjacentes)."""
        ax, ay = a
        bx, by = b
        return math.hypot(bx - ax, by - ay) * self.taille_cellule

    def distance_heuristique(self, a: Cellule, b: Cellule) -> float:
        """
        Distance octile entre deux cellules, en unites : heuristique admissible et
        coherente pour un cout de deplacement euclidien 8-connexe (utilisee par A*,
        Theta* et D*-Lite).
        """
        dc = abs(a[0] - b[0])
        dl = abs(a[1] - b[1])
        droit = max(dc, dl) - min(dc, dl)
        diagonal = min(dc, dl)
        return (droit + diagonal * math.sqrt(2)) * self.taille_cellule

    def ligne_de_vue_libre(self, a: Cellule, b: Cellule) -> bool:
        """
        Vrai si le segment entre les centres de `a` et `b` ne traverse aucune cellule
        occupee (Bresenham, toutes directions). Les deux extremites elles-memes ne sont
        pas testees : seules les cellules strictement intermediaires comptent.
        """
        self._verifier_dans_la_grille(a)
        self._verifier_dans_la_grille(b)
        
        if a == b:
            return True

        ax, ay = a
        bx, by = b
        dx = bx - ax
        dy = by - ay

        # Directions de parcours
        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1

        # Distances en "unites de cellule" depuis le centre de la cellule courante jusqu'à la frontière
        # Le centre est à 0.5 de la frontière.
        # Si dx > 0, on avance vers la droite. La frontière est à 0.5 cellule.
        # Si dx < 0, on avance vers la gauche. La frontière est à 0.5 cellule.
        
        # On utilise des entiers pour éviter les problèmes de flottants.
        # On multiplie tout par 2 pour travailler avec des demi-unités si nécessaire, ou simplement des entiers si possible.
        # Ici, les coordonnées sont des entiers. Le segment va de (ax+0.5, ay+0.5) à (bx+0.5, by+0.5).
        
        # DDA standard :
        # tMaxX : distance paramétrique pour atteindre la prochaine frontière verticale
        # tMaxY : distance paramétrique pour atteindre la prochaine frontière horizontale
        
        # On travaille dans le repère des centres.
        # Position initiale : (0, 0) relativement à a.
        # Position cible : (dx, dy).
        
        # Frontières :
        # Si dx > 0 : prochaine frontière x est à 0.5. tMaxX = 0.5 / dx
        # Si dx < 0 : prochaine frontière x est à -0.5. tMaxX = 0.5 / -dx = 0.5 / |dx|
        # tDeltaX = 1 / |dx| (distance paramétrique entre deux frontières verticales)
        
        # Pour éviter les flottants, on peut utiliser des fractions.
        # tMaxX = 1 / (2 * |dx|)
        # tDeltaX = 1 / |dx|
        
        # Nous allons utiliser une approche par entiers en comparant les fractions.
        # Soit t le paramètre du segment [0, 1].
        # x(t) = ax + 0.5 + t * dx
        # y(t) = ay + 0.5 + t * dy
        
        # On cherche les valeurs de t où x(t) ou y(t) est un entier (frontière).
        
        # Si dx != 0 :
        # x(t) = k (entier) => t = (k - ax - 0.5) / dx
        # Les k possibles sont les entiers strictement entre ax et bx (bornes exclues car on ne teste pas les extrémités, mais on doit tester les cellules traversées).
        # En fait, on parcourt les cellules.
        
        # Algorithme DDA classique :
        # 1. Calculer tMaxX et tMaxY pour la première frontière.
        # 2. Calculer tDeltaX et tDeltaY.
        # 3. Boucle : avancer vers la frontière la plus proche (tMaxX < tMaxY ? X : Y).
        # 4. Tester la nouvelle cellule.
        
        # Pour gérer le cas du "coin partagé", il faut détecter si on passe exactement par un coin.
        # Cela arrive si tMaxX == tMaxY (à la précision près, ou exactement en fractions).
        
        # Utilisons des entiers pour les comparaisons exactes.
        # tMaxX = numX / denX
        # tMaxY = numY / denY
        
        # Si dx > 0 : première frontière x est à ax + 1. Distance = 0.5. t = 0.5 / dx.
        # Si dx < 0 : première frontière x est à ax. Distance = 0.5. t = 0.5 / (-dx).
        
        # On peut simplifier :
        # tMaxX = 1 / (2 * abs(dx))
        # tMaxY = 1 / (2 * abs(dy))
        
        # tDeltaX = 1 / abs(dx)
        # tDeltaY = 1 / abs(dy)
        
        # Comparaison de tMaxX et tMaxY :
        # 1 / (2 * abs(dx)) < 1 / (2 * abs(dy))  <=>  abs(dy) < abs(dx)
        
        # Égalité : abs(dx) == abs(dy) (et même signe relatif pour le pas ? Non, juste les valeurs absolues pour la distance).
        
        # Si dx == 0 : tMaxX = inf
        # Si dy == 0 : tMaxY = inf
        
        # Implémentation avec entiers :
        # On garde une fraction t = t_num / t_den ? Non, c'est plus simple de comparer les temps.
        
        # Soit :
        # t_max_x = 1 / (2 * |dx|) si dx != 0 else inf
        # t_max_y = 1 / (2 * |dy|) si dy != 0 else inf
        
        # On compare 1/|dx| et 1/|dy| pour savoir qui est le plus petit (la frontière la plus proche).
        # 1/|dx| < 1/|dy|  <=> |dy| < |dx|
        
        # Si |dx| == |dy|, on arrive au coin.
        
        # Cellule courante : (cx, cy) = a
        cx, cy = a
        
        # Temps restant jusqu'à la fin du segment ? On peut s'arrêter quand on atteint b.
        # Mais b est dans une cellule. Si on atteint la frontière de b, on entre dans b.
        # On ne doit pas tester b.
        
        # On boucle tant qu'on n'a pas atteint la cellule b.
        # Mais comment savoir si on a atteint b ?
        # Si on fait un pas et qu'on arrive dans b, on s'arrête.
        
        # Attention aux cas où dx ou dy est 0.
        
        # Variables pour le DDA :
        # t_max_x : temps pour atteindre la prochaine frontière X
        # t_max_y : temps pour atteindre la prochaine frontière Y
        
        # On utilise des fractions pour la comparaison exacte.
        # t_max_x = num_x / den_x
        # t_max_y = num_y / den_y
        
        if dx == 0:
            t_max_x_num, t_max_x_den = 1, 0 # inf
        else:
            t_max_x_num, t_max_x_den = 1, 2 * abs(dx)
            
        if dy == 0:
            t_max_y_num, t_max_y_den = 1, 0 # inf
        else:
            t_max_y_num, t_max_y_den = 1, 2 * abs(dy)
            
        # t_delta_x : temps pour traverser une cellule complète
        if dx == 0:
            t_delta_x_num, t_delta_x_den = 1, 0
        else:
            t_delta_x_num, t_delta_x_den = 1, abs(dx)
            
        if dy == 0:
            t_delta_y_num, t_delta_y_den = 1, 0
        else:
            t_delta_y_num, t_delta_y_den = 1, abs(dy)
            
        # Boucle principale
        # On s'arrête quand on atteint la cellule b.
        # Comme on ne teste pas b, on peut s'arrêter dès qu'on "entre" dans b.
        
        # Mais attention : si a et b sont adjacents, on ne visite aucune cellule intermédiaire.
        # Si a=(0,0), b=(1,0). dx=1, dy=0.
        # t_max_x = 1/2. t_max_y = inf.
        # On avance en X. Nouvelle cellule (1,0). C'est b. On s'arrête. Retourne True.
        
        # Si a=(0,0), b=(2,0). dx=2.
        # t_max_x = 1/4.
        # Avance X -> (1,0). Ce n'est pas b. Tester (1,0).
        # t_max_x += 1/2 -> 3/4.
        # Avance X -> (2,0). C'est b. Arrêt.
        
        # Si a=(0,0), b=(1,1). dx=1, dy=1.
        # t_max_x = 1/2, t_max_y = 1/2. Égalité.
        # On avance en X et Y. Nouvelle cellule (1,1). C'est b. Arrêt.
        # Mais il faut vérifier le coin !
        
        # Cas du coin :
        # Si on avance en diagonale (t_max_x == t_max_y), on passe par le coin (cx+step_x, cy+step_y).
        # Il faut vérifier si les deux cellules adjacentes (cx+step_x, cy) et (cx, cy+step_y) sont occupées.
        # Si oui, bloquer.
        
        # Algorithme :
        while (cx, cy) != (bx, by):
            # Comparer t_max_x et t_max_y
            # t_max_x = num_x / den_x
            # t_max_y = num_y / den_y
            
            # Comparaison : num_x * den_y vs num_y * den_x
            # Si den_x == 0 (inf), alors t_max_x est inf.
            
            left = t_max_x_num * t_max_y_den if t_max_x_den != 0 else float('inf')
            right = t_max_y_num * t_max_x_den if t_max_y_den != 0 else float('inf')
            
            # Plus simple : gérer les infinis explicitement.
            
            x_is_inf = t_max_x_den == 0
            y_is_inf = t_max_y_den == 0
            
            if x_is_inf and y_is_inf:
                break # Ne devrait pas arriver si a != b
                
            if x_is_inf:
                move_x = False
                move_y = True
            elif y_is_inf:
                move_x = True
                move_y = False
            else:
                # Comparer 1/(2|dx|) et 1/(2|dy|)
                # Équivaut à comparer |dy| et |dx|
                # Si |dy| < |dx|, alors 1/|dx| < 1/|dy| => t_max_x < t_max_y => avancer en X
                # Si |dy| > |dx|, alors t_max_y < t_max_x => avancer en Y
                # Si |dy| == |dx|, égalité => avancer en diagonale
                
                if abs(dy) < abs(dx):
                    move_x = True
                    move_y = False
                elif abs(dy) > abs(dx):
                    move_x = False
                    move_y = True
                else:
                    move_x = True
                    move_y = True
            
            # Avant de bouger, si on bouge en diagonale, vérifier le coin.
            if move_x and move_y:
                # On part de (cx, cy) vers (cx+step_x, cy+step_y)
                # Le coin est partagé par (cx+step_x, cy) et (cx, cy+step_y)
                # Attention : si on est déjà à la bordure ? Le DDA s'arrête à la grille, mais ici on s'arrête à b.
                # Les cellules adjacentes doivent être dans la grille pour exister.
                cote_a = (cx + step_x, cy)
                cote_b = (cx, cy + step_y)
                
                # Si ces cellules sont dans la grille et occupées, bloquer.
                if self.est_dans_la_grille(cote_a) and self.est_dans_la_grille(cote_b):
                    if cote_a in self._occupees and cote_b in self._occupees:
                        return False
            
            # Effectuer le déplacement
            if move_x:
                cx += step_x
                # Mettre à jour t_max_x
                # t_max_x += t_delta_x
                # t_max_x = num_x/den_x + num_dx/den_dx
                # = (num_x * den_dx + num_dx * den_x) / (den_x * den_dx)
                if t_max_x_den != 0 and t_delta_x_den != 0:
                    new_num = t_max_x_num * t_delta_x_den + t_delta_x_num * t_max_x_den
                    new_den = t_max_x_den * t_delta_x_den
                    # Simplifier ? Pas nécessaire pour la comparaison si on refait le calcul à chaque fois,
                    # mais les nombres peuvent devenir grands.
                    # Pour une grille 64x64, c'est négligeable.
                    t_max_x_num, t_max_x_den = new_num, new_den
                # Si l'un des deux était inf, le reste inf (mais on n'ajoute pas à inf)
                
            if move_y:
                cy += step_y
                if t_max_y_den != 0 and t_delta_y_den != 0:
                    new_num = t_max_y_num * t_delta_y_den + t_delta_y_num * t_max_y_den
                    new_den = t_max_y_den * t_delta_y_den
                    t_max_y_num, t_max_y_den = new_num, new_den
            
            # Après le déplacement, on est dans la nouvelle cellule (cx, cy).
            # Si c'est b, on s'arrête (la boucle while s'occupera de ça).
            # Sinon, on teste si (cx, cy) est occupée.
            if (cx, cy) != (bx, by):
                if (cx, cy) in self._occupees:
                    return False
        
        return True

    def cellules_obstacle(self) -> frozenset[Cellule]:
        """Copie immuable des cellules actuellement occupees, pour l'affichage."""
        return frozenset(self._occupees)
