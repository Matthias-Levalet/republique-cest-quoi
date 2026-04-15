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

- [ ] Aviser conflits noms quand pas bons gens identifiés (fuzzyfuzz) et/ou id_acteur!=id_orateur
- [ ] Aviser choix variables d'affiliation
- [ ] voir la liste que je sors des sans affiliations (pas nombreux)
- [ ] Aviser cas gouvernement
- [ ] Aviser cas affiliation multiples (ex gauche ans groupe comme RN, etc.)
- [ ] Aviser cas houplain NI/RN
- [ ] REGROUPEMENT INTERVENTIONS FOIRE

## 3-identify-republic

- TODO: vérifier "République Sudafricaine" (cf liste pays)
- Et aviser avec la nouvelle remontée d'exclusions possibles.

En détail : 
« [Ll]es Républicains » 6686 ; « aux Républicains » (51); « [Dd]es Républicains » (428); « [Cc]ollègue[s]? Républicains » (26) « sénateurs Républicains »(2); « députés Républicains » (6); « entre Républicains » (4) « ex-Républicains » (1); « anciens Républicains » (1), « seuls Républicains » (1); « parlementaires Républicains » (1), « élus Républicains » (2); « groupeLes Républicains » (1); « Les Républicain » (4); « [Nn]ous Républicains » (2); « certains Républicains » (4); « élus Républicains » (2); « nos amis Républicains » (1); « droite, Républicains et macronistes » (1); « Républicains-Front national » (1); « Macronistes, Républicains, lepénistes »(1); « Rassemblement national, Républicains et macronistes » (1): (Attention, enlever sensitif à la casse) 



Ligne de code : 

r"\b[Ll]es Républicains|[Dd]es Républicains|aux Républicains|sénateurs Républicains|députés Républicains|entre Républicains|[Cc]ollègue[s]? Républicain[s]?|ex-Républicains|anciens Républicains|seuls Républicains|parlementaires Républicains|élus Républicains|groupeLes Républicains|Les Républicain|[Nn]ous? Républicains|certains Républicains|élus Républicains|nos amis Républicains|droite, Républicains et macronistes|Républicains-Front national|Républicains, lepénistes|Rassemblement national, Républicains\b",
    #re.I,



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