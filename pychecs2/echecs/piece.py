# -*- coding: utf-8 -*-
"""Module contenant la classe de base Piece, ainsi qu'une classe fille pour chacun des types de pièces du jeu d'échecs.

"""
# TODO: Si votre système n'affiche pas correctement les caractères unicodes du jeu d'échecs,
# mettez cette constante (variable globale) à False. Un tutoriel est présent sur le site Web
# du cours pour vous aider à faire fonctionner les caractères Unicoe sous Windows.
UTILISER_UNICODE = True


class Piece:
    """Une classe de base représentant une pièce du jeu d'échecs. C'est cette classe qui est héritée plus bas pour fournir
    une classe par type de pièce (Pion, Tour, etc.).

    Attributes:
        couleur (str): La couleur de la pièce, soit 'blanc' ou 'noir'.
        peut_sauter (bool): Si oui ou non la pièce peut "sauter" par dessus d'autres pièces sur un échiquier.

    Args:
        couleur (str): La couleur avec laquelle créer la pièce.
        peut_sauter (bool): La valeur avec laquelle l'attribut peut_sauter doit être initialisé.

    """
    def __init__(self, couleur, peut_sauter, peut_roquer=False, peut_prendre_en_passant=False, est_eligible_a_promotion=False):
        # Validation si la couleur reçue est valide.
        assert couleur in ('blanc', 'noir')

        # Création des attributs avec les valeurs reçues.
        self.couleur = couleur
        self.peut_sauter = peut_sauter

    def est_blanc(self):
        """Retourne si oui ou non la pièce est blanche.

        Returns:
            bool: True si la pièce est blanche, et False autrement.

        """
        return self.couleur == 'blanc'

    def est_noir(self):
        """Retourne si oui ou non la pièce est noire.

        Returns:
            bool: True si la pièce est noire, et False autrement.

        """
        return self.couleur == 'noir'

    def peut_se_deplacer_vers(self, position_source, position_cible):
        """Vérifie si, selon les règles du jeu d'échecs, la pièce peut se déplacer d'une position à une autre.

        Une position est une chaîne de deux caractères.
            Le premier caractère est une lettre entre a et h, représentant la colonne de l'échiquier.
            Le second caractère est un chiffre entre 1 et 8, représentant la rangée de l'échiquier.

        Args:
            position_source (str): La position source, suivant le format ci-haut. Par exemple, 'a8', 'f3', etc.
            position_cible (str): La position cible, suivant le format ci-haut. Par exemple, 'b6', 'h1', etc.

        Warning:
            Comme nous sommes dans la classe de base et non dans l'une des classes filles, nous ne savons pas
            (encore) comment cette pièce se déplace. Cette méthode est donc à redéfinir dans chacune des
            classes filles.

        Warning:
            Comme la classe Piece est indépendante de l'échiquier (et donc on ne sait pas si une pièce est "dans le
            chemin"), on doit ignorer le contenu de l'échiquier : on ne se concentre que sur les règles de mouvement
            des pièces.

        Returns:
            bool: True si le déplacement est valide en suivant les règles de la pièce, et False autrement.

        """
        # On lance une exception (on y reviendra) indiquant que ce code n'a pas été implémenté. Ne touchez pas
        # à cette méthode : réimplémentez-la dans les classes filles!
        raise NotImplementedError

    def peut_faire_une_prise_vers(self, position_source, position_cible):
        """Vérifie si, selon les règles du jeu d'échecs, la pièce peut "manger" (faire une prise) une pièce ennemie.
        Pour la plupart des pièces, la règle est la même, on appelle donc la méthode peut_se_deplacer_vers.

        Si ce n'est pas le cas pour une certaine pièce, on peut simplement redéfinir cette méthode pour programmer
        la règle.

        Args:
            position_source (str): La position source, suivant le format ci-haut. Par exemple, 'a8', 'f3', etc.
            position_cible (str): La position cible, suivant le format ci-haut. Par exemple, 'b6', 'h1', etc.

        Returns:
            bool: True si la prise est valide en suivant les règles de la pièce, et False autrement.

        """
        return self.peut_se_deplacer_vers(position_source, position_cible)


class Pion(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, False)

    def peut_se_deplacer_vers(self, position_source, position_cible):
        # Le déplacement se fait sur une même colonne.
        if  ord(position_source[0])!= ord(position_cible[0]):
            return False

        # Le pion ne peut se déplacer que d'une case:  pour les noirs vers le bas et
        # pour les blancs, vers le haut.
        rangee_source = int(position_source[1])
        rangee_cible = int(position_cible[1])
        if self.est_blanc():
            depart = 2
            ecart = 1
        else:
            depart = 7
            ecart = -1
        if rangee_cible - rangee_source == ecart:
            return True

        # Si le pion est sur sa rangée de départ, il peut bouger de deux rangées.
        if rangee_source == depart:
            if rangee_cible - rangee_source == 2 * ecart:
                return True
        return False

    def peut_faire_une_prise_vers(self, position_source, position_cible):
        # La colonne doit changer de un
        if abs(ord(position_source[0]) - ord(position_cible[0])) != 1:
            return False

        # La pion doit se déplacer d'une rangée dans le sens de la progression
        if self.est_blanc():
            ecart = 1
        else:
            ecart = -1
        if int(position_cible[1]) - int(position_source[1]) == ecart:
            return True
        return False

    def __repr__(self):
        """Redéfinit comment on affiche un pion à l'écran. Nous utilisons la constante UTILISER_UNICODE
        pour déterminer comment afficher le pion.

        Returns:
            str: La chaîne de caractères représentant le pion.

        """
        if self.est_blanc():
            if UTILISER_UNICODE:
                return '\u2659'
            else:
                return 'PB'
        else:
            if UTILISER_UNICODE:
                return '\u265f'
            else:
                return 'PN'


