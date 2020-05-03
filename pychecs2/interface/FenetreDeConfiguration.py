from tkinter import Toplevel, Label, Entry, Button, Radiobutton, Checkbutton, Tk, W, N, S, E, EW, BooleanVar, StringVar, NORMAL, DISABLED, ALL
from pychecs2.interface.ControleurDePartie import ControleurDePartie
from pychecs2.interface.ControleurDePartieContre import ControleurDePartieContre
from pychecs2.sunfish.sunfish import ControleurDeSunfish

from tkinter import ttk

class FenetreDeConfiguration(Toplevel):

    def __init__(self, master=None):

        Toplevel.__init__(self, master)
        self.title("Nouvelle partie")
        self.configure(bg="light grey")
        self.protocol("WM_DELETE_WINDOW", self.quitter)

        # Variables

        self.nom_blancs = StringVar()
        self.nom_blancs.set("Blancs")
        self.nom_noirs = StringVar()
        self.nom_noirs.set("Noirs")

        self.chrono_selectionne = BooleanVar()
        self.temps = StringVar()
        self.temps.trace_add("write", self.valider_temps)
        self.temps.set("")
        self.aide_selectionnee = BooleanVar()

        self.jouer_contre_ordinateur = BooleanVar()
        self.jouer_contre_ordinateur.set("False")

        # Widgets

        self.fonte = ("default", 25, "normal")

        self.nom_blancs_label = Label(self, text="Nom du joueur blanc:  ", font=self.fonte, bg="light grey")
        self.nom_noirs_label = Label(self, text="Nom du joueur noir:  ", font=self.fonte, bg="light grey")
        self.type_noirs_label = Label(self, text="Le joueur noir sera:  ", font=self.fonte, bg="light grey")
        self.check_chrono = Checkbutton(self, text="Partie chronométrée", variable=self.chrono_selectionne, font=self.fonte, bg="light grey", command=self.chrono)
        self.check_aide = Checkbutton(self, text="Montrer les mouvements permis", variable=self.aide_selectionnee, font=self.fonte, bg="light grey")
        self.nom_blancs_entry = Entry(self, textvariable=self.nom_blancs, font=self.fonte, bg="light grey")
        self.nom_noirs_entry = Entry(self, textvariable=self.nom_noirs, state=NORMAL, font=self.fonte, bg="light grey")
        self.ordi_radio = Radiobutton(self, text="L'ordinateur", variable=self.jouer_contre_ordinateur, value=True, font=self.fonte, bg="light grey", command=self.ordi_radio_selectionne)
        self.humain_radio = Radiobutton(self, text="Un humain", variable=self.jouer_contre_ordinateur, value=False, font=self.fonte, bg="light grey", command=self.humain_radio_selectionne)
        self.chrono_entry = Entry(self, textvariable=self.temps, state=DISABLED, font=self.fonte, bg="light grey", width=4)
        self.chrono_label = Label(self, text="minutes (1-60)", font=self.fonte, bg="light grey")
        self.jouer_button = Button(self, text="JOUER!", font=self.fonte, bg="light grey", command=self.bouton_jouer_presse)

        self.nom_blancs_label.grid(row=1, column=1, sticky=W, pady=10, padx=10)
        self.type_noirs_label.grid(row=2, column=1, sticky=W, pady=10, padx=10)
        self.nom_noirs_label.grid(row=3, column=1, sticky=W, pady=10, padx=10)
        self.check_chrono.grid(row=4, column=1, sticky=W, pady=10, padx=10)
        self.check_aide.grid(row=5, column=1, sticky=W, pady=10, padx=10)
        self.nom_blancs_entry.grid(row=1, column=2, columnspan=2, sticky=EW, pady=10, padx=10)
        self.ordi_radio.grid(row=2, column=2, sticky=W, pady=10, padx=10)
        self.humain_radio.grid(row=2, column=3, sticky=W, pady=10, padx=10)
        self.nom_noirs_entry.grid(row=3, column=2, columnspan=2, sticky=EW, pady=10, padx=10)
        self.chrono_entry.grid(row=4, column=2, sticky=E, pady=10, padx=10)
        self.chrono_label.grid(row=4, column=3, sticky=W, pady=10, padx=10)
        self.jouer_button.grid(row=6, column=1, columnspan=3, pady=10, padx=10)

        self.options = {}

    def quitter(self):
        self.master.bienvenue_apparait()
        self.destroy()

    def chrono(self):
        if self.chrono_selectionne.get():
            self.temps.set("20")
            self.chrono_entry.config(state=NORMAL, validate=ALL, validatecommand=self.valider_temps())
        else:
            self.temps.set("")
            self.chrono_entry.config(state=DISABLED)

    def ordi_radio_selectionne(self):

        self.nom_noirs_entry.config(state=DISABLED)
        self.nom_noirs.set("Sunfish")
        print(self.jouer_contre_ordinateur.get())

    def humain_radio_selectionne(self):

        self.nom_noirs_entry.config(state=NORMAL)
        self.nom_noirs.set("")
        print(self.jouer_contre_ordinateur.get())

    def bouton_jouer_presse(self):

        self.withdraw()

        if self.nom_blancs.get() == "":
            self.options["nom_blancs"] = "Blancs"
        else:
            self.options["nom_blancs"] = self.nom_blancs.get()

        if self.jouer_contre_ordinateur.get():
            self.options["ordinateur"] = True
            self.options["nom_noirs"] = "Sunfish"
        else:
            self.options["ordinateur"] = False
            if self.nom_noirs.get() == "":
                self.options["nom_noirs"] = "Noirs"
            else:
                self.options["nom_noirs"] = self.nom_noirs.get()

        self.options["aide"] = self.aide_selectionnee.get()

        self.options["chrono"] = self.chrono_selectionne.get()
        if self.options["chrono"]:
            self.options["temps"] = int(self.temps.get())
        else:
            self.options["temps"] = 0

        if self.options["ordinateur"]:
            self.master.controleur = ControleurDePartieContre(adversaire=ControleurDeSunfish(),
                                                              couleur_joueur="blanc",
                                                              master=self.master,
                                                              dictionnaire=None,
                                                              nom_blancs=self.options["nom_blancs"],
                                                              nom_noirs=self.options["nom_noirs"],
                                                              option_aide=self.options["aide"],
                                                              option_chrono=self.options["temps"])
        else:
            self.master.controleur = ControleurDePartie(master=self.master,
                                                        dictionnaire=None,
                                                        nom_blancs=self.options["nom_blancs"],
                                                        nom_noirs=self.options["nom_noirs"],
                                                        option_aide=self.options["aide"],
                                                        option_chrono=self.options["temps"])

    def valider_temps(self, *args):

        try:
            v = int(self.temps.get())
        except ValueError:
            self.temps.set("")
            return False
        else:
            if 0 < v < 60:
                return True
            self.temps.set("")
            return False





if __name__=="__main__":
    f = Tk()
    s = FenetreDeConfiguration(f)
    f.mainloop()
