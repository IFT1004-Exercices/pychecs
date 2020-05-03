from random import randrange
import socket
import threading
import sys
from time import sleep
import json
from pychecs2.interface.ControleurDePartieContre import ControleurDePartieContre

from tkinter import Tk

HOST = "192.168.2.17"
PORT = 60002

class ThreadSaisieDeMessages(threading.Thread):
    """Thread permettant au joueur de converser avec l'adversaire en simultané."""

    def __init__(self, controleur):
        threading.Thread.__init__(self)
        self.controleur = controleur
        self.message = ""

    def run(self):
        print(f"Client {self.controleur.nom} prêt à fonctionner.")
        self.message = input(f"{self.controleur.nom} votre message >> ")
        while self.controleur.attendreReponses:

            # Pour interrompre la connexion
            if self.message == "FIN":
                break
            else:
                self.controleur.nouveauMessage(self.message)
                self.message = input(f"{self.controleur.nom} votre message >> ")
        print("Fin du threadSaisieDeMessage")


class ControleurDeClient():
    """Objet controleur générique.  Contient les méthodes interface avec l'objet SimpleClient:

    obtenirLeNom:  retourne un nom d'utilisateur
    genererDesMessages:  rajoute des messages à envoyer sur une liste d'attente
    recevoirMessage:  reçoit des messages et les dispatch adéquatement à l'utilisateur
    dernierMessage:  retourne le prochain message à envoyer"""

    def __init__(self, nom=None):

        # Ici nom est notre propre nom!
        if nom is None:
            self.nom = f"Controleur {randrange(10000)}"
        else:
            self.nom = nom

        # Liste des messages en attente d'envoi
        self.messagesEnAttente = []

        # Il faudra implémenter un hread indépendant qui saisit des messages et les installe dans la liste d'attente.
        self.attendreReponses = True
        self.generateurDeMessages = ThreadSaisieDeMessages(self)
        self.generateurDeMessages.start()

    def obtenir_le_nom(self):
        return self.nom

    def nouveauMessage(self, message):
        self.messagesEnAttente.append(message)

    def recevoirMessage(self, message):
        print(message)

    def dernierMessage(self):
        if self.messagesEnAttente:
            return(self.messagesEnAttente.pop(0))
        else:
            return ""


class ThreadRecepteur(threading.Thread):
    """Thread récepteur du client.  Contôle aussi un thread émetteur.

    Attributes:
        connexion:  Connexion au socket serveur
        controleur:  Objet responsable de recevoir, interpréter et envoyer les messages
        threadEmetteur:  Thread émetteur qui sera terminé par le thread récepteur."""

    def __init__(self, connexion, controleur, threadEmetteur):
        threading.Thread.__init__(self)
        self.connexion = connexion
        self.controleur = controleur
        self.threadEmetteur = threadEmetteur

    def run(self):
        """Accepte les messages du serveur et les envoie au contrôleur"""
        #print("Thread récepteur en marche")
        while True:
            message = self.connexion.recv(1024).decode("Utf8")
            if message == "FIN":
                break
            elif message:
                self.controleur.recevoirMessage(message)
            else:
                pass
        print("Client se déconnecte.")
        self.threadEmetteur.terminer()
        self.connexion.close()
        print("Connexion client terminée.")


class ThreadEmetteur(threading.Thread):
    """Thread émetteur du client:  prend fin lorsque le thread récepteur prend fin.

    Attributes:
        connexion:  Connexion au socket serveur
        controleur:  Objet responsable de recevoir interpréter et renvoyer des messages
        continuer:  Si True, le thread continue
        """

    def __init__(self, connexion, controleur):
        threading.Thread.__init__(self)
        self.connexion = connexion
        self.controleur = controleur
        self.continuer = True

    def run(self):
        """Envoie les messages du contrôleur au serveur"""
        #print("Thread émetteur en marche")
        while self.continuer:
            message = self.controleur.dernierMessage()
            if message:
                print(f"Thread émetteur message = {message}")
                self.connexion.send(message.encode("Utf8"))

    def terminer(self):
        """Met fin au thread émetteur"""
        self.continuer = False


