# trace histo todo

Fichier retraçant les choix sur les todo

## Vire

- TODO: check seance ref et session ref qu'on recup mal (et peut être pas partout dans fichier) ? utile ?
  - -> nope pas dans fichiers
- TODO: role débat : c'est que c'est mal identifié dans les fichiers tout cour ou on a un possible pb ?
  - -> mal identifié fichiers

- TODO: on parle dans l'intro d'exclure congrès + lamartine. C'est fait ? pas directement non ?
  - Ou alors c'est fait en mode pas explicite mais bien le cas par les différents filtres ?
  - -> virer de l'introduction si pas fait dans le code.

- TODO : rares cas d'interventions mal identifiées par leur PA, mais  bon nom
  - M. Éric Poulliat, identifié sous PA Darmanin sur une interv (id_syceron : 2394545)
  - notre code nettoyage renvoi le nom nettoyé majoritaire darmain associé au PA
  - -> on peut pas tout avoir parfait, moindre mal plutôt que ne pas avoir des noms homogènes
  - -> et surtout se réfère au PA qui est plus stable dans l'ensemble
  - -> dernière option serait sinon de pas toucher aux noms puis de faire un fuzzy match pour garder qu'une forme ?
  - -> mais trop éloigné pour certains quand ajoute la qualité de ministre, etc.
  - -> ajout d'un com dans le code sur limite de la fonction

- TODO: cas rares ou ID orateur plus précis (bon code) que ID acteur qui a PA0
  - -> NON : en fait ce sont des interruptions avec plusieurs locuteurs.
  - id_orateur en renvoie (mal) un seul -> on préfère garder le PA0 (neutre)

- TODO : on pourrait imaginer une dernière étape de check nom original vs final renvoyé pour gérer les cas limites ?
  - semble ok jusque là, aviser en fonction si gros souci ?

