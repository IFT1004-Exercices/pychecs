from time import time
from tkinter import StringVar, Label, Tk, Frame, Button, DISABLED, NORMAL

class Chronometre(Label):
    def __init__(self, master, minutes=15, texte_initial="", alarme="", nobutton=True, **kwargs):

        Label.__init__(self, master, kwargs)
        self.texte_initial = texte_initial
        self.nobutton = nobutton
        self.temps = int(minutes * 60)
        self.ecoule = 0
        self.duree_affichee = StringVar()
        self.duree_affichee.set(self.texte_initial + f"{int(minutes):02d}:00")
        self.texte_alarme = alarme
        self.config(textvariable=self.duree_affichee)
        self.marche=None

        if not nobutton:
            self.bou = Button(master, text="Durée", command=self.debuter)
            self.bou.pack()
        else:
            self.debuter()



    def debuter(self):
        if not self.nobutton:
            self.bou.config(text="Pause", command=self.arreter)
        self.debut = time()
        self.marche=True
        self.tic()

    def mise_a_jour(self, duree):
        min = int(duree // 60)
        sec = int(duree % 60)
        self.duree_affichee.set(self.texte_initial + f"{min:02d}:{sec:02d}")
        if not(min or sec):
            self.arreter()
            self.alarme()

    def tic(self):

        self.ecoule = time() - self.debut
        afterId = self.after(1000, self.tic)
        self.mise_a_jour(self.temps - self.ecoule)
        if not self.marche:
            self.after_cancel(afterId)

    def continuer(self):
        t_offset = time() - self.t_arret
        self.debut += t_offset
        self.bou.config(text="Pause", command=self.arreter)
        self.marche=True
        self.tic()


    def arreter(self):
        self.t_arret = time()
        if not self.nobutton:
            self.bou.config(text="Continuer", command=self.continuer)
        self.marche=False

    def alarme(self):
        self.duree_affichee.set(self.texte_initial + self.texte_alarme)
        if not self.nobutton:
            self.bou.config(state=DISABLED)


    def raz(self):
        self.ecoule = 0
        self.mise_a_jour(0)
        if not self.nobutton:
            self.bou.config(state=NORMAL)


if __name__ == "__main__":
    f = Tk()
    c = Chronometre(f, 0.2, "", "00:00", nobutton=False)
    c.pack()
    f.mainloop()