class SimpleClient():
    """Client qui utilise les threads émetteur et receveur pour relayer des messages d'un serveur à un objet
     controleur.

     Attributs:

     controleur:  Objet qui reçoit, interprète et renvoie des messages
     connexion:  Connexion au serveur
     threadEmetteur:  thread qui envoie des messages au serveur
     threadRecepteur:  thread qui reçoit les messages du serveur."""

    def __init__(self, controleur):

        self.controleur = controleur
        self.nom = controleur.nom
        self.connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Demander une connexion au serveur
        try:
            self.connexion.connect((HOST, PORT))
        except IOError:
            sys.exit()

        # Authentifier en envoyant son nom
        sleep(1)
        self.connexion.send(self.nom.encode("Utf8"))

        #print(f"Connecté au serveur sous le nom: {self.nom}")

        # Commencer à émettre et recevoir
        self.threadEmetteur = ThreadEmetteur(self.connexion, self.controleur)
        self.threadRecepteur = ThreadRecepteur(self.connexion, self.controleur, self.threadEmetteur)
        self.threadEmetteur.start()
        self.threadRecepteur.start()

class ThreadAttendreUnCoup(threading.Thread):

    def __init__(self, controleur):
        threading.Thread.__init__(self)
        self.controleur = controleur
        self.arretUrgence = False

    def run(self):
        print("En attente de la riposte adverse...")
        while True:
            if self.controleur.riposte or self.arretUrgence:
                break
        print("Attente terminée...")

    def setArretUrgence(self):
        self.arretUrgence = True

