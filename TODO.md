# TODO

## 1-data-extraction

### stabiliser l'extraction

-   [ ] stabiliser le tout en comparant entre fichiers de plusieurs législatures pour être sur que leur structure reste cohérente
-   [ ] Remarque : en fait j'aurai probablement pu cibler directement juste les textes qui ont un texte stime= qui semblent être ceux des vrais gens quand du texte venant juste de complément mise en page et contexte a pas de stime ? -\> non finalement car des scories et des NA qui sont bien des prises de paroles
-   [ ] une fois avisé, stabiliser les noms (pas de maj, probablement plutôt reprendre noms de base ? etc.)

### sinon voir des alternatives

-   [ ] check xmltodict ? (<https://github.com/martinblech/xmltodict>) -\> essayé, meeehhhhh

## 2-clean&filter

-   garder en tête : import des fichiers et dtypes : pb des ID et autres vus comme floats

### filtrer interventions

### Match info députés

-   **(ou déplacer plus tard dans le code pour éviter traiter données pour rien ?)**
-   \[\] aviser pour les données assemblée lorsque passera historique avec enjeux appartenance groupe à un temps t (cf les députés qui changent de groupe, et notmament avec apparition LREM)
-   \[\] anticiper : possible pb des membres gouvernement sans fonction député (et donc pas de match dans base ?)
    -   Vérifier les valeurs manquantes
    -   9400 et quelques manquantes (mais doublons de personnes = nb interventions, pas gens qui manquent)
    -   Normalement des membres gouv pas élus avant ? Voir un jour si il y a une base avec tous les ID ?
    -   Sinon renvoyer une info gouv / sans attache ?
    -   si fait ça, le faire aussi pour les autres où il y a un match (et perte d'info)
    -   ou, renvoyer la couleur politique du gouv ? (pour pas mélanger dans une catégorie gouv de droite et gauche)
    -   Honnêtement, quasi juste que des membres du gouv sans mandat, le reste (avec un - dedans) sont des gens auditionnés.
    -   Se contenter d'un GOUV. Mmais alors retourner aussi ça pour les autres concernés membre de gouv mais encien mandant ? pense pas
    -   préciser une affiliation si existe ailleurs (genre être maire rép sans être député et donc sort pas dans la base assemblée ?)
    -   ou alors encore juste mettre l'affiliation maj de leur gouv.
    -   Si vraiment pb, créer une catégorie non-affilié (qui existe peut-être ailleurs ?
    -   Mais ils sont 27, pas un drame (même si beaucoup d'interventions)
-   [x] JOIN INTRODUIT UN SOUCIS D'ÉCRITURE/LECTURE ENSUITE DU CSV QUI AUGMENTE NB LIGNES. Resolu pour l'instant avec quotes.
-   [ ] Virer les trucs qu'on veut pas et voir si améliore au pire ?
-   [ ] Même si resolu pour l'instant avec quotes, voir quand même d'ou vient dans les données du join

PB JOIN : exemple de trucs qui avaient l'air de faire merder autour de Eric Martineau, \<www.ericmartineauavecvous.fr\> (etc.) qui dans un autre test se retrouvent dans seance ref session ref et un missing dans UID.

``` markdown
eric.martineau@assemblee-nationale.fr,"@EricMartineau72
","Eric Martineau",www.ericmartineauavecvous.fr
```

## 3-identify-republic

### nettoyer les textes ?

-   [x] nettoyer les balises
-   [x] nettoyer les parenthèses (applaudissements, etc.)
-   [x] ÉVITER DE PASSER EN LOWCASE (utile pour l'identification avec regex, ou sinon ne pas la faire sur le même texte)
-   [ ] repérer ce qu'il y a d'autre, etc.

### stabiliser regex

-   [ ] LLM : aviser si fait ensuite passer un modèle pour exclure ce qui est toujours hors scope (voir test ollama)
-   [ ] few-shot ?
-   [ ] activetigger : ou alors utiliser un modèle pour carrément sélectionner ou entrainer un classifier et faire tourner sur tout. MAIS pas trop le temps pour l'instant ? avancer pour l'instant en mode essai/demo et affiner comme il faut ensuite ?
-   [ ] Sinon aviser pour également exclure république + pays
-   [ ] Matthias : faire un export avec les exclusions les républicains pour controler ce qui sort

## 4-analysis ?

### de nouveau pré-traitement des textes ?

### dates

-   [ ] Vérif la conversion : visiblement des outliers

### Bert, etc

-   [ ] decider du focus sentence/paragraph/intervention/etc.

## x-ollama

-   test prompts
-   test max nb annotation
-   on peut faire des envois en batch ?
-   need to check prompt struct to be sure of what is going to ollama