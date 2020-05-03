import socket, sys, threading

host = "192.168.2.17"
port = 50000

class ThreadClient(threading.Thread):

    def __init__(self, connexion):

        threading.Thread.__init__(self)
        self.connexion = connexion

    def run(self):

        nom = self.getName()

        while True:

            msgClient = self.connexion.recv(1024).decode("Utf8")

            if not msgClient or msgClient.upper() == "FIN":
                break

            message = f"{nom}> {msgClient}"
            print(message)

            for cle in  connexion_client:
                if cle != nom:
                    connexion_client[cle].send(message.encode("Utf8"))

        self.connexion.close()
        del connexion_client[nom]
        print(f"Client {nom} déconnecté.")


monSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    monSocket.bind((host, port))

except OSError:
    print(f"Liaison échouée à {host}:{port}")
    sys.exit()

print("Serveur prêt, en attente de requête...")

monSocket.listen(5)
connexion_client = {}

while True:

    connexion, adresse = monSocket.accept()
    th = ThreadClient(connexion)
    th.start()

    it = th.getName()
    connexion_client[it] = connexion
    print(f"Client {it} connecté à {adresse[0]}:{adresse[1]}")
    msg = "Vous êtes connecté.  Envoyez votre message:  "
    connexion.send(msg.encode("Utf8"))