class ControleurPychecs(ControleurDeClient):

    def __init__(self, nom=None, fenetre=None):

        self.mode = "solitaire"
        ControleurDeClient.__init__(self, nom)

        # Le client transmettra le nom au serveur pour se connecter
        self.client = SimpleClient(self)

        # Variable d'état indiquant si on peut jouer: "solitaire", "attente", "sollicite", ou "apparie"

        self.nom_adversaire = ""
        self.jetonsAcceptes = {"solitaire": ["JOINDRE", "LISTE"],
                               "attente": ["ACCEPTER", "CONFIRMER", "REFUSER"],
                               "apparie": ["JOUER", "CONVERSER", "FIN"]}

        # Variable d'état lorsqu'on joue
        self.trait = False
        self.couleur = ""

        # Variable contenant le coup à renvoyer à l'utilisateur
        self.riposte = ""

        # Variable contenant une réponse attendue
        self.reponseUtilisateur = ""

        # Thread d'attente du prochain coup
        self.threadAttendreUnCoup = ThreadAttendreUnCoup(self)

        # Thread d'attente d'une réponse
        self.threadAttendreReponseUtilisateur = ThreadAttendreUneReponseUtilisateur(self)
        self.threadAttendreReponseUtilisateur.start()

        # Objets graphiques
        self.partie = None
        self.fenetre = fenetre

    def obtenir_le_nom(self):
        if self.nom_adversaire:
            return self.nom_adversaire
        else:
            return "Adversaire X"

    def recevoirMessage(self, message):
        print(f"Message reçu: {message}")
        print(f"mode actuel = {self.mode}")

        jeton = message.split("$")
        print(jeton)

        # Les messages doivent être acceptés selon le mode du contrôleur
        if not jeton[1] in self.jetonsAcceptes[self.mode]:
            return

        # En mode solitaire:  recevoir la liste des clients ou une demande de pairage
        if self.mode == "solitaire":
            if jeton[1] == "JOINDRE":
                print(f"Client {jeton[0]} veut jouer avec vous.")
                self.nom_adversaire = jeton[0]
                return
            if jeton[1] == "LISTE":
                try:
                    liste = json.loads(jeton[2])
                except Exception:
                    print("Le serveur a renvoyé une liste illisible.")
                    return
                if liste:
                    print(f"Liste des clients connectés: {liste}")
                    return
                print("Aucun client connecté au serveur.")
            return

        # En mode apparié, on peut converser, jouer ou terminer le pairage
        if self.mode == "apparie":
            if self.nom_adversaire != jeton[0]:
                return
            if jeton[1] in self.jetonsAcceptes["apparie"]:
                if jeton[1] == 'FIN':
                    print(f"Votre partenaire {self.nom_adversaire} se déconnecte.")
                    self.mode = "solitaire"
                    self.nom_adversaire = ""
                    return
                if jeton[1] == "CONVERSER":
                    if jeton[2]:
                        print(f"{self.nom_adversaire} >> {jeton[2]}")
                        return
                    return
                if jeton[1] == "JOUER":
                    self.riposte = json.loads(jeton[2])
                    print(f"recevoir message a la riposte: {self.riposte}")
                    return


        # En mode attente il faut être accepté, refusé ou confirmé
        if self.mode == "attente":
            if jeton[1] == "ACCEPTER":

                # On va passer en mode apparié et débuter la partie lorsque le message confirmer sera envoyé.
                print(f"{jeton[0]} accepte de jouer avec vous.  Veuillez confirmer.")
                return

            if jeton[1] == "REFUSER":
                self.mode = "solitaire"
                print(f"{jeton[0]} ne veut plus jouer.")
                return

            if jeton[1] == "CONFIRMER":
                print(f"{jeton[0]} a confirmé vouloir jouer.  Vous aurez les blancs.")
                self.mode = "apparie"
                self.couleur = "blanc"
                self.trait = True
                print("DÉMARRAGE DE PARTIE BLANCS!!!")
                if not self.partie is None:
                    print("Il y a déja une partie démarrée.")
                    return
                self.partie = ControleurDePartieContre(adversaire=self,
                                                  couleur_joueur="blanc",
                                                  master=self.fenetre,
                                                  dictionnaire=None,
                                                  nom_blancs=self.nom,
                                                  nom_noirs=self.nom_adversaire,
                                                  joueur_actif="blanc",
                                                  id_partie=None,
                                                  liste_coups=None,
                                                  gagnant=None,
                                                  sauvegardee=False,
                                                  fichier_sauvegarde=None)
                return

                # TODO: Ici insérer le code pour débuter une nouvelle partie avec les noirs, mon nom et self.nom_adversaire
                # TODO:  Il faut aussi démarrer le thread de conversation
            print(f"Mode résultant: {self.mode}")

    def nouveauMessage(self, message):
        """Reçoit les messages saisis dans le thread de saisie de message.  Les traite selon le mode actuel."""

        if not message:
            return

        jeton = ["", self.nom, "", ""]

        if self.mode == "apparie":
            jeton[0] = self.nom_adversaire

            if message.lower() in ["fin", "finir", "quit", "quitter"]:
                jeton[2] = "FIN"
                self.attendreReponses = False

            else:
                tokens = message.split("$")
                if len(tokens) == 4 and tokens[2] == "JOUER":
                    print(f"Message envoyé: {message}")
                    ControleurDeClient.nouveauMessage(self, message)
                    return
                else:
                    jeton[2] = "CONVERSER"
                    jeton[3] = message

        elif self.mode == "attente":
            jeton[0] = self.nom_adversaire
            if message.lower() in ["refuser", "refus", "non"]:
                jeton[2] = "REFUSER"
                self.mode = "solitaire"
                self.nom_adversaire = ""

            elif message.lower() in ["confirmer", "confirme"]:
                self.mode = "apparie"
                self.trait = False
                self.couleur = "noir"
                # TODO Il faut ici démarrer une partie sous notre nom et nom adv, nous avons les noirs
                jeton[2] = "CONFIRMER"
                print("DÉMARRAGE DE PARTIE AVEC LES NOIRS")
                if not self.partie is None:
                    print("Il y a déja une partie démarrée.")
                    return
                self.partie = ControleurDePartieContre(adversaire=self,
                                                       couleur_joueur="noir",
                                                       master=self.fenetre,
                                                       dictionnaire=None,
                                                       nom_blancs=self.nom_adversaire,
                                                       nom_noirs=self.nom,
                                                       joueur_actif="blanc",
                                                       id_partie=None,
                                                       liste_coups=None,
                                                       gagnant=None,
                                                       sauvegardee=False,
                                                       fichier_sauvegarde=None)
                self.attendre()

            else:
                print("Commande acceptées à ce stade:  confirmer ou refuser")
                return

        elif self.mode == "solitaire":

            if message.lower() in ["liste", "list"]:
                jeton = ["LISTE"]

            elif message.lower() in ["fin", "finir"]:
                self.attendreReponses = False
                jeton = ["FIN"]

            else:
                mots = message.split(" ")
                if len(mots) < 2:
                    print("Réponse illisible.  SVP faire 'joindre nom' ou 'accepter nom' ou 'refuser nom'")
                    return

                jeton[0] = mots[1]
                if mots[0].lower() in ["join", "joindre"]:
                    jeton[2] = "JOINDRE"
                    self.mode = "attente"
                    self.nom_adversaire = mots[1]

                elif mots[0].lower() in ["accepter", "accept"]:
                    jeton[2] = "ACCEPTER"
                    self.mode = "attente"

                elif mots[0].lower() in ["refuser", "refus"]:
                    jeton[2] = "REFUSER"
                    self.nom_adversaire = ""
                else:
                    print("Commandes acceptées à ce stade:  joindre, accepter, refuser, liste")
                    return
        else:
            print(f"Erreur interne du serveur, mode non valable: {self.mode}")
            return

        messageEnvoye = "$".join(jeton)
        print(f"Message envoyé:  {messageEnvoye}")
        ControleurDeClient.nouveauMessage(self, messageEnvoye)

    def attendre(self):
        # Attendre la riposte avec un thread approprié.  Le thread cesse lorsque la riposte est non-vide.
        self.riposte = ""
        self.threadAttendreUnCoup.start()

        # Retourner la riposte
        return self.riposte

    def jouer(self, coup):
        """Méthode interface avec le contrôleur de partie contre.  Accepte un coup de ce contrôleur et retourne une
        riposte de l'adversaire distant."""

        # Traduire le dict coup en format json
        code = json.dumps(coup)

        # L'emballer et mettre le message dans la file d'attente
        message = "$".join([self.nom_adversaire, self.nom, "JOUER", code])
        self.nouveauMessage(message)

        # Attendre la riposte avec un thread approprié.  Le thread cesse lorsque la riposte est non-vide.
        self.riposte = ""

        self.threadAttendreUnCoup.start()

        # Retourner la riposte
        return self.riposte