class Tour(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, False)

    def peut_se_deplacer_vers(self, position_source, position_cible):
        return (position_source[0] == position_cible[0]) or (position_source[1] == position_cible[1])

    def __repr__(self):
        if self.est_blanc():
            if UTILISER_UNICODE:
                return '\u2656'
            else:
                return 'TB'
        else:
            if UTILISER_UNICODE:
                return '\u265c'
            else:
                return 'TN'


class Cavalier(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, True)

    def peut_se_deplacer_vers(self, position_source, position_cible):
        delta_colonne = abs(ord(position_cible[0]) - ord(position_source[0]))
        delta_rangee = abs(int(position_cible[1]) - int(position_source[1]))
        return (delta_colonne == 1 and delta_rangee == 2) or (delta_colonne == 2 and delta_rangee == 1)

    def __repr__(self):
        if self.est_blanc():
            if UTILISER_UNICODE:
                return '\u2658'
            else:
                return 'CB'
        else:
            if UTILISER_UNICODE:
                return '\u265e'
            else:
                return 'CN'


class Fou(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, False)
        
    def peut_se_deplacer_vers(self, position_source, position_cible):
        delta_colonne = abs(ord(position_cible[0]) - ord(position_source[0]))
        delta_rangee = abs(int(position_cible[1]) - int(position_source[1]))
        return delta_colonne == delta_rangee

    def __repr__(self):
        if self.est_blanc():
            if UTILISER_UNICODE:
                return '\u2657'
            else:
                return 'FB'
        else:
            if UTILISER_UNICODE:
                return '\u265d'
            else:
                return 'FN'


class Roi(Piece):
    def __init__(self, couleur, peut_roquer=True):
        super().__init__(couleur, False)
        self.peut_roquer = peut_roquer

    def peut_se_deplacer_vers(self, position_source, position_cible):
        delta_colonne = abs(ord(position_cible[0]) - ord(position_source[0]))
        delta_rangee = abs(int(position_cible[1]) - int(position_source[1]))

        return ((delta_rangee < 2) and (delta_colonne < 2))

    def __repr__(self):
        if self.est_blanc():
            if UTILISER_UNICODE:
                return '\u2654'
            else:
                return 'RB'
        else:
            if UTILISER_UNICODE:
                return '\u265a'
            else:
                return 'RN'


class Dame(Piece):
    def __init__(self, couleur):
        super().__init__(couleur, False)
    
    def peut_se_deplacer_vers(self, position_source, position_cible):
        return Fou.peut_se_deplacer_vers(self, position_source, position_cible) or Tour.peut_se_deplacer_vers(self, position_source, position_cible)

    def __repr__(self):
        if self.est_blanc():
            if UTILISER_UNICODE:
                return '\u2655'
            else:
                return 'DB'
        else:
            if UTILISER_UNICODE:
                return '\u265b'
            else:
                return 'DN'

class Constructeur_de_piece():
    """Classe auxiliaire servant à convertir un code Unicode ou texte en pièce correspondante.  Est utilisé pour la
    récupération des fichiers de match, puisque les coups sont notés en format JSON et qu'il faut reconvertir les
    codes de pièces en objets pièces."""

    str_to_piece= {'\u2659': (Pion, 'blanc'), 'PB': (Pion, 'blanc'),
                       '\u265f': (Pion, 'noir'), 'PN': (Pion, 'noir'),
                       '\u2656': (Tour, 'blanc'), 'TB': (Tour, 'blanc'),
                       '\u265c': (Tour, 'noir'), 'TN': (Tour, 'noir'),
                       '\u2658': (Cavalier, 'blanc'), 'CB': (Cavalier, 'blanc'),
                       '\u265e': (Cavalier, 'noir'), 'CN': (Cavalier, 'noir'),
                       '\u2657': (Fou, 'blanc'), 'FB': (Fou, 'blanc'),
                       '\u265d': (Fou, 'noir'), 'FN': (Fou, 'noir'),
                       '\u2654': (Roi, 'blanc'), 'RB': (Roi, 'blanc'),
                       '\u265a': (Roi, 'noir'), 'RN': (Roi, 'noir'),
                       '\u2655': (Dame, 'blanc'), 'DB': (Dame, 'blanc'),
                       '\u265b': (Dame, 'noir'), 'DN': (Dame, 'noir')}

    @classmethod
    def convertir(cls, code):
        """Convertit un caractère unicode en pièce d'échec.
        Args:
            code(str):  Soit le caractère unicode de la pièce, soit le code texte ad hoc.
        Returns:
            (objet pièce):  Un objet du type et de la couleur correspondants.  Si retourne un roi, celui-ci ne peut
            pas roquer d'emblée."""

        assert code in cls.str_to_piece.keys(), f"Code erroné dans Constructeur_de_piece.convertir: {code}"
        constructeur, couleur = Constructeur_de_piece.str_to_piece[code]
        return constructeur(couleur)


