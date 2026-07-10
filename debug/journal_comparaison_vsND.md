# bilan journal compraison vs ND

## 1. Résumé Global (par `id_syceron` uniquement)

=== RÉSUMÉ GLOBAL (par id_syceron uniquement) ===
IDs communs              :  1,065,985
Uniquement dans extract  :     61,477
Uniquement dans ND15-16  :     43,516

Total IDs extract :  1,127,462
Total IDs ND      :  1,109,501

| Métrique                      | Valeur    |
| ----------------------------- | --------- |
| **IDs communs**               | 1,065,985 |
| **Uniquement dans `extract`** | 61,477    |
| **Uniquement dans `ND15-16`** | 43,516    |
| **Total IDs `extract`**       | 1,127,462 |
| **Total IDs `ND15-16`**       | 1,109,501 |


**→ 94,5% des IDs sont communs aux deux jeux de données.**

## 2. Analyse des écarts (IDs uniques à un seul jeu de données)

### Constat général

Les IDs présents uniquement dans l’un ou l’autre des DataFrames correspondent quasi exclusivement à :

- **Bruit** : didascalies, adoptions d’amendements, etc.
- **Absence d’intervenant** : lignes sans `parlementaire`, `personnalite`, `id_acteur`, `nom_orateur`, ou `id_orateur`.

| DataFrame             | Lignes sans intervenant | Total lignes uniques | % de bruit |
| --------------------- | ----------------------- | -------------------- | ---------- |
| **`df_only_ND`**      | 44,570 / 45,408         | 45,408               | **\~98%**  |
| **`df_only_extract`** | 60,274 / 61,843         | 61,843               | **\~97%**  |

**Conclusion** : Les écarts sont principalement dus à des **lignes sans intervenant identifié** (bruit).

## 3. Analyse des sous-ensembles (avec/sans intervenant)

### `df_only_ND_no_speaker` (Lignes sans `parlementaire` ET sans `personnalite`)

-> OK c'est des trucs deg, y compris des codes titres "<p>Après l'article 3</p>" / <p>Rappel au règlement</p>

- **Contenu** :
  - Textes non attribuables : codes titres (`<p>Après l'article 3</p>`, `<p>Rappel au règlement</p>`), didascalies, etc.
  - **Aucun intervenant identifié** → **Bruit pur**.
- **Action** : **Exclure de l’analyse** (déjà fait via `df_only_ND_with_speaker`).


### `df_only_extract_no_speaker` (Lignes sans `id_acteur`, `nom_orateur`, `id_orateur`)

-> ok c'est deg aussi : des parenthèses, des signatures (Le Directeur du service du compte rendu de la séance etc.)

- **Contenu** :
  - Parentheses, signatures (*"Le Directeur du service du compte rendu de la séance"*).
  - Suspensions/reprises de séance, points de suspension (`........`).
  - **2 interventions cheloues** (mais parmis 60K) :
    > *"On connaît la lourdeur et l’ampleur des responsabilités relatives à la charge de diriger une association ; or il nous semble qu’avec cette rédaction de l’alinéa 13, vous n’avez pas trouvé le bon équilibre, celui susceptible de garantir le respect plein et entier de la liberté d’association."*  
    > *"L’amélioration de la situation sanitaire a permis à la conférence des présidents de faire évoluer nos règles de fonctionnement : tous les députés peuvent de nouveau être présents dans l’hémicycle. Dès lors qu’il ne sera pas possible de respecter les règles de distance physique, les députés et les ministres devront porter un masque, sauf quand ils prendront la parole. Les huissiers tiennent des masques à leur disposition."*


### `df_only_ND_with_speaker` (Lignes **avec** intervenant dans ND15-16 uniquement)

