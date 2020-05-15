import tkinter as tk
from pychecs2.echecs.echiquier import Echiquier
from pychecs2.interface.PychecsException import PychecsException, CaseDepartVideException, ClicHorsEchiquierException
from pychecs2.interface.PychecsException import TourException
from pychecs2.interface.AideContextuellePychecs import AIDE_CONTEXTUELLE
from pychecs2.echecs.piece import Dame, Tour, Fou, Cavalier, Constructeur_de_piece


########################################################################################################################
# Objets graphiques utilisés pour gérer la promotion du pion
########################################################################################################################

class BoutonPiece(tk.Button):
    """Widget auxiliaire pour afficher des boutons avec un caractère de pièce dessus."""

    def __init__(self, master, piece):
        tk.Button.__init__(self, master)
        car = str(piece)
        self.configure(text=car, font=("default", 50, "normal"), highlightcolor="blue")


class FenetreChoixPromotion(tk.Toplevel):
    """Widget qui affichera une fenêtre pop-up pour demander au joueur de choisir l'une des quatre pièces suivantes:
    Dame, Tour, Cavalier et Fou, d'une couleur donnée.  Lorsque le choix est confirmé, la fenêtre disparait.
    Utilisé pour la promotion du pion!

    Attributs:

    master(widget):  Widget maître, un Canvasechiquier
    code_piece_choisie(StringVar):  Contiendra le choix du joueur
    couleur (StringVar): La couleur de la pièce"""

    def __init__(self, master, couleur, **kwargs):

        # Le widget est une fenêtre qui sera esclave d'un échiquier
        tk.Toplevel.__init__(self, master)

        self.master = master
        self.master.passer_en_mode_attente()
        self.transient(self.master)
        self.code_piece_choisie = tk.StringVar()
        self.couleur = tk.StringVar()
        self.couleur.set(couleur)

        # Frames contenant les widgets esclaves, pour la mise en page
        self.frameMessage = tk.Frame(self)
        self.frameBouton = tk.Frame(self)
        self.frameChoix = tk.Frame(self)

        # Les boutons et leurs handlers
        self.boutonDame = BoutonPiece(self.frameBouton, Dame(couleur))
        self.boutonDame.configure(command=lambda: self.decider("D"))

        self.boutonTour = BoutonPiece(self.frameBouton, Tour(couleur))
        self.boutonTour.configure(command=lambda: self.decider("T"))

        self.boutonFou = BoutonPiece(self.frameBouton, Fou(couleur))
        self.boutonFou.configure(command=lambda: self.decider("F"))

        self.boutonCavalier = BoutonPiece(self.frameBouton, Cavalier(couleur))
        self.boutonCavalier.configure(command=lambda: self.decider("C"))

        self.bouton_ok = tk.Button(self.frameChoix, text="Choisir", font=("default", 25, "normal"),
                                   state=tk.DISABLED, command=self.disparaitre)

        self.messagePromotion = tk.Label(self.frameMessage, text="Vous devez choisir une pièce pour promouvoir le pion",
                                         font=("default", 25, "normal"))

        self.boutons = {"D": self.boutonDame,
                        "T": self.boutonTour,
                        "F": self.boutonFou,
                        "C": self.boutonCavalier}

        # Assemblage de la fenêtre
        self.messagePromotion.pack()
        self.boutonDame.pack(side=tk.LEFT, padx=20)
        self.boutonTour.pack(side=tk.LEFT, padx=20)
        self.boutonFou.pack(side=tk.LEFT, padx=20)
        self.boutonCavalier.pack(side=tk.LEFT, padx=20)
        self.bouton_ok.pack(padx=20)

        self.frameMessage.pack(side=tk.TOP, padx=20, pady=20)
        self.frameBouton.pack(side=tk.BOTTOM, padx=20, pady=20)
        self.frameChoix.pack(side=tk.BOTTOM, padx=20, pady=20)

        # On ne veut pas que le joueur puisse cliquer sur l'échiquier quand la fenêtre est affichée
        self.focus_set()
        self.grab_set()

    def disparaitre(self):
        """Remettre l'échiquier en mode actif avant de disparaître"""
        self.master.passer_en_mode_actif()
        self.destroy()

    def decider(self, piece):
        """Le joueur choisit une pièce, mais le choix n'est pas encore confirmé."""

        # Changer la couleur du bouton pressé
        for code, bouton in self.boutons.items():
            if code == piece:
                self.boutons[code].config(state=tk.ACTIVE)
            else:
                self.boutons[code].config(state=tk.NORMAL)

        # Changer la variable à retourner et activer le bouton de confirmation
        self.code_piece_choisie.set(piece)
        self.bouton_ok.config(state=tk.ACTIVE)

    def apparaitre(self):
        """Fonction interface avec laquelle on invoque la fenêtre.  Sera appelée par le maître."""

        self.deiconify()
        self.wait_window()
        return self.code_piece_choisie.get()


