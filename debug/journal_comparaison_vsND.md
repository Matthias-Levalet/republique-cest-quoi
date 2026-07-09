# bilan journal compraison vs ND

=== RÉSUMÉ GLOBAL (par id_syceron uniquement) ===
IDs communs              :  1,065,985
Uniquement dans extract  :     61,477
Uniquement dans ND15-16  :     43,516

Total IDs extract :  1,127,462
Total IDs ND      :  1,109,501

Dans les id seulement dans l'un ou l'autre du df : quasi que du bruit (didascalies, adoption amendement etc.) sans intervenant :
- df_only_ND : Lignes sans parlementaire ET sans personnalite : 44,570 / 45,408
- df_only_extract : Lignes sans id_acteur ET sans nom_orateur ET sans id_orateur: 60,274 / 61,843
- des choses liées au choix de virer des fichiers (macron, etc.)

Cas des sous df pour affiner :
### df_only_ND_no_speaker
-> OK c'est des trucs deg, y compris des codes titres "<p>Après l'article 3</p>" / <p>Rappel au règlement</p>

### df_only_extract_no_speaker
-> ok c'est deg aussi : des parenthèses, des signatures (Le Directeur du service du compte rendu de la séance etc.)
Suspension et reprise de la séance, des ..............
Et peut-être deux interventions chelous (sur 60000 et quelques) :
- On connaît la lourdeur et l’ampleur des responsabilités relatives à la charge de diriger une association ; or il nous semble qu’avec cette rédaction de l’alinéa 13, vous n’avez pas trouvé le bon équilibre, celui susceptible de garantir le respect plein et entier de la liberté d’association.
- L’amélioration de la situation sanitaire a permis à la conférence des présidents de faire évoluer nos règles de fonctionnement : tous les députés peuvent de nouveau être présents dans l’hémicycle. Dès lors qu’il ne sera pas possible de respecter les règles de distance physique, les députés et les ministres devront porter un masque, sauf quand ils prendront la parole. Les huissiers tiennent des masques à leur disposition.

### df_only_ND_with_speaker
-> un grand nombre viennent de fichier congrès

http://www.assemblee-nationale.fr/15/cri/congres/20184001.asp    305
http://www.assemblee-nationale.fr/15/cri/congres/20174001.asp     55

Également pas mal viennent de fichier extra :
EX
-> mais quand on va vraiment sur la page, on retrouve le xml et on l'a bien et on a bien les id_syceron qu'il contient
-> possible que la conversion pnum->id_syceron ne soit pas valable pour scéances extra ?

ex :
pnum 989943 vs id_syceron 989508
(idem pnum 984462 iv id_syceron 984462)
- le pnum 989943 est affiché comme exclusif au ND
- en fait le lien est celui là : http://www.assemblee-nationale.fr/15/cri/2016-2017-extra/20171010.asp#P989943
- mais en réalité il pointe vers : https://www.assemblee-nationale.fr/dyn/15/comptes-rendus/seance/session-extraordinaire-de-2016-2017/deuxieme-seance-du-mercredi-12-juillet-2017#P989943
- qui renvoie en réalité en début de page
- Et si on cherche l'id_syceron dans xml de l'assemblée : existe pas
- et si on cherche le texte en question copie le lien depuis le widget de l'assemblée : noyé en fait dans un bloc plus gros
https://www.assemblee-nationale.fr/dyn/15/comptes-rendus/seance/session-extraordinaire-de-2016-2017/deuxieme-seance-du-mercredi-12-juillet-2017#989508
-  qui lui colle, mais donc pas le num ou le lien que l'on a.
- et qui existe bien chez nous ainsi que dans le XML en ligne, mais donc regroupé dans l'intervention de l'id 989508


Dans les pas extra :
http://www.assemblee-nationale.fr/15/cri/2018-2019/20190028.asp
-> soutiens et discussion d'amendements

ou encore :
pnum 3507002 vs id_syceron 3507003
aide à mourir soit vraiment collégiale
- lien : https://www.assemblee-nationale.fr/16/cri/2023-2024/20240235.asp#3507002
- renvoie à : https://www.assemblee-nationale.fr/dyn/16/comptes-rendus/seance/session-ordinaire-de-2023-2024/troisieme-seance-du-vendredi-07-juin-2024#3507002 -> renvoie haut du doc
- copier lien depuis texte page : https://www.assemblee-nationale.fr/dyn/16/comptes-rendus/seance/session-ordinaire-de-2023-2024/troisieme-seance-du-vendredi-07-juin-2024#3507003
- et don id 3507003

### df_only_extract_with_speaker
des fichiers spécifiques ? CRSANR5L15S2018E1N007