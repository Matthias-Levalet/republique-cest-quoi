# Journal de comparaisons : mentions de "République"

Extrait du script `3_1_identification_republique.py`, pour ne pas alourdir
le code. Comptages obtenus lors des premiers tests de la fonction
`contains_lexical_outside_excl` (avec exclusions), selon la source du corpus.

Réactualisé depuis MAJ extraction fichiers (qui semble changer shape df et récupérer
les interventions qui faisaient anciennement une diff)
(Vérifier si bruit ?)

## Match valide (avec exclusions)

NOTE : colle pas pile à la shape df avec Nan,
(ou incongruences entre versions si vire ou pas selon présence combinée id_orateur/id_acteur/nom_orateur, etc.)

| Source                                    | Shape       | False       | True   |
|--------------------------------------------|------------:|------------:|-------:|
| Fichier NosDéputés (ND15+16_interventions_hemicycle_rich.tsv)      | 1391207   | 1377345   | 13862 (13862 aussi nettoyé) |
| Extraction brute (1_2_extract_15_16_concat.csv)        | 1127829   | 1113965   | 13864 (13277 nettoyé) |
| Fichier maison (2_4_interventions_nettoyees)          | 517023   | 506104   | (11336 brut) 10876 (net = de base car déjà fait) |

**TODO** :  ~600 manquants entre "NosDéputés" et "extraction brute" sur texte nettoyé

**NOTE** : écart sur même regex entre texte nettoyé et texte brut :
espaces multiples non normalisés dans texte_brut.
"le Président de                            la République" -> pas exclu car des espaces, etc.
repu_match_valide (texte nettoyé) : True      10876
repu_match_valide (texte_brut) : True      11336



## Match "républi" sans aucune exclusion

NOTE : colle pas pile à la shape df avec Nan etc.

Pour référence, `pattern_lexical = re.compile(r"républi", re.I)` seul,
sans passer par `contains_lexical_outside_excl` :

| Source                                    | False       | True   |
|--------------------------------------------|------------:|-------:|
| Interventions groupées                      |   485 683   | 31 340 |
| Idem, avec normalisation NFC                |   485 683   | 31 340 |
| Extraction brute (sans regroupement)        | 1 083 667   | 44 089 |
| NosDéputés 15+16                            | 1 345 638   | 45 569 |

Comparaison externe (non recalculée dans ce projet) :
site [an-4931d4.gitpages.huma-num.fr/debats-AN](https://an-4931d4.gitpages.huma-num.fr/debats-AN#tableau-complet)
annonçant ~2 010 738 interventions en mémoire (2011-2026) pour 33 694
interventions matchées — période plus longue que la nôtre mais total de
matches inférieur, à creuser (source potentiellement moins exhaustive sur
cette période, ou méthode de comptage différente).


## DIVERGENCES

CAS LIMITES :

**comparaison absence par pnum vs_idsyceron**
pas forcément vraie source différence mais aide comparaison par pnum / id_syceron

- Mauvais pnum mais bien dans le df maison qui match :
  - liste par ex : 1381312, 1381313, 1627250, 2396860, 2397067, 2397071, 2480254 
  - Ex pnum 1381312 vs id 1381415  = des biens communs peuvent fondamentalement nous aider à refonder notre République"
  - Ex idem 1381313 vs 1381415 = "le principal défi auquel est confrontée notre République est de savoir qui exerce "
  - Ex idem 1433638 vs 1433583 = "le Français, le Républicain, l'Européen est reconnaissant"
- erreur ND avec passage en texte de l'intervention ce qui est en fait pour nous le niveau de discussion (et donc pas d'orateur associé)
  - voir ex dessous

ex :
```
<p>Prééminence des lois de la République</p>
<p>Respect des principes de la République</p>
<p>respect des principes de la république</p>
<p>Convention relative à la nationalité entre la République française et le royaume d'Espagne</p>
<p>Dissolution des groupuscules fascistes et antirépublicains</p>
<p>État de l'école de la République</p>
<p>Fonds Marianne pour la République</p>
<p>Valeurs républicaines à l'école</p>
<p>Arc républicain et extrême droite</p>
<p>Prestation de serment d'une juge suppléante à la Cour de la République</p>
# et ceux là (pris après nettoyage, mais sinon y a les balises p aussi normalement)
Attaques contre les élus de la République
Attaques contre la République et les institutions démocratiques
Quartiers de reconquête républicaine en Seine-Saint-Denis
Quartiers de reconquête républicaine
Crise de la République
Valeurs de la République à l'école
Valeurs de la République à l'école
```

et donc : 
2337471,Prééminence des lois de la République,True
2384869,Respect des principes de la République,True
2385355,Respect des principes de la République,True
2388583,Respect des principes de la République,True
2388644,Respect des principes de la République,True
2390359,Respect des principes de la République,True
2391120,Respect des principes de la République,True
2391958,Respect des principes de la République,True
2393319,Respect des principes de la République,True
2394501,respect des principes de la république,True
2394572,Respect des principes de la République,True
2396343,Respect des principes de la République,True
2397284,Respect des principes de la République,True
2399758,Respect des principes de la République,True
2402544,Respect des principes de la République,True
2403554,Respect des principes de la République,True
2404746,Respect des principes de la République,True
2405372,Respect des principes de la République,True
2407066,Respect des principes de la République,True
2407841,Respect des principes de la République,True
2408605,Respect des principes de la République,True
2410818,Respect des principes de la République,True
2411493,Respect des principes de la République,True
2416482,respect des principes de la république,True
2567101,Respect des principes de la République,True
2568277,Respect des principes de la République,True
2569825,Respect des principes de la République,True
2569941,Respect des principes de la République,True
2571429,Respect des principes de la République,True
2571899,Respect des principes de la République,True
2572873,Respect des principes de la République,True
2574330,Respect des principes de la République,True
2597558,Respect des principes de la République,True
2771128,Convention relative à la nationalité entre la République française et le royaume d'Espagne,True
2881613,Dissolution des groupuscules fascistes et antirépublicains,True
2975816,État de l'école de la République,True
2976329,État de l'école de la République,True
3096183,Fonds Marianne pour la République,True
3121590,Valeurs républicaines à l'école,True
3194896,Arc républicain et extrême droite,True
3453420,Prestation de serment d'une juge suppléante à la Cour de la République,True
1581096,Attaques contre les élus de la République,True
1611606,Attaques contre la République et les institutions démocratiques,True
1625180,Quartiers de reconquête républicaine en Seine-Saint-Denis,True
1626627,Quartiers de reconquête républicaine,True
1805669,Crise de la République,True
2239001,Valeurs de la République à l'école,True
2239014,Valeurs de la République à l'école,True


# VRAIS CHECK À FAIRE :

