

from pychecs2.interface.EchiquierGraphique import CanvasEchiquier
from pychecs2.echecs.piece import Constructeur_de_piece
from pychecs2.interface.chrono import Chronometre

from tkinter import Tk, Frame, Button, Label, filedialog, messagebox, Toplevel, BooleanVar
from tkinter import BOTTOM, RIGHT, LEFT, TOP
from tkinter import DISABLED, NORMAL

# Pour les entrées sorties avec les fichiers
import json

# Génération de l'identificateur de partie
from hashlib import sha256

# Gestion du temps
from datetime import datetime

# Widget dérivé de ListBox qui facilite le travail
from pychecs2.interface.ListeDeroulante import ListeDeroulante

# Pour aider avec le widget filedialog
from os import getcwd

class EncodeurDePartie(json.JSONEncoder):
    """Objet servant à convertir un objet ControleurDePartie en objet JSON."""

    def default(self, objet):
        """Méthode effectuant cette conversion.
        Args:
            objet(ControleurDePartie object):  Objet à sérialiser.
        Returns:
            (dict):  Les données sérialisées en dict."""

        if isinstance(objet, ControleurDePartie):
            return {'nom_blancs': objet.nom_joueur_blanc,
                    'nom_noirs': objet.nom_joueur_noir,
                    'joueur_actif': objet.echiquier_graphique.joueur_actif,
                    'id_partie': objet.id_partie,
                    "gagnant": objet.gagnant,
                    "sauvegardee": objet.sauvegardee.get(),
                    "fichier_sauvegarde": objet.fichier_sauvegarde,
                    'dictionnaire_pieces': objet.convertir_json(),
                    'liste_coups': objet.liste_coups}
        else:
            return json.JSONEncoder.default(self, objet)

