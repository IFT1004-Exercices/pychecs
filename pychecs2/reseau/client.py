import socket, threading, sys

host = '192.168.2.17'
port = 50000

class ThreadReception(threading.Thread):
    def __init__(self, connexion, thread_emission):
        threading.Thread.__init__(self)
        self.connexion = connexion
        self.thread_emission = thread_emission

    def run(self):
        while True:
            message_recu = self.connexion.recv(1024).decode("Utf8")
            print("*" + message_recu + "*")
            if not message_recu or message_recu.upper() == "FIN":
                break
        self.thread_emission._stop()
        print("Client arrêté, connexion interrompue.")
        self.connexion.close()

class ThreadEmission(threading.Thread):
    def __init__(self, connexion):
        threading.Thread.__init__(self)
        self.connexion = connexion

    def run(self):
        while True:
            message_emis = input("***")
            self.connexion.send(message_emis.encode("Utf8"))

connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    connexion.connect((host, port))
except socket.error:
    print("Échec de connexion.")
    sys.exit()
else:
    print("Connecté au serveur")

    thE = ThreadEmission(connexion)
    thR = ThreadReception(connexion, thE)
    thE.start()
    thR.start()

    




