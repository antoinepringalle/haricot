# Haricot

## Description
Haricot est un prototype d’un boitier basé sur une **Raspberry Pi** permettant de réaliser automatiquement la vidéo de
**la pousse d’une plante**. Ce prototype utilise une caméra Raspberry Pi pointée sur une plante qui prend des photos à
un intervalle de temps donné. Ces photos sont stockées sur la Raspberry et sont accessibles sur le Wi-Fi de cette
dernière via une application web. Cette application permet aussi de réaliser le **timelapse** de la plante.

Une description du projet est disponible sur le site d'[Eirlab](https://www.eirlab.net/2022/01/09/haricots/), elle offre une présentation de ce projet avec des photos et un exemple de réalisation.

## Interface utilisateur
L’application web est une interface permettant de configurer et de monitorer la prise des photos. Elle donne accès notamment à un **dashboard** rassemblant les informations utiles (temps avant prochaine photo, espace mémoire restant sur la Raspberry, nombre de photos prises, et le temps écoulé depuis le debut de la capture.

Il est également possible de visionner les photos prises dans l’onglet **Photos**. Vous pourrez aussi supprimer les anciennes photos pour commencer un nouveau timelapse.

L’onglet **Timelapse** vous permet de générer un timelapse à partir des photos prises. Vous préciserez le nom de votre timelapse et le nombre d’images par secondes. L’option interpolation d’image permet de générer une image entre deux photos pour doubler le nombre d’images en entrée (⚠️ cette option est purement expérimentale, elle rajoute du flou).

Enfin dans les paramètres vous retrouverez une page pour modifier l’intervalle entre deux photos. Prenez un intervalle supérieur à 5 secondes pour éviter tout problème avec `raspistill` (le programme utilisé pour prendre la photo).

## Installation et Utilisation

Imprimez les pièces du dossier hardware et assemblez la coque de protection de la Raspberry Pi 4 et le bras de la caméra. 

Installez un Raspberry Pi OS disponible sur le [site officiel de la Raspberry Pi](https://www.raspberrypi.com/software/operating-systems/).

Pour installer Haricot sur votre Raspberry Pi, il suffit d'exécuter les scripts [`setup-hotspot.sh`](setup-hotspot.sh) et [`install-service.sh`](install-service.sh) pour lancer l'application au démarrage de la Raspberry. Pour lancer l'application directement, lancez `sudo systemctl start haricot-app`. Le serveur web est accessible sur le port `5000`.

Vous pouvez modifier les paramètres au démarrage de l'application en modifiant le fichier [`config.txt` ](config.txt). Si vous modifiez les credentials du hotspot, pensez à relancer le script [`setup-hotspot.sh`](setup-hotspot.sh).

## Remerciments

- L'interface web utilise le thème bootstrap [SB Admin 2](https://startbootstrap.com/theme/sb-admin-2). Merci à [Start Bootstrap](https://startbootstrap.com) pour leur travail.

- Merci à [Sébastien Delpeuch](https://github.com/Sdelpeuch) pour les scripts de génération de timelapse.
