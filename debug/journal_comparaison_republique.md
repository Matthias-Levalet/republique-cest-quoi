# Journal de comparaison : mentions de "République"

Extrait du script `3_1_identification_republique.py`, pour ne pas alourdir
le code. Comptages obtenus lors des premiers tests de la fonction
`contains_lexical_outside_excl` (avec exclusions), selon la source du corpus.  
Actualisé depuis changement extraction (br/italique) / changement nettoyage / changement regex

## 1. Résumé global regex repu vs différents fichiers

### 1.1 Match regex avec exclusions lexicales

NOTE : colle pas pile à la shape df avec Nan,
(ou incongruences entre versions si vire ou pas selon présence combinée id_orateur/id_acteur/nom_orateur, etc.)

| Source                                    | Shape       | False       | True   |
|--------------------------------------------|------------:|------------:|-------:|
| Fichier NosDéputés (ND15+16_interventions_hemicycle_rich.tsv)      | 1391207   | 1377532 (1377532)   | 13675 (13675 nettoyé) |
| Extraction brute (1_2_extract_15_16_concat.csv)        | 1127829   | 1114011 (1114734)   | 13818 (13095 nettoyé) |
| Fichier maison (2_4_interventions_nettoyees)          | 517023   | (506192) 505725   | (11298 brut) 10831 (net = de base) |

**Écart observé :**
NosDéputés : 13675 mentions valides (nettoyé comme brut)
Extraction nettoyée : 13095 mentions valides sur texte nettoyé (13818 sur brut)
Différence : 580 occurrences
(pour rappel sur fusion interruptions : 10831 (11298 sur brut))

**TODO :**
- comprendre les ~600 occurrences présentes côté NosDéputés mais absentes de l’extraction nettoyée ;
- distinguer :
  - différence de périmètre ;
  - découpage différent des interventions ;
  - perte lors extraction/nettoyage.

### 1.2 Effet du nettoyage texte brut vs texte nettoyé

Dans le texte brut, les espaces multiples empêchent certaines exclusions.

Ex : Écart identifié :
- "le Président de                            la République"

Conclusion :

- la normalisation des espaces modifie le résultat de la regex ;
- le texte brut produit davantage de faux positifs car certaines expressions exclues ne sont plus reconnues.

### 1.3 Impact de la présence d'un speaker sur les matchs regex

