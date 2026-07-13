# Journal de comparaison : mentions de "République"

Extrait du script `3_1_identification_republique.py`, pour ne pas alourdir
le code. Comptages obtenus lors des premiers tests de la fonction
`contains_lexical_outside_excl` (avec exclusions), selon la source du corpus.  
Actualisé depuis changement extraction (br/italique) / changement nettoyage / changement regex

## Match valide

NOTE : colle pas pile à la shape df avec Nan,
(ou incongruences entre versions si vire ou pas selon présence combinée id_orateur/id_acteur/nom_orateur, etc.)

| Source                                    | Shape       | False       | True   |
|--------------------------------------------|------------:|------------:|-------:|
| Fichier NosDéputés (ND15+16_interventions_hemicycle_rich.tsv)      | 1391207   | 1377345   | 13675 (13675 aussi nettoyé) |
| Extraction brute (1_2_extract_15_16_concat.csv)        | 1127829   | 1113965   | 13820 (13097 nettoyé) |
| Fichier maison (2_4_interventions_nettoyees)          | 517023   | 506104   | (11300 brut) 10833 (net = de base) |

**TODO** :  ~600 manquants entre "NosDéputés" et "extraction brute" sur texte nettoyé

**NOTE** : écart sur même regex entre texte nettoyé et texte brut :
espaces multiples non normalisés dans texte_brut.
"le Président de                            la République" -> pas exclu car des espaces, etc.
repu_match_valide (texte nettoyé) : True      10876
repu_match_valide (texte_brut) : True      11336

### Match après exclusions sans orateurs
df_brut_with_speaker shape :  (1027685, 41)
repu_match_valide counts : True       13819
repu_match_valide_net counts : True       13097

df_ND1516_with_speaker shape :  (1088105, 20)
repu_match_valide counts : True       13623
repu_match_valide_net : True       13623

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

Exploration des cas LIMITES :

### comparaison absence par pnum vs_idsyceron
Pas forcément la vraie/seule source différence mais aide comparaison par pnum / id_syceron
(cf exploration manuelle de `nd_pnum_absentes_de_brut_match.csv`)

