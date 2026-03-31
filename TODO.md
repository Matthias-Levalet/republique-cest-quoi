# TODO

## Général

## 1-data-extraction

- [ ] TODO: s'assurer que l'extraction marche bien avec la 15ème législature
- [ ] TODO: déduplication ? -> poposé un truc déjà, vérif (pas sur soit utile)
- [ ] TODO: vérifier si on a pas d'autres doublons de fichier mal placés dans les législatures
- [ ] (cf df_16 = df_16[df_16["UID"] != "CRSANR5L16S2021O1N144"])
- [ ] TODO: check si possible automatiser à la lecture de tous les uid vs seance ref, etc. ?

## 2-clean&filter

- [ ] TODO: cf Vérif id_orateur vs id_acteur ? visiblement je l'ai fait, vérif, nb2
- [ ] garder en tête : import des fichiers et dtypes : pb des ID et autres vus comme floats
- [ ] Aviser du cas des membres du gouvernement = décider de ce qu'on fait du statut de la parole des membre gouvernement (qui sont eux même députés à d'autre moment)
- [ ] lié point précédent : aviser pour ceux qui ont pas de parti_affiliation mais bien un groupeabrev
- [ ] 

### id_acteur vs id_orateur — point d'attention
À vérifier Des cas id_acteur="PA0" existent en L15 (8 cas dans L15-014, davantage en L15-020) mais pas en L16. Ce sont des interventions collectives ou anonymes ("Un député du groupe LR"). Le id_orateur vaut 0 ou un id réel (605518). Si vous comptez sur id_acteur pour joindre un référentiel acteur, ces lignes seront orphelines.
À vérifier En L15, id_orateur (issu de <orateur><id>) est un numéro brut ex: 720622, tandis que id_acteur (attribut du paragraphe) vaut PA720622. Le code extrait les deux séparément — vérifiez que votre logique de jointure normalise bien (ex: id_orateur = "PA" + id_orateur) pour comparer les deux colonnes.


### filtrer interventions

- [ ] aviser pour les codes parole avis du gvt etc.

### Match info députés

- [ ] anticiper : possible pb des membres gouvernement avec ou sans fonction député. = est-ce qu'on veut leur affiliation partisanne dans tous les cas, ou une catégorie membre gouvernement, etc.
- [ ] possiblement avoir dans ce cas une variable supplémentaire quand intervention comme membre du gouv au pire en fait ?
- [ ] visiblement a peu près toutes les infos "manquantes" concernent des membres du gouv sans jamais de mandat (si pas de groupeabrev) (ou sans affiliation lors de l'intervention pour parti_affiliation). Le reste des interventions, c'est soit des orateurs qui sont des gens auditionnés (avec un - dedans), ou des codes paroles spécifiques.

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

### Nettoyage

Nettoyer les noms de députés (parfois des balises, espaces, groupes, qualité) car on s'en sert possiblement, ou feinter juste sur l'ID_Orateur et renvoyer un nom clean avec


pb possible voir nb2:
Créer une nouvelle variable d’affiliation politique par groupe parlementaire + gouvernement séparé
df["groupe&gvt_affiliation"] = df["groupe_députés_affiliation"].fillna("GVT")
TODO: LM vérifier ça avec matthias : on est sur que les NA = gouv ?
genre y a pas plein d'autres cas interv extérieurs etc ?
-> puis genre tous les cas de membre du gouv identifiés avec ancienne affiliation si on fait ?

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