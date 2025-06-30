# TODO

## 1-data-extraction

- [ ] vérifier si le pattern d'extraction est ok (cf petits fichier identifiés à la fin)
- [ ] (les différences avec la v3 ont été testées et l'écart de nb c'était des infos inutiles)
- [ ] stabiliser le tout en comparant entre fichiers pour être sur que leur structure reste cohérente
- [ ] une fois avisé, stabiliser les noms (pas de maj, probablement plutôt reprendre noms de base ? etc.)
- [ ] check xmltodict ? (<https://github.com/martinblech/xmltodict>) -> essayé, meeehhhhh
  
## 2-clean&filter

- garder en tête : import des fichiers et dtypes : pb des ID et autres vus comme floats

### nettoyer les textes ?

- [ ] nettoyer les balises
- [ ] nettoyer les parenthèses (applaudissements, etc.)
- [ ] repérer ce qu'il y a d'autre, etc.
- [ ] ÉVITER DE PASSER EN LOWCASE (utile pour l'identification avec regex, ou sinon ne pas la faire sur le même texte)


### filtrer interventions

- [X] pour l'analyse, virer les prises de parole de Mme la présidente / le président (texte court et passage de parole)
- [ ] aviser pour virer selon les types d'intervention (Code_parole) et leur taille (intervention générique / accepté/ pour contre ammendement, mais parfois une justification donc aviser ?)
- [ ] remplacer les nan dans code parole par des "standard" ou "sans_type"
- [ ] VOIRE DATES : df["Session"].value_counts() -> session ordinaire 2020-2021 (EN MIN CONTRE LES AUTRES QUI ON MAJ EN INITIALE + VÉRIF SI VIENT DU CODE ?)

### Match info députés

- **(ou déplacer plus tard dans le code pour éviter traiter données pour rien ?)**
- [] aviser pour les données assemblée lorsque passera historique avec enjeux appartenance groupe à un temps t (cf les députés qui changent de groupe, et notmament avec apparition LREM)
- [] anticiper : possible pb des membres gouvernement sans fonction député (et donc pas de match dans base ?)
  - Vérifier les valeurs manquantes
  - 9400 et quelques manquantes (mais doublons de personnes = nb interventions, pas gens qui manquent)
  - Normalement des membres gouv pas élus avant ? Voir un jour si il y a une base avec tous les ID ?
  - Sinon renvoyer une info gouv / sans attache ?
  - si fait ça, le faire aussi pour les autres où il y a un match (et perte d'info)
  - ou, renvoyer la couleur politique du gouv ? (pour pas mélanger dans une catégorie gouv de droite et gauche)
- [X] pour ça, voir les fichiers datan & assemblée. datan ok pour ça (tout pret) MAIS seulement dernier groupe parlementaire
- [X] changer ID base perso. numéros orateurs etc. dispo, mais on récupère une version sans "PA" (bloc id est pas id_acteur=). ajouter en dur en début de chaine, ou alors changer le code de l'extraction
- [X] paser les ID "PA+Id" et faire match
- [X] TODO: PB = JOIN INTRODUIT UN SOUCIS D'ÉCRITURE/LECTURE ENSUITE DU CSV QUI AUGMENTE NB LIGNES (avec des trucs vides visiblement?). Avait déjà eu l'impresison d'avoir un truc du genre. Checker comme il faut, grave problématique > resolu pour l'instant avec quotes.
- [ ] Même si resolu pour l'instant avec quotes, voir quand même d'ou vient dans les données du join (ex de trucs qui avaient l'air de faire merder autour de Eric Martineau, www.ericmartineauavecvous.fr (etc.) qui dans un autre test se retrouvent dans seance ref session ref et un missing dans UID.
- Virer les trucs qu'on veut pas et voir si améliore au pire ?
- Genre un des machins qui posent soucis :

```markdown
eric.martineau@assemblee-nationale.fr,"@EricMartineau72
","Eric Martineau",www.ericmartineauavecvous.fr
```

Honnêtement, quasi juste que des membres du gouv sans mandat, le reste (avec un - dedans) sont des gens auditionnés.
- Se contenter d'un GOUV (mais alors retourner aussi ça pour les autres concernés membre de gouv mais encien mandant ? pense pas)
- préciser une affiliation si existe ailleurs (genre être maire rép sans être député et donc sort pas dans la base assemblée ?)
- ou alors encore juste mettre l'affiliation maj de leur gouv.
- Si vraiment pb, créer une catégorie non-affilié (qui existe peut-être ailleurs ?
- Mais ils sont 27, pas un drame (même si beaucoup d'interventions)


## 3-identify-republic

- [x] pb ici : vérifier d'ou vient mais changement taille fichier entrée (check) et (par conséquent ?) parfois match_valide 4900/4592 et match_simple 4500/4114. -> après vérif semble ok, sans doute vautré avant ça dans l'execution et le traitement des données ?
- [X] améliorer la regex -> pas sur que ma stratégie d'inclusion exclusion marche bien, vérif à la main sur des exemples manuels -> works okay(ish?)
- [X] au pire virer le (?<!\w)(anti-?|pré-?|post-?|pro?)? -> genre on raterait irrépublicain et je vois pas de mots qui auraient républi quelque chose en milieu de mot qu'on voudrait pas.
- [X] Limite même pareil pour la fin
- [ ] aviser si fait ensuite passer un modèle pour exclure ce qui est toujours hors scope (voir test ollama)
- [ ] ou alors utiliser un modèle pour carrément sélectionner ou entrainer un classifier et faire tourner sur tout. MAIS pas trop le temps pour l'instant ? avancer pour l'instant en mode essai/demo et affiner comme il faut ensuite ?
- [ ] few-shot ?
- [ ] à virer  : Gauche démocrate et républicaine, La République en marche / République en marche, les Républicains (en plus de Les Républicains), procureur de la République ?, république islamique d’Iran, République démocratique du Congo
- présidence de la République ?
- (école de la République me semble plus coller, etc. élus de la république ?


## 4-analysis ?

### de nouveau pré-traitement des textes ?

### dates

- [ ] Vérif la conversion : visiblement des outliers

### Bert, etc.

- [ ] decider du focus sentence/paragraph/intervention/etc.

## x-ollama

- test prompts
- test max nb annotation
- on peut faire des envois en batch ?
- need to check prompt struct to be sure of what is going to ollama
