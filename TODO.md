# TODO

## Général

## 1-data-extraction

## Global

- passer tout sous UV
- finaliser pipeline
- ajouter infos sur téléchargement fichiers et ou option exécution code
- ajouter liste pays txt pour reproductibilité

## À voir

- [ ] SOUCIS REGROUPEMENT INTERVENTIONS FOIRE -> nouvelle version semble okayish
  - toujours un mini écart, semble plus stable de pas trier les fichiers par numéro ordre  :
  - les interventions sont déjà dans l'ordre, les id numérotés semblent pas super stables ?
  - et donc au final le résultat semble meilleur sans réappliquer de tri. Mais pq cet écart ?
  - tester avec le id_syceron ? -> test réalisé, c'est naze.
- [X] EXCLURE LAMARTINE OU PAS ? -> DONE = non : passage des acteurs restant en externes
- [X] récupération des points de contexte parents(cf tentative Matthias) = DONE
- [ ] check par matthias si contexte est OK.
- [ ] check repu against ND

## 2-clean&filter

- [X] voir la liste que je sors des sans affiliations (pas nombreux)
- [X] Aviser cas gouvernement
- [X] Aviser cas affiliation multiples (ex gauche sans groupe comme RN, etc.)
- [X] Aviser cas houplain NI/RN
- [X] Aviser lamartine et pb soucis identification -> DONE avec le passage en externes
- [ ] syceron 2827575 2827576 2827577 = M. Lionel Tivoli = PA793298 ?
  - [X] sans doute pas : cas ultra spécifique et doit y en avoir d'autres (voir point suivant)
  - [X] désormais géré par le fait que conserve une trace sur-imprimée de nom_orateur sur nom_orateur_clean quand on en a pas si PA0
- [X] Vérif cas de nom orateur sans nom orateur clean plus qu'1 (cf depuis gestion en cas de PA0)
- [X] Vérif cas de nom orateur clean sans nom orateur -> pas concluant ~13 cas (président séances autres mal identif (chenu, laporte)


## 3-identify-republic

- [X] check "\t" vs rien dans liste pays république -> DONE
- [ ] ajouter les nouveaux cas identifiés
- [ ] aviser avec la nouvelle remontée d'exclusions possibles.
- [ ] check repu against ND

# NOTE : quelques (~10) "république islamique" sans précision pour parler de l'Iran
# mais risque de supprimer d'autres occurrences que l'on veut garder
# Ou alors aviser maj a République vs sans ?

### nettoyer les textes ?

- [X] ENJEU DES ACCENTS À TESTER ! DONE fait avec unicodedata, pas de diff -> introduit quand même dans nettoyage 2_1
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
