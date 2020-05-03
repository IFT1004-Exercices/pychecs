import tkinter as tk

class ListeDeroulante(tk.Frame):

    def __init__(self, maitre, elements = None, lignes=15, largeur=30, texteInitial="", **kwargs):
        """Constructeur

        Args:
            maitre(widget):  Objet maître
            elements([str]):  Éléments à afficher
            **kwargs(dict):  Options du Frame parent"""

        # Initialisation du parent, c'est un simple cadre
        tk.Frame.__init__(self, maitre, **kwargs)

        # Source de données de l'objet graphique:  liste d'éléments textuels.
        # Par-défaut, il n'y a pas d'élément sélectionné dans la liste, ni de résultat de recherche
        if elements is None:
            self.elements = []
        else:
            self.elements = elements
        self.elementSelectionne = tk.IntVar()
        self.elementSelectionne.set(None)
        self.elementsRecherches = []

        # Créer deux sous-cadres pour faciliter la répartition des éléments:  un pour la zone de recherche et un pour
        # la liste déroulante.
        self.cadreRecherche = tk.Frame(self, bg="yellow")
        self.cadreListe = tk.Frame(self, bg="pink")


        # Créer une liste et une barre de défilement
        self.barre = tk.Scrollbar(self.cadreListe, orient=tk.VERTICAL, bg="light grey", troughcolor="light grey")
        self.liste = tk.Listbox(self.cadreListe, height=lignes, width=largeur, yscrollcommand=self.barre.set, bg="light grey")


        # Remplir la liste avec les éléments
        for item in self.elements:
            self.liste.insert(tk.END, item)
        self.liste.see(tk.END)

        # Associer l'évènement double-clic dans la zone de recherche à la sélection d'un élément
        self.liste.bind("<Double-Button-1>", self.selectionDansListe)



        # Créer une zone d'entrée de texte pour la recherche d'un élément avec une variable texte associée
        self.nomRecherche = tk.StringVar()
        self.nomRecherche.set(texteInitial)
        self.zoneDeRecherche = tk.Entry(self.cadreRecherche, textvariable = self.nomRecherche, bg = "light grey", borderwidth=0, highlightthickness=0)
        self.zoneDeRecherche.bind('<Return>', self.selectionDansListe)

        # Associer la variable texte de la zone de saisie à la fonction de rechercher dans la liste
        self.nomRecherche.trace("w", self.actualiserListe)

        # Associer la barre de défilement avec la liste d'éléments, répartir dans leur cadres respectifs
        self.zoneDeRecherche.pack(side=tk.LEFT, fill=tk.X, anchor=tk.N, expand=1)
        self.barre.config(command=self.liste.yview)
        self.barre.pack(side=tk.RIGHT, fill=tk.Y)
        self.liste.pack(side=tk.LEFT, anchor=tk.N, fill=tk.BOTH, expand=1)

        # Répartir les deux sous-cadres dans le cadre parent
        self.cadreRecherche.pack(side=tk.TOP, fill=tk.X, anchor=tk.N, expand=1)
        self.cadreListe.pack(anchor="ne", fill=tk.BOTH, expand=1)

    def actualiserListe(self, *argument):
        """Permet de rechercher un élément de la liste à-partir de la zone de saisie"""

        # Liste des résultats de la recherche remise à zéro
        self.elementsRecherches = []

        # Repasser tous les éléments de la liste initiale, et trouver ceux qui contiennent le texte recherché
        for item in self.elements:
            if self.nomRecherche.get().lower() in item.lower():
                self.elementsRecherches.append(item)

        # Aucun élément retrouvé: retourner
        if len(self.elementsRecherches) == 0:
            return

        # Éléments trouvés: effacer la liste, et afficher seulement les éléments de la liste des résultats
        self.liste.delete(0, tk.END)
        for item in self.elementsRecherches:
            self.liste.insert(tk.END, item)

    def selectionDansListe(self, event):

        # Touche return pressée dans la zone de saisie
        if event.type == tk.EventType.KeyPress:

            # Aucun élément dans la liste des recherches
            if len(self.elementsRecherches) == 0:
                self.elementSelectionne.set(None)

            # Si la liste ne contient plus qu'un seul élément, le sélectionner, sinon, sortir
            if len(self.elementsRecherches)==1:
                self.elementSelectionne.set(self.elementsRecherches[0])

        # Double-clic dans la liste:  retourner la sélection active
        elif event.type == tk.EventType.ButtonPress:

            # On ne va sélectionner qu'un seul élément
            self.elementSelectionne.set(self.liste.curselection()[0])

    def selection(self):
        """Méthode interface permettant d'accéder à la sélection courante.  None si rien n'a été sélectionné."""
        return self.elementSelectionne

    def update(self, nouvelle_liste = None):
        if not nouvelle_liste is None:
            self.elements = nouvelle_liste
        self.liste.delete(0, tk.END)
        for element in self.elements:
            self.liste.insert(tk.END, element)
        self.liste.see(tk.END)

    def insert(self, index, element):
        self.elements.append(element)
        self.liste.insert(tk.END, element)
        self.liste.see(tk.END)

    def delete(self, first, last=None):
        self.liste.delete(first)
        self.liste.see(tk.END)

if __name__ == "__main__":
    liste = [1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,123]
    listestr = [str(i) for i in liste]

    fen=tk.Tk()

    obj = ListeDeroulante(fen, listestr)
    obj.pack()
    fen.mainloop()
