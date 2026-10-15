# TODO

## Général

## 1-data-extraction

## Global

- passer tout sous UV
- finaliser pipeline
- ajouter infos sur téléchargement fichiers et ou option exécution code
- ajouter liste pays txt pour reproductibilité
- REPRENDRE DEMANDE AJOUT COMMISSIONS ETC DÉPUTÉS POUR MATTHIAS
- Aviser si fichier datan diffusables. Sinon voir pour reproductibilité
- REPRENDRE LE **README** !!!!


## À voir

## 1-extraction

## 2-clean&filter

- [ ] 2.4 affiliation : depuis le doc mandats de la datan, repasser leur comission d'appartenance + leur "codeQualite" et libelleAbrev = REPRENDRE DEMANDE AJOUT COMMISSIONS ETC DÉPUTÉS POUR MATTHIAS

## 3-identify-republic

### nettoyer les textes ?

- [ ] RAS ?

## 4-analysis ?

- [ ] repartir de ce qu'a fait matthias, mettre à plat, vérifier, stabiliser, améliorer, etc.
- [ ] envisager stat en nb occurrence, % des interventions, et même chose hors interruption(doc actualiser numérateur et dénominateur)
- [ ] aviser en % nb mots / ngrams ?
- [ ] faire des sorties vizu pour avoir une base de discussion de ce qu'on veut (= avoir des exemples pour imaginer ce qui est réalisable et utile)

### dates

- [ ] Vérif la conversion : visiblement des outliers -> vérif ??

## 5-embeddings et topic-modeling

### 5_1_embeddings

- [ ] aviser si nécessaire de refaire tourner une fois le fichier final export repu consolidé
  - [ ] à ce jour : toujours ok sur nb interventions, mais probalbme ajout de colones info députés entre temps (comission, etc.), voir pour une fusuion si nécessaire
- [ ] Aviser les possibles embeddings qwen, alibaba et explo topic modelling depuis activetigger
- [ ] **decider du focus sentence/paragraph/intervention/etc.**

### 5_2_topic_modeling

- [ ] revoir regroupement des topics
  - [ ] idée de le faire chacun séparément pour confronter ensuite
  - [ ] jouer sur la seed (pas pour optimiser mais à l'inverser vérifier risque variabilité)
  - [ ] jouer sur paramètres UMAP / HDBSCAN : mais ici on préfère un travail de recoupement fin à la main.
- [ ] aviser genAI sur le nom des topics ? -> meh.

## Pistes, etc.

Analyses.ipynb pour le fichier ok de matthias.

https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/debats-en-seance-publique
https://data.assemblee-nationale.fr/archives-16e/debats

https://data.assemblee-nationale.fr/static/openData/repository/15/vp/syceronbrut/syseron.xml.zip
https://data.assemblee-nationale.fr/static/openData/repository/16/vp/syceronbrut/syseron.xml.zip