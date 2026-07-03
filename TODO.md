# TODO

## Général

## 1-data-extraction

## À voir
- TODO: plus tard, aviser récupération des points de contexte parents(cf tentative Matthias)
- REGROUPEMENT INTERVENTIONS FOIRE -> nouvelle version semble okayish
- toujours un mini écrat, semble plus rentable de pas trier les fichiers par numéro ordre  :
  - les interventions sont déjà dans l'ordre, les id numérotés semblent pas super stables ?
  - et donc au final le résultat semble meilleur sans réappliquer de tri. Mais pq cet écart ?


## 2-clean&filter
- Aviser dernières exclusions de filtrage
- [ ] Aviser conflits noms quand pas bons gens identifiés (fuzzyfuzz) et/ou id_acteur!=id_orateur
- [ ] Aviser choix variables d'affiliation
- [ ] voir la liste que je sors des sans affiliations (pas nombreux)
- [ ] Aviser cas gouvernement
- [ ] Aviser cas affiliation multiples (ex gauche ans groupe comme RN, etc.)
- [X] Aviser cas houplain NI/RN
- TODO : aviser lamartine et pb soucis identification

## 3-identify-republic

- TODO: vérifier "République Sudafricaine" (cf liste pays)
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