########################################################################################################################
# Widget gérant l'interaction d'un échiquier avec le joueur par le biais de la souris
########################################################################################################################

class CanvasEchiquier(tk.Canvas, Echiquier):
    """Widget permettant d'afficher un échiquier et d'interagir avec, par le biais de la souris.
    Attributs:

    dictionnaire_graphique(dict):  Dictonnaire donnant, pour chaque case occupée, l'index du dessin de la pièce sur
    cette case.

    dictionnaire_cases(dict):  Dictionnaire donnant pour toutes les positions de l'échiquier l'index du dessin de la
    case.

    message(StringVar):  Contenu de la banderole indiquant les principales informations sur la partie:  qui a le trait
    et si on est en échec.

    joueur_actif(str):  Qui a le trait: "blanc" ou "noir"

    coup_joue (dict):  Le dernier coup joué.

    nombre_de_coups_joues (intVar):  Compte les coups.  Utilisé pour signaler au maitre qu'un coup a été joué.  Ne
    compte pas fidèlement les coups car n'est pas resetté par une annulation.

    partie_modifiee (BooleanVar):  True si un coup a été joué depuis la dernière sauvegarde.

    partie_terminee (BooleanVar):  True dès qu'un coup résulte en un mat ou un pat ou s'il y a abandon.

    gagnee (bool):  True si la partie est terminée sur un mat ou un abandon, False si la partie n'est pas terminée ou
    se termine sur une nulle.

    message_erreur(BooleanVar):  Contenu de la banderole indiquant une tentative de coup illégal ou autre erreur.

    message_aide_contextuelle (str):  Message d'aide plus détaillé.

    n_pixels_par_case(int):  Grandeur des cases en pixels
    taille_piece(int):  Grandeur des pièces en pixels, environ 60% de la case.
    n_lignes(int):  8 rangées
    n_colonnes(int): 8 colonnes
    x_coin, y_coin (int):  offset du coin supérieur gauche de l'échiquier par-rapport au coin supérieur gauche du
    canvas. Devrait-être au-moins égal à n_pixels_par_case

    piece_selectionnee(bool):  True si une pièce a été sélectionnée par le joueur
    piece_a_deplacer(objet Piece):  La pièce en question
    case_depart(str):  Case départ du prochain coup
    case_arrivee(str):  Case arrivée du prochain coup
    """

    joueurs = {"blanc": "noir", "noir": "blanc"}
    modes = {"actif": "attente", "attente": "actif"}

    #############################################################################
    # CONSTRUCTEUR
    #############################################################################

    def __init__(self, maitre=None, n_pixels_par_case=50,
                 dictionnaire=None, joueur_actif=None,
                 option_chrono=False, option_aide=False,
                 **kwargs):
        """Constructeur:

        Args:
            maitre (widget):  Widget qui contiendra notre échiquier.
            n_pixels_par_case (int):  Taille des cases en pixels.
            x_coin(int):  Coordonnée x du coin supérieur gauche de l'échiquier sur le canvas.
            y_coin(int):  Coordonnée y du coin supérieur gauche de l'échiquier sur le canvas.
            **kwargs:  Options du canvas."""

        # Constructeurs des parents.
        tk.Canvas.__init__(self, maitre, **kwargs)
        Echiquier.__init__(self, dictionnaire)

        # Structure de données contenant les objets graphiques sur le canvas.
        self.dictionnaire_graphique = {}
        self.dictionnaire_cases = {}

        # Variable contenant les messages à l'utilisateur et le statut de la partie, en cours ou gagnée

        self.message = tk.StringVar()

        if not joueur_actif:
            self.joueur_actif = "blanc"
            self.message.set("Début de la partie:  au tour des blancs de jouer.")
        else:
            self.joueur_actif = joueur_actif
            self.message.set(f"Au tour des {self.joueur_actif}s de jouer.")

        ##########################
        # Le dernier coup complété
        ##########################

        self.coup_joue = {}

        ##############################################################
        # Compteur de coups.  Sera suivi dans le contrôleur de partie
        ##############################################################

        self.nombre_de_coups_joues = tk.IntVar()
        self.nombre_de_coups_joues.set(0)

        ####################################################
        # Semaphore avertissant le controleur d'un évènement
        ####################################################

        self.evenement = tk.StringVar()
        self.evenement.set("debut")

        self.exception = None

        ##################################################
        # Paramètres géométriques du dessin de l'échiquier
        ##################################################

        self.n_pixels_par_case = n_pixels_par_case
        self.taille_pieces = int(round(self.n_pixels_par_case * 60 / 100))
        self.n_lignes = 8
        self.n_colonnes = 8
        self.x_coin = 2 * self.n_pixels_par_case
        self.y_coin = 2 * self.n_pixels_par_case

        ############################################################################################
        # Informations sur le mouvement demandé:  utilisé dans clic-souris pour la sélection du coup
        ############################################################################################

        self.piece_selectionnee = False
        self.piece_a_deplacer = None
        self.case_depart = ""
        self.case_arrivee = ""

        #######################################################################
        # Dessin initial de l'échiquier avec les pièces à leurs place de départ
        #######################################################################

        self.dessiner_cases()
        self.dessiner_reperes()
        self.initialiser_canvas_depart()

        # Lier l'évenement clic-souris à la méthode correspondante
        self.bind("<Button-1>", self.clic_souris)

        # Cette variable sera utilisée par un controleur de partie pour forcer l'échiquier à attendre le prochain
        # coup lorsqu'on jouera contre un adversaire.  Deux valeurs seront possible: "actif" et "attente".
        # En mode "attente" l'échiquier ne réagira plus aux clics de souris.

        self.mode = "actif"

        # Options de jeu:  chronomètre et afficher les mouvements possibles
        self.option_chrono = option_chrono
        self.option_aide = option_aide

        ##############################################################################
        # Ce dict contient les cases surlignées pour indiquer les mouvements possibles
        ##############################################################################

        self.cases_modifiees_pour_aider = {}

    ####################################################################################################################
    # FIN DU CONSTRUCTEUR
    ####################################################################################################################

    #######################################################################
    # Interface avec le contrôleur
    #######################################################################

    def passer_en_mode_actif(self):
        self.mode = "actif"

    def passer_en_mode_attente(self):
        self.update()
        self.mode = "attente"

    def basculer_mode(self):
        self.mode = self.modes[self.mode]

    def joueur_inactif(self):
        return self.joueurs[self.joueur_actif]

    def basculer_joueur_actif(self):
        """Bascule le joueur actif de blanc à noir et de noir à blanc."""
        self.joueur_actif = self.joueur_inactif()

    def activer(self, couleur):
        """Méthode interface permettant au contrôleur d'imposer le joueur actif"""
        self.joueur_actif = couleur

    def dernier_coup(self):
        return self.coup_joue

    def reveler_exception(self):
        return self.exception

    ####################################################################################################################
    # Dessin des pièces et des cases
    ####################################################################################################################

    def initialiser_canvas_depart(self):
        """Initialiser le dictionnaire contenant les objets graphiques représentant les pièces sur l'échiquier.  Nous
        aurons donc deux dictionnaires, self.dictionnaire_pieces qui est la représentation interne du jeu, et
        self.dictionnaire_graphique qui est le reflet du premier, pour la représentation à l'écran."""

        for position, piece in self.dictionnaire_pieces.items():
            self.dictionnaire_graphique[position] = self.dessiner_piece(piece, position)

    def rangs_vers_position(self, numero_rangee, numero_colonne):
        return self.lettres_colonnes[numero_colonne] + self.chiffres_rangees[self.n_lignes - numero_rangee - 1]

    def dessiner_cases(self):
        """Dessine l'échiquier.  Les cases seront stockées dans une structure de données permettant de les retrouver et
        les modifier au besoin."""

        for ligne in range(self.n_lignes):
            ulc_x = ligne * self.n_pixels_par_case + self.x_coin
            for colonne in range(self.n_colonnes):
                ulc_y = colonne * self.n_pixels_par_case + self.y_coin

                if (ligne + colonne) % 2:
                    couleur = "dark gray"
                else:
                    couleur = "white"

                self.dictionnaire_cases[self.rangs_vers_position(colonne, ligne)] = self.create_rectangle(ulc_x,
                                                                                                          ulc_y,
                                                                                                          ulc_x + self.n_pixels_par_case,
                                                                                                          ulc_y + self.n_pixels_par_case,
                                                                                                          fill=couleur)

    def dessiner_reperes(self):
        """Dessine les lettres et les chiffres autour de l'échiquier."""

        offset = int(round(self.n_pixels_par_case / 2))
        for ligne in range(self.n_lignes):
            x = self.x_coin - offset
            y = self.y_coin + offset + ligne * self.n_pixels_par_case
            self.create_text(x, y, font=("default", -self.taille_pieces), text=self.chiffres_rangees[-1 - ligne])
        for colonne in range(self.n_colonnes):
            x = self.x_coin + offset + colonne * self.n_pixels_par_case
            y = self.y_coin + self.n_colonnes * self.n_pixels_par_case + offset
            self.create_text(x, y, font=("default", -self.taille_pieces), text=self.lettres_colonnes[colonne])

    def coordonnees_cases(self, position):
        """Pour une position donnée, retourne les coordonnées du coin supérieur gauche de la case.

        Args:
            position (str):  Identifiant de la case

        Returns:
            (int, int):  Coordonnées x, y du coin supérieur gauche de la case.

        Raises:
            AssertionError pour une position invalide."""

        assert self.position_est_valide(position), self.message.set(
            f"Code de position non reconnu dans coordonnees_cases: {position}")
        return ((ord(position[0]) - ord("a")) * self.n_pixels_par_case + self.x_coin,
                (self.n_lignes - int(position[1])) * self.n_pixels_par_case + self.y_coin)

    def coordonnees_centre_case(self, position):
        """Pour une case donnée, retourne les coordonnées x,y du centre de la case.

        Args:
            position(str):  Identifiant de case

        Raises:
            AssertionError si la position en argument est invalide."""

        x, y = self.coordonnees_cases(position)
        offset = int(round(self.n_pixels_par_case / 2))
        return x + offset, y + offset

    def dessiner_piece(self, piece, position):
        """Ajoute un objet graphique correspondant à une pièce du jeu sur l'échiquier.

        Args:
            piece (objet Piece):  Pièce à dessiner
            position(str):  Case où place le dessin.

        Returns:
            (int):  Le numéro d'identification du dessin de la pièce sur le canvas."""

        x, y = self.coordonnees_centre_case(position)
        return self.create_text(x, y, text=str(piece), font=("default", -self.taille_pieces), disabledfill="red")

    def coordonnees_est_dans_echiquier(self, x, y):
        """Retourne True si le point x, y est sur la surface de l'échiquier."""
        return self.x_coin < x < self.x_coin + self.n_colonnes * self.n_pixels_par_case and self.y_coin < y < self.y_coin + self.n_lignes * self.n_pixels_par_case

    def coordonnees_vers_position(self, x, y):
        """Identifie la case de l'échiquier contenant le point x, y

        Args:
            x(int):  Coordonnée x
            y(int):  Coordonnée y

        Returns:
            (str):  L'identifiant de la case.

        Raises:
            AssertionError si le point n'est pas sur l'échiquier."""

        if self.coordonnees_est_dans_echiquier(x, y):
            return (self.lettres_colonnes[(x - self.x_coin) // self.n_pixels_par_case] +
                    self.chiffres_rangees[-1 - (y - self.y_coin) // self.n_pixels_par_case])
        raise ClicHorsEchiquierException

    def deplacer_de_case_a_case(self, position_source, position_cible):
        """Efface une pièce de la case source et la dessine à la case cible."""

        # Calculer le déplacement à faire sur l'échiquier
        xinit, yinit = self.coordonnees_centre_case(position_source)
        xfin, yfin = self.coordonnees_centre_case(position_cible)
        dx, dy = xfin - xinit, yfin - yinit

        # Déplacer la pièce
        self.move(self.dictionnaire_graphique[position_source], dx, dy)

        # Mettre le dictionnaire graphique à jour
        self.dictionnaire_graphique[position_cible] = self.dictionnaire_graphique.pop(position_source)

    def effacer_la_piece_a_position(self, position):
        self.delete(self.dictionnaire_graphique[position])
        del self.dictionnaire_graphique[position]

    def effacer_echiquier(self):
        for position in self.dictionnaire_graphique.copy().keys():
            self.effacer_la_piece_a_position(position)

    def mise_a_jour_echiquier(self):
        self.effacer_echiquier()
        self.initialiser_canvas_depart()
        self.update()

    def selectionner_la_case(self, position):
        assert position in self.dictionnaire_cases.keys(), "Argument position erroné dans selectionner_la_case"

        self.itemconfig(self.dictionnaire_cases[position], width=2, outline="blue")

    def deselectionner_la_case(self, position):
        assert position in self.dictionnaire_cases.keys(), "Argument position erroné dans deselectionner_la_case"

        self.itemconfig(self.dictionnaire_cases[position], width=1, outline="black")

    def selectionner_la_piece(self, position):
        assert position in self.dictionnaire_graphique.keys(), "Argument erroné dans selectionner_la_piece"
        self.itemconfig(self.dictionnaire_graphique[position],
                        font=("default", -int(round(self.taille_pieces * 1.3)), "bold"),
                        fill="blue")
        if self.option_aide:
            self.remettre_a_zero_les_cases_modifiees()
            self.montrer_les_mouvements_possibles_a_partir_de(position)

    def deselectionner_la_piece(self, position):
        assert position in self.dictionnaire_graphique.keys(), "Argument erroné dans deselectionner_la_piece"
        self.itemconfig(self.dictionnaire_graphique[position],
                        font=("default", -self.taille_pieces, "normal"),
                        fill="black")
        if self.option_aide:
            self.remettre_a_zero_les_cases_modifiees()

    def remettre_a_zero_les_cases_modifiees(self):
        print("Remettre a zero")
        print(self.cases_modifiees_pour_aider)
        for position in self.cases_modifiees_pour_aider.copy():
            self.delete(self.cases_modifiees_pour_aider.pop(position))

    def modifier_la_case(self, position, couleur):
        print("Modifions cases: ", position)
        x, y = self.coordonnees_centre_case(position)
        rad = int(round(self.n_pixels_par_case * 0.45))
        if position not in self.cases_modifiees_pour_aider.keys():
            self.cases_modifiees_pour_aider[position] = self.create_rectangle(x - rad, y - rad, x + rad, y + rad,
                                                                              outline=couleur, fill="")

    def montrer_les_mouvements_possibles_a_partir_de(self, position):
        for destination, coup in self.mouvements_possibles_de_la_piece(position):
            self.modifier_la_case(destination, "blue")

    def cacher_les_mouvements_possibles_a_partir_de(self, position):
        for destination, coup in self.mouvements_possibles_de_la_piece(position):
            self.deselectionner_la_case(destination)

    def montrer_tous_les_mouvements_possible_pour_la_couleur(self, couleur):
        for mouvement in self.mouvements_possibles_de_couleur(couleur):
            print("Mouvement: ", mouvement[0], mouvement[1])
            self.modifier_la_case(mouvement[0], "red")
            self.modifier_la_case(mouvement[1], "red")

    def rearmer_les_selections(self, *selection):
        for case in selection:
            self.deselectionner_la_piece(case)
        self.deselectionner_la_case(self.case_depart)
        self.case_arrivee = ""
        self.case_depart = ""
        self.piece_a_deplacer = None

    ####################################################################################################################
    # Méthodes permettant de jouer des coups
    ####################################################################################################################

    def deplacer(self, position_source, position_cible):
        """Effectue un déplacement de pièce si celui-ci est permis, dans l'objet echiquier et sur le canvas.

        Args:
            position_source(str):  Case de départ
            position_cible(str):  Case d'arrivée

        Returns:
            (bool):  True si le déplacement est valide et a été effectué, sinon False."""

        # Vérifier et faire le déplacement dans la source de données
        try:
            coup = Echiquier.deplacer(self, position_source, position_cible)

        # Déplacement impossible:  propager l'exception au contrôleur d'évenement
        except PychecsException as erreur:
            raise erreur

        # Sinon réfléter le changement au niveau graphique...
        else:
            # Si une prise est faite:  éliminer l'objet graphique du canvas et de la liste des objets dessinés
            if position_cible in self.dictionnaire_graphique.keys():
                self.effacer_la_piece_a_position(position_cible)

            # Mettre à jour la liste graphique et faire le déplacement sur le canvas
            self.deplacer_de_case_a_case(position_source, position_cible)

            # Si c'est un des roques, il faut aussi déplacer la tour.  Cela a été fait dans l'échiquier mais non avec
            # les objets graphiques!
            if "roque" in coup["special"]:
                couleur = self.dictionnaire_pieces[position_cible].couleur
                position_initiale, position_finale = self.parametres_du_roque(couleur, coup["special"])
                self.deplacer_de_case_a_case(position_initiale, position_finale)

            # Si c'est une prise en passant, il faut éliminer un objet objet graphique pion à la case appropriée
            if coup["special"] == "en passant":
                position_prise = position_cible[0] + position_source[1]
                if position_prise in self.dictionnaire_graphique.keys():
                    self.effacer_la_piece_a_position(position_prise)

            # Si c'est une promotion, il faut remplacer le pion promu par la pièce choisie
            # Il faut aussi réévaluer si le roi est en échec, mat ou pat.
            if coup["special"] == "promotion":
                coup["special"] += self.promouvoir(position_cible)
                coup["resultat"] = self.resultat_du_coup(self.joueur_inactif())

            return coup

    @staticmethod
    def code_de_promotion(self, piece):
        codes = {"D": Dame, "T": Tour, "F": Fou, "C": Cavalier}
        return codes[piece]

    def promouvoir(self, position_cible):

        if position_cible[1] == "8":
            couleur = "blanc"
        else:
            couleur = "noir"
        assert couleur == self.couleur_piece_a_position(position_cible), "Erreur dans promouvoir()"

        code_piece_choisie = FenetreChoixPromotion(self, couleur).apparaitre()
        assert code_piece_choisie in ["D", "T", "F", "C"]
        self.dictionnaire_pieces[position_cible] = (self.code_de_promotion(code_piece_choisie))(couleur)
        self.effacer_la_piece_a_position(position_cible)
        self.dictionnaire_graphique[position_cible] = self.dessiner_piece(self.dictionnaire_pieces[position_cible],
                                                                          position_cible)
        return code_piece_choisie

    def case_depart_est_occupee(self, case):
        """Vérifier si la case départ est occupée par une pièce de la couleur active, sinon lever une exception.

        Args:
            case(str):  Position à contrôler

        Raises:
            CaseDepartVideException si la case est inoccupée
            TourException si la case est occupée par une pièce inactive."""

        couleur_case_depart = self.couleur_piece_a_position(case)
        if not couleur_case_depart:
            raise CaseDepartVideException(case)
        elif couleur_case_depart != self.joueur_actif:
            raise TourException(self.joueur_actif)

    def jouer_le_coup(self, case_depart, case_arrivee):

        self.case_depart = case_depart
        self.case_arrivee = case_arrivee
        message_echec = ""

        # Vérifier la légalité du déplacement et modifier le dictionnaire
        try:
            coup = self.deplacer(self.case_depart, self.case_arrivee)

        # Si le déplacement demandé est impossible avertir l'utilisateur
        except PychecsException as erreur:
            # self.message_erreur.set(str(erreur))
            # self.message_aide_contextuelle = erreur.message
            self.exception = erreur

        # Si un déplacement a été fait, redessiner l'échiquier et basculer le joueur actif et vérifier si la
        # partie est terminée!  Aussi effacer le message d'erreur, et enregistrer le coup joué.
        # Vérifier si le roi adverse est en échec
        else:
            self.coup_joue = coup
            self.nombre_de_coups_joues.set(self.nombre_de_coups_joues.get() + 1)

            assert isinstance(self.coup_joue, dict), "Coup retourné n'est pas un dict"
            assert "resultat" in self.coup_joue.keys()

            # Échec et mat!  Quitter la fonction et terminer la partie
            if self.coup_joue["resultat"] == "++":
                return

            # Échec!  Avertir les joueurs
            elif self.coup_joue["resultat"] == "+":
                message_echec = "ÉCHEC!  "
                self.message_aide_contextuelle = AIDE_CONTEXTUELLE["echec"]

            else:
                self.message_aide_contextuelle = AIDE_CONTEXTUELLE["PychecsException"]

            # Passer au prochain joueur!
            self.basculer_joueur_actif()
            self.message_erreur.set("")
            self.message.set(message_echec + f"C'est maintenant aux {self.joueur_actif}s à jouer!")

    def clic_souris(self, event):
        """Le coeur de cette classe.  C'est le handler des clics de souris, responsable des interactions avec les
        joueurs.  Interagit avec echiquier pour permettre la sélection d'une pièce et le choix d'un déplacement, si
        celui-ci est permis par les règles du jeu.

        Args:
            event(objet Event):  Évènement de type ButtonClick.  Fournira les coordonnées x, y du clic de souris."""

        # L'échiquier attend qu'un adversaire joue, on ne répond plus aux clics de souris!
        if self.mode == "attente":
            return

        # Avertir le contrôleur qu'un clic de souris a été fait
        self.evenement.set("clic")

        # Identifier la case qui est cliquée.  Sortir si l'utilisateur a cliqué hors de l'échiquier.
        try:
            case = self.coordonnees_vers_position(event.x, event.y)
        except ClicHorsEchiquierException as erreur:
            self.exception = erreur
            self.evenement.set("erreur")
            return

        # Si une pièce est déjà sélectionnée, il faut une case arrivée
        if self.piece_a_deplacer:

            # Annuler le coup si le joueur a recliqué la case départ et désélectionner la pièce la couleur de départ
            if case == self.case_depart:
                self.rearmer_les_selections(self.case_depart)

            # Assigner la case arrivée et demander à l'échiquier de faire le déplacement.  Réarmer la sélection.
            else:
                self.case_arrivee = case

                # Vérifier la légalité du déplacement et modifier le dictionnaire
                try:
                    coup = self.deplacer(self.case_depart, self.case_arrivee)

                # Si le déplacement demandé est impossible avertir l'utilisateur
                # La variable coup_valide indique si un coup a été joué auquel cas il faut réarmer la case
                except PychecsException as erreur:
                    self.exception = erreur
                    self.evenement.set("erreur")
                    self.rearmer_les_selections(self.case_depart)

                # Si un déplacement a été fait, avertir le contrôleur avec la variable nombre_de_coups_joues.
                # Aussi effacer le message d'erreur, et enregistrer le coup joué.

                else:
                    self.rearmer_les_selections(self.case_arrivee)
                    self.coup_joue = coup
                    self.nombre_de_coups_joues.set(self.nombre_de_coups_joues.get() + 1)



        # Pas de pièce déjà sélectionnée...
        else:

            # Vérifier si la case départ est occupée par une pièce active
            try:
                self.case_depart_est_occupee(case)

            # Sinon lever l'exception et aviser l'utilisateur
            except PychecsException as erreur:
                self.exception = erreur
                self.evenement.set("erreur")

            # Une pièce de la couleur active a été cliquée, la sélectionner.
            else:
                self.case_depart = case
                self.piece_a_deplacer = self.recuperer_piece_a_position(self.case_depart)
                self.selectionner_la_piece(self.case_depart)
                self.selectionner_la_case(self.case_depart)

    def annuler_le_dernier_coup(self, dernier_coup, avant_dernier_coup=None):

        # Dans le cas d'un abandon, aucune pièce n'a été déplacée:  on saute cette étape
        if dernier_coup["special"] != "Abandon":

            # Annuler le mouvement sur l'échiquier logique
            piece_jouee = Constructeur_de_piece.convertir(dernier_coup["jouee"])
            depart = dernier_coup["source"]
            arrivee = dernier_coup["cible"]

            if dernier_coup["prise"]:
                piece_prise = Constructeur_de_piece.convertir(dernier_coup["prise"])
                self.dictionnaire_pieces[arrivee] = piece_prise
            else:
                del self.dictionnaire_pieces[arrivee]

            # Remettre la pièce jouée sur la case départ
            self.dictionnaire_pieces[depart] = piece_jouee

            # Dans le cas d'un roque: il faut aussi remettre les tours à leur place
            if dernier_coup["special"] == "grand roque":
                if piece_jouee.couleur == "blanc":
                    self.dictionnaire_pieces["a1"] = self.dictionnaire_pieces.pop("d1")
                else:
                    self.dictionnaire_pieces["a8"] = self.dictionnaire_pieces.pop("d8")
            elif dernier_coup["special"] == "petit roque":
                if piece_jouee.couleur == "blanc":
                    self.dictionnaire_pieces["h1"] = self.dictionnaire_pieces.pop("f1")
                else:
                    self.dictionnaire_pieces["h8"] = self.dictionnaire_pieces.pop("f8")

            # Remettre à jour l'échiquier graphique d'après l'échiquier logique
            self.mise_a_jour_echiquier()

        # Ensuite il faut remettre à jour les permissions de prise en passant et du roque, sauf si on est au premier
        # coup.  Dans ce cas on est certain qu'elles n'ont pas changé.  L'avant-dernier coup devient le coup joué.
        if avant_dernier_coup is not None:
            self.coup_joue = avant_dernier_coup
            self.pion_vient_de_sauter_une_case = avant_dernier_coup["pion a saute"]
            self.piece_a_bouge = avant_dernier_coup["piece a bouge"]
        else:
            self.coup_joue = None
            self.pion_vient_de_sauter_une_case = ""
            self.piece_a_bouge = ""

    def __repr__(self):
        return Echiquier.__repr__(self)


if __name__ == "__main__":
    root = tk.Tk()

    code = FenetreChoixPromotion(root, "blanc").apparaitre()
    print(code)
    root.mainloop()

    while True:
        pass

    # Widget maitre
    fenetre = tk.Tk()

    # Création de l'échiquier
    objet = CanvasEchiquier(fenetre, width=1000, height=600)

    # Création d'un label pour les messages à l'utilisateur
    billboard = tk.Label(fenetre, textvariable=objet.message)
    errorboard = tk.Label(fenetre, textvariable=objet.message_erreur)
    coupBoard = tk.Label(fenetre, textvariable=objet.coup_joue)

    # Placer les objets et commencer...
    billboard.pack(side=tk.TOP)
    errorboard.pack()
    coupBoard.pack()
    objet.pack()
    fenetre.mainloop()