La comparaison avec et sans restriction aux interventions disposant d'un speaker montre que les matchs valides de la regex repu dépendent très peu des interventions sans speaker (50aine de cas).  
(Ce qui est donc très différent des explications de différence du nombre de lignes dans le cas de l'ensemble des interventions (voir journal dédié vs nd), majoritairement due aux interventions sans speakers)

> À noter que ce résultat est très différent de l’analyse des écarts de volumétrie brute entre fichiers : les lignes sans intervenant expliquent une grande partie des différences de structure (voir journal dédié vs nd), mais contribuent très peu aux matchs regex valides.

| Texte        | Corpus     | Sans filtre speaker | Avec speaker | Écart |
| ------------ | ---------- | ------------------: | -----------: | ----: |
| `texte_brut` | NosDéputés |              13 675 |       13 623 |   -52 |
| `texte_brut` | Extraction |              13 818 |       13 817 |    -1 |
| `texte_net`  | NosDéputés |              13 675 |       13 623 |   -52 |
| `texte_net`  | Extraction |              13 095 |       13 095 |     0 |


Ces résultats indiquent que les écarts observés entre NosDéputés et l'extraction ne semblent pas principalement liés à la présence ou absence d'un orateur associé aux interventions.

Les divergences proviennent plutôt (voir plus bas) :

- des différences de découpage des interventions
- des différences de contenu textuel
- des traitements de nettoyage et normalisation
- des modalités d'extraction des textes
- des vrais soucis de diff (à identifier)

### 1.4 Match "républi" brut sans aucune exclusion de termes (pour trace)

Pour trace et idée (sans nettoyage spécifiques ni verif speakers etc.)
NOTE : colle pas pile à la shape df avec Nan etc.

Pour référence, `pattern_lexical = re.compile(r"républi", re.I)` seul,
sans passer par `contains_lexical_outside_excl` :

(NOTE : avant modif extraction et gestion balises, mais doit pas compter ici car pas exclusion)

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

## 2. Analyse des divergences regex repu

Exploration des cas LIMITES :

### 2.1 Comparaison absence par pnum vs_idsyceron

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

### 2.2 Comparaison par snippets de texte

cf. exploration manuelle des fichiers sortie

- CHECK : des cas ou snippet peut pas bien comparer car **normalisation des textes** (avant même fonction nettoyage) colle pas ?
  - TODO souci fonction nettoyage qui marche bien mais qui plante dans le fichier extract ?
  - fait pour br et italique -> retester
- Snippet échoue car texte extract **contient des parenthèses**, (virent avec nettoyage) -> mais **match pas avec format ND** qui renvoie **interventions séparées** si parenthèses de didascalies
  - Nombre de snippets ND absents de brut avec parenthèses : 32
  - Nombre de snippets brut absents de ND avec parenthèses : 2032
- Même idée **points suspension** ?
  - Fait (cf 2.3) : le check confirme que les points de suspension expliquent une part substantielle des "absents", plus importante en proportion que les parenthèses côté ND->extract (617 vs 32), et comparable côté extract->ND (1049 vs 2032). Chevauchement partiel entre les deux patterns (union croisée < somme simple, cf 2.3) : certaines lignes cumulent les deux causes.
  

ex parenthèses : 
CRSANR5L15S2017E1N012,,,20170713150000000,jeudi 13 juillet 2017,2,12,AN,15,Première session extraordinaire 2017,20171012,Présidence de M. François de Rugy,Renforcement du dialogue social > Discussion des articles (suite) > Après l’article 3 (suite),4,Renforcement du dialogue social,Discussion des articles (suite),Après l’article 3 (suite),,Après l’article 3 (suite),(n[[o]] 19),Après_ 3,DISC_ARTICLES_3_1,1,1,62,PA717379,PM723282,DISC_ARTICLES_1_30_1,NORMAL,PAROLE_1_2,991112,,M. Sylvain Maillard,,717379.0,,"Je tenais à saluer votre première présidence de séance, monsieur le président. (Applaudissements sur les bancs des groupes REM et MODEM.) Nous sommes fiers de vous voir à cette place. Vous êtes le plus jeune vice-président de l’histoire de la VeRépublique. Félicitations ! Nous comptons sur vous. (Applaudissements sur les bancs du groupe REM.)","Je tenais à saluer votre première présidence de séance, monsieur le président. Nous sommes fiers de vous voir à cette place. Vous êtes le plus jeune vice-président de l'histoire de la VeRépublique. Félicitations ! Nous comptons sur vous.",1,True,"Je tenais à saluer votre première présidence de séance, monsieur le président. Nous sommes fiers de vous voir à cette place. Vous êtes le plus jeune v",False

### 2.3 Confrontation systématique (script factorisé) : orig/net × tous/speaker

Résultats du script de confrontation factorisé (4 configurations :
texte_brut / texte_net × tous / avec-orateur uniquement).

NOTE : la comparaison par pnum/id_syceron (identifiants) est valide dans les 4 configs.
La comparaison par snippets, elle, repose sur une égalité de sous-chaîne exacte entre les deux corpus.
Et elle n'est donc pertinente que sur texte_net, où les deux textes sont normalisés de façon comparable (balises, apostrophes,; espaces).
Sur texte_brut, elle donne un taux d'"introuvable" artificiellement proche de 100%, donc non calculée / non retenue ici.

/!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ 
# TODO : creuser tout ce qui est ci-dessous
/!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ 

#### a) pnum vs id_syceron

| Configuration        | Lignes ND | Absentes de l'extraction | Dont mention valide de République |
|-----------------------|----------:|--------------------------:|-----------------------------------:|
| texte_brut             | 1 391 207 |                     45 410 |                                 130 |
| texte_brut_speaker     | 1 088 105 |                        841 |                                  81 |
| texte_net              | 1 391 207 |                     45 410 |                                 130 |
| texte_net_speaker      | 1 088 105 |                        841 |                                  81 |

**Constats :**

- TODO : Les comptes sont identiques entre `texte_brut` et `texte_net` (130 / 81) :
  sur ce sous-ensemble précis (lignes ND absentes de l'extraction), les
  variantes brut/net de la regex ne divergent pas — contrairement à l'écart
  observé en 1 sur l'ensemble du corpus
  (13818 vs 13095 nettoyé fichier extraction ; 10831 vs 11 298 fishier fusion) 
- Le filtre "avec speaker" fait chuter les lignes absentes de 45410 à 841
  (-98%) : cohérent avec l'hypothèse "texte vs niveau point" de 2.1 — la
  grande majorité de l'écart pnum/id_syceron correspond à des lignes ND sans
  speaker associé (titres/niveaux de discussion), pas à un vrai défaut
  d'extraction.

#### b) Snippets (texte_net uniquement)

| Config             | Direction       | Introuvable / total | dont parenthèses | dont points_suspension | dont ≥ 1 pattern (croisé) |
|--------------------|-----------------|--------------------:|-----------:|-------------:|--------------:|
| texte_net          | ND -> extract    |      1 229 / 13 675 |         32 |          617 |           642 |
| texte_net          | extract -> ND    |      2 577 / 13 095 |      2 032 |        1 049 |         2 362 |
| texte_net_speaker  | ND -> extract    |      1 209 / 13 623 |         32 |          617 |           642 | 
| texte_net_speaker  | extract -> ND    |      2 579 / 13 095 |      2 033 |        1 050 |         2 364 |

**Constats :**
- Le filtre speaker ne fait presque pas bouger les deux comptes ND->extract
  (1229->1209) et extract->ND (2577->2579), et ce n'est **pas symétrique par
  hasard** : côté "extract avec mention valide" la population reste
  identique (13 095-> 13 095, quasi aucune ligne extract sans orateur), donc
  seule la population *cherchée* côté ND diminue (13675->13623), ce qui peut
  faire baisser légèrement son propre taux d'introuvable (1229->1209) tout en
  faisant *monter* légèrement l'autre sens, puisque le "big" ND utilisé comme
  cible de recherche rétrécit (2577->2579). Cf. discussion détaillée dans le
  script de confrontation.
- Union croisée (`check_au_moins_un`) < somme simple des deux patterns dans
  les deux sens : léger chevauchement de lignes qui cumulent parenthèses et
  points de suspension (7 lignes en ND->extract, 719 en extract->ND, en
  texte_net non filtré).
- Il reste un residu non expliqué par ces deux patterns : **587** côté
  ND->extract et **215** côté extract->ND (texte_net). C'est ce résidu qui
  mériterait l'exploration manuelle prioritaire (cf. TODO ci-dessous).

#### c) Focus patterns

**Cas liés aux parenthèses :**
ND absent dans extraction Total : 1229  
Avec parenthèses dans texte original : 32  

Extraction absente dans ND Total : 2577  
Avec parenthèses dans texte original : 2032  

**Cas liés aux points de suspension**

ND absent extraction Avec points de suspension : 617  
Extraction absente ND Avec points de suspension : 1049  

Hypothèse : les points de suspension peuvent donc révéler :

- découpage différent des interventions
- troncature
- fusion/séparation de blocs.

/!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ 
# TODO :
- sur texte_net, pas de diff réelle entre avec et sans speaker
- possiblement car fonction nettoyage renvoie déjà des textes vides, donc regex = false pour pas mal de cas sans speakers:(Applaudissements), etc.


POUR LA SCIENCE :
(même si pas de sens/logique puisque pas normalisé, mais pour observer les écarts)

============================================================
CONFIGURATION : texte_brut
============================================================
---------- pnum vs id_syceron [texte_brut] ----------
Lignes ND : 1391207 | absentes de l'extraction : 45410
Dont mention valide de République : 130
---------- snippets [texte_brut] ----------
Lignes ND avec mention repu valide       : 13675
Lignes extract avec mention repu valide  : 13818
ND (repu) introuvable dans extract : 13675 / 13675
  dont patterns (dans le texte original) :
    dont avec parentheses : 589
    dont avec points_suspension : 2368
  dont avec au moins un pattern (croisé) : 2851
Extract (repu) introuvable dans ND : 12685 / 13818
  dont patterns (dans le texte original) :
    dont avec parentheses : 6420
    dont avec points_suspension : 2653
  dont avec au moins un pattern (croisé) : 7688
============================================================
CONFIGURATION : texte_brut_speaker
============================================================
---------- pnum vs id_syceron [texte_brut_speaker] ----------
Lignes ND : 1088105 | absentes de l'extraction : 841
Dont mention valide de République : 81
---------- snippets [texte_brut_speaker] ----------
Lignes ND avec mention repu valide       : 13623
Lignes extract avec mention repu valide  : 13817
ND (repu) introuvable dans extract : 13623 / 13623
  dont patterns (dans le texte original) :
    dont avec parentheses : 589
    dont avec points_suspension : 2367
  dont avec au moins un pattern (croisé) : 2850
Extract (repu) introuvable dans ND : 12684 / 13817
  dont patterns (dans le texte original) :
    dont avec parentheses : 6419
    dont avec points_suspension : 2653
  dont avec au moins un pattern (croisé) : 7687

NOTE : Et le reste :

============================================================
CONFIGURATION : texte_net
============================================================
---------- pnum vs id_syceron [texte_net] ----------
Lignes ND : 1391207 | absentes de l'extraction : 45410
Dont mention valide de République : 130
---------- snippets [texte_net] ----------
Lignes ND avec mention repu valide       : 13675
Lignes extract avec mention repu valide  : 13095



Lignes ND : 1391207 | absentes de l'extraction : 45410
Dont mention valide de République : 130
---------- snippets [texte_brut] ----------
Lignes ND avec mention repu valide       : 13675
Lignes extract avec mention repu valide  : 13818
ND (repu) introuvable dans extract : 13675 / 13675
  dont patterns (dans le texte original) :
    dont avec parentheses : 589
    dont avec points_suspension : 2368
  dont avec au moins un pattern (croisé) : 2851
Extract (repu) introuvable dans ND : 12685 / 13818
  dont patterns (dans le texte original) :
    dont avec parentheses : 6420
    dont avec points_suspension : 2653
  dont avec au moins un pattern (croisé) : 7688
============================================================
CONFIGURATION : texte_brut_speaker
============================================================
---------- pnum vs id_syceron [texte_brut_speaker] ----------
Lignes ND : 1088105 | absentes de l'extraction : 841
Dont mention valide de République : 81
---------- snippets [texte_brut_speaker] ----------
Lignes ND avec mention repu valide       : 13623
Lignes extract avec mention repu valide  : 13817






-----------------
--- df_extract ---
-----------------
repu_match_valide
False    1114011
True       13818
Name: count, dtype: int64
(1127829, 39)

df_extract_with_speaker repu_match_valide counts :
 repu_match_valide
False    1013868
True       13817
Name: count, dtype: int64


-----------------
repu_match_valide_net
False    1114734
True       13095
Name: count, dtype: int64
(1127829, 41)

-----------------
df_extract_with_speaker repu_match_valide_net counts :
 repu_match_valide_net
False    1014590
True       13095
Name: count, dtype: int64
-----------------


-----------------
--- df_ND1516 ---
-----------------
repu_match_valide
False    1377532
True       13675
Name: count, dtype: int64
(1391207, 18)

df_ND1516_with_speaker repu_match_valide counts :
 repu_match_valide
False    1074482
True       13623
Name: count, dtype: int64
-----------------



-----------------
repu_match_valide_net
False    1377532
True       13675
Name: count, dtype: int64
(1391207, 20)

-----------------

df_ND1516_with_speaker repu_match_valide_net counts :
 repu_match_valide_net
False    1074482
True       13623
Name: count, dtype: int64