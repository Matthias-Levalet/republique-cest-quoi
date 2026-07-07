# Journal de comparaisons : mentions de "République"

Extrait du script `3_1_identification_republique.py`, pour ne pas alourdir
le code. Comptages obtenus lors des premiers tests de la fonction
`contains_lexical_outside_excl` (avec exclusions), selon la source du corpus.

## Match valide (avec exclusions)

| Source                                    | False       | True   |
|--------------------------------------------|------------:|-------:|
| Fichier NosDéputés (sans regroupement)      | 1 377 276   | 13 924 |
| Extraction brute (sans regroupement)        | 1 016 076   | 13 333 |
| Fichier maison (avec regroupement)          |   506 104   | 10 922 |

**TODO non résolu** : aller voir les ~600 manquants entre "NosDéputés" et
"extraction brute (sans regroupement)".

## Match "républi" sans aucune exclusion

Pour référence, `pattern_lexical = re.compile(r"républi", re.I)` seul,
sans passer par `contains_lexical_outside_excl` :

| Source                                    | False       | True   |
|--------------------------------------------|------------:|-------:|
| Interventions groupées                      |   485 686   | 31 340 |
| Idem, avec normalisation NFC                |   485 686   | 31 340 |
| Extraction brute (sans regroupement)        | 1 083 748   | 44 090 |
| NosDéputés 15+16                            | 1 345 638   | 45 569 |

Comparaison externe (non recalculée dans ce projet) :
site [an-4931d4.gitpages.huma-num.fr/debats-AN](https://an-4931d4.gitpages.huma-num.fr/debats-AN#tableau-complet)
annonçant ~2 010 738 interventions en mémoire (2011-2026) pour 33 694
interventions matchées — période plus longue que la nôtre mais total de
matches inférieur, à creuser (source potentiellement moins exhaustive sur
cette période, ou méthode de comptage différente).
