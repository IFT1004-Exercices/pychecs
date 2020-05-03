import socket
import threading
import sys
import json
from random import randrange

HOST = "192.168.2.17"
PORT = 60002



class ThreadClient(threading.Thread):
    def __init__(self, serveur, connexion, nom):

        threading.Thread.__init__(self)
        self.serveur = serveur
        self.connexion = connexion
        self.nom = nom

    def run(self):
        """Exécution du thread client: reçoit des messages et les renvoit au bon destinataire."""
        print(f"Thread client {self.nom} en marche")
        while True:
            message = self.connexion.recv(1024).decode("Utf8")
            print(f"{self.nom} >> {message}")
            if message and not self.transmettre(message):
                break

        # Le thread va fermer:  si on a un partenaire, il n'en a plus.  On s'enlève de la liste des clients et on
        # libère la connexion
        print(f"Fermeture du thread {self.nom} par le client.")
        del self.serveur.clients[self.nom]
        self.connexion.close()
        print(f"Client {self.nom} déconnecté.")

    def transmettre(self, message):

        jeton = message.split("$")

        # Cas d'une requête LISTE, il n'y a pas de destinataire, le serveur renvoie la liste des clients sans autre
        # forme de procès.  Peut-être utilisé pour tester la connexion.
        # Une requête FIN aussi peut être envoyée pour mettre fin à la connexion.

        if len(jeton) == 1:

            if jeton[0] == "LISTE":
                self.connexion.send(self.listeDesClients())
                return True

            if jeton[0] == "FIN":
                print(f"Client {self.nom} demande à déconnecter.")
                self.connexion.send('FIN'.encode("Utf8"))
                return False

        # Le message est mal formé ou des champs sont vides
        if not (jeton[0] or jeton[1] or jeton[2]):
            erreur = f"ERREUR$Message invalide: partiellement vide: {message}, envoyé à {self.nom}"
            self.connexion.send(erreur.encode("Utf8"))
            return True

        # Le destinataire est inconnu, on laisse tomber le message
        if not (jeton[0] in [nom for nom in self.serveur.clients.keys() if nom != self.nom]):
            erreur = f"ERREUR$Message de destinataire inconnu: {message}, envoyé à {self.nom}."
            self.connexion.send(erreur.encode("Utf8"))
            return True

        # L'envoyeur ne correspond pas au nom de notre thread, laisser tomber le message
        if not (jeton[1] == self.nom):
            erreur = f"ERREUR$Envoyeur inconnu: {message}"
            self.connexion.send(erreur.encode("Utf8"))
            return True

        # Trouver la connexion du destinataire, enlever son nom du message et transmettre
        connexion_destinataire = self.serveur.clients[jeton[0]][0]
        reponse = "$".join(jeton[1:])
        connexion_destinataire.send(reponse.encode("Utf8"))

        # Dans le cas où on veut une déconnexion:  enlever le client de la liste et mettre fin au thread
        if jeton[2] == "FIN":
            print(f"Client {self.nom} demande à déconnecter.")
            self.connexion.send('FIN'.encode("Utf8"))
            return False

        return True

    # def envoyerAClient(self, nom, message):
    #     if nom in self.serveur.clients.keys():
    #         connexion = self.serveur.clients[nom][0]
    #         connexion.send(message)
    #
    # def envoyerAPartenaire(self, message):
    #     connexion = self.serveur.clients[self.partenaire][0]
    #     connexion.send(message)

    def listeDesClients(self):
        """Retourne une liste de clients sérialisée et encodée"""

        liste = list(self.serveur.clients.keys())
        msg = "serveur$LISTE$" + json.dumps(liste)
        return msg.encode("Utf8")

    # def demandeDeConnexion(self, nom):
    #     if nom in self.serveur.clients.keys():
    #         if self.serveur.clients[nom][2] == "":
    #             return f"JOINDRE${self.nom}".encode("Utf8")
    #     return None

class RelaisServeur:
    def __init__(self):

        # Connexion initiale du serveur
        self.socketServeur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socketServeur.bind((HOST, PORT))
        except IOError:
            print(f"Le serveur ne peut établir la connection: {HOST}:{PORT}")
            sys.exit()
        print("Serveur Pascal en attente de message")
        self.socketServeur.listen(5)

        # Structure de données principale du serveur.
        # Chaque entrée sera un tuple:  connexion, thread, receveur
        self.clients = {}

        # Gestion des demandes de connexion
        # D'abord demander le nom du client et lui autoriser d'être inscrit
        while True:
            connexion, adresse = self.socketServeur.accept()

            decision = self.identifier(connexion)
            if decision:
                nom, client = decision
                print(f"Client {nom} connecté.")
                client.start()
                self.clients[nom] = connexion, client, ""
            else:
                print(f"Connexion refusée à {adresse}")
                connexion.close()

    def identifier(self, connexion):
        """Une fois la connexion établie, attend que le client fournisse un nom"""

        nom = ""
        while not nom:
            nom = connexion.recv(1024).decode("Utf8")
            if nom in self.clients.keys():
                reponse = f"Le nom {nom} est déjà présent dans la liste des clients!".encode("Utf8")
                connexion.send(reponse)
                return None
        return nom, ThreadClient(self, connexion, nom)



if __name__ == "__main__":

    serveur = RelaisServeur()

     # pascal = ControleurDeTest("Pascal")
     # client = SimpleClient(pascal)