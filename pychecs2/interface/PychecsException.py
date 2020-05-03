

from pychecs2.interface.AideContextuellePychecs import AIDE_CONTEXTUELLE, AIDE_CONTEXTUELLE_DEPLACER, generer_aide_chemin_bloque, AIDE_CONTEXTUELLE_PRENDRE
from pychecs2.echecs.piece import Pion, Tour, Cavalier, Fou, Dame, Roi


class PychecsException(Exception):
    def __init__(self, *args):
        self.message = AIDE_CONTEXTUELLE["PychecsException"]
    def __str__(self):
        return "Erreur dans Pychecs."


class ClicHorsEchiquierException(PychecsException):
    def __init__(self, *args):
        self.message = AIDE_CONTEXTUELLE["ClicHorsEchiquierException"]
    def __str__(self):
        return "Pour jouer, veuillez cliquer une case de l'échiquier."


class CaseInexistanteException(PychecsException):
    def __str__(self):
        return "Un identifiant de case inexistant a été utilisé."


class ReglesException(PychecsException):
    def __str__(self):
        return "Ce coup est interdit dans le jeu."


class TourException(ReglesException):
    def __init__(self, *args):
        if args:
            self.message_court = f"ATTENTION:  C'est au tour des {args[0]}s de jouer."
        else:
            self.message_court = f"Ne sautez pas votre tour!"
        self.message = AIDE_CONTEXTUELLE["TourException"]
    def __str__(self):
        return self.message_court


class CaseDepartVideException(ReglesException):
    def __init__(self, case):
        self.case = case
        self.message = AIDE_CONTEXTUELLE["CaseDepartVideException"]
    def __str__(self):
        return f"La case {self.case} est vide.  Il faut saisir une pièce!"


class CheminBloqueException(ReglesException):
    def __init__(self, source=None, cible=None, liste=None):
        if source is None or cible is None or liste is None:
            self.message = AIDE_CONTEXTUELLE["CheminBloqueException"]
        else:
            self.message = generer_aide_chemin_bloque(source,
                                                      cible,
                                                      liste) + "\n\n" + AIDE_CONTEXTUELLE["CheminBloqueException"]
    def __str__(self):
        return "Le chemin doit être libre entre les deux positions demandées."


class DeplacementImpossibleException(ReglesException):
    def __init__(self, *args):
        if not args is None:
            piece = args[0]
        else:
            piece=None
        if isinstance(piece, Pion):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Pion"]
        elif isinstance(piece, Tour):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Tour"]
        elif isinstance(piece, Cavalier):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Cavalier"]
        elif isinstance(piece, Fou):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Fou"]
        elif isinstance(piece, Dame):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Dame"]
        elif isinstance(piece, Roi):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Roi"]
        else:
            self.message = AIDE_CONTEXTUELLE["DeplacementImpossibleException"]

    def __str__(self):
        return "Le déplacement demandé est impossible pour cette pièce."


class PriseImpossibleException(ReglesException):

    def __init__(self, *args):

        if not args is None:
            piece = args[0]
        else:
            piece = None

        # Seul le pion fait une prise de manière différente.
        if isinstance(piece, Pion):
            self.message = AIDE_CONTEXTUELLE_PRENDRE["Pion"]
        elif isinstance(piece, Tour):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Tour"]
        elif isinstance(piece, Cavalier):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Cavalier"]
        elif isinstance(piece, Fou):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Fou"]
        elif isinstance(piece, Dame):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Dame"]
        elif isinstance(piece, Roi):
            self.message = AIDE_CONTEXTUELLE_DEPLACER["Roi"]
        else:
            self.message = AIDE_CONTEXTUELLE["DeplacementImpossibleException"]

    def __str__(self):
        return "La prise demandée est impossible pour cette pièce."


class CaseArriveeOccupeeException(ReglesException):
    def __init__(self, *args):
        if args:
            self.case = args[0]
        self.message = AIDE_CONTEXTUELLE["CaseArriveeOccupeeException"]
    def __str__(self):
        return f"La case d'arrivée {self.case} est occupée."


class RoqueNonAutoriseException(ReglesException):
    def __init__(self, *args):
        if args is None:
            self.message = AIDE_CONTEXTUELLE["RoqueNonAutoriseException"]
        else:
            self.message = args[0] + "\n" + AIDE_CONTEXTUELLE["RoqueNonAutoriseException"]
    def __str__(self):
        return f"Le roque n'est pas autorisé."


class EchecAuRoiProvoqueException(ReglesException):
    def __str__(self):
        return "On ne peut mettre, ni laisser son propre roi en échec."


class PriseEnPassantNonAutoriseeException(ReglesException):
    def __init__(self):
        self.message = AIDE_CONTEXTUELLE["PriseEnPassantNonAutoriseeException"]
    def __str__(self):
        return "La prise en passant n'est pas autorisée."


class CouleurSeMetElleMemeEnEchecException(ReglesException):
    def __init__(self, *args):
        self.message = AIDE_CONTEXTUELLE["CouleurSeMetElleMemeEnEchecException"]
    def __str__(self):
        return "Un joueur ne peut jamais mettre, ni laisser son propre roi en échec."


if __name__ == "__main__":
    pass