class ControleurDePartie(Toplevel):
    """Classe responsable de contrôler le flot de parties d'échecs jouées sur un objet CanvasEchiquier.  Dans cette
    classe, on retrouve les méthodes responsables de solliciter les joueurs, de désigner le gagnant, d'arrêter,
    démarrer et sauvegarder des parties d'échec.  Des objets dérivés pourront servir à interagir avec d'autre type de
    d'adversaires:  moteurs d'échec ou joueurs en réseau."""

    MSG_SPLASH_SCREEN = """Cliquez une pièce pour la sélectionner. Cliquez ensuite sur l'échiquier pour la déplacer. Recliquez la pièce pour annuler.
    
Boutons: 

Sauvegarder:  enregistrer la partie

Annuler: revenir en arrière d'un coup

Aide:  obtenir des explications 

Interrompre:  abandonner, suspendre ou charger une nouvelle partie."""

    def __init__(self,
                 master=None,
                 dictionnaire=None,
                 nom_blancs="Blancs",
                 nom_noirs="Noirs",
                 joueur_actif = "blanc",
                 id_partie=None,
                 liste_coups=None,
                 gagnant="aucun",
                 sauvegardee=False,
                 fichier_sauvegarde=None,
                 option_chrono=0,
                 option_aide=False):

        """Constructeur:  crée une nouvelle partie par défaut."""

        # Configuration de la fenêtre de base
        Toplevel.__init__(self, master)
        time_of_creation = datetime.now()
        self.title(f"{nom_blancs} contre {nom_noirs}, {time_of_creation.isoformat()}")
        self.protocol("WM_DELETE_WINDOW", self.fenetre_est_fermee)
        self.config(bg="light grey")

        # Noms des deux adversaires
        self.nom_joueur_blanc = nom_blancs
        self.nom_joueur_noir = nom_noirs

        # Numéro d'identification de la partie
        if not id_partie:
            self.id_partie = self.generer_id_partie(time_of_creation)
        else:
            self.id_partie = id_partie

        # Variable indiquant si la partie est terminée
        self.gagnant = gagnant

        # Variables contrôlant la sauvegarde
        self.sauvegardee = BooleanVar()
        self.sauvegardee.set(sauvegardee)
        self.sauvegardee.trace_add("write", self.etat_sauvegardee_change)

        if fichier_sauvegarde is None:
            self.fichier_sauvegarde = self.nom_sauvegarde_defaut()
            self.utilisateur_a_choisi_un_nom_fichier = False
        else:
            self.fichier_sauvegarde = fichier_sauvegarde
            self.utilisateur_a_choisi_un_nom_fichier = True

        # Options diverses: partie chronométrée et indiquer les déplacements de la pièce sélectionnée

        self.option_chrono = option_chrono
        self.option_aide = option_aide

        # Les cadres principaux de l'application

        self.cadre_echiquier = Frame(self, bg="light grey", borderwidth=0)
        self.cadre_boutons = Frame(self, bg="light grey", borderwidth=0)
        self.cadre_liste = Frame(self, bg="light grey", borderwidth=0)
        self.cadre_messages = Frame(self, bg="light grey", borderwidth=0)

        # Objet graphique contenant l'échiquier
        self.echiquier_graphique = CanvasEchiquier(self.cadre_echiquier,
                                                   dictionnaire=dictionnaire,
                                                   joueur_actif=joueur_actif,
                                                   option_chrono=self.option_chrono,
                                                   option_aide=self.option_aide,
                                                   width=600, height=600,
                                                   bg="light grey",
                                                   borderwidth=0, highlightthickness=0)
        self.echiquier_graphique.partie_modifiee.trace_add("write", self.utilisateur_a_modifie_la_partie)

        self.bouton_arret = Button(self.cadre_boutons,
                                   text="Interrompre",
                                   command=self.bouton_arreter_presse,
                                   state=NORMAL,
                                   fg="black",
                                   bg="light grey",
                                   width=16,
                                   disabledforeground="dark grey",
                                   highlightbackground="light grey")

        self.bouton_sauvegarder = Button(self.cadre_boutons,
                                         text="Sauvegarder",
                                         fg="black",
                                         bg="light grey",
                                         width=16,
                                         disabledforeground="dark grey",
                                         state=DISABLED,
                                         highlightbackground="light grey",
                                         command=self.bouton_sauvegarder_presse)

        self.bouton_aide = Button(self.cadre_boutons,
                                         text="Aide",
                                         fg="black",
                                         bg="light grey",
                                         state=NORMAL,
                                         width=16,
                                         disabledforeground="dark grey",
                                         highlightbackground="light grey",
                                         command=self.bouton_aide_presse)

        self.bouton_annuler_coup = Button(self.cadre_boutons,
                                         text="Annuler",
                                         fg="black",
                                         bg="light grey",
                                         state=NORMAL,
                                         width=16,
                                         disabledforeground="dark grey",
                                         highlightbackground="light grey",
                                         command=self.annuler_le_dernier_coup)

        # Structure de données contenant tous les coups joués, retournés par l'échiquier graphique.  Chaque coup est
        # un dict contenant toutes les informations permettant de décrire la partie.
        if not liste_coups:
            self.liste_coups = []
        else:
            self.liste_coups = liste_coups


        # Les coups seront affichés dans une liste déroulante

        # Cette liste contient les lignes de texte de la liste déroulante, qui contiennent 2 coups: un blanc et un noir
        # self.lignes_registres_coups est une liste contenant une description textuelle des coups en notation algébrique
        # standard. self.registre_coups est un objet ListeDeroulante permettant d'afficher self.lignes_registres_coups

        self.largeur_du_registre = 14
        self.lignes_registre_coups = self.initialiser_registre()

        self.registre_coups = ListeDeroulante(self.cadre_liste, self.lignes_registre_coups,
                                              lignes=20, largeur=self.largeur_du_registre, texteInitial="Liste des coups")
        self.registre_coups.config(bg="light grey")

        # Mécanisme principal par lequel l'échiquier annonce un coup joué
        self.echiquier_graphique.nombre_de_coups_joues.trace_add("write", self.mise_a_jour_liste_coups)



        # cadre_messages contiendra les messages à l'usager sous forme de labels
        self.message_affiche = Label(self.cadre_messages, width=50,
                                     textvariable=self.echiquier_graphique.message,
                                     fg="black", bg="light grey",
                                     font=("default", 25, "normal"))
        self.erreur_affiche = Label(self.cadre_messages, width=50,
                                    textvariable=self.echiquier_graphique.message_erreur,
                                    fg="black", bg="light grey",
                                    font=("default", 25, "normal"))

        # Pour une partie chronométrée, on rajoute l'objet chronomètre
        if self.option_chrono:
            self.chrono = Chronometre(self.cadre_messages, minutes=self.option_chrono, alarme="00:00", width=4,
                                      fg="black", bg="light grey",
                                      font=("default", 25, "normal"))
            self.echiquier_graphique.message.trace_add("write", self.repartir_le_chrono)


        # Mise en place des éléments graphiques
        self.bouton_arret.pack(side=RIGHT, padx=40, pady=20)
        self.bouton_sauvegarder.pack(side=LEFT, padx=40, pady=20)
        self.bouton_aide.pack(side=RIGHT, padx=40, pady=20)
        self.bouton_annuler_coup.pack(side=RIGHT, padx=40, pady=20)
        self.cadre_boutons.pack(side=BOTTOM)

        self.message_affiche.pack(side=TOP)
        self.erreur_affiche.pack(side=BOTTOM)
        if self.option_chrono:
            self.chrono.pack(side=BOTTOM)
        self.cadre_messages.pack(side=TOP)

        self.echiquier_graphique.pack()
        self.cadre_echiquier.pack(side=LEFT)

        self.registre_coups.pack()
        self.cadre_liste.pack(side=RIGHT, padx=20)

        self.echiquier_graphique.update()
        messagebox.showinfo(title="Pychecs", message= self.MSG_SPLASH_SCREEN, parent=self.echiquier_graphique)

    def repartir_le_chrono(self, *args):
        """Lorsqu'on bascule le joueur actif, doit repartir le chrono à zéro.  Doit arrêter le chrono lorsque la
        partie est terminée."""

        if self.echiquier_graphique.message.get().startswith("C'est"):
            self.chrono.debuter()
        else:
            # TODO Bug à arranger:  ça n'arrête pas.
            self.chrono.arreter()

    def fenetre_est_fermee(self):
        """Si la fenêtre de partie est fermée, la fenêtre de bienvenue apparait, permettant de redémarrer une partie.
        """

        self.destroy()
        self.master.bienvenue_apparait()

    @classmethod
    def charger_dictionnaire(cls, dictionnaire_json):
        """Convertit un dictionnaire contenant les représentations des pièces en dictionnaire d'objets Piece.
        Args:
            dictionnaire_json(dict):  Dictionnaire stocké dans un objet json
        Returns:
            (dict):  Dictionnaire d'objets Piece utilisable par la classe CanvasEchiquier
        Raises:
            Exception:  Si les données du dictionnaire ne sont pas lisibles."""

        dictionnaire = {}
        for position, piece in dictionnaire_json.items():
            dictionnaire[position] = Constructeur_de_piece.convertir(piece)
        return dictionnaire

    @classmethod
    def charger(cls, master, fichier, charger_seulement_la_liste=False):
        """Crée un objet ControleurDePartie à-partir d'un fichier JSON.  C'est un overload du constructeur.
        Args:
            fichier(file object):  Objet fichier ouvert au préalable.
        Returns:
            (ControleurDePartie object):  Un nouveau contrôleur de partie."""

        try:

            # Lire les données et convertir le résultat en dict à-partir du fichier JSON
            info_partie = json.load(fichier)

            # Lire les infos de la partie à-partir du dictionnaire récupéré
            nom_joueur_blanc = info_partie["nom_blancs"]
            nom_joueur_noir = info_partie["nom_noirs"]
            joueur_actif = info_partie["joueur_actif"]
            id_partie = info_partie["id_partie"]

            # Il faut convertir les données du dictionnaire de pièces en objets correpondants
            dictionnaire_pieces = ControleurDePartie.charger_dictionnaire(info_partie["dictionnaire_pieces"])
            liste_coups = info_partie["liste_coups"]
            gagnant = info_partie["gagnant"]
            sauvegardee = info_partie["sauvegardee"]
            fichier_sauvegarde = info_partie["fichier_sauvegarde"]

        # Données incomplètes
        except KeyError:
            print("Il manque des informations dans le fichier de données.")
            return

        # Option utilisée lorsqu'on veut réviser le déroulement d'une partie.
        if charger_seulement_la_liste:
            return liste_coups

        # Appeler le constructeur avec les infos de la partie
        return cls(master=master,
                   dictionnaire=dictionnaire_pieces,
                   nom_blancs=nom_joueur_blanc,
                   nom_noirs=nom_joueur_noir,
                   joueur_actif=joueur_actif,
                   id_partie=id_partie,
                   liste_coups=liste_coups,
                   gagnant=gagnant,
                   sauvegardee=True,
                   fichier_sauvegarde=fichier_sauvegarde)

    @classmethod
    def reconstituer_avec_liste_de_coups(cls,
                                         liste_de_coups,
                                         vitesse=0,
                                         master=None,
                                         dictionnaire=None,
                                         nom_blancs="Blancs",
                                         nom_noirs="Noirs",
                                         id_partie=None,
                                         liste_coups=None,
                                         gagnant="aucun",
                                         sauvegardee=False,
                                         fichier_sauvegarde=None):



        # On commence par recréer une partie initiale avec les même paramètres de départ, sauf gagnant est remis à
        # aucun, liste_coups est remis à None et sauvegardee à False.  Le dictionnaire est aussi réinitialisé à None

        controleur = cls(master=master,
                         dictionnaire=None,
                         nom_blancs=nom_blancs,
                         nom_noirs=nom_noirs,
                         joueur_actif="blanc",
                         id_partie=id_partie,
                         liste_coups=None,
                         gagnant="aucun",
                         sauvegardee=False,
                         fichier_sauvegarde=fichier_sauvegarde)

        # On rejoue les coups l'un après l'autre.  Le défilement est contrôlé par le paramètre vitesse.

        for coup in liste_de_coups:
            controleur.jouer_le_coup(coup)
            if vitesse:
                controleur.after(vitesse)
                controleur.echiquier_graphique.update()
        controleur.sauvegardee.set(False)
        return controleur

    def jouer_le_coup(self, coup):
        """Demander à l'échiquier de jouer un coup.
        Args:
            coup(dict):  Le coup à jouer"""

        # Condition nécessaire: si on abandonne, le contrôleur adverse retourne un coup None
        if coup is not None:
            depart = coup["source"]
            arrivee = coup["cible"]
            self.echiquier_graphique.jouer_le_coup(depart, arrivee)

    def annuler_le_dernier_coup(self):
        """Demander à l'échiquier d'annuler le dernier cooup joué."""

        # Si on n'a pas encore joué on ne peut pas annuler
        if not self.liste_coups:
            return

        # On retire ce coup de la liste
        dernier_coup = self.liste_coups.pop()

        # On va aussi retirer l'avant-dernier coup s'il existe.  C'est pour gérer les droits de prise en passant.
        if len(self.liste_coups) > 1:
            avant_dernier_coup = self.liste_coups[-1]
        else:
            avant_dernier_coup = None

        # Envoyer ces infos à l'échiquier et rafraichir la liste.
        self.echiquier_graphique.annuler_le_dernier_coup(dernier_coup, avant_dernier_coup)
        self.mise_a_jour_liste_coups()

    def initialiser_registre(self):
        """Générateur des lignes du registre des coups.  Aligne les coups 2 à 2."""

        # Initialisation d'une liste avec la ligne titre

        lignes = ["{:<7s}{:>7s}".format("Blancs", "Noirs")]
        blanc = True

        # Passer la liste des coups et construire les lignes du registre
        for coup in self.liste_coups:

            # Coup des blancs:  on remplit la ligne à gauche
            if blanc:
                ligne = "{:<7s}".format(self.coup_vers_str(coup))
                lignes.append(ligne)

            # Coup des noirs:  On complète la ligne à droite
            else:
                ligne = lignes.pop()
                ligne = "{:<7s}{:>7s}".format(ligne, self.coup_vers_str(coup))
                lignes.append(ligne)

            # Alterner blanc-noir
            blanc = not blanc
        return lignes

    @staticmethod
    def coup_vers_str(coup=None):
        """Méthode utilitaire servant à convertir un dict coup en notation algébrique.
        Args:
            coup(dict):  Coup à traduire."""

        if not coup:
            return ""
        if coup["special"] == "Abandon":
            return "Abandon "
        if coup["special"] == "grand roque":
            return "0-0-0   "
        if coup["special"] == "petit roque":
            return "0-0     "
        texte = coup["jouee"]
        if coup["prise"]:
            texte += "x"
        texte += coup["cible"]
        if coup["special"] == "en passant":
            texte += "e.p."

        # Dans le cas d'une promotion on a stocké l'abbréviation appropriée à la suite du str "promotion"
        if "promotion" in coup["special"]:
            texte += coup["special"].lstrip("promotion")
        texte += coup["resultat"]

        return f"{texte:<12s}"

    def mise_a_jour_liste_coups(self, *args):
        """Annexe le dernier coup joué dans l'échiquier à la liste, met à jour la liste déroulante.

        Args:
            *args:  Non-utilisé.  Arguments pour compatibilité avec trace_add"""

        # Si un coup a été joué l'annexer à la liste (sinon le coup a été annulé!
        if self.echiquier_graphique.coup_joue:
            self.liste_coups.append(self.echiquier_graphique.coup_joue)

        # Afficher correctement la liste des coups dans le registre
        self.affichage_de_la_liste_des_coups()

    def affichage_de_la_liste_des_coups(self):
        """Sert à peupler le registre des coups."""
        # TODO Vérifier si on pourrait l'éliminer.

        coup_precedent = None
        blancs_jouent = True
        self.lignes_registre_coups = []

        for coup in self.liste_coups:
            texte_coup = self.coup_vers_str(coup)

            # Si ce sont les blancs
            if blancs_jouent:
                self.lignes_registre_coups.append("{:s}".format(texte_coup))

            # Pour les noirs, on doit complèter la ligne à droite
            else:
                self.lignes_registre_coups.pop()
                assert not coup_precedent is None, "Problème d'alternance dans affichage_de_la_liste_des_coups"
                texte_coup_precedent = self.coup_vers_str(coup_precedent)
                self.lignes_registre_coups.append("{:s}{:s}".format(texte_coup_precedent, texte_coup))
            blancs_jouent = not blancs_jouent
            coup_precedent = coup

        # Afficher la ListeDeroulante avec les données à jour
        self.registre_coups.update(self.lignes_registre_coups)

    def generer_liste_des_prises(self):
        """Retourne la lise des pièces prises"""

        liste = []
        for coup in self.liste_coups:
            if coup["prise"]:
                liste.append(coup["prise"])
        return liste

    def afficher_liste_des_prises(self):
        # TODO à compléter
        pass

    # def remettre_echiquier_a_zero(self):
    #     del self.echiquier_graphique
    #     self.echiquier_graphique = CanvasEchiquier(self.cadre_echiquier,
    #                                                dictionnaire=None, width=600, height=600, bg="light grey")
    #     # self.echiquier_graphique.coup_joue.trace_add("write", self.mise_a_jour_liste_coups())

    # def avancer_la_partie_avec_liste(self, index):
    #     # TODO a completer
    #     for coup in self.liste_coups[:index]:
    #         pass

    def convertir_json(self):
        """Convertit un dictionnaire d'objets Piece en dictionnaire de caractères correspondants."""

        return {cle: str(piece) for cle, piece in self.echiquier_graphique.dictionnaire_pieces.items()}

    def etat_sauvegardee_change(self, *args):
        """Si la partie a été modifiée depuis la dernière sauvegarde, activer le bouton sauvegarde"""

        if self.sauvegardee.get():
            self.bouton_sauvegarder.config(state=DISABLED)
        else:
            self.bouton_sauvegarder.config(state=NORMAL)

    def nom_sauvegarde_defaut(self):
        """Génère un nom de fichier sauvegarde par défaut pour la partie."""

        return self.id_partie[:8] + ".pychecs"

    def sauvegarder(self, fichier):
        """Sauvegarder les données au format JSON dans un fichier.
        Args:
            fichier(file object):  objet fichier sauvegarde."""
        json.dump(self, fichier, cls=EncodeurDePartie)

    def generer_id_partie(self, maintenant):
        """Génère un numéro d'identification unique pour une nouvelle partie, à-partir de la date et l'heure actuelle,
        et des noms des joueurs."""

        noyau = (str(maintenant) + self.nom_joueur_blanc + self.nom_joueur_noir).encode("Utf8")
        return sha256(noyau).hexdigest()

    def quitter_la_partie(self):
        """Quitter le controleur de partie. Il faut passer la main au widget de bienvenue."""

        self.destroy()
        self.master.bienvenue_apparait()

    def utilisateur_sauve_la_partie(self):
        """Interface de sauvegarde.  Interagit avec l'utilisateur pour sauvegarder les données dans un fichier de son
        choix.  Utilise des widgets préfabriqués."""

        # Décision initiale: demander à l'utilisateur s'il désire sauvegarder les données
        if not self.echiquier_graphique.partie_terminee.get():
            message = "Vous vous apprêtez à quitter sans avoir sauvé cette partie.  Désirez-vous enregistrer la partie?"
        else:
            message = f"La partie est terminée.  Félicitations aux {self.echiquier_graphique.couleur_gagnante}s!!!  " \
                      f"Désirez-vous enregistrer la partie? "

        confirme_enregistrer = messagebox.askyesnocancel(title="Sauvegarde de la partie",
                                                         message=message,
                                                         default=messagebox.YES,
                                                         parent=self.echiquier_graphique)

        # Si oui, repérer le fichier sauvegarde.  Proposer initialement un fichier sauvegarde déjà employé, ou alors le
        # fichier par défaut.
        if confirme_enregistrer:
            return self.bouton_sauvegarder_presse()


        # Si cancel:  on retourne sans rien faire
        elif confirme_enregistrer is None:
            return None

        # Si non: on ne sauvegardera pas et on continuera l'action en cours
        else:
            return False

    def utilisateur_a_modifie_la_partie(self, *args):
        """Dès qu'un coup est réalisé sur l'échiquier, devient False"""

        if self.echiquier_graphique.partie_modifiee.get():
            self.sauvegardee.set(False)
            self.bouton_sauvegarder.config(state=NORMAL)

    def nom_joueur_actif(self):
        """Retourne le nom du joueur actif"""

        if self.echiquier_graphique.joueur_actif == "blanc":
            return self.nom_joueur_blanc
        return self.nom_joueur_noir

    def nom_joueur_inactif(self):

        if self.echiquier_graphique.joueur_actif == "blanc":
            return self.nom_joueur_noir
        return self.nom_joueur_blanc

    def verifier_abandon(self):
        """L"utilisateur a arrêté la partie, vérifier s'il veut abandonner car cette action est irréversible."""

        # Afficher la boîte de dialogue
        message = self.nom_joueur_actif() + ", abandonnez-vous la partie?"
        confirme_abandon = messagebox.askyesnocancel(title="Abandon?",
                                                     message=message,
                                                     default=messagebox.NO,
                                                     parent=self.echiquier_graphique)

        # Si l'utilisateur abandonne:  la partie est gagnée par l'adversaire et donc terminée
        if confirme_abandon is None:
            return None
        elif confirme_abandon:
            self.echiquier_graphique.couleur_gagnante = {"blanc": "noir", "noir": "blanc"}[self.echiquier_graphique.joueur_actif]
            self.echiquier_graphique.coup_joue = {"special": "Abandon",
                                                  "source": "",
                                                  "cible": "",
                                                  "jouee": "",
                                                  "prise": "",
                                                  "resultat": ""}
            self.echiquier_graphique.nombre_de_coups_joues.set(self.echiquier_graphique.nombre_de_coups_joues.get() + 1)
            self.echiquier_graphique.basculer_joueur_actif()
            self.echiquier_graphique.partie_terminee.set(True)
            self.echiquier_graphique.update()
            return True

        # Sinon, on suppose que les adversaires veulent reprendre plus tard, la partie est laissée en-cours...
        else:
            return False

    def partie_est_finie(self, *args):
        """La partie a été terminée par l'échiquier:  soit qu'elle a été remportée par mat, ou le roi est pat est c'est
         automatiquement une partie nulle."""


        # Si la partie a été modifiée depuis la dernière sauvegarde, proposer de sauvegarder.
        if not self.sauvegardee.get():
            resultat = self.utilisateur_sauve_la_partie()

            # L'utilisateur a annulé la sauvegarde, on retourne
            if resultat is None:
                return

            # L'utilisateur a sauvegardé ou choisi de ne pas sauvegarder
            self.sauvegardee.set(resultat)
            self.echiquier_graphique.partie_modifiee.set(False)

        # Dernière chance de se rattraper...
        message = "Quitter la partie?"
        reponse = messagebox.askyesno(title="Quitter?",
                                      message=message,
                                      default=messagebox.NO,
                                      parent=self.echiquier_graphique)
        if reponse:
            self.quitter_la_partie()
        return

    def bouton_arreter_presse(self):
        """Le bouton d'arrêt a été pressé, on interrompt ou on arrête la partie"""

        # Si la partie est en cours, vérifier si c'est un abandon
        if not self.echiquier_graphique.partie_terminee.get():
            reponse = self.verifier_abandon()
            if reponse is None:
                return

        # Si la partie a été modifiée depuis la dernière sauvegarde, proposer de sauvegarder.
        if not self.sauvegardee.get():
            resultat = self.utilisateur_sauve_la_partie()

            # L'utilisateur a annulé la sauvegarde, on retourne
            if resultat is None:
                return

            # L'utilisateur a sauvegardé ou a choisi de ne pas sauvegarder
            self.sauvegardee.set(resultat)
            self.echiquier_graphique.partie_modifiee.set(False)

        # Dernière chance de se rattraper...
        if self.sauvegardee.get():
            message = "La partie a été sauvegardée.  Êtes-vous certain de vouloir quitterla partie?"
        else:
            message = "Êtes-vous certain de vouloir quitter la partie?"
        reponse = messagebox.askyesnocancel(title="Quitter",
                                            message=message,
                                            default=messagebox.NO,
                                            parent=self.echiquier_graphique,
                                            icon='error')
        if reponse:
            self.quitter_la_partie()
        return

    def bouton_sauvegarder_presse(self):
        """Va demander un fichier sauvegarde à l'utilisateur"""

        while True:
            if not self.utilisateur_a_choisi_un_nom_fichier:
                nom = filedialog.asksaveasfilename(message="Veuillez choisir un fichier de sauvegarde",
                                                   initialfile=self.fichier_sauvegarde,
                                                   initialdir=getcwd(),
                                                   filetypes=[("Pychecs files", ".pychecs")])
                if not nom:
                    return False
                self.fichier_sauvegarde = nom
                self.utilisateur_a_choisi_un_nom_fichier = True

            # Ouverture du fichier
            try:
                with open(self.fichier_sauvegarde, "w") as fichier:
                    self.sauvegarder(fichier)
            except OSError:
                reponse = messagebox.askretrycancel("Erreur d'ouverture du fichier demandé.")
                if not reponse:
                    return False
                else:
                    # Si on ne peut ouvrir un fichier en écriture on a probablement le mauvais path.
                    # Laisser à l'utilisateur la possibilité de choisir un nouveau pathname.
                    self.utilisateur_a_choisi_un_nom_fichier = False
                    continue
            else:
                self.sauvegardee.set(True)
                self.echiquier_graphique.partie_modifiee.set(False)
                messagebox.showinfo("Pychecs info", f"La partie a été enregistrée dans {self.fichier_sauvegarde}")
                break
        return True

    def bouton_aide_presse(self):
        """Afficher l'aide contextuelle"""

        messagebox.showinfo(title="Aide Pychecs",
                            message=self.echiquier_graphique.message_aide_contextuelle,
                            parent=self)

    # def envoyer_un_coup_a_sunfish(self):
    #     coup = self.liste_coups[-1]
    #     return(coup["source"] + coup["cible"])

    # def recevoir_un_coup_de_sunfish(self, coup_de_sunfish):
    #     assert len(coup_de_sunfish) == 4
    #
    #     source, cible = coup_de_sunfish[:2],coup_de_sunfish[2:]
    #     self.jouer_le_coup({"source": source, "cible": cible})

    def __repr__(self):
        """Imprime l'échiquier courant et les infos de partie."""

        return self.echiquier_graphique.__repr__() + "\n\n" + self.id_partie

if __name__=="__main__":
    fen=Tk()
    fen.title("Pychecs")

    def testCreateSave():
        obj = ControleurDePartie(fen, nom_blancs="Pascal", nom_noirs="Bruce")
        obj.echiquier_graphique.pack()
        obj.echiquier_graphique.mainloop()

    def testLoad():
        fichier=filedialog.askopenfile(title="Ouvrir une partie",
                                       message="Veuillez choisir un fichier de partie",
                                       initialdir=getcwd())
        obj= ControleurDePartie.charger(fen, fichier)
        print(obj.echiquier_graphique.dictionnaire_pieces)
        print(obj.echiquier_graphique.dictionnaire_graphique)
        obj.echiquier_graphique.pack() 
        obj.echiquier_graphique.mainloop()

    def test_interface_sunfish():
        import pychecs2.sunfish.sunfish as sunfish
        obj = ControleurDePartie(fen, nom_blancs="Pascal", nom_noirs="Sunfish")
        sunfish.jouer_avec_le_controleur(obj)
        obj.pack()
        obj.mainloop()




    test_interface_sunfish()
