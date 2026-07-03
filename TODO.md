# TODO

## Général

## 1-data-extraction

## À voir
- TODO: plus tard, aviser récupération des points de contexte parents(cf tentative Matthias)
- REGROUPEMENT INTERVENTIONS FOIRE -> nouvelle version semble okayish
- toujours un mini écrat, semble plus rentable de pas trier les fichiers par numéro ordre  :
  - les interventions sont déjà dans l'ordre, les id numérotés semblent pas super stables ?
  - et donc au final le résultat semble meilleur sans réappliquer de tri. Mais pq cet écart ?
- EXCLURE LAMARTINE OU PAS ?

## 2-clean&filter
- [ ] Aviser dernières exclusions de filtrage
- [ ] Aviser conflits noms quand pas bons gens identifiés (fuzzyfuzz) et/ou id_acteur!=id_orateur
- [ ] # TODO : les autres repérés dans le identif.csv et ajout_id_acteur.csv (si pas déjà dans identif)
- [ ] # TODO: syceron 2827575 2827576 2827577 = M. Lionel Tivoli = PA793298 ?
- [ ] LES PASSER id acteur EN PA0, remettre un nomorateurclean neutre/vide ET BASTA !!!!!!!!

3 options :
1/ Prendre les id syceron de la liste ok identif et ok ajout id acteur pbmatique -> les passer PA0

2/ OU : faire le fussy fuzz, puis gérer juste les cas interruptions députés :
sans casse : 
un député
une députée
les députés
plusieurs députés
quelques députés

3/ faire le fuzz et tous les passer en PA SAUF SI :
(mais un peu arme nucléaire si on applique sans regarder a de nouvelles données)

PA345619,PA345619,PA345619,M. Edouard Philippe,M. Édouard Philippe,1003045,55.55555555555556,1
PA720480,PA720480,PA720480,Mme Charlotte Lecocq,Mme Charlotte Parmentier-Lecocq,1313542,62.745098039215684,1
PA718910,PA718910,PA718910,Mme Claire Colomb-Pitollat,Mme Claire Pitollat,3426399,71.11111111111111,1
PA719756,PA719756,PA719756,Mme Christine Cloarec,Mme Christine Le Nabour,1482943,72.72727272727273,1
PA267042,PA267042,PA267042,M. Yannick Favennec-Bécot,M. Yannick Favennec Becot,2705353,75.0,1
PA267042,PA267042,PA267042,M. Yannick Favennec-Bécot (HOR),M. Yannick Favennec Becot,2888382,75.0,1
PA721296,PA721296,PA721296,M. Guillaume Gouffier Valente,M. Guillaume Gouffier-Cha,3352527,76.92307692307692,1
PA721296,PA721296,PA721296,M. Guillaume Gouffier Valente (RE),M. Guillaume Gouffier-Cha,3500806,76.92307692307692,1
PA720046,PA720046,PA720046,Mme Audrey Dufeu,Mme Audrey Dufeu Schubert,2241019,78.04878048780488,1
PA719130,PA719130,PA719130,Mme Monica Michel-Brassart,Mme Monica Michel,2791001,79.06976744186046,1
PA795636,PA795636,PA795636,M. Benjamin Lucas-Lundy,M. Benjamin Lucas,3433491,84.21052631578947,1
PA795636,PA795636,PA795636,M. Benjamin Lucas-Lundy (Écolo-NUPES),M. Benjamin Lucas,3445135,84.21052631578947,1
PA719756,PA719756,PA719756,Mme Christine Cloarec-Le Nabour,Mme Christine Le Nabour,2048546,85.18518518518519,1
PA721442,PA721442,PA721442,Mme Christelle Petex,Mme Christelle Petex-Levet,3455066,86.95652173913044,1
PA720764,PA720764,PA720764,Mme Florence Lasserre,Mme Florence Lasserre-David,2726474,87.5,1
PA720764,PA720764,PA720764,Mme Florence Lasserre (Dem),Mme Florence Lasserre-David,2893631,87.5,1
PA718728,PA718728,PA718728,Mme Laurence Vanceunebrock-Mialon,Mme Laurence Vanceunebrock,1856208,88.13559322033898,1
PA791812,PA791812,PA791812,Sophia Chikirou,Mme Sophia Chikirou,3301217,88.23529411764706,1
PA-121559,PA-121559,PA-121559,Emmanuelle Auriol,Mme Emmanuelle Auriol,2742412,89.47368421052632,1
PA721764,PA721764,PA721764,Mme Olivia Gregoire,Mme Olivia Grégoire,1426437,94.73684210526316,1

4 / fuzz propre sur ratio, puis paf sous les  77.27272727272727 








- [ ] Aviser choix variables d'affiliation
- [ ] voir la liste que je sors des sans affiliations (pas nombreux)
- [ ] Aviser cas gouvernement
- [ ] Aviser cas affiliation multiples (ex gauche sans groupe comme RN, etc.)
- [X] Aviser cas houplain NI/RN
- TODO : aviser lamartine et pb soucis identification

## 3-identify-republic

- TODO : ajouter les nouveaux cas identifiés
- Et aviser avec la nouvelle remontée d'exclusions possibles.
- check "\t" vs rien dans liste pays république


### nettoyer les textes ?

- [ ] RAS ?

## 4-analysis ?

- [ ] repartir de ce qu'a fait matthias, mettre à plat, vérifier, stabiliser, améliorer, etc.
- [ ] envisager stat en nb occurrence, % des interventions, et même chose hors interruption(doc actualiser numérateur et dénominateur)

### dates

- [ ] Vérif la conversion : visiblement des outliers -> vérif ??

### Bert, etc

- [ ] Aviser les possibles embeddings qwen, alibaba et explo topic modelling depuis activetigger
- [ ] **decider du focus sentence/paragraph/intervention/etc.**
- [ ] revoir regroupement des topics
- [ ] revoir Topic distribution
- [ ] aviser genAI sur le nom des topics ? -> meh.

## Pistes, etc.

# TODO
- TODO lamartine : en réalité vérifier avec matthias y avait des possibles soucis
seances_lamartine = [
    "CRSANR5L16S2023O1N201",
    "CRSANR5L16S2024O1N124",
    "CRSANR5L16S2024O1N098",
    "CRSANR5L16S2024O1N095",
    "CRSANR5L16S2024O1N063",
    "CRSANR5L16S2023O1N226",
    "CRSANR5L16S2023O1N128",
    "CRSANR5L16S2023O1N200",
    "CRSANR5L16S2023O1N156",
    "CRSANR5L16S2024O1N125",
    "CRSANR5L15S2021O1N207",
    "CRSANR5L16S2024O1N184",
    "CRSANR5L16S2024O1N171",
    "CRSANR5L16S2024O1N167",
    "CRSANR5L16S2024O1N166",
    "CRSANR5L16S2024O1N130",
    "CRSANR5L16S2024O1N129",
    "CRSANR5L15S2020O1N119",
    "CRSANR5L16S2023O1N106",
    "CRSANR5L15S2022O1N139",
    "CRSANR5L15S2022O1N112",
    "CRSANR5L15S2021O1N258",
    "CRSANR5L15S2020O1N137",
]