- **Origine des écarts** :
  - Cas soutiens et discussion d'amendements ??
  - **Fichiers Congrès** (ex: `http://www.assemblee-nationale.fr/15/cri/congres/20184001.asp` > 305 lignes, `20174001.asp` → 55 lignes).
  - des **Pnum qui correspondent plus à un réel id_syceron** = intervention comprise **dans un bloc plus large** (qu'on retrouve bien)
  - **Exemple** : pnum 989943 vs id_syceron 989508 (idem pnum 984462 iv id_syceron 984462)
    - Le `pnum` dans ND ne correspond pas à l’`id_syceron` dans le XML officiel sur la page ou le fichier dispo (regroupement d’interventions).
    - L’`id_syceron 989508` existe bien dans le XML et dans `extract`.
    - Le `pnum` existe "plus" mais la numérotation collerait avec un sous paragraphe de l'intervention globale id_syceron**
  - **Détail** :
    - lien http://www.assemblee-nationale.fr/15/cri/2016-2017-extra/20171010.asp#P989943 qui pointe vers : https://www.assemblee-nationale.fr/dyn/15/comptes-rendus/seance/session-extraordinaire-de-2016-2017/deuxieme-seance-du-mercredi-12-juillet-2017#P989943 (renvoie en fait en haut de page)
    - si on cherche l'id_syceron dans xml de l'assemblée : existe pas
    - si on cherche le texte en question copie le lien depuis le widget de l'assemblée : noyé en fait dans un bloc plus gros : https://www.assemblee-nationale.fr/dyn/15/comptes-rendus/seance/session-extraordinaire-de-2016-2017/deuxieme-seance-du-mercredi-12-juillet-2017#989508
    -  qui lui colle, mais donc pas le num ou le lien que l'on a.
    - et qui existe bien chez nous ainsi que dans le XML en ligne, mais donc regroupé dans l'intervention de l'id 989508
  - Ou encore :
      - pnum 3507002 vs id_syceron 3507003 "aide à mourir soit vraiment collégiale"
      - lien : https://www.assemblee-nationale.fr/16/cri/2023-2024/20240235.asp#3507002
      - renvoie à : https://www.assemblee-nationale.fr/dyn/16/comptes-rendus/seance/session-ordinaire-de-2023-2024/troisieme-seance-du-vendredi-07-juin-2024#3507002 -> renvoie haut du doc
      - copier lien depuis texte page : https://www.assemblee-nationale.fr/dyn/16/comptes-rendus/seance/session-ordinaire-de-2023-2024/troisieme-seance-du-vendredi-07-juin-2024#3507003
      - et donc id 3507003


### `df_only_extract_with_speaker` (Lignes **avec** intervenant dans `extract` uniquement)

- **Origine des écarts** :
  - **Fichiers spécifiques** : Exemple : `CRSANR5L15S2018E1N007` (à identifier).
  - **Problème similaire** : Possible mauvaise identification `pnum` > `id_syceron` pour ces fichiers.
- **Action** :
  - **Lister les `source` uniques** de ce sous-ensemble pour identifier les fichiers problématiques ?
  - **Comparer manuellement** quelques exemples avec les XML officiels.
  - **EN COURS** : **comparaison auto **par snipet

## 4. Résultats recherche texte rapide (snippets)

fast_only_extract_with_speaker -> found: 899 / 1569
fast_only_ND_with_speaker -> found: 382 / 838

--- Décompte SANS les cas 'congres' ---
fast_only_ND_with_speaker -> found (sans congres): 330 / 478

| Jeu de données                                  | Trouvés (`found=True`) | Total   | % de correspondance |
| ----------------------------------------------- | ---------------------- | ------- | ------------------- |
| `extract`  dans `ND15-16`                      | 899                    | 1569    | **57%**             |
| `ND15-16`  dans `extract`                      | 382                    | 838     | **46%**             |
| **`ND15-16`  dans `extract` (sans "congres")** | **330**                | **478** | **69%**             |

**Observations** :

- Partie des écarts liés aux **fichiers Congrès** qu'il faut virer (305 + 55 = 360 lignes dans `ND15-16`).
- **Sans les Congrès**, le taux de correspondance passe de 46% à 69% pour `ND15-16` > **`extract`**.
- **Prochaine étape** : Creuser les 148 cas restants (478 - 330) dans `ND15-16` sans "congres" qui ne sont **pas trouvés dans `extract`**.
- 
# TODO : aller creuser les cas pas trouver pour voir

-> bilan : dans les derniers
- certain liés au fichier zelensky
- des cas qui existent pas/plus dans le fichier ?
  - ex : https://www.assemblee-nationale.fr/16/cri/2022-2023/20230100.asp#2966325,2966325,Louis Boyard,,1055581,que vous a-t-il dit d'autre ?,False -> introuvable dans le doc en question
- certains liés même erreur pnum vs id_syceron quand regroupé dans une intervention
  - (mais le snipet ne flag pas car des "…" séparent des interventions, parfois aussi des transfo de balises mal lues vs nos députés ie chez nous : <exposant>o</exposant>, devient "no" VS chez eux "n°".
  - ex : après normalisation eux "n° 2779" vs nous "no 2779" ?
  - ex : pnum 2964497 vs syceron 2971505 / https://www.assemblee-nationale.fr/16/cri/2022-2023/20230100.asp#2964497
 -> normalisation texte suffit pas
  - TEST après remplacement exposant vs ° ( texte = re.sub(r"<exposant>o</exposant>", "°", texte) #)
    - -> meh ?, suffit pas, affiner ? mais en tout cas trouve bien à la main les cas identifiés 
- pnum et id diff mais flag pas texte car des textes qui collent pas (corrections entre fichiers ?) :
  - ex : pnum 1505471 vs id_syceron 1515918
  - http://www.assemblee-nationale.fr/15/cri/2018-2019/20190059.asp#P1505471,1505471,Hugues Renson,,299372,"cet après-midi, l'assemblée a commencé la discussion des articles du projet de loi, s'arrêtant à l'article 4 et à l'état a annexé.",False
  - en vrai : https://www.assemblee-nationale.fr/dyn/15/comptes-rendus/seance/session-ordinaire-de-2018-2019/deuxieme-seance-du-lundi-12-novembre-2018#1515918 
  - -> "des articles **de la première partie** du projet de loi" 