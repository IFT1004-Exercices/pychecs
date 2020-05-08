# -*- coding: utf-8 -*-

from pychecs2.echecs.piece import Pion, Tour, Fou, Cavalier, Dame, Roi, UTILISER_UNICODE
from pychecs2.interface.PychecsException import PychecsException, CaseInexistanteException, ReglesException
from pychecs2.interface.PychecsException import CaseDepartVideException, CheminBloqueException
from pychecs2.interface.PychecsException import DeplacementImpossibleException, PriseImpossibleException
from pychecs2.interface.PychecsException import RoqueNonAutoriseException, PriseEnPassantNonAutoriseeException
from pychecs2.interface.PychecsException import CouleurSeMetElleMemeEnEchecException, CaseArriveeOccupeeException

class Echiquier:
    """Classe Echiquier, implémentée avec un dictionnaire de pièces.


    Attributes:
        dictionnaire_pieces (dict): Un dictionnaire dont les clés sont des positions, suivant le format suivant:
            Une position est une chaîne de deux caractères.
            Le premier caractère est une lettre entre a et h, représentant la colonne de l'échiquier.
            Le second caractère est un chiffre entre 1 et 8, représentant la rangée de l'échiquier.
        chiffres_rangees (list): Une liste contenant, dans l'ordre, les chiffres représentant les rangées.
        lettres_colonnes (list): Une liste contenant, dans l'ordre, les lettres représentant les colonnes.
        self.piece_a_bouge (dict):  Un dictionnaire indiquant si les tours ou les rois ont été déplacés une fois.
        self.roques (dict):  Un dictionnaire contenant les paramètres d'un roque.
        pion_vient_de_sauter_une_case (dict):  Dictionnaire indiquant si un pion vient de faire un coup de deux cases.

    """

    # Permet de basculer facilement les couleurs
    couleurs = {"blanc": "noir", "noir": "blanc"}

    # Mouvements de la tour pour le roque
    roques = {("e1", "c1"): ("grand roque", "blanc", "a1"), ("e1", "g1"): ("petit roque", "blanc", "h1"),
              ("e8", "c8"): ("grand roque", "noir", "a8"), ("e8", "g8"): ("petit roque", "noir", "h8")}

    # Cases où le pion peut sauter pour la prise en passant
    pion_peut_sauter_vers = {"blanc": ["a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4"],
                                  "noir": ["a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5"]}


    @classmethod
    def couleur_adversaire(cls, couleur):
        """Retourne la couleur adverse:  "noir" si "blanc" et vice-versa."""

        assert couleur in cls.couleurs, f"Couleur erronée dans Echiquier.couleur_adversaire: {couleur}"
        return cls.couleurs[couleur]

    def __init__(self, dictionnaire=None):

        # Ces listes pourront être utilisées dans les autres méthodes, par exemple pour valider une position.
        self.chiffres_rangees = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.lettres_colonnes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        # Variables permettant de valider et effectuer le roque
        self.piece_a_bouge = {"e1": False,
                              "e8": False,
                              "a1": False,
                              "a8": False,
                              "h1": False,
                              "h8": False}



        # Variables d'état pour la prise en passant
        # self.pion_vient_de_sauter_une_case = {"a4": False, "a5": False,
        #                                       "b4": False, "b5": False,
        #                                       "c4": False, "c5": False,
        #                                       "d4": False, "d5": False,
        #                                       "e4": False, "e5": False,
        #                                       "f4": False, "f5": False,
        #                                       "g4": False, "g5": False,
        #                                       "h4": False, "h5": False}
        self.pion_vient_de_sauter_une_case = ""


        if not dictionnaire:
            self.initialiser_echiquier_depart()
        else:
            self.dictionnaire_pieces = dictionnaire

    def position_est_valide(self, position):
        """Vérifie si une position est valide (dans l'échiquier). Une position est une concaténation d'une lettre de
        colonne et d'un chiffre de rangée, par exemple 'a1' ou 'h8'.

        Args:
            position (str): La position à valider.

        Returns:
            bool: True si la position est valide, False autrement.

        """
        if len(position) == 2:
            return position[0] in self.lettres_colonnes and position[1] in self.chiffres_rangees
        else:
            return False

    def mettre_a_jour_pion_a_saute(self, position_source, position_cible):
        """Remet à jour, à chaque coup, la variable self.pion_vient_de_sauter_une_case.  Si un pion vient de sauter,
        sa position est mise à True, et toutes les autres remises à False.

        Args:
            position_source(str):  Départ du coup
            position_cible(str):  Arrivée du coup"""

        # Si un pion a sauté au coup avant le coup précédent, il ne vient plus de sauter
        self.pion_vient_de_sauter_une_case = ""

        piece_deplacee = self.dictionnaire_pieces[position_source]

        # Si un pion a sauté: marquer qu'il vient de sauter
        if position_cible in self.pion_peut_sauter_vers[piece_deplacee.couleur]:

            if isinstance(piece_deplacee, Pion) and abs(ord(position_source[1]) - ord(position_cible[1])) == 2:
                self.pion_vient_de_sauter_une_case = position_cible

    def recuperer_piece_a_position(self, position):
        """Retourne la pièce qui est située à une position particulière, reçue en argument. Si aucune pièce n'est
        située à cette position, retourne None.

        Args:
            position (str): La position où récupérer la pièce.

        Returns:
            Piece or None: Une instance de type Piece si une pièce était située à cet endroit, et None autrement.

        """
        if position in self.dictionnaire_pieces.keys():
            return self.dictionnaire_pieces[position]
        else:
            return None

    def couleur_piece_a_position(self, position):
        """Retourne la couleur de la pièce située à la position reçue en argument, et une chaîne vide si aucune
        pièce n'est à cet endroit.

        Args:
            position (str): La position où récupérer la couleur de la pièce.

        Returns:
            str: La couleur de la pièce s'il y en a une, et '' autrement.

        """
        if position in self.dictionnaire_pieces.keys():
            return self.dictionnaire_pieces[position].couleur
        else:
            return ""

    def rangees_entre(self, rangee_debut, rangee_fin):
        """Retourne la liste des rangées qui sont situées entre les deux rangées reçues en argument, exclusivement.
        Attention de conserver le bon ordre.

        Args:
            rangee_debut (str): Le caractère représentant la rangée de début, par exemple '1'.
            rangee_fin (str): Le caractère représentant la rangée de fin, par exemple '4'.

        Exemple:
            >>> echiquier.rangees_entre('1', '1')
            []
            >>> echiquier.rangees_entre('2', '3')
            []
            >>> echiquier.rangees_entre('2', '8')
            ['3', '4', '5', '6', '7']
            >>> echiquier.rangees_entre('8', '3')
            ['7', '6', '5', '4']

        Indice:
            Utilisez self.chiffres_rangees pour obtenir une liste des rangées valides.

        Returns:
            list: Une liste des rangées (en str) entre le début et la fin, dans le bon ordre.

        """
        debut = self.chiffres_rangees.index(rangee_debut)
        fin = self.chiffres_rangees.index(rangee_fin)
        if fin >= debut:
            sens = 1
        else:
            sens = -1
        return self.chiffres_rangees[debut+sens:fin:sens]

    def colonnes_entre(self, colonne_debut, colonne_fin):
        """Retourne la liste des colonnes qui sont situées entre les deux colonnes reçues en argument, exclusivement.
        Attention de conserver le bon ordre.

        Args:
            colonne_debut (str): Le caractère représentant la colonne de début, par exemple 'a'.
            colonne_fin (str): Le caractère représentant la colonne de fin, par exemple 'h'.

        Exemple:
            >>> echiquier.colonnes_entre('a', 'a')
            []
            >>> echiquier.colonnes_entre('b', 'c')
            []
            >>> echiquier.colonnes_entre('b', 'h')
            ['c', 'd', 'e', 'f', 'g']
            >>> echiquier.colonnes_entre('h', 'c')
            ['g', 'f', 'e', 'd']

        Indice:
            Utilisez self.lettres_colonnes pour obtenir une liste des colonnes valides.

        Returns:
            list: Une liste des colonnes (en str) entre le début et la fin, dans le bon ordre.

        """
        debut = self.lettres_colonnes.index(colonne_debut)
        fin = self.lettres_colonnes.index(colonne_fin)
        if fin >= debut:
            sens = 1
        else:
            sens = -1
        return self.lettres_colonnes[debut + sens:fin:sens]

    def chemin_libre_entre_positions(self, position_source, position_cible):
        """Vérifie si la voie est libre entre deux positions, reçues en argument. Cette méthode sera pratique
        pour valider les déplacements: la plupart des pièces ne peuvent pas "sauter" par dessus d'autres pièces,
        il faut donc s'assurer qu'il n'y a pas de pièce dans le chemin.

        On distingue quatre possibilités (à déterminer dans votre code): Soit les deux positions sont sur la même
        rangée, soit elles sont sur la même colonne, soit il s'agit d'une diagonale, soit nous sommes dans une
        situation où nous ne pouvons pas chercher les positions "entre" les positions source et cible. Dans les trois
        premiers cas, on fait la vérification et on retourne True ou False dépendamment la présence d'une pièce ou non.
        Dans la dernière situation, on considère que les positions reçues sont invalides et on retourne toujours False.

        Args:
            position_source (str): La position source.
            position_cible (str): La position cible.

        Warning:
            Il ne faut pas vérifier les positions source et cible, puisqu'il peut y avoir des pièces à cet endroit.
            Par exemple, si une tour "mange" un pion ennemi, il y aura une tour sur la position source et un pion
            sur la position cible.

        Returns:
            bool: True si aucune pièce n'est située entre les deux positions, et False autrement (ou si les positions
                ne permettaient pas la vérification).

        """
        # Générer liste des cases entre source et cible
        positions_inter = self.cases_entre_positions(position_source, position_cible)

        # Vérifier si les positions intermédiaires sont occupées: les cases occupées sont les clés du dictionnaire.
        # Si la liste est vide, retournera True.
        return not [pos for pos in positions_inter if pos in self.dictionnaire_pieces.keys()]

    def cases_occupees_entre_positions(self, position_source, position_cible):
        # Générer liste des cases entre source et cible
        positions_inter = self.cases_entre_positions(position_source, position_cible)

        # Vérifier si les positions intermédiaires sont occupées: les cases occupées sont les clés du dictionnaire.
        # Si la liste est vide, retournera True.
        return [pos for pos in positions_inter if pos in self.dictionnaire_pieces.keys()]

    def cases_entre_positions(self, position_source, position_cible):
        """Compile la liste des cases sur un trajet rectiligne entre deux cases données.

        Args:
            position_source(str):  Position de départ.
            position_cible(str):  Case d'arrivée.

        Returns:
            [str]:  Les cases intermédiaires.  Liste vide si les cases sont adjacentes, ou si le mouvement n'est pas
            rectiligne."""

        # On commence par calculer le décalage horizontal et vertical des deux positions.
        colonne_source = position_source[0]
        rangee_source = position_source[1]
        colonne_cible = position_cible[0]
        rangee_cible = position_cible[1]

        delta_colonne = abs(ord(colonne_source) - ord(colonne_cible))
        delta_rangee = abs(int(rangee_source) - int(rangee_cible))

        # Générer la liste des positions intermédiaires entre les deux positions extrêmes,  3 cas:

        # Déplacement horizontal:  pas de décalage de rangées.
        if delta_rangee == 0:
            positions_entre = [col + rangee_source for col in self.colonnes_entre(colonne_source, colonne_cible)]

        # Déplacement vertical:  pas de décalage de colonnes.
        elif delta_colonne == 0:
            positions_entre = [colonne_source + ran for ran in self.rangees_entre(rangee_source, rangee_cible)]

        # Déplacement diagonal:  décalage rangées et colonnes sont égaux (en valeur absolue!)
        elif delta_rangee == delta_colonne:
            positions_entre = [col + ran for (ran, col) in zip(self.rangees_entre(rangee_source, rangee_cible),
                                                               self.colonnes_entre(colonne_source, colonne_cible))]
        else:
            positions_entre = []

        return positions_entre

    def roque_est_valide(self, position_source, position_cible, exception=True):
        """Vérifie si le roque demandé est permis.

        Args:
            position_source(str):  Départ du roi
            position_cible(str): Arrivée du roi
            exception(bool):  Si False, la fonction retournera un bool.  Si True elle lèvera une exception."""

        assert (position_source, position_cible) in self.roques.keys(), "Le mouvement demandé n'est pas un roque."

        # Le roi ne peut être en échec
        if self.roi_de_couleur_est_en_echec(self.dictionnaire_pieces[position_source].couleur):
            if exception:
                raise RoqueNonAutoriseException("Le roi est en échec.")
            else:
                return False

        # Calcul des paramètres du roque demandé:  type de roque, identification de la tour et des cases intermédiaires
        coup = self.roques[(position_source, position_cible)][0]
        couleur_adverse = Echiquier.couleur_adversaire(self.roques[(position_source, position_cible)][1])
        position_tour = self.roques[(position_source, position_cible)][2]
        cases_inter = self.cases_entre_positions(position_source, position_tour)

        # Les pièces concernées ne doivent pas avoir bougé
        autorisation = not(self.piece_a_bouge[position_source]) and not(self.piece_a_bouge[position_tour])
        if not autorisation:
            if exception:
                raise RoqueNonAutoriseException("Le roi ou la tour a été déplacé.")
            else:
                return False

        # Les cases intermédiaires doivent être libres et non menacées
        for case in cases_inter:
            if case in self.dictionnaire_pieces.keys() or self.position_est_menacee_par(case, couleur_adverse):
                if exception:
                    raise RoqueNonAutoriseException(f"La case {case} est occupée ou menacée.")
                else:
                    return False

        # On ne valide pas si la position source met le roi en échec car ce sera fait dans deplacement_est_valide()
        if exception:
            return coup
        else:
            return bool(coup)

    def prise_en_passant_autorisee(self, position_source, position_cible):
        """Autoriser la prise en passant.

        Args:
            position_source(str):  Case départ du coup
            position_cible(str): Case d'arrivée du coup

        Returns:
            (bool):  True si la prise en passant est autorisée, False autrement"""

        assert not position_cible in self.dictionnaire_pieces.keys(), f"Erreur dans la validation de la prise en passant {position_cible}"

        # Seul un pion peut faire ce mouvement
        piece_jouee = self.dictionnaire_pieces[position_source]
        if not isinstance(piece_jouee, Pion):
            return False

        # Il doit être sur les rangées 4 ou 5
        if piece_jouee.couleur == "noir":
            if not position_source[1] == "4":
                return False
        else:
            if not position_source[1] == "5":
                return False
        # Il doit se déplacer en diagonale, comme pour une prise normale
        if not piece_jouee.peut_faire_une_prise_vers(position_source, position_cible):
            return False

        # Il doit y avoir un pion à prendre, de couleur opposée!
        position_prise = position_cible[0] + position_source[1]
        if not position_prise in self.dictionnaire_pieces.keys() or not isinstance(self.dictionnaire_pieces[position_prise], Pion):
            return False

        if self.dictionnaire_pieces[position_prise].couleur == piece_jouee.couleur:
            return False

        # Ce pion doit venir de faire un saut!
        if self.pion_vient_de_sauter_une_case == position_prise:
            return True
        else:
            raise PriseEnPassantNonAutoriseeException

    def deplacement_est_valide(self, position_source, position_cible, verifier_echec=True):
        """Vérifie si un déplacement serait valide dans l'échiquier actuel. Notez que chaque type de
        pièce se déplace de manière différente, vous voudrez probablement utiliser le polymorphisme :-).

        Règles pour qu'un déplacement soit valide:
            1. Il doit y avoir une pièce à la position source.
            2. La position cible doit être valide (dans l'échiquier).
            3. Si la pièce ne peut pas sauter, le chemin doit être libre entre les deux positions.
            4. S'il y a une pièce à la position cible, elle doit être de couleur différente.
            5. Le déplacement doit être valide pour cette pièce particulière.

        Args:
            position_source (str): La position source du déplacement.
            position_cible (str): La position cible du déplacement.
            verifier_echec (bool): Si True, on va aussi vérifier si le joueur se met lui-même en échec.

        Returns:
            (str): Une chaîne vide si le coup demandé est régulier et autorisé.  Une chaîne de caractère indiquant la
            nature du coup si c'est un coup spécial comme le roque ou la prise en passant.

        Raises:
            PychecsException si le déplacement n'est pas valide.

        """

        # Vérifier si la case source est occupee, extraire la pièce source, si elle est vide, terminer.
        piece_deplacee = self.recuperer_piece_a_position(position_source)
        if not piece_deplacee:
            raise CaseDepartVideException(position_source)

        # Vérifier que la position cible est dans l'échiquier, sinon terminer.
        if not self.position_est_valide(position_cible):
            raise CaseInexistanteException

        # Si la case cible est vide, vérifier que le déplacement est valide pour la pièce source
        if not self.recuperer_piece_a_position(position_cible):

            # Est-ce un roque?
            if (position_source, position_cible) in self.roques.keys():
                try:
                    coup = self.roque_est_valide(position_source, position_cible)
                except RoqueNonAutoriseException as erreur:
                    raise erreur
                else:
                    return coup

            # Ou une prise en passant!!!
            if self.prise_en_passant_autorisee(position_source, position_cible):
                return "en passant"

            if not piece_deplacee.peut_se_deplacer_vers(position_source, position_cible):
                raise DeplacementImpossibleException(piece_deplacee)

        # Si la case cible est occupée, elle doit l'être par une pièce de couleur opposée et on doit la prendre
        else:

            # Si la case cible est occupée:  pièce de couleur opposée
            if self.couleur_piece_a_position(position_source) == self.couleur_piece_a_position(position_cible):
                raise CaseArriveeOccupeeException(position_cible)

            # Prise possible:
            if not piece_deplacee.peut_faire_une_prise_vers(position_source, position_cible):
                raise PriseImpossibleException(piece_deplacee)

        # Si le chemin n'est pas libre et que la pièce ne peut sauter, terminer.
        if not piece_deplacee.peut_sauter and not self.chemin_libre_entre_positions(position_source,
                                                                                    position_cible):
            raise CheminBloqueException(position_source,
                                        position_cible,
                                        self.cases_occupees_entre_positions(position_source, position_cible))

        # Finalement, on ne doit jamais se mettre soi-même en échec
        # On va permettre de sauter cette étape, si la méthode est appelée par se_met_en_echec() car on
        # obtiendra sinon une récursion infinie.
        if (verifier_echec and self.se_met_en_echec(position_source, position_cible)):
            raise CouleurSeMetElleMemeEnEchecException

        # Le déplacement est légal et ce n'est pas un coup spécial on retourne une chaîne vide!
        return ""

    def position_est_menacee_par(self, cible, couleur):
        """Retourne un dictionnaire des pièces d'une couleur donnée, menaçant une case cible.

        Args:
            cible (str):  Position cible à vérifier
            couleur (str):  Couleur des pièces qui menacent la cible.

        Returns:
            (dict):  Dictionnaire des pièces de couleur donnée, pouvant faire une prise à cible avec un chemin dégagé.
            """

        dictionnaire = {}
        for depart, piece in self.dictionnaire_pieces.items():
            if (piece.couleur == couleur
                and
               (piece.peut_sauter or self.chemin_libre_entre_positions(depart, cible))
                and
                piece.peut_faire_une_prise_vers(depart, cible)):
                    dictionnaire[depart] = piece
        return dictionnaire

    def position_est_accessible_par(self, cible, couleur):
        """Compile la liste des pièces d'une couleur donnée, pouvant accéder à une case donnée.  Diffère de la méthode
        position_est_menacee_par car le mouvement du pion condidéré est un simple déplacement et non une prise.

        Args:
            cible(str):  Case à vérifier
            couleur(str):  Couleur des pièces pouvant y accéder.

        Returns:
            (dict):  Dictionnaire des pièces de couleur donnée en argument, pouvant aller sur la case cible."""

        dictionnaire = {}
        for depart, piece in self.dictionnaire_pieces.items():
            if (piece.couleur == couleur
                and
                (piece.peut_sauter or self.chemin_libre_entre_positions(depart, cible))
                and
                piece.peut_se_deplacer_vers(depart, cible)):
                    dictionnaire[depart] = piece
        return dictionnaire

    def position_du_roi_de_couleur(self, couleur):
        """Retrouve le roi d'une couleur donnée dans l'échiquier.
        Args:
            couleur(str):  Couleur du roi cherché.
        Returns:
            (str):  Case sur laquelle se trouve le roi.

        Raises:
            assertionError si le roi est absent de l'échiquier."""

        assert self.roi_de_couleur_est_dans_echiquier(couleur), "Il n'y a pas de roi à mettre en échec."
        for position, piece in self.dictionnaire_pieces.items():
            if isinstance(piece, Roi) and self.couleur_piece_a_position(position) == couleur:
                return position

    def roi_de_couleur_est_en_echec(self, couleur):
        """Compile un dictionnaire des pièces adverses menaçant un roi de couleur donnée.

        Args:
            couleur(str):  Couleur du roi attaqué.

        Returns:
            {str:str}:  Dictionnaire des pièces menaçant le roi."""

        pieces_menacantes = self.position_est_menacee_par(self.position_du_roi_de_couleur(couleur), Echiquier.couleur_adversaire(couleur))
        return pieces_menacantes

    def generer_toutes_les_positions(self):
        """Générateur qui retourne toutes les cases de l'échiquier."""

        for col in self.lettres_colonnes:
            for ran in self.chiffres_rangees:
                yield(col+ran)

    def se_met_en_echec(self, source, cible):
        """Vérifie si le coup joué résulte en un échec pour le joueur.  Crée une copie de l'échiquier pour faire la
        vérification.

        Args:
            source(str):  Case départ du coup
            cible(str):  Case arrivée du coup

        Returns:
            (bool):  True si le coup est illégal."""

        couleur = self.couleur_piece_a_position(source)

        # On crée une copie de l'échiquier, avec une copie du dictionnaire de pièces.
        echiquier_fictif = Echiquier(self.dictionnaire_pieces.copy())

        # On fait le déplacement, mais il ne faut pas appeler se_met_en_echec() récursivement!
        # Donc on utilise la version sans_verifier_echec
        echiquier_fictif.deplacer_sans_verifier_echec(source, cible)

        # Si la liste des menaces est vide on retourne False.
        return bool(echiquier_fictif.roi_de_couleur_est_en_echec(couleur))

    def roi_de_couleur_peut_eviter_echec(self, couleur):
        """Vérifier si le roi peut se déplacer pour esquiver l'attaque.  Retire le roi du jeu, vérifie tous les mouvements
        possibles avec le roi de la couleur attaquée, et regarde si ces mouvements résultent en un échec.

        Args:
            couleur:  Couleur du roi attaqué.

        Returns:
            ([str]):  Liste des cases où le roi peut fuir."""

        position_du_roi = self.position_du_roi_de_couleur(couleur)

        # On enlève temporairement le roi du jeu, sinon il pourrait se "protéger" lui-même!
        roi = self.dictionnaire_pieces.pop(position_du_roi)
        liste_des_deplacements = []

        # On examine toutes les cases du jeu:  si le roi peut se déplacer dans l'une d'elle en sécurité:  ajouter à la
        # liste
        for position in self.generer_toutes_les_positions():

            # Soit la case visée est vide ou occupée par une pièce adverse ET le roi peut s'y déplacer
            if self.couleur_piece_a_position(position) != couleur and roi.peut_se_deplacer_vers(position_du_roi, position):

                # Dans ce cas il faut vérifier que le roi ne se remet pas en échec
                if not self.position_est_menacee_par(position, Echiquier.couleur_adversaire(couleur)):
                    liste_des_deplacements.append(position)

        # Une fois la liste compilée, remettre le roi à sa place, et retourner la liste.
        self.dictionnaire_pieces[position_du_roi] = roi
        return liste_des_deplacements

    def pieces_de_couleur(self, couleur):
        """Générateur qui retourne toutes les pièces d'une couleur donnée."""

        for position, piece in self.dictionnaire_pieces.items():
            if piece.couleur == couleur:
                yield(position)

    def mouvements_possibles_de_la_piece(self, position):
        """Générateur qui retourne tous les mouvements qu'une pièce peut faire sur un échiquier donné, compte tenu des
        autres pièces.  Si le mouvement résulte en un échec, il n'est pas inclus!"""

        for cible in self.generer_toutes_les_positions():
            if cible != position:
                try:
                    coup = self.deplacement_est_valide(position, cible, verifier_echec=True)
                except ReglesException:
                    continue
                else:
                    yield cible, coup

    def mouvements_possibles_de_couleur(self, couleur):

        # On compile la liste de tous les mouvements possibles de couleur:  le roi est pat si aucun mouvement n'est
        # disponible, mais que le roi n'est pas mat.

        liste_des_mouvements_restants = []
        for position_depart in self.pieces_de_couleur(couleur):
            for coup in self.mouvements_possibles_de_la_piece(position_depart):
                liste_des_mouvements_restants.append((position_depart, coup[0], coup[1]))
        return liste_des_mouvements_restants

    def roi_de_couleur_est_pat(self, couleur):
        """Retourne True si le roi est pat:  aucun coup disponible mais non en échec."""

        return not self.mouvements_possibles_de_couleur(couleur) and not self.roi_de_couleur_est_en_echec(couleur)

    def roi_de_couleur_est_mat(self, couleur):
        """Retourne True si le roi est en échec et aucun mouvement n'est disponible."""

        return not self.mouvements_possibles_de_couleur(couleur) and self.roi_de_couleur_est_en_echec(couleur)

    def roi_de_couleur_est_immobilise(self, couleur):
        """Vérifie si un roi donnée a des mouvements possibles et est en échce

        Returns:
            (bool, bool): (Couleur a des coups possibles, roi de couleur est en échec)"""

        return (not bool(self.mouvements_possibles_de_couleur(couleur)), bool(self.roi_de_couleur_est_en_echec(couleur)))

    def resultat_du_coup(self, couleur):
        """Analyse le résultat d'un coup

        Args:
            couleur(str):  Si "blanc" vient de jouer un coup, on analyse le résultat pour "noir".

        Returns:
            (str):  "++" si le roi de couleur est mat, "pat" s'il est pat, "+" s'il est en échec, sinon chaîne vide."""

        resultat = {(True, True): "++", (True, False): "pat", (False, True): "+", (False, False): ""}
        return resultat[self.roi_de_couleur_est_immobilise(couleur)]

    # def roi_de_couleur_est_mat_2(self, couleur):
    #     """Vérifier si le roi de couleur donnée est mat.
    #
    #     Args:
    #         couleur(str):  Couleur du roi attaqué
    #
    #     Returns:
    #         (bool):  True si le roi est mat"""
    #
    #     # Répertorier les pièces menaçant le roi
    #     menaces = self.roi_de_couleur_est_en_echec(couleur)
    #
    #     # Il n'y en a pas:  le roi n'est pas en échec, sortir
    #     if not menaces:
    #         return False
    #
    #     # Vérifier d'abord si le roi peut se déplacer vers une case sécuritaire
    #     if self.roi_de_couleur_peut_eviter_echec(couleur):
    #         return False
    #
    #     # Si le roi ne peut se déplacer et que c'est un échec multiple:  Mat.
    #     if len(menaces) > 1:
    #         return True
    #
    #     # Cas d'un simple échec, une seule pièce menace le roi.  On peut la prendre ou la bloquer.
    #     assert len(menaces) == 1, "Ce doit être un simple échec."
    #     for position_ennemie, piece_ennemie in menaces.items():
    #
    #         # Vérifier si on peut prendre la pièce menaçant le roi
    #         # Liste de ces positions (il doit y en avoir une seulement!)
    #         liste_des_prises_defensives = self.position_est_menacee_par(position_ennemie, couleur)
    #
    #         # Éliminer les prises par le roi sur une case protégée, ou les prises découvrant un autre échec
    #         for case_menace, piece_menace in liste_des_prises_defensives.copy().items():
    #
    #             if self.position_est_menacee_par(case_menace, Echiquier.couleur_adversaire(couleur)):
    #
    #                 # Si le roi lui-même peut prendre la pièce mais que celle-ci est protégée, le coup est interdit
    #                 if isinstance(piece_menace, Roi):
    #                     del liste_des_prises_defensives[case_menace]
    #
    #                 # Si une autre pièce peut faire la prise, vérifier que ce coup ne découvre pas un autre échec
    #                 else:
    #                     try:
    #                         self.se_met_en_echec(case_menace, position_ennemie)
    #                     except CouleurSeMetElleMemeEnEchecException:
    #                         del liste_des_prises_defensives[case_menace]
    #
    #         # Si la liste des prises défensives n'est pas vide:  le roi n'est pas mat.
    #         if bool(liste_des_prises_defensives):
    #             return False
    #
    #         # On peut bloquer la pièce menaçant le roi
    #         cases_a_bloquer = self.cases_entre_positions(self.position_du_roi_de_couleur(couleur), position_ennemie)
    #         for case_a_bloquer in cases_a_bloquer:
    #             pieces_bloquantes = self.position_est_accessible_par(case_a_bloquer, couleur)
    #             if self.position_du_roi_de_couleur(couleur) in pieces_bloquantes.keys():
    #                 pieces_bloquantes.pop(self.position_du_roi_de_couleur(couleur))
    #             if pieces_bloquantes:
    #                 return False
    #
    #     # Échec et mat!
    #     return True

    def parametres_du_roque(self, couleur, type_de_roque):
        """Retourne les positions départ et arrivée de la tour pour un roque demandé."""

        parametres = {("blanc", "grand roque"): ("a1", "d1"),
                      ("blanc", "petit roque"): ("h1", "f1"),
                      ("noir", "grand roque"): ("a8", "d8"),
                      ("noir", "petit roque"): ("h8","f8")}
        return parametres[couleur, type_de_roque]

    def promouvoir(self, position):
        # Déléguée à la classe dérivée car elle nécessite un choix de l'utilisateur
        pass

    def deplacer(self, position_source, position_cible):
        """Joue le coup demandé, en vérifiant s'il est valide.  Dans le cas d'un coup spécial, appelle les méthodes
        appropriées pour valider le coup spécial et le faire.

        Args:
            position_source (str): La position source.
            position_cible (str): La position cible.

        Returns:
            (dict):  Le coup joué et toutes ses info.
            Clés:
            "source":  Position de départ du coup
            "cible":  Position d'arrivée du coup
            "special":  "grand roque", "petit roque", "en passant", "promotion" ou ""
            "jouee":  Unicode de la pièce jouée
            "prise":  Unicode de la pièce prise, sinon ""
            "resultat":  mat: "++" échec: "+" pat: "pat" sinon ""
            "pion a saute": contenu de la variable self.pion_vient_de_sauter_une_case (pour la prise en passant)
            "piece a bouge": contenu de la variable self.piece_a_bouge (pour le roque)

        Raises:
            PychecsException si le déplacement n'est pas valide

        """

        code_coup =  {"source": position_source,
                      "cible": position_cible,
                      "special": "",
                      "jouee": "",
                      "prise" : "",
                      "resultat": "",
                      "pion a saute": None,
                      "piece a bouge": None}
        try:
            code_coup["special"] = self.deplacement_est_valide(position_source, position_cible)
            couleur_active = self.couleur_piece_a_position(position_source)

        # Si le déplacement demandé n'est pas valide, on va propager l'exception jusqu'au contrôleur de l'échiquier
        except PychecsException as erreur:
            raise erreur

        # Déplacement valide:  modifier le dictionnaire des pièces et retourner le coup en notation algébrique
        else:
            if not code_coup["special"]:

                # Mettre à jour la permission de roquer pour le roi, enregistrer l'état de cette permission dansle
                # dictionnaire du coup
                if position_source in self.piece_a_bouge.keys():
                    self.piece_a_bouge[position_source] = True
                    #if isinstance(self.piece_a_bouge[position_source], Roi):
                    #    self.dictionnaire_pieces[position_source].peut_roquer = False

                # Mettre à jour les pions pouvant être pris en passant, enregistrer l'état de cette permission dans
                # le dictionnaire du coup joué
                self.mettre_a_jour_pion_a_saute(position_source, position_cible)

                # Retirer la pièce jouée de la case départ, et l'installer sur la case arrivée.
                piece_jouee = self.dictionnaire_pieces.pop(position_source)
                code_coup["jouee"] = str(piece_jouee)

                if not self.couleur_piece_a_position(position_cible):
                    code_coup["prise"] = ""
                else:
                    code_coup["prise"] = str(self.dictionnaire_pieces.pop(position_cible))
                self.dictionnaire_pieces[position_cible] = piece_jouee

                # Vérifier si on doit faire la promotion du pion
                if (isinstance(piece_jouee, Pion) and
                    ((piece_jouee.couleur == "blanc")and (position_cible[1] == "8") or
                    (piece_jouee.couleur == "noir") and (position_cible[1] == "1"))):
                    code_coup["special"] = "promotion"

            # Grand roque
            if code_coup["special"] == "grand roque":
                piece_jouee = self.dictionnaire_pieces.pop(position_source)
                code_coup["jouee"] = str(piece_jouee)
                assert isinstance(piece_jouee, Roi), "On tente de roquer une autre pièce que le roi."
                piece_jouee.peut_roquer = False
                self.dictionnaire_pieces[position_cible] = piece_jouee
                position_initiale, position_finale = self.parametres_du_roque(piece_jouee.couleur, code_coup["special"])
                self.dictionnaire_pieces[position_finale] = self.dictionnaire_pieces.pop(position_initiale)

            # Petit roque
            elif code_coup["special"] == "petit roque":
                piece_jouee = self.dictionnaire_pieces.pop(position_source)
                code_coup["jouee"] = str(piece_jouee)
                assert isinstance(piece_jouee, Roi), "On tente de roquer une autre pièce que le roi."
                piece_jouee.peut_roquer = False
                self.dictionnaire_pieces[position_cible] = piece_jouee
                position_initiale, position_finale = self.parametres_du_roque(piece_jouee.couleur, code_coup["special"])
                self.dictionnaire_pieces[position_finale] = self.dictionnaire_pieces.pop(position_initiale)

            # Prise en passant
            elif code_coup["special"] == "en passant":
                piece_jouee = self.dictionnaire_pieces.pop(position_source)
                code_coup["jouee"] = str(piece_jouee)
                position_prise = position_cible[0] + position_source[1]
                code_coup["prise"] = str(self.dictionnaire_pieces.pop(position_prise))
                self.dictionnaire_pieces[position_cible] = piece_jouee

        # Verifier le résultat du coup sur le roi adverse
        code_coup["resultat"] = self.resultat_du_coup(self.couleur_adversaire(couleur_active))

        # Mais attention:  il faut aussi s'assurer que le roi qui vient de jouer ne serait pas pat!!!
        #if self.roi_de_couleur_est_pat(couleur_active):
        #   code_coup["resultat"] = "pat"

        # Enregistrer les autorisations à jour pour les coups spéciaux: roque et prise en passant
        code_coup["piece a bouge"] = self.piece_a_bouge
        code_coup["pion a saute"] = self.pion_vient_de_sauter_une_case

        print(code_coup)
        return code_coup

    def deplacer_sans_verifier_echec(self, position_source, position_cible):
        """Effectue le déplacement d'une pièce en position source, vers la case en position cible. Vérifie d'abord
        si le déplacement est valide, et ne fait rien (puis retourne False) dans ce cas. Si le déplacement est valide,
        il est effectué (dans l'échiquier actuel) et la valeur True est retournée.

        Args:
            position_source (str): La position source.
            position_cible (str): La position cible.

        Raises:
            PychecsException si le déplacement n'est pas valide

        """

        try:
            self.deplacement_est_valide(position_source, position_cible, verifier_echec=False)

        # Si le déplacement demandé n'est pas valide, on va propager l'exception jusqu'au contrôleur de l'échiquier
        except PychecsException as erreur:
            raise erreur

        # Déplacement valide:  modifier le dictionnaire des pièces
        else:
            self.dictionnaire_pieces[position_cible] = self.dictionnaire_pieces.pop(position_source)

    def roi_de_couleur_est_dans_echiquier(self, couleur):
        """Vérifie si un roi de la couleur reçue en argument est présent dans l'échiquier.

        Args:
            couleur (str): La couleur (blanc ou noir) du roi à rechercher.

        Returns:
            bool: True si un roi de cette couleur est dans l'échiquier, et False autrement.

        """
        for piece_sur_echiquier in self.dictionnaire_pieces.values():
            if isinstance(piece_sur_echiquier, Roi) and piece_sur_echiquier.couleur == couleur:
                return True
        return False

    def initialiser_echiquier_depart(self):
        """Initialise l'échiquier à son contenu initial. Pour faire vos tests pendant le développement,
        nous vous suggérons de vous fabriquer un échiquier plus simple, en modifiant l'attribut
        dictionnaire_pieces de votre instance d'Echiquier.

        """
        self.dictionnaire_pieces = {
            'a1': Tour('blanc'),
            'b1': Cavalier('blanc'),
            'c1': Fou('blanc'),
            'd1': Dame('blanc'),
            'e1': Roi('blanc'),
            'f1': Fou('blanc'),
            'g1': Cavalier('blanc'),
            'h1': Tour('blanc'),
            'a2': Pion('blanc'),
            'b2': Pion('blanc'),
            'c2': Pion('blanc'),
            'd2': Pion('blanc'),
            'e2': Pion('blanc'),
            'f2': Pion('blanc'),
            'g2': Pion('blanc'),
            'h2': Pion('blanc'),
            'a7': Pion('noir'),
            'b7': Pion('noir'),
            'c7': Pion('noir'),
            'd7': Pion('noir'),
            'e7': Pion('noir'),
            'f7': Pion('noir'),
            'g7': Pion('noir'),
            'h7': Pion('noir'),
            'a8': Tour('noir'),
            'b8': Cavalier('noir'),
            'c8': Fou('noir'),
            'd8': Dame('noir'),
            'e8': Roi('noir'),
            'f8': Fou('noir'),
            'g8': Cavalier('noir'),
            'h8': Tour('noir'),
        }

    def __repr__(self):
        """Affiche l'échiquier à l'écran. Utilise des codes Unicode, si la constante UTILISER_UNICODE est à True dans
        le module piece. Sinon, utilise seulement des caractères standards.

        Vous n'avez pas à comprendre cette partie du code.

        """
        chaine = ""
        if UTILISER_UNICODE:
            chaine += '  \u250c' + '\u2500\u2500\u2500\u252c' * 7 + '\u2500\u2500\u2500\u2510\n'
        else:
            chaine += '  +' + '----+' * 8 + '\n'

        for rangee in range(7, -1, -1):
            if UTILISER_UNICODE:
                chaine += '{} \u2502 '.format(self.chiffres_rangees[rangee])
            else:
                chaine += '{} | '.format(self.chiffres_rangees[rangee])
            for colonne in range(8):
                piece = self.dictionnaire_pieces.get('{}{}'.format(self.lettres_colonnes[colonne], self.chiffres_rangees[rangee]))
                if piece is not None:
                    if UTILISER_UNICODE:
                        chaine += str(piece) + ' \u2502 '
                    else:
                        chaine += str(piece) + ' | '
                else:
                    if UTILISER_UNICODE:
                        chaine += '  \u2502 '
                    else:
                        chaine += '   | '

            if rangee != 0:
                if UTILISER_UNICODE:
                    chaine += '\n  \u251c' + '\u2500\u2500\u2500\u253c' * 7 + '\u2500\u2500\u2500\u2524\n'
                else:
                    chaine += '\n  +' + '----+' * 8 + '\n'

        if UTILISER_UNICODE:
            chaine += '\n  \u2514' + '\u2500\u2500\u2500\u2534' * 7 + '\u2500\u2500\u2500\u2518\n'
        else:
            chaine += '\n  +' + '----+' * 8 + '\n'

        chaine += '    '
        for colonne in range(8):
            if UTILISER_UNICODE:
                chaine += self.lettres_colonnes[colonne] + '   '
            else:
                chaine += self.lettres_colonnes[colonne] + '    '
        chaine += '\n'
        return chaine


