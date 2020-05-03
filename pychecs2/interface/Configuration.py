from tkinter import Toplevel, Frame, StringVar, TOP, Tk, BOTH, LEFT, Label, Entry, Radiobutton

class FenetreDeConfiguration(Toplevel):
    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        self.config(bg="light grey")
        self.title("Configuration de la partie")

        self.nom_joueur = ""
        self.couleur_joueur = ""
        self.nom_adversaire = ""
        self.couleur_adversaire = ""
        self.type_adversaire = StringVar()
        self.type_adversaire.set("")
        self.temps_chrono = 0
        self.option_aide = False

        self.cadres = {}
        self.cadres["titre"] = Frame(self, bg="light blue")
        self.cadres["joueur"] = Frame(self, bg="blue")
        self.cadres["adversaire"] = Frame(self, bg="light green")
        self.cadres["chrono"] = Frame(self, bg="green")
        self.cadres["aide"] = Frame(self, bg="pink")


        # Géométrie


        self.pady_defaut = 5
        self.padx_defaut = 10

        self.largeur_fenetre = 600
        self.hauteur_fenetre = 550
        self.largeur_cadres = self.largeur_fenetre - 2 * self.padx_defaut
        self.hauteur_cadres = int(round(self.hauteur_fenetre / len(self.cadres))) - 2 * self.pady_defaut

        self.cadre_titre_labels = Frame(self.cadres["titre"], bg="brown", height=self.hauteur_cadres,
                                        width=self.largeur_cadres / 2)
        self.cadre_titre_entrees = Frame(self.cadres["titre"], bg="beige", height=self.hauteur_cadres,
                                         width=self.largeur_cadres / 2)

        self.cadre_titre_labels.pack(side=LEFT, fill=BOTH, expand=1)
        self.cadre_titre_entrees.pack(side=LEFT, fill=BOTH, expand=1)

        self.label_nom_joueur = Label(self.cadre_titre_labels)
        self.label_couleur_joueur = Label(self.cadre_titre_labels)
        self.label_nom_joueur.config(text="Votre nom:  ")
        self.label_couleur_joueur.config(text="Vous jouerez avec les:  ")

        self.label_nom_joueur.pack(side=TOP, fill=BOTH, expand=1)
        self.label_couleur_joueur.pack(side=TOP, fill=BOTH, expand=1)

        self.entry_nom_jouer = Entry(self.cadre_titre_entrees)
        self.cadre_radio_couleur = Frame(self.cadre_titre_entrees)
        self.radio_joueur_blanc = Radiobutton(self.cadre_radio_couleur)
        self.radio_joueur_noir = R

        self.geometry(f"{str(self.largeur_fenetre)}x{str(self.hauteur_fenetre)}")
        for cadre in self.cadres.values():
            cadre.config(width=self.largeur_cadres, height=self.hauteur_cadres)
            cadre.pack(side=TOP, pady=self.pady_defaut, padx=self.padx_defaut, fill=BOTH, expand=1)



if __name__=="__main__":
    fenetre = Tk()
    fenetre.withdraw()
    conf = FenetreDeConfiguration(fenetre)
    conf.deiconify()

    fenetre.mainloop()


