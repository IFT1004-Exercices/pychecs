from pychecs2.interface.ControleurDePartie import ControleurDePartie
from pychecs2.sunfish.sunfish import ControleurDeSunfish
from tkinter import DISABLED, NORMAL, messagebox

class ControleurDePartieContre(ControleurDePartie):
    """Classe permettant de faire un partie contre un adversaire qui n'utilise pas notre échiquier, soit un adversaire
    en réseau, ou un moteur d'échec.

    Attributs:

    adversaire:  Le controleur de l'adversaire.  Doit disposer d'une méthode nom() qui retourne son nom, ainsi qu'une
    méthode jouer() qui accepte un coup sous forme de dict et retourne une riposte.

    couleur_joueur(str):  La couleur de notre joueur, l'adversaire aura donc l'autre couleur."""

    def __init__(self,
                 adversaire,
                 couleur_joueur = "blanc",
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
                 option_chrono=False,
                 option_aide=False):

        ControleurDePartie.__init__(self,
                                    master=master,
                                    dictionnaire=dictionnaire,
                                    nom_blancs=nom_blancs,
                                    nom_noirs=nom_noirs,
                                    joueur_actif=joueur_actif,
                                    id_partie=id_partie,
                                    liste_coups=liste_coups,
                                    gagnant=gagnant,
                                    sauvegardee=sauvegardee,
                                    fichier_sauvegarde=fichier_sauvegarde,
                                    option_chrono=option_chrono,
                                    option_aide=option_aide)

        self.adversaire = adversaire
        if couleur_joueur == "blanc":
            self.nom_noirs = self.adversaire.obtenir_le_nom()
        else:
            self.nom_blancs = self.adversaire.obtenir_le_nom()

    def mise_a_jour_liste_coups(self, *args):
        """Méthode interface avec l'adversaire.  Cette méthode est appelée lorsque l'échiquier graphique a enregistré
        un coup.  On va mettre à jour la liste de coup, et temporairement suspendre l'activité de l'échiquier en
        attendant que l'adversaire riposte.  On va repasser cette riposte à l'échiquier avec la méthode jouer_le_coup."""

        # Annexer notre coup à la liste puis attendre la réponse
        ControleurDePartie.mise_a_jour_liste_coups(self, args)

        # Dans le cas d'un abandon, on ne va pas plus loin car sunfish ne peut pas riposter...
        if self.liste_coups[-1]["special"] == "Abandon":
            return

        # On ne pourra pas annuler un coup pendant que l'ordi réfléchit
        self.bouton_annuler_coup.config(state=DISABLED)
        self.echiquier_graphique.passer_en_mode_attente()

        # L'adversaire nous communique son coup
        riposte = self.adversaire.jouer(self.echiquier_graphique.coup_joue)

        # On joue le coup sur l'échiquier et on l'annexe sur notre liste
        self.jouer_le_coup(riposte)
        ControleurDePartie.mise_a_jour_liste_coups(self, args)

        # Quitter le mode attente pour réagir aux clics du joueur et permettre l'annulation...
        self.echiquier_graphique.passer_en_mode_actif()
        self.bouton_annuler_coup.config(state=NORMAL)

    def annuler_le_dernier_coup(self):
        """Annuler un coup contre le contrôleur de partie adverse est un peu plus subtil:  On ne peut pas annuler
        seulement un coup des noirs, car ils vont toujours rejouer le même coup ensuite.  Il faut donc annuler son
        propre coup,  ou par groupes de deux.  De plus il faudrait renverser la configuration du contrôleur adverse."""

        # Donc annulation du coup dans le cas d'un match contre Sunfish, on peut seulement annuler lorsqu'on a le trait
        # Et il faut annuler le dernier coup de sunfish + notre propre coup, donc par deux!
        # ...
        # Sauf si on a abandonné!!!   Dans ce cas on annule seulement notre abandon et c'est à nous de jouer...

        if isinstance(self.adversaire, ControleurDeSunfish):

            # D'abord on met l'échiquier en mode attente...
            self.echiquier_graphique.passer_en_mode_attente()

            # On n'a pas joué, on ne peut donc annuler...
            if not self.liste_coups:
                return

            dernier_coup = self.liste_coups.pop()

            if len(self.liste_coups) > 1:
                avant_dernier_coup = self.liste_coups[-1]
            else:
                avant_dernier_coup = None

            # Dans le cas d'un abandon il faut seulement annuler le dernier coup car sunfish n'a pas pu réagir
            if dernier_coup["special"] == "Abandon":
                self.echiquier_graphique.annuler_le_dernier_coup(dernier_coup, avant_dernier_coup)
                ControleurDePartie.mise_a_jour_liste_coups(self)
                self.echiquier_graphique.passer_en_mode_actif()
                return

            # D'abord annuler le dernier coup des noirs sur l'échiquier
            self.echiquier_graphique.annuler_le_dernier_coup(dernier_coup, avant_dernier_coup)

            # Maintenant il faut demander à sunfish de revenir en arrière...
            self.adversaire.annuler_le_dernier_coup()

            # Ensuite mettre la liste à jour, méthode parent pour éviter de resolliciter sunfish
            ControleurDePartie.mise_a_jour_liste_coups(self)

            # Ensuite annuler le dernier coup des blancs: même démarche...
            dernier_coup = self.liste_coups.pop()
            if len(self.liste_coups) > 1:
                avant_dernier_coup = self.liste_coups[-1]
            else:
                avant_dernier_coup = None
            self.echiquier_graphique.annuler_le_dernier_coup(dernier_coup, avant_dernier_coup)
            self.adversaire.annuler_le_dernier_coup()
            ControleurDePartie.mise_a_jour_liste_coups(self)

            # Rétablir l"échiquier
            self.echiquier_graphique.passer_en_mode_actif()

        else:
            messagebox.showwarning(title="Annulation impossible",
                                   message="Malheureusement, cette option n'est pas disponible contre cet adversaire.")




if __name__=="__main__":

    from tkinter import Tk
    from pychecs2.sunfish.sunfish import ControleurDeSunfish

    def testCreateSave():
        fen = Tk()
        fen.title("Pychecs")
        adv = ControleurDeSunfish()
        obj = ControleurDePartieContre(adv,
                                       couleur_joueur="blanc",
                                       master=fen,
                                       dictionnaire=None,
                                       nom_blancs="Pascal",
                                       nom_noirs="Bruce",
                                       joueur_actif="blanc",
                                       id_partie=None,
                                       liste_coups=None,
                                       gagnant=None,
                                       sauvegardee=False,
                                       fichier_sauvegarde=None)
        fen.mainloop()

    testCreateSave()