- Flag contenu dans des **fichiers que l'on exclut** de notre côté (**congrès**, doublons, etc.)
- Même sans fusion interventions, **pas même gestion du nb lignes par interventions** (parenthèses applaudissements dans l'intervention chez nous, renvoi à une autre inter chez ND)
  - ex : 15 vs 18 interv pour la déclaration politique générale du 4 juillet 2017
- **Mauvais pnum** mais bien dans le df maison qui match :
  - liste par ex : pnum 1381312 (vs id 1381415), 1381313 (vs encore 1381415), 1433638 (vs 1433583), 1627250, 2396860, 2397067, 2397071, 2480254
- **Texte vs niveau point** : "erreur" ND avec passage en texte de l'intervention ce qui est en fait pour nous le niveau de discussion (et donc pas d'orateur associé)
  - voir ex dessous (Respect des principes de la République, Valeurs républicaines à l'école, etc.)
  - cf pnum 2337471, 2384869, 2385355, 2388583, 2388644, 2390359, 2391120, 2391958, 2393319, 2394501, 2394572, 2396343, 2397284, 2399758, 2402544, 2403554, 2404746, 2405372, 2407066, 2407841, 2408605, 2410818, 2411493, 2416482, 2567101, 2568277, 2569825, 2569941, 2571429, 2571899, 2572873, 2574330, 2597558, 2771128, 2975816, 2976329, 3096183, 3121590, 3194896, 3453420, 1581096, 1611606, 1626627, 1805669, 2239001, 2239014


Exemple :
```
<p>Prééminence des lois de la République</p>, <p>Respect des principes de la République</p>, <p>respect des principes de la république</p>, <p>Convention relative à la nationalité entre la République française et le royaume d'Espagne</p>, <p>Dissolution des groupuscules fascistes et antirépublicains</p>, <p>État de l'école de la République</p>, <p>Fonds Marianne pour la République</p>, <p>Valeurs républicaines à l'école</p>, <p>Arc républicain et extrême droite</p>, <p>Prestation de serment d'une juge suppléante à la Cour de la République</p>,
# et ceux là (pris après nettoyage, mais sinon y a les balises p aussi normalement)
Attaques contre les élus de la République, Attaques contre la République et les institutions démocratiques, Quartiers de reconquête républicaine en Seine-Saint-Denis, Quartiers de reconquête républicaine, Crise de la République, Valeurs de la République à l'école, Valeurs de la République à l'école
```

### comparaison par snippets de texte

cf. exploration manuelle de `nd_snippets_absent_de_brut.csv`

- des cas ou snippet peut pas bien comparer car normalisation des textes (avant même fonction nettoyage collent pas) ?
- TODO souci fonction nettoyage qui marche bien mais qui plante dans le fichier extract ?
- fait pour br et italique -> retester
- 
- ex : dans ND

- CRSANR5L15S2017E1N003,,,20170706093000000,jeudi 06 juillet 2017,1,3,AN,15,Première session extraordinaire 2017,20171003,Présidence de M. François de Rugy,Prorogation de l’état d’urgence > Discussion générale,2,Prorogation de l’état d’urgence,Discussion générale,,Discussion générale,Discussion générale,,,DISC_GENERALE_1,1,12,452,PA720454,PM722968,DISC_GENERALE_2_3,NORMAL,PAROLE_1_2,982987,,M. Dimitri Houbron,,720454.0,,"…pour inscrire dans le droit commun des mesures efficaces assurant la protection de **nos concitoyens.N’oublions** pas ceux qui perdent la vie dans ces actes terroristes ! N’oublions pas que les victimes du terrorisme sont notre démocratie et notre innocence ! N’oublions pas que nous devons la sécurité à nos concitoyens, que nous, élus de la République, sommes responsables ! Je vois un pays splendide et un peuple de génie résister à cet abîme ; je vois les êtres pour lesquels nous nous sommes engagés, apaisés, déterminés et libres. Ce que nous allons accomplir aujourd’hui est bien meilleur que tous nos actes passés. (Applaudissements sur les bancs du groupe REM.)","…pour inscrire dans le droit commun des mesures efficaces assurant la protection de nos concitoyens.N'oublions pas ceux qui perdent la vie dans ces actes terroristes ! N'oublions pas que les victimes du terrorisme sont notre démocratie et notre innocence ! N'oublions pas que nous devons la sécurité à nos concitoyens, que nous, élus de la République, sommes responsables ! Je vois un pays splendide et un peuple de génie résister à cet abîme ; je vois les êtres pour lesquels nous nous sommes engagés, apaisés, déterminés et libres. Ce que nous allons accomplir aujourd'hui est bien meilleur que tous nos actes passés.",1,True,…pour inscrire dans le droit commun des mesures efficaces assurant la protection de nos concitoyens.N'oublions pas ceux qui perdent la vie dans ces ac,False

# VRAIS CHECK À FAIRE :


CRSANR5L15S2017E1N003,,,20170706093000000,jeudi 06 juillet 2017,1,3,AN,15,Première session extraordinaire 2017,20171003,Présidence de M. François de Rugy,Prorogation de l’état d’urgence > Discussion générale,2,Prorogation de l’état d’urgence,Discussion générale,,Discussion générale,Discussion générale,,,DISC_GENERALE_1,1,12,452,PA720454,PM722968,DISC_GENERALE_2_3,NORMAL,PAROLE_1_2,982987,,M. Dimitri Houbron,,720454.0,,"…pour inscrire dans le droit commun des mesures efficaces assurant la protection de nos concitoyens.N’oublions pas ceux qui perdent la vie dans ces actes terroristes ! N’oublions pas que les victimes du terrorisme sont notre démocratie et notre innocence ! N’oublions pas que nous devons la sécurité à nos concitoyens, que nous, élus de la République, sommes responsables ! Je vois un pays splendide et un peuple de génie résister à cet abîme ; je vois les êtres pour lesquels nous nous sommes engagés, apaisés, déterminés et libres. Ce que nous allons accomplir aujourd’hui est bien meilleur que tous nos actes passés. (Applaudissements sur les bancs du groupe REM.)","…pour inscrire dans le droit commun des mesures efficaces assurant la protection de nos concitoyens.N'oublions pas ceux qui perdent la vie dans ces actes terroristes ! N'oublions pas que les victimes du terrorisme sont notre démocratie et notre innocence ! N'oublions pas que nous devons la sécurité à nos concitoyens, que nous, élus de la République, sommes responsables ! Je vois un pays splendide et un peuple de génie résister à cet abîme ; je vois les êtres pour lesquels nous nous sommes engagés, apaisés, déterminés et libres. Ce que nous allons accomplir aujourd'hui est bien meilleur que tous nos actes passés.",1,True,…pour inscrire dans le droit commun des mesures efficaces assurant la protection de nos concitoyens.N'oublions pas ceux qui perdent la vie dans ces ac,False
