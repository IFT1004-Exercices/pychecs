
from pychecs2.interface.ControleurDePartie import ControleurDePartie
from pychecs2.interface.ControleurDePartieContre import ControleurDePartieContre
from pychecs2.sunfish.sunfish import ControleurDeSunfish
from pychecs2.interface.FenetreDeConfiguration import FenetreDeConfiguration
from tkinter import Tk, Toplevel, Label, Button, filedialog, messagebox
from os import getcwd

class FenetreBienvenue(Toplevel):

    def __init__(self, master=None):

        Toplevel.__init__(self, master)
        self.title("Pychecs")
        self.titre = Label(self, text="Bienvenue dans Pychecs!", fg="dark grey", bg="light grey", font=("default", 50, "normal"))
        self.titre.config(width=20)
        self.geometry("600x500+100+100")
        self.resizable(height=False, width=False)
        self.config(bg="light grey", width=500, height=500)
        self.protocol("WM_DELETE_WINDOW", self.quitter)

        self.bouton_nouvelle_partie = Button(self, text="Démarrer une nouvelle partie", command=self.demarrer)
        self.bouton_recuperer_partie = Button(self, text="Récupérer une partie sauvegardée", command=self.recuperer)
        self.bouton_quitter = Button(self, text="Quitter", command=self.quitter)
        self.configurer_les_boutons(self.bouton_nouvelle_partie,
                                    self.bouton_recuperer_partie,
                                    self.bouton_quitter,
                                    width=25,
                                    font=("default", 30, "normal"),
                                    foreground="dark grey",
                                    background="green",
                                    highlightbackground="light grey")

        self.titre.grid(column=0, row=0, pady=40)
        self.bouton_nouvelle_partie.grid(column=0, row=1, pady=30)
        self.bouton_recuperer_partie.grid(column=0, row=2, pady=30)
        self.bouton_quitter.grid(column=0, row=3, pady=30)

    def configurer_les_boutons(self, *args, **kwargs):
        for bouton in args:
            bouton.config(kwargs)

    def demarrer(self):
        # reponse = messagebox.askyesno(parent=self,
        #                               title="Choix de l'adversaire",
        #                               message="Voulez-vous jouer contre l'ordinateur?")


        self.withdraw()

        fenetre_de_configuration = FenetreDeConfiguration(master=self.master)
        # if reponse:
        #     self.master.controleur = ControleurDePartieContre(ControleurDeSunfish(),
        #                                couleur_joueur="blanc",
        #                                master=self.master,
        #                                dictionnaire=None,
        #                                nom_blancs="Pascal",
        #                                nom_noirs="Sunfish",
        #                                joueur_actif="blanc",
        #                                id_partie=None,
        #                                liste_coups=None,
        #                                gagnant=None,
        #                                sauvegardee=False,
        #                                fichier_sauvegarde=None)
        # else:
        #     self.master.controleur = ControleurDePartie(self.master)

    def recuperer(self):
        self.withdraw()
        fichier = filedialog.askopenfile(initialdir=getcwd(),
                                         defaultextension=".pychecs",
                                         filetypes=[("Pychecs files", "*.pychecs")])
        if not fichier is None:
            reponse = messagebox.askyesnocancel(title="Charger une partie",
                                                message="Désirez-vous revoir le déroulement de la partie avant de reprendre?")

            if reponse:
                liste =  ControleurDePartie.charger(self.master, fichier, charger_seulement_la_liste=True)
                self.master.controleur = ControleurDePartie.reconstituer_avec_liste_de_coups(liste, vitesse=1000)
            else:
                liste = ControleurDePartie.charger(self.master, fichier, charger_seulement_la_liste=True)
                self.master.controleur = ControleurDePartie.reconstituer_avec_liste_de_coups(liste, vitesse=0)
                #self.master.controleur = ControleurDePartie.charger(self.master, fichier)
        else:
            self.deiconify()

    def quitter(self):
        self.master.quit()

class PychecsApplication(Tk):
    def __init__(self):
        self.fichier = None

        Tk.__init__(self)
        self.withdraw()
        self.bienvenue = FenetreBienvenue(self)

        self.mainloop()

    def bienvenue_apparait(self):
        self.bienvenue.deiconify()


if __name__ == "__main__":
    PychecsApplication()
