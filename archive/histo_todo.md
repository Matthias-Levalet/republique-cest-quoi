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

- TODO : recodage automatique temporel si NA entre GOUV le même jour :
  - 14 si sur affiliation après avoir forcé groupeAbrev
  - 67 si fait avant (sur affiliation_mandat_députés)
  - == FAIRE AVANT !!!
  - 

- TODO : cf FAIRE plus restrictif ?
  - depuis l'affil députés, pour éviter de rater des cas ou on aurait forcé un groupe à un ministre et qu'on flague pas qu'il est pas identifié comme ministre sur une intervention où il l'est
  - -> FAIT
- TODO: comparer ce que ça donne pour gouv entre affiliation_mandat_députés et affiliation_et_gouv pour voir si ça correspond bien
  - = cf on en trouvait sans doute comme ça des vides dans affiliation_mandat_députés qui étaient en fait des membres du gouv et que là on recode selon leur affiliation et pas en GOUV si l'info qualité orateur est pas bonne
  - pas identifié ministre machin car info manquante, autre statut comme rapporteur, etc.
  - ->  FAIT
- TODO: géréer les cas limites gouv quand sont commissaires, etc. (EDM, etc.)
  - -> normalement fait en prenant cas NA encadrés par GOUV

- TODO: autre option enchainement -> c'est ce qui est fait au final !
  - 1 tempo dynamique
  - 2 var affil_gouv : en ajoutant les cas qualite_orateur
  - 3 identifier les cas limites quand gouv + info manquante parfois
  - 4 si il faut les ajouter en "doute"
  - 5 forcer les affil restantes par dessus avec groupeAbrev.
  - 6 et au pire donc pour la var affil complète, réimposer les groupes pour le gouv


- TODO : check nb extract contre fichiers nosdeputés (en virant les italiques etc.)
- TODO: déduplication ? -> proposé un truc déjà, vérif (pas sur soit utile)
  - plus tard : # choisir la clé la plus pertinente
  - (["uid", "id_syceron", "texte"] VS uid + id_syceron seulement)
  - en réalité encore des choses qui ont double entrée pour même ID_paragraphe
  - mais avec texte différent = des didascalies, texte italique, etc.
  - si pas de Texte, 370 lignes supprimées (mais qui vireraient sans doute au cleaning des données)
- TODO: vérifier si on a pas d'autres doublons de fichier mal placés dans les législatures
  - check si possible automatiser à la lecture de tous les uid vs seance ref, etc. ?
- TODO : ON PEUT CHOPER LA DUPLICATION DE CAS PAR L'ID_SYCERON ET TEXTES !!
- TODO : tests congrès et pb séances doublons.

# TODO : exclusion fichiers jo :
- Avant exclusion des fichiers doublons / congrès :
- Shape du df chargé :  (1128128, 29)
- Shape du df après pré-nettoyage et pré-filtrage :  (683680, 32)
- après :
- Shape du df chargé :  (1127838, 29)
- Shape du df après pré-nettoyage et pré-filtrage :  (683489, 32)

sans rien :
 Extraction terminée : 791311 lignes consolidées


Groupes dupliqués distincts : 260
Lignes supprimées prévues : 260
concat 791311 + 337041 -> 1128352 lignes ; après déduplication 1128092 lignes

 Export CSV : (1128092 lignes)
 
En virant congrès mais gardant le fichier doublon 15/16:

Suppression UID ciblés - df_15 : 213 ligne(s)
Suppression UID ciblés - df_16 : 77 ligne(s)

 Export CSV df_16: (336964 lignes)

 Export CSV df_15: (791098 lignes)

Groupes dupliqués distincts : 217
Lignes supprimées prévues : 217
concat 791098 + 336964 -> 1128062 lignes ; après déduplication 1127845 lignes

 Export CSV : (1127845 lignes)

en virant tous les fichiers avant :
Export CSV df_16: (336740 lignes)

 Export CSV df_15: (791098 lignes)

Pas de doublons avec les clés choisies
concat 791098 + 336740 -> 1127838 lignes

dedup rate/manque 7 lignes :
moins 224 par supr fichier vs moins 217 par deduplication = manque sans doute quelques lignes qui sont pas doublonnées du fichier (les débuts annonce, ou snas texte etc.)
-> plus propre de virer après identification