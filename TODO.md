# TODO

## Général

- [ ] regrouper les interventions séparées pas interruption ?
- [ ] Aviser du cas des membres du gouvernement = décider de ce qu'on fait du statut de la parole des membre gouvernement (qui sont eux même députés à d'autre moment)
- [ ] lié point précédent : aviser pour ceux qui ont pas de parti_affiliation mais bien un groupeabrev
- [ ] remonter les éventuelles modif du code depuis exploration matthias

## 1-data-extraction

### stabiliser l'extraction

- [ ] stabiliser le tout en comparant entre fichiers de plusieurs législatures pour être sur que leur structure reste cohérente
- [ ] une fois avisé, stabiliser les noms des variables (pas de maj, probablement plutôt reprendre noms de base (id_syceron) ? etc.)

## 2-clean&filter

- garder en tête : import des fichiers et dtypes : pb des ID et autres vus comme floats
- [ ] Aviser du cas des membres du gouvernement = décider de ce qu'on fait du statut de la parole des membre gouvernement (qui sont eux même députés à d'autre moment)
- [ ] lié point précédent : aviser pour ceux qui ont pas de parti_affiliation mais bien un groupeabrev
- **TODO: regroup without interruption ?**
- Reprendre en compte le fait de vouloir joindre les interventions victimes d'interruptions ?

### filtrer interventions

- [ ] aviser pour les codes parole avis du gvt etc.

### Match info députés

- [ ] anticiper : possible pb des membres gouvernement avec ou sans fonction député. = est-ce qu'on veut leur affiliation partisanne dans tous les cas, ou une catégorie membre gouvernement, etc.
- [ ] possiblement avoir dans ce cas une variable supplémentaire quand intervention commme membre du gouv au pire en fait ?
- [ ] visiblement a peu près toutes les infos "manquantes" concernent des membres du gouv sans jamais de mandat (si pas de groupeabrev) (ou sans affiliation lors de l'intervention pour parti_affiliation). Le reste des interventions, c'est soit des orateurs qui sont des gens auditionnés (avec un - dedans), ou des codes paroles spécifiques.

- [ ] Gérer les edge cases individuels (voir-dessous):
- [ ] 
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

Nettoyer les noms de députés (parfois des balises, espaces, groupes, qualité) car on s'en sert possiblement, ou feinter juste sur l'ID_Orateur et renvoyer un nom clean avec)

## 3-identify-republic

- TODO: vérifier "République Sudafricaine" (cf liste pays)


### nettoyer les textes ?

- [] RAS ?

### stabiliser regex

- [ ] LLM : aviser si fait ensuite passer un modèle pour exclure ce qui est toujours hors scope (voir test ollama)
- [ ] few-shot ?
- [ ] activetigger : modèle entrainé sur la regex inclusion famille de mot "République", à ne garder que les occurrences de la FDM appartenant à l'idée de "République" (= exclure les pays, institutions, noms de groupes et partis)

## 4-analysis ?

### de nouveau pré-traitement des textes ?

### dates

- [ ] Vérif la conversion : visiblement des outliers

### Bert, etc

- [ ] Aviser les possibles embeddings alibaba et explo topic modelling depuis activetigger
- [ ] **decider du focus sentence/paragraph/intervention/etc.**
- [ ] Tester Flaubert et autres, qwen, etc. ALibaba = cry in GPU, , etc. Aviser dans colab ou humanum ?
  - [ ] Qwen pour sa Context Length ? + est multilingue ?
  - [ ] pousser vers leur 4B ou 8B si ressources suffisantes ?
- [ ] revoir regroupement des topics
- [ ] revoir Topic distribution
- [ ] aviser genAI sur le nom des topics ?

## x-ollama

- test prompts
- test max nb annotation
- on peut faire des envois en batch ?
- need to check prompt struct to be sure of what is going to ollama
- en profiter pour comparer des modèles entre eux et leur perf ?

