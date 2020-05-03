from pychecs2.echecs.piece import Pion, Tour, Cavalier, Fou, Dame, Roi

AIDE_CONTEXTUELLE = {
    "PychecsException":
        """Bienvenue!  Au jeu d'échec, deux adversaires, représentés par les couleurs blanche et noire des pièces, s'affrontent  en déplaçant à tour de rôle leurs pièces sur les cases de l'échiquier. 
         
         Le but du jeu est de capturer le roi adverse.
         
        Il est interdit de jouer deux tours de suite, ou de sauter un tour.  
        
        Pour jouer, cliquez sur une pièce pour la sélectionner.
        
        Ensuite cliquez sur la case où vous voulez déplacer la pièce: cette case doit être vide, ou occupée par une pièce adverse, qui sera alors enlevée du jeu.""",

    "ClicHorsEchiquierException":
        """Pour jouer, cliquez sur une des cases de l'échiquier.  Aucun mouvement ou coup ne sera possible en-dehors de la surface de jeu.""",

    "CaseInexistanteException": "",

    "ReglesException": "",

    "TourException":
        """Les deux joueurs doivent jouer à tour de rôle.  Il est interdit de jouer deux fois consécutives, et il est aussi interdit de sauter son tour.""",

    "CaseDepartVideException":
        """Un joueur doit déplacer une pièce à tous les coups.  Donc, un coup doit toujours commencer par la sélection d'une pièce.  
        
        Il est impossible de débuter un coup en sélectionnant une case vide.""",

    "CheminBloqueException":
        """Pour déplacer une pièce d'une case à l'autre, les cases situées sur le trajet de la pièce doivent être libres.
        
        La case d'arrivée, quant à elle, doit être soit libre, soit occupée par une pièce de couleur adverse, qui seraalors retirée du jeu.
        
        Seul le cavalier peut sauter par-dessus d'autres pièces.""",

    "DeplacementImpossibleException":
        """La pièces sélectionnée ne peut faire ce déplacement.""",

    "PriseImpossibleException":
        """La pièce sélectionnée ne peut faire le coup demandé.""",

    "CaseArriveeOccupeeException":
        """Lorsque l'on déplace une pièce d'une case à l'autre, la case de destination ne peut pas être occupée par une autre pièce de la même couleur.""",

    "RoqueNonAutoriseException":
        """Pour pouvoir roquer, le roi ne peut être en échec, les cases entre le roi et la tour doivent être libres, aucune de ces cases ne peut être menacée par une pièce adverse, et le roi et la tour ne doivent pas avoir été déplacées.""",

    "PriseEnPassantNonAutoriseeException":
        """La prise en passant n'est possible que pour un pion blanc situé sur la rangée 5 ou un pion noir situé sur la
        rangée 4.  Le pion pris en passant doit avoir sauté une case au coup précédent.""",

    "CouleurSeMetElleMemeEnEchecException":

    "Il est interdit à un joueur de se mettre lui-même en échec, que ce soit en déplaçant son roi à portée d'une pièce adverse, "
    "ou en enlevant une de ses propres pièces qui bloquait une menace au roi.",

    "echec":

    """Vous êtes en échec car votre roi est menacé.  Il est obligatoire de sauver votre roi, en le déplaçant, en prenant la pièce qui le menace, ou en bloquant le trajet de cette pièce.  Si l'option aide a été sélectionnée, les mouvements possibles sont indiqués en rouge sur l'échiquier."""}


AIDE_CONTEXTUELLE_DEPLACER = {"Pion": """Le pion ne peut avancer que d'une case, sur la même colonne.  Il ne peut jamais reculer, ni bouger latéralement ou diagonalement.  Par-contre, lorsqu'il se trouve sur sa case de départ, il peut sauter une case et avancer de deux.""",
                              "Tour": """La tour peut se déplacer en ligne droite, d'une ou plusieurs cases, soit sur la même ligne ou la même colonne.  Elle ne peut jamais se déplacer en diagonale, ni sur un trajet qui n'est pas une ligne droite.""",
                              "Cavalier":  """Le cavalier est la seule pièce qui peut sauter par-dessus d'autres pièces.  Il suit toujours un trajet en forme de "L":  deux cases horizontalement puis une case verticalement, ou deux cases verticalement et une case horizontalement.""",
                              "Fou": """Le fou se déplace en ligne droite, d'une ou plusieurs cases, toujours sur une diagonale.  Donc, un fou sur une case noire devrait toujours rester sur les cases  noires, et vice-versa.""",
                              "Dame": """La dame peut se déplacer en ligne droite, d'une ou plusieurs cases, soit horizontalement, soit verticalement, soit sur une diagonale.""",
                              "Roi": """Le roi peut se déplacer horizontalement, verticalement ou diagonalement, mais toujours d'une seule case."""}

AIDE_CONTEXTUELLE_PRENDRE = {"Pion":  """Le déplacement et la prise sont différents pour un pion.  Le pion prend une pièce en se déplaçant en diagonale, d'une seule case, alors qu'il se déplace verticalement s'il ne fait pas de prise."""}

MSG_CHEMIN_BlOQUE = """Vous avez tenté de déplacer une pièce entre {} et {}, mais {} {} {} le chemin."""

def generer_aide_chemin_bloque(source, cible, liste):
    if len(liste) == 1:
        txt_case = "la case"
        txt_occ = "est occupée et bloque"
        enumeration = liste[0]
    else:
        txt_case = "les cases"
        txt_occ = "sont occupées et bloquent"
        enumeration = ""
        for item in liste:
            enumeration += item + ", "
    return MSG_CHEMIN_BlOQUE.format(source, cible, txt_case, enumeration, txt_occ)