class ThreadAttendreUneReponseUtilisateur(threading.Thread):

    def __init__(self, controleur):
        threading.Thread.__init__(self)
        self.controleur = controleur
        self.message = ""

    def run(self):
        print("Début du thread attendre reponse")
        print(f"Client {self.controleur.nom} prêt à fonctionner.")
        self.message = input(f"{self.controleur.nom} votre message >> ")
        print(self.controleur.attendreReponses)
        while self.controleur.attendreReponses:

            # Pour interrompre la connexion
            if self.message.lower() in ["fin", "finir", "quitter", "exit"]:
                self.controleur.nouveauMessage("FIN")
                break
            else:
                self.controleur.nouveauMessage(self.message)
                self.message = input(f"{self.controleur.nom} votre message >> ")
        print("Fin du threadAttendreUneReponseUsager")




    # def __init__(self, controleur):
    #     threading.Thread.__init__(self)
    #     self.controleur = controleur
    #
    # def run(self):
    #     nom = self.controleur.nom
    #     while self.controleur.attendreReponses:
    #         self.controleur.reponseUtilisateur = input(f"{nom} >> ")
    #         if self.controleur.reponseUtilisateur:
    #             break

class ThreadEchiquier(threading.Thread):
    def __init__(self, adversaire, couleur, master):
        threading.Thread.__init__(self)
        self.adversaire = adversaire
        self.couleur = couleur
        self.master = master

    def run(self):
        partie = ControleurDePartieContre(adversaire=self.adversaire, couleur_joueur=self.couleur, master=self.master)







if __name__ == "__main__":

    fenetre = Tk()
    client = ControleurPychecs(input("Votre nom: "), fenetre=fenetre)
    fenetre.mainloop()

