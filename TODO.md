# TODO

## 1-data-extraction

- vérifier si le pattern d'extraction est ok (cf petits fichier identifiés à la fin)
- (les différences avec la v3 ont été testées et l'écart de nb c'était des infos inutiles)
- stabiliser le tout en comparant entre fichiers pour être sur que leur structure reste cohérente
- une fois avisé, stabiliser les noms (pas de maj, probablement plutôt reprendre noms de base ? etc.)
- check xmltodict ? (<https://github.com/martinblech/xmltodict>)
  
## 2-clean&filter

filtrer interventions:

- [x] pour l'analyse, virer les prises de parole de Mme la présidente / le président (texte court et passage de parole)
- [ ] aviser pour virer selon les types d'intervention (Code_parole) et leur taille (intervention générique / accepté/ pour contre ammendement, mais parfois une justification donc aviser ?)
- [ ] remplacer les nan de code parole par des "standard" ou "sans_type"

nettoyer les textes

- [ ] nettoyer les balises
- [ ] nettoyer les parenthèses (applaudissements, etc.)
- [ ] repérer ce qu'il y a d'autre, etc.
- [ ] ÉVITER DE PASSER EN LOWCASE (utile pour l'identification avec regex, ou sinon ne pas la faire sur le même texte)

## 3-identify-republic

- [x] pb ici : vérifier d'ou vient mais changement taille fichier entrée (check) et (par conséquent ?) parfois match_valide 4900/4592 et match_simple 4500/4114. -> après vérif semble ok, sans doute vautré avant ça dans l'execution et le traitement des données ?
- [ ] améliorer la regex
- [ ] aviser si fait ensuite passer un modèle pour exclure ce qui est toujours hors scope (voir test ollama)
- [ ] ou alors utiliser un modèle pour carrément sélectionner ou entrainer un classifier et faire tourner sur tout. MAIS pas trop le temps pour l'instant ? avancer pour l'instant en mode essai/demo et affiner comme il faut ensuite ?

## 4-analysis ?

- [] decider du focus sentence/paragraph/intervention/etc.

## x-ollama

- test prompts
- test max nb annotation
- on peut faire des envois en batch ?
- need to check prompt struct to be sure of what is going to ollama
