# TODO

## Général

## 1-data-extraction

## À voir

- TODO: déduplication ? -> proposé un truc déjà, vérif (pas sur soit utile)
  - plus tard : # choisir la clé la plus pertinente
  - (["uid", "id_syceron", "texte"] VS uid + id_syceron seulement)
  - en réalité encore des choses qui ont double entrée pour même ID_paragraphe
  - mais avec texte différent = des didascalies, texte italique, etc.
  - si pas de Texte, 370 lignes supprimées (mais qui vireraient sans doute au cleaning des données)
- TODO: vérifier si on a pas d'autres doublons de fichier mal placés dans les législatures
  - check si possible automatiser à la lecture de tous les uid vs seance ref, etc. ?
- TODO: plus tard, aviser récupération des points de contexte parents(cf tentative Matthias)


## 2-clean&filter

- [ ] TODO: on parle dans l'intro d'exclure congrès + lamartine. C'est fait ? pas directement non ?
- [ ] Ou alors c'est fait en mode pas explicite mais bien le cas par les différents filtres ?
- [ ] TODO: cf Vérif id_orateur vs id_acteur ? visiblement je l'ai fait, vérif, nb2
- [ ] garder en tête : import des fichiers et dtypes : pb des ID et autres vus comme floats
- [ ] Aviser du cas des membres du gouvernement = décider de ce qu'on fait du statut de la parole des membre gouvernement (qui sont eux même députés à d'autre moment)
- [ ] lié point précédent : aviser pour ceux qui ont pas de parti_affiliation mais bien un groupeabrev

### filtrer interventions

- [ ] aviser pour les codes parole avis du gvt etc.
- [ ] = cf = TODO: on parle dans l'intro d'exclure congrès + lamartine. C'est fait ? pas directement non ?

### Match info députés

- [ ] anticiper : possible pb des membres gouvernement avec ou sans fonction député. = est-ce qu'on veut leur affiliation partisanne dans tous les cas, ou une catégorie membre gouvernement, etc.
- [ ] possiblement avoir dans ce cas une variable supplémentaire quand intervention comme membre du gouv au pire en fait ?
- [ ] visiblement a peu près toutes les infos "manquantes" concernent des membres du gouv sans jamais de mandat (si pas de groupeabrev) (ou sans affiliation lors de l'intervention pour parti_affiliation). Le reste des interventions, c'est soit des orateurs qui sont des gens auditionnés (avec un - dedans), ou des codes paroles spécifiques.
  
Cf revoir ce que j'avais dans missing_info.ipynb:
"""
Honnêtement, quasi juste que des membres du gouv sans mandat, le reste (avec un - dedans) sont des gens auditionnés.
- Se contenter d'un GOUV (mais alors retourner aussi ça pour les autres concernés membre de gouv mais encien mandant ? pense pas)
- préciser une affiliation si existe ailleurs (genre être maire rép sans être député et donc sort pas dans la base assemblée ?)
- ou alors encore juste mettre l'affiliation maj de leur gouv.
- Si vraiment pb, créer une catégorie non-affilié (qui existe peut-être ailleurs ?
- Mais ils sont 27, pas un drame (même si beaucoup d'interventions)
"""

- [ ] Gérer les edge cases individuels (voir-dessous):
Cas des députés FN-RN en NI lors de la 15e faute d’être assez pour avoir un groupe parlementaire : 
Bruno Bilde PA720822
Emmanuel Blairy  PA720668
Sébastien Chenu PA720468
Marine Le Pen PA720614
Nicolas Meizonnet PA719436
Catherine Pujol PA720802
Emmanuelle Ménard (élue RN sans y être adhérente) PA719608
Ludovic Pajot  PA720606
Myriane Houplain
Gilbert Collard PA606212
Louis Aliot PA720798

### catégories (membres gouv, etc.)

Créer une nouvelle variable d’affiliation politique par groupe parlementaire + gouvernement séparé
df["groupe&gvt_affiliation"] = df["groupe_députés_affiliation"].fillna("GVT")
TODO: LM vérifier ça avec matthias : on est sur que les NA = gouv ?
genre y a pas plein d'autres cas interv extérieurs etc ?
-> puis genre tous les cas de membre du gouv identifiés avec ancienne affiliation si on fait ?
possible autre moyen de choper :
-> oui peut-être : ID mandat en -1 semble souvent = ministre (pas rapporteur, etc.)
-> qualite_orateur et semble également un bon indicateur : ministre, rapporteur, etc. (mais pas que)
-> code parole ne colle pas (avis gvt, avis com etc, mais couvre pas leurs autres interventions)

## 3-identify-republic

- TODO: vérifier "République Sudafricaine" (cf liste pays)
- Et aviser avec la nouvelle remontée d'exclusions possibles.

### nettoyer les textes ?

- [ ] RAS ?

## 4-analysis ?

- [ ] repartir de ce qu'a fait matthias, mettre à plat, vérifier, stabiliser, améliorer, etc.

### dates

- [ ] Vérif la conversion : visiblement des outliers -> vérif ??

### Bert, etc

- [ ] Aviser les possibles embeddings qwen, alibaba et explo topic modelling depuis activetigger
- [ ] **decider du focus sentence/paragraph/intervention/etc.**
- [ ] revoir regroupement des topics
- [ ] revoir Topic distribution
- [ ] aviser genAI sur le nom des topics ? -> meh.

## Pistes, etc.

### stabiliser regex et ou autres alternatives

Serait presque plutôt l'idée d'un papier méthodo en vrai :

- [ ] LLM : aviser si fait ensuite passer un modèle pour exclure ce qui est toujours hors scope (voir test ollama)
- [ ] few-shot ?
- [ ] activetigger : modèle entrainé sur la regex inclusion famille de mot "République", à ne garder que les occurrences de la FDM appartenant à l'idée de "République" (= exclure les pays, institutions, noms de groupes et partis)

### ollama

- test prompts
- test max nb annotation
- on peut faire des envois en batch ?
- need to check prompt struct to be sure of what is going to ollama
- en profiter pour comparer des modèles entre eux et leur perf ?