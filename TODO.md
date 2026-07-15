# TODO

## Général

## 1-data-extraction

## Global

- passer tout sous UV
- finaliser pipeline
- ajouter infos sur téléchargement fichiers et ou option exécution code
- ajouter liste pays txt pour reproductibilité

## À voir

## 1-extraction
- [ ] SOUCIS REGROUPEMENT INTERVENTIONS FOIRE -> nouvelle version semble okayish
  - toujours un mini écart, semble plus stable de pas trier les fichiers par numéro ordre  :
  - les interventions sont déjà dans l'ordre, les id numérotés semblent pas super stables ?
  - et donc au final le résultat semble meilleur sans réappliquer de tri. Mais pq cet écart ?
  - tester avec le id_syceron ? -> test réalisé, c'est naze.
- [X] EXCLURE LAMARTINE OU PAS ? -> DONE = non : passage des acteurs restant en externes
- [X] récupération des points de contexte parents(cf tentative Matthias) = DONE
- [ ] check par matthias si contexte est OK.
- [ ] check repu against ND
- [ ] IMPORTANT : check si implementation gestion balises <br/> ET italique est ok
- [ ] sans doute devoir l'implementer aussi pour récupération du niv point : des trucs qui passent sur plusieurs lignes
- [ ] IE :voir ce qui foire pour rappel réglement sur plusieurs lignes :
  - [ ] ex : CRSANR5L15S2017E1N007, CRSANR5L15S2018E1N027, CRSANR5L15S2018O1N284
  - [ ] etc.

20171007,Présidence de M. François de Rugy,"Renforcement du dialogue social > Discussion des articles (suite) > Rappel
            s
             au règlement",3,Renforcement du dialogue social,Discussion des articles (suite),"Rappel
            s
             au règlement","Rappel
            s
             au règlement","Rappel
            s
             au règlement"

ex : dans CRSANR5L15S2018E1N027

            <titreStruct id_syceron="1386637">
              <intitule>
                <italique>Rappel</italique>
                <italique>s</italique>
                <italique> au règlement<br/></italique>
              </intitule>

        <point nivpoint="3" valeur_ptsodj="1" ordinal_prise="2" id_preparation="0" ordre_absolu_seance="15" code_grammaire="RAP_REGLEMENT_1_1" code_style="Suspension rappel" code_parole="" sommaire="1" id_syceron="1386637" valeur="">
          <orateurs/>
          <texte>
            <italique>Rappel</italique>
            <italique>s</italique>
            <italique> au règlement</italique>
          </texte>


- [ ] MAIS AUSSI AUTRE CHOSE : CRSANR5L15S2019O1N021
CRSANR5L15S2019O1N021,,,20181017150000000,mercredi 17 octobre 2018,1,21,AN,15,Session ordinaire 2018-2019,20180021,Présidence de M. Richard Ferrand,"Projet de loi de finances pour 2019 > Première partie 
        (suite) > Après l’article 2 (suite)",4,Projet de loi de finances pour 2019,"Première partie 
        (suite)",Après l’article 2 (suite),,Après l’article 2 (suite),,Après_ 2,DISC_

Cf
        <sommaire2 type_debat="PLF">
          <titreStruct type_debat="PLF" id_syceron="1456429">
            <intitule>
              <italique>Première partie </italique>
              <italique>(suite)</italique>
              <italique>
                <br/>
              </italique>
            </intitule>
          </titreStruct>
          <sommaire3 type_debat="PLF">
            <titreStruct type_debat="PLF" id_syceron="1456431">
              <intitule>Après l’article 2 <italique>(suite)</italique></intitule>
            </titreStruct>

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

- [X] ON PERD DES OCCURRENCES AVEC LE NETTOYAGE TEXTE -> normal, espaces multiples mal gérés par regex si pas nettoyé avant
- [X] check "\t" vs rien dans liste pays république -> DONE
- [X] ajouter les nouveaux cas identifiés
- [X] aviser avec la nouvelle remontée d'exclusions possibles.
- [ ] voir pour un check des ajouts avec matthias si c'est ok
- [ ] check repu against ND

ENCORE des trucs qui flaguent ? sans trop savoir pourquoi ?
ex

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

