# pychecs

Pychecs est un projet d'interface graphique en python pour jouer aux échecs.

## Installation

La version actuelle du programme est démarrée en exécutant __main__.py à-partir du dossier /pychecs.
Les librairies suivantes sont requises:

tkinter,
hashlib,
json,
time,
sys,
os

## Fonctionnalités actuelles

On peut jouer contre l'ordinateur ou contre un adversaire humain sur le même écran.  Le moteur d'échec
employé est [sunfish](https://github.com/thomasahle/sunfish), sous licence GNU GPL par Daniel Ahle, un moteur remarquable par sa légèreté.

Toutes les règles des échecs sont respectées, et l'interface détecte les mats, pats, mises en échec,
ainsi que la promotion du pion.  Si l'utilisateur le désire, l'interface peut indiquer les mouvements
qu'une pièce peut faire, ainsi que les mouvements possibles lorsqu'on est en échec.

Les coups peuvent être annulés en cascade jusqu'au début des parties.

## Fonctionnalités futures ou souhaitées

Affichage des pièces prises, drag and drop, mouvements animés des pièces avec sons.

Possibilité de configurer l'interface avec des thèmes

## Le jeu en réseau est le but ultime du projet:

Malheureusement je n'ai pas réussi à écrire un programme client fonctionnel, je me suis perdu dans un
dédale de threads...

## Contributions

Toutes les contributions sont les bienvenues, y-compris la traduction en anglais.  Les critiques et les
discussions sont aussi les bienvenues.

## Auteur

Pascal Charpentier

## Remerciements

Daniel Ahle pour [sunfish](https://github.com/thomasahle/sunfish)

## Droits

Ce code source est sous licence [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/).




