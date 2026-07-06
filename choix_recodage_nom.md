# trace choix recodage nom brut vs nom clean

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