if __name__ == '__main__':

    def test_couleur_adversaire():
        assert Echiquier.couleur_adversaire("blanc") == 'noir'
        assert Echiquier.couleur_adversaire("noir") == 'blanc'
        try:
            Echiquier.couleur_adversaire("vert")
        except AssertionError:
            pass
        else:
            raise Exception

    def test_cases_entre_positions():
        obj = Echiquier()
        assert obj.cases_entre_positions("a1", "a2") == []
        assert obj.cases_entre_positions("d5", "e6") == []
        assert obj.cases_entre_positions("e2", "f2") == []
        assert obj.cases_entre_positions("a1", "e5") == ["b2", "c3", "d4"]
        assert obj.cases_entre_positions("f7", "f1") == ["f6", "f5", "f4", "f3", "f2"]
        assert obj.cases_entre_positions("d6", "g7") == []

    def test_chemin_libre_entre_positions():
        obj = Echiquier(dictionnaire={"b2": Pion("noir"), "f4": Pion("noir"), })
        assert obj.chemin_libre_entre_positions("a1", "a2") == True
        assert obj.chemin_libre_entre_positions("d5", "e6") == True
        assert obj.chemin_libre_entre_positions("e2", "f2") == True
        assert obj.chemin_libre_entre_positions("a1", "e5") == False
        assert obj.chemin_libre_entre_positions("f7", "f1") == False
        assert obj.chemin_libre_entre_positions("d6", "g7") == True
        assert obj.chemin_libre_entre_positions("b3", "b8") == True
        assert obj.chemin_libre_entre_positions("a4", "h4") == False
        assert obj.chemin_libre_entre_positions("a5", "h5") == True
        assert obj.chemin_libre_entre_positions("b3", "g8") == True

    def test_position_est_menacee_par():
        obj = Echiquier(dictionnaire={"b2": Pion("blanc"),
                                      "b1": Cavalier("blanc"),
                                      "g5": Fou("blanc"),
                                      "f7": Pion("noir"),
                                      "h8": Tour("noir"),
                                      "a6": Dame("noir"),
                                      "d8": Roi("noir"),
                                      "h6": Pion("noir")})

        assert obj.position_est_menacee_par("b3", "blanc") == {}
        assert obj.position_est_menacee_par("b3", "noir") == {}
        assert not obj.position_est_menacee_par("a3", "blanc") == {}
        assert not obj.position_est_menacee_par("a3", "noir") == {}
        assert not obj.position_est_menacee_par("d2", "blanc") == {}
        assert obj.position_est_menacee_par("d2", "noir") == {}
        assert obj.position_est_menacee_par("c5", "noir") == {}
        assert obj.position_est_menacee_par("h3", "noir") == {}
        assert not obj.position_est_menacee_par("g5", "noir") == {}
        print(obj.position_est_menacee_par("e6", "noir"))
        print(obj.position_est_menacee_par("d2", "blanc"))

    def test_position_roi_de_couleur():
        obj = Echiquier({"b6": Roi("noir"),
                         "h3": Roi("blanc"),
                         "d8": Dame("noir"),
                         "f2": Fou("blanc")})
        assert obj.position_du_roi_de_couleur("noir") == "b6"
        assert obj.position_du_roi_de_couleur("blanc") == "h3"

    def test_roi_de_couleur_est_en_echec():
        obj = Echiquier({"d8": Roi("noir"),
                         "c7": Pion("noir"),
                         "e7": Pion("noir"),
                         "c6": Cavalier("blanc"),
                         "f6": Fou("blanc"),
                         "d5": Dame("blanc"),
                         "d3": Tour("noir"),
                         "c2": Cavalier("noir"),
                         "d2": Pion("noir"),
                         "d1": Roi("blanc"),
                         "e1": Fou("noir")})

        assert not obj.roi_de_couleur_est_en_echec("noir") == {}
        assert obj.roi_de_couleur_est_en_echec("blanc") == {}
        print(obj.roi_de_couleur_est_en_echec("noir"))
        print(obj.roi_de_couleur_est_en_echec("blanc"))

    def test_roi_de_couleur_peut_eviter_echec():
        obj = Echiquier({"d8": Roi("noir"),
                         "c7": Pion("noir"),
                         "e7": Pion("noir"),
                         "c6": Cavalier("blanc"),
                         "f6": Fou("blanc"),
                         "d5": Dame("blanc"),
                         "d3": Tour("noir"),
                         "c2": Cavalier("noir"),
                         "b3": Pion("noir"),
                         "d1": Roi("blanc"),
                         "e1": Fou("noir")})

        print(obj.roi_de_couleur_peut_eviter_echec("noir"))
        print(obj.roi_de_couleur_peut_eviter_echec("blanc"))

    def test_roi_de_couleur_est_mat():

        obj = Echiquier({"h8": Roi("noir", False),
                         "h7": Tour("blanc"),
                         "f6": Cavalier("blanc")})

        assert obj.roi_de_couleur_est_mat("noir")

        obj = Echiquier({'a7': Tour('blanc'),
                         "b8": Tour("blanc"),
                         "g8": Roi("noir", False),
                         })

        assert obj.roi_de_couleur_est_mat("noir")

        obj = Echiquier({"d7": Tour("noir"),
                         "d6": Pion("noir"),
                         "d5": Cavalier("noir"),
                         "e6": Roi("noir", False),
                         "e4": Dame("blanc"),
                         "f1": Tour("blanc")})

        assert obj.roi_de_couleur_est_mat("noir")

    def test_se_met_en_echec():
        obj = Echiquier({"d4": Dame("blanc"),
                         "d6": Roi("noir")})
        try:
            obj.deplacement_est_valide("d6", "d7")
        except CouleurSeMetElleMemeEnEchecException:
            print("d7")
        try:
            obj.deplacement_est_valide("d6", "d5")
        except CouleurSeMetElleMemeEnEchecException:
            print("d5")
        try:
            obj.deplacement_est_valide("d6", "c5")
        except CouleurSeMetElleMemeEnEchecException:
            print("c5")
        try:
            obj.deplacement_est_valide("d6", "e5")
        except CouleurSeMetElleMemeEnEchecException:
            print("e5")
        try:
            obj.deplacement_est_valide("d6", "c6")
        except CouleurSeMetElleMemeEnEchecException:
            print("c6")
        try:
            obj.deplacement_est_valide("d6", "c7")
        except CouleurSeMetElleMemeEnEchecException:
            print("c7")
        try:
            obj.deplacement_est_valide("d6", "e7")
        except CouleurSeMetElleMemeEnEchecException:
            print("e7")
        try:
            obj.deplacement_est_valide("d6", "e6")
        except CouleurSeMetElleMemeEnEchecException:
            print("e6")
        obj = Echiquier({"d4": Dame("blanc"),
                         "d6": Roi("noir"),
                         "d5": Cavalier("noir")})
        try:
            obj.deplacement_est_valide("d5", "c7")
        except CouleurSeMetElleMemeEnEchecException:
            print("c7")

        obj = Echiquier({"d4": Dame("blanc"),
                         "d6": Roi("noir"),
                         "d5": Tour("noir")})
        try:
            obj.se_met_en_echec("d5", "e5")
        except CouleurSeMetElleMemeEnEchecException:
            print("e5")
        try:
            obj.se_met_en_echec("d5", "d4")
        except CouleurSeMetElleMemeEnEchecException:
            print("d4")

    def test_mat_anormal():
        obj=Echiquier({'d8': Dame("noir"),
                       "e8": Roi("noir"),
                       "f8": Fou("noir"),
                       "d7": Cavalier("blanc"),
                       "a4": Fou("blanc"),
                       "e1": Roi("blanc")})

        print(obj.roi_de_couleur_est_mat("noir"))
        obj.deplacer("d7", "f6")
        print(obj.roi_de_couleur_est_mat("noir"))

    def test_prise_en_passant():
        obj = Echiquier({"e5": Pion("blanc"),
                         "d5": Pion("noir")})
        obj.pion_vient_de_sauter_une_case["d5"] = True
        assert obj.prise_en_passant_autorisee("e5", "d6")

    def test_roi_de_couleur_est_pat():
        obj = Echiquier({"a8": Roi("noir", False),
                         "b6": Dame("blanc")})

        assert obj.roi_de_couleur_est_pat("noir")

        obj = Echiquier({"h8": Roi("noir", False),
                         "f7": Roi("blanc", False),
                         "f5": Fou("blanc")})
        assert obj.roi_de_couleur_est_pat("noir")

    def test_roi_de_couleur_est_mat_2():

        obj = Echiquier({"h8": Roi("noir", False),
                         "h7": Tour("blanc"),
                         "f6": Cavalier("blanc")})

        assert obj.roi_de_couleur_est_mat_2("noir")

        obj = Echiquier({'a7': Tour('blanc'),
                         "b8": Tour("blanc"),
                         "g8": Roi("noir", False),
                         })

        assert obj.roi_de_couleur_est_mat_2("noir")

        obj = Echiquier({"d7": Tour("noir"),
                         "d6": Pion("noir"),
                         "d5": Cavalier("noir"),
                         "e6": Roi("noir", False),
                         "e4": Dame("blanc"),
                         "f1": Tour("blanc")})

        assert obj.roi_de_couleur_est_mat_2("noir")


    # Exemple de __main__ qui crée un nouvel échiquier, puis l'affiche à l'éran. Vous pouvez ajouter des instructions ici
    # pour tester votre échiquier, mais n'oubliez pas que le programme principal est démarré en exécutant __main__.py.
    test_couleur_adversaire()
    test_cases_entre_positions()
    test_chemin_libre_entre_positions()
    test_position_est_menacee_par()
    test_position_roi_de_couleur()
    test_roi_de_couleur_est_en_echec()
    test_roi_de_couleur_peut_eviter_echec()
    test_se_met_en_echec()
    test_roi_de_couleur_est_mat()
    test_mat_anormal()
    test_prise_en_passant()
    test_roi_de_couleur_est_pat()

