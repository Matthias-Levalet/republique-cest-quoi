# %% [markdown]
# # 2-clean&filter

# %%
# TODO : exploser et refacto tout ça ?

# genre (pas parfait, colle pas nickel mais pour l'idée)

# 2a_filtrage.py
# 2.1 début : exclusion président, code_style, code_grammaire, nettoyage textes, textes parasites

# 2b_identification.py
# fusion id_acteur/id_orateur, nom le plus fréquent, correction erreurs id_acteur, correction fuzzy

# 2c_match_deputes.py
# 2.2.1 + 2.2.2 : merge données députés + affiliation temporelle

# 2d_affiliations_gouv.py
# 2.2.3 + 2.2.4 : GOUV, fallback groupeAbrev, cas RN, export final
# (ou groupé avec l'affiliation tout court ?)

# 2e_diagnostics.py
# tout le bloc "GESTION DES CAS RESTANTS" + "EXPLORATION"

# %% [markdown]
# ## 2.1 pré-nettoyage, pré-filtrage et pré-recodages

# %%
import pandas as pd
import re
from rapidfuzz import fuzz


# Charger le df concaténé des deux législatures
df = pd.read_csv(
    "../data/interim/interventions_regroupees.csv",  # interventions_regroupees ou extract_15_16_concat
    low_memory=False,
    dtype={
        "id_orateur": str  # éviter identification en float avant d'avoir ajouté le "PA"
    },
)

print("Shape du df chargé : ", df.shape)


# ===========================================================
# FILTRAGE DES INTERVENTIONS
# ===========================================================

"""
nb : précision choix 
- exclusion président.e :
role_debat n'est pas toujours bien identifié, utiliser aussi nom_orateur
(avant de le recoder/nettoyer car sinon risque perte par remplacement)
"""

# Exclure les prises de parole de "Mme la présidente" et "M. le président"
df = df[~df["nom_orateur"].str.strip().isin(["M. le président", "Mme la présidente"])]
# Exclure les éléments restants en roledebat == president
df = df[~df["roledebat"].str.strip().isin(["president"])]

# Exclure les lignes pour lesquelles on n'a pas d'info orateurs (pas exploitable ici)
df = df[~(df["id_acteur"].isna() & df["nom_orateur"].isna() & df["id_orateur"].isna())]

# Ne garder que le code style NORMAL
df = df[df["code_style"] == "NORMAL"]

# Changer les missing values pour non_précisé (majoritaire) dans Code_parole
# (normalement géré dans la section fusion des interventions interrompues)
# (mais si des gens veulent s'en passer le faire ici)
df["code_parole"] = df["code_parole"].fillna("non_précisé")

# Garder une trace de la longueur des interventions brutes
# (nb : varie selon qu'on groupe ou non les interventions interrompues en amont)
df["len_texte_brut"] = df["texte"].str.len()

print("Shape du df après pré-filtrage : ", df.shape)

# ========== Gestion codes grammaires ==========
# virer les codes grammaires inutiles qui restent après premiers filtres
# (peut varier selon les choix de filtrage en amont)
exclusion_code_grammaire = [
    "OUV_SEAN_2_1",
    "FUSION",
    "FIN_SEAN_2_1",
    "DISC_ARTICLES_3_9_1",  # interv président.es mal identifiées
    "DISC_ARTICLES_3_1",
    "ANN_SCR_AUTRE_1_0",
    # # Pour trace mais pas utile ici :
    # "ODJ_APPEL_DISCUSSION"
    # "DISC_ARTICLES_1_30"
]

n_avant = len(df)

mask_excl_code_grammaire = df["code_grammaire"].isin(exclusion_code_grammaire)
print(f"Lignes à exclure (code_grammaire) : {mask_excl_code_grammaire.sum()}")

df = df[~mask_excl_code_grammaire]

print(f"Shape après exclusion code_grammaire : {df.shape})")


# ===========================================================
# NETTOYAGE DES TEXTES PUIS EXCLUSION DES VIDES ET PARASITES
# ===========================================================

# ========== Nettoyer les textes et supprimer les lignes vides ==========


# nettoyage basique du texte
def nettoyer_texte(texte):
    if not isinstance(texte, str):
        return texte
    # Supprimer les balises HTML/XML
    texte = re.sub(r"<[^>]+>", "", texte)
    # Supprimer contenu entre parenthèses
    texte = re.sub(r"\([^)]*\)", "", texte)
    # Supprimer les espaces multiples
    texte = re.sub(r"\s+", " ", texte).strip()
    # uniformise pour avoir les bons apostrophes (nécessaire pour regex)
    texte = texte.replace("’", "'")
    return texte


df["texte_brut"] = df["texte"]  # garder une version brute du texte
df["texte"] = df["texte"].apply(nettoyer_texte)

# supprimer les lignes où "texte" est manquant ou vide
mask_texte_vide = df["texte"].isna() | (df["texte"] == "")
print(f"Lignes supprimées pour texte vide : {mask_texte_vide.sum()}")
df = df[~mask_texte_vide]


# ========== Gestion textes parasites ==========

# Varie selon les choix de filtrage en amont (sur les président.es)
# mais il peut y avoir quelques cas spécifiques de textes parasites
# Mais autant avoir une fonction si on devait généraliser à d'autres données

# cf les spécifiques :
# "……………………………………………………………."
# "………………………………………………………………………………………"
# "------------------Cette partie de la séance est en cours de finalisation---------------------------------------------"  #
# "------------------Cette partie de la séance est en cours de finalisation---------------------------------------------Madame la ministre, (blablablabla)"


# identification textes parasites
def est_texte_parasite(texte):
    if not isinstance(texte, str):
        return False
    nettoyé = re.sub(
        r"Cette partie de la séance est en cours de finalisation", "", texte
    )
    nettoyé = re.sub(r"[-–—.…\s]+", "", nettoyé)
    return nettoyé == ""


mask_parasite = df["texte"].apply(est_texte_parasite)
print(f"Lignes parasites supprimées : {mask_parasite.sum()}")
df = df[~mask_parasite]

print("Shape du df après nettoyage et exclusion des textes : ", df.shape)


# ===========================================================
# FUSION DES IDENTIFIANTS D'ACTEURS,
# RÉCUPÉRATION ET NETTOYAGE DU NOM LE PLUS FRÉQUENT
# (et correction d'erreurs id_acteur)
# ===========================================================

# ========== Fusion id_acteur et id_orateur ==========
"""
NOTE:
- id_acteur vs id_orateur :
certains cas (~3000) ont un id_orateur plus précis (un code PA) que id_acteur qui a PA0
Mais en fait ce sont presque 100% des interruptions avec souvent plusieurs locuteurs.
id_orateur en renvoie (mal) un seul -> on préfère garder le PA0 (neutre)
"""

# # Stabiliser le id_orateur pour être au format AN
# df["id_orateur"] = "PA" + df["id_orateur"]
# # Remplacer les valeurs manquantes de id_acteur par id_orateur quand disponible
# df["id_acteur_originel"] = df["id_acteur"]  # garder une trace
# df["id_acteur"] = df["id_acteur"].combine_first(df["id_orateur"])


# ========== Recoder par noms les plus fréquents et nettoyer ==========

# Fonction pour le nom le plus fréquent


def calculer_nom_plus_frequent(df):
    """
    Calcule, pour chaque id_acteur, le nom_orateur le plus fréquent (mode).
    Version plus stable que value_counts().idxmax() en cas d'ex-aequo.
    """
    return df.groupby("id_acteur")["nom_orateur"].agg(
        lambda x: x.dropna().mode().iloc[0] if x.dropna().size > 0 else None
    )  # version plus stable que value_counts().idxmax() en cas d'ex-aequo


# Fonction pour renvoyer le nom en question
# Renvoyer le nom le plus fréquent sauf si id_acteur == PA0 ou id_acteur est manquant
# NOTE : voir limite de la fonction en description


def get_most_frequent_name(row):
    """
    Récupération de la forme la plus fréquente du nom,
    uniquement pour acteurs différents de PA0.
    if PA0 : nom brut, else : nom le plus fréquent pour cet id.
    /!\ Limite de la fonction :
    - 1. invisibilise les rares cas d'interventions mal identifiées
    par leur PA, mais qui ont le bon nom (ici le nom majoritaire sera renvoyé)
    - 2. pourrait poser problème si on gardait les M/Mme président.e
    (qui pourraient être majoritaires plutôt que le nom de la personne)
    - 3. dépend de most_frequent_name calculé par ailleurs
    """
    if row["id_acteur"] == "PA0" or pd.isna(row["id_acteur"]):
        return row["nom_orateur"]
    return most_frequent_name.get(row["id_acteur"], row["nom_orateur"])


# Fonction nettoyage des noms d'orateurs


def nettoyer_nom(texte):
    """
    la fonction est proche du nettoyage texte mais supprime aussi les virgules.
    On garde deux fonctions séparées pour plus de clarté et pour pouvoir les modifier indépendamment.
    """
    if not isinstance(texte, str):
        return texte
    # Supprimer les balises HTML/XML
    texte = re.sub(r"<[^>]+>", "", texte)
    # Supprimer contenu entre parenthèses
    texte = re.sub(r"\([^)]*\)", "", texte)
    # Supprimer les virgules
    texte = texte.replace(",", " ")
    # Supprimer les espaces multiples
    texte = re.sub(r"\s+", " ", texte).strip()
    # uniformise pour les apostrophes
    texte = texte.replace("’", "'")
    return texte


# appliquer le nom le plus fréquent + le nettoyage sur celui-ci
most_frequent_name = calculer_nom_plus_frequent(df)

df["nom_orateur_clean"] = df.apply(get_most_frequent_name, axis=1).apply(nettoyer_nom)


# ========== Correction automatique des erreurs id_acteur =============

"""
NOTE : nb traçabilité :
Cas problématiques id_acteur != id_orateur & nom_orateur != nom_orateur_clean
-> on considère que le texte (et donc le nom inscrit) du CR fait foi
-> et donc que l'id_orateur est le bon, on l'utilise pour écraser id_acteur
-> Si id_acteur != id_orateur mais que les noms sont similaires,
c'est que l'erreur porte sur l'id_orateur et ça nous gène pas (pas celui utilisé ensuite).

nb : Dans notre cas, l'égalité sur la base des noms nettoyés suffit
(après vérification manuelle de tous les cas)
Mais il faudrait possiblement une version plus tolérante
si l'on voulait généraliser à d'autres données.
ex : fuzzy fuzz ou virer les accents, etc.
"""

# Mask des cas problématiques id_acteur vs id_orateur et noms différents
mask_pb_id = (
    df["id_acteur"].notna()
    & df["id_orateur"].notna()
    & (df["id_acteur"] != "PA0")
    & (df["id_orateur"] != "PA0")
    & (df["id_acteur"] != df["id_orateur"])
    & (
        df["nom_orateur"].apply(nettoyer_nom) != df["nom_orateur_clean"]
    )  # nettoyer pour commensurabilité
)
# cols pour affichage diagnostic
cols_check = [
    "id_acteur",
    "id_orateur",
    "nom_orateur",
    "nom_orateur_clean",
    "id_syceron",
]

print("\nSituations problématiques id_acteur vs id_orateur avant correction :\n")
print(df.loc[mask_pb_id, cols_check].sort_values("id_syceron").to_string(index=False))

# Correction : id_acteur <- id_orateur
df.loc[mask_pb_id, "id_acteur"] = df.loc[mask_pb_id, "id_orateur"]
print(f"\nLignes corrigées dans df : {mask_pb_id.sum()}")

# Recalculer le nom plus fréquent après correction des identifiants acteurs.
# = réactualiser (puisqu'on en a modifié, pourrait changer le plus fréquent)
most_frequent_name = calculer_nom_plus_frequent(df)

# et ré-appliquer la récup (= la fonction change pas)
df["nom_orateur_clean"] = df.apply(get_most_frequent_name, axis=1).apply(nettoyer_nom)

print("\nSituations après correction :\n")
print(
    df.loc[mask_pb_id, cols_check]
    .drop_duplicates("id_syceron")
    .sort_values("id_syceron")
    .to_string(index=False)
)


# ========================================================================
# DÉTECTION ET CORRECTION DES ERREURS PROBABLES D'IDENTIFICATION
# (comparaison nom_orateur brut vs nom identifié, via score de similarité fuzzy)
# ========================================================================

# ========== Comparaison nom_orateur brut vs nom_orateur_clean ==========

"""
NOTE : nb traçabilité :
Contrairement au cas précédent id_acteur et id_orateur ne diffèrent pas nécessairement
et donc pas possible de renvoyer au "bon" (si tant est qu'il existe).

Comparaison nom_orateur brut vs nom_orateur_clean via score de similarité fuzzy.
= Repérer les cas où le nom le plus fréquent assigné à un id_acteur
diffère du nom brut de l'intervention -> signe possible d'une erreur d'id_acteur / orateur

Sous le seuil optimisé, on considère qu'il s'agit d'une véritable erreur d'id_acteur / orateur
(et non d'une simple variante du même nom) -> réaffectation à PA0 + surimpression du nom brut.
Illustration des cas rencontrés :
- des interruptions attribuées à l'orateur en cours,
- un PA pour un ensemble de députés qui s'expriment en interruption,
- des erreurs de saisie sur des noms proches / des PA proches (de l'auto completion steno ?)
"""

# ========== identification des cas où l'identification semble erronée/problématique ==========


def normaliser_nom_fuzzy(x):
    if not isinstance(x, str):
        return x
    x = nettoyer_nom(x).lower().strip()
    # retire ponctuation pour éviter de flag juste une virgule/point,
    # mais normalement fait par nettoyer_nom
    x = re.sub(r"[^\w\s'-]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


# Noms normalisés
# pour nom orateur = appliquer aussi le nettoyage standard pour comparabilité
nom_brut_norm = df["nom_orateur"].apply(normaliser_nom_fuzzy)
nom_clean_norm = df["nom_orateur_clean"].apply(normaliser_nom_fuzzy)

# Score fuzzy (0-100)
# utiliser ratio ou WRatio
# car tests avec alternatives token sont problématiques (gros écarts pour juste des accents, etc.)
score_fuzzy = [
    fuzz.ratio(a, b) if isinstance(a, str) and isinstance(b, str) else None
    for a, b in zip(nom_brut_norm, nom_clean_norm)
]
df["score_nom_fuzzy"] = score_fuzzy

# Seuil optimisé après inspection manuelle
# NOTE: à vérifier et adapter si veut généraliser à d'autres données
# ici les deniers cas sont Mme Audrey Dufeu vs Mme Audrey Dufeu Schubert (78.04878048780488)
# et Mme Christine Cloarec vs Mme Christine Le Nabour (77.27272727272727) -> mais bien la même personne
seuil_correction = 77.27272727272727

mask_a_corriger = (
    (df["id_acteur"] != "PA0")
    & nom_brut_norm.notna()
    & nom_clean_norm.notna()
    & (nom_brut_norm != nom_clean_norm)
    & (df["score_nom_fuzzy"] < seuil_correction)
)

# Trace des cas affectés, avant écrasement (si nécessaire)
cols_check_fuzz = cols_check + ["score_nom_fuzzy"]

df.loc[mask_a_corriger, cols_check_fuzz].copy().to_csv(
    "../data/temp/trace_correction_diff_nom.csv", index=False
)

print("\nSituations problématiques nom_orateur vs nom_orateur_clean :")
print("(similarité fuzzy nom_orateur brut vs nom_orateur_clean identifié)")
print(f"Nombre de cas à corriger erreur identification : {mask_a_corriger.sum()}")

# ===== Correction (réaffectation à PA0 + correction nom_orateur_clean) =====
df.loc[mask_a_corriger, "id_acteur"] = "PA0"
df.loc[mask_a_corriger, "nom_orateur_clean"] = df.loc[mask_a_corriger, "nom_orateur"]

print("\nShape du df en sortie : ", df.shape)


# %%
# TODO: syceron 2827575 2827576 2827577 = M. Lionel Tivoli = PA793298
# (alors que ici en neutre non identifié et sous PA0)
# (on s'en cogne vu le nb et doit y en avoir d'autres ?)

# %% [markdown]
# ## 2.2 Match des infos sur les députés (données datan)

# %% [markdown]
# ### 2.2.1 Match des infos générales

# %%
# ==============================
# MATCH DONNÉES DÉPUTÉS
# ==============================

df_deputes = pd.read_csv("../data/raw/id-dep/deputes-historique(datan-datagouv).csv")

# suppression des colonnes non utiles qui introduisent soucis parsing
df_deputes = df_deputes.drop(
    columns=[
        "mail",
        "twitter",
        "facebook",
        "website",
        "active",
        "scoreParticipationSpecialite",
        "datePriseFonction",
        "groupe",
        "naissance",
    ]
)

# ======Fusion des données députés======

print("shape avant fusion:", df.shape)

assert df_deputes["id"].is_unique, "ids du df_deputes non uniques !"

# Merger et virer la col id pour éviter doublon
df = df.merge(
    df_deputes,
    left_on="id_acteur",
    right_on="id",
    how="left",
    suffixes=("", "_dep"),
    validate="many_to_one",  # check if merge keys are unique in right dataset
).drop(columns=["id"])  # supprimer la colonne id du df_deputes

print("shape après fusion données députés:", df.shape)

# %% [markdown]
# ### 2.2.2 Match temporel des affiliations

# %%
# ======================================================
# AFFILIATION PARLEMENTAIRE
# Logique suivie :
# 1. récupérer le groupe a date d'intervention si dispo
#   -> var affiliation_mandat_députés
# 2. ajouter les affiliations gouvernementales
#   -> var affiliation_et_gouv
#   - corriger les données manquantes gouv quand entre des bornes gouv meme jour
# 3. fallback sur dernière affiliation connue (groupe/groupeabrev)
#   -> var affiliation_et_gouv complétée
#   - TODO: actuellement ne recupère plus que 3 et peut être qu'il faut pas les corriger
#   - correction des affil NI/RN
# ======================================================

# %%
# ======================================================
# RECODAGE ET MATCH TEMPOREL DES AFFILIATIONS PARLEMENTAIRES
# cf. affiliation lors de telle prise de parole
# ======================================================


# ========== Recodage des dénominations de groupes ==========
"""
nb : ici choix de recoder avec les principaux noms sur la législature
des groupes parlementaires (objet d'étude), et non nom de parti car 
plus restreint que les cas ici étudiés.
"""

# Lecture du fichier d'affiliation par périodes
df_affiliation = pd.read_csv(
    "../data/raw/id-dep/datan_affiliations.csv", encoding="latin1", sep=";"
)  # format dégueu

# Recodage des groupes parlementaires pour stabilité temporelle des noms
recodage_affiliation = {
    "RE": "LAREM",
    "EPR": "LAREM",
    "MODEM": "DEM",
    "SOC": "SOC-A",
    "NG": "SOC-A",
    "LFI-NUPES": "LFI",
    "FI": "LFI",
    "UDI-AGIR": "UDI",
    "UDI-A-I": "UDI",
    "LC": "UDI",
    "UDI_I": "UDI",
    "UDI-I": "UDI",
    "ECOLO": "ECO",
    "GDR-NUPES": "GDR",
    "LT": "LIOT",
    # Garde pour trace mais pas nécessaire car pas de changement
    # "LIOT": "LIOT",
    # "LR": "LR",
    # "RN": "RN",
    # "LAREM": "LAREM",
    # "MODEM": "MODEM",
    # "LFI": "LFI",
    # "HOR": "HOR",
    # "DEM": "DEM",
}

# Application du recodage des noms de groupes parlementaires au df d'affiliation
df_affiliation["libelleAbrev"] = df_affiliation["libelleAbrev"].astype(str).str.strip()
df_affiliation["parti_recod"] = df_affiliation["libelleAbrev"].replace(
    recodage_affiliation
)

# ========== Match temporel des affiliations ==========

"""
nb : Plutôt qu'un merge foireux, parti sur un lookup ligne à ligne
(= pb des orateurs non députés qui étaient pas présents, etc.)
Le fichier est suffisamment réduit pour que le surplus de calcul soit pas un pb
nb : attention aux bornes temporelles (cf.normalize() pour ignorer l'heure)
"""

# préparation des dates
df["dateSeance_ts"] = pd.to_datetime(
    df["dateSeance"], format="%Y%m%d%H%M%S%f", errors="raise"
)
df_affiliation["dateDebut"] = pd.to_datetime(
    df_affiliation["dateDebut"], errors="raise"
)
df_affiliation["dateFin"] = pd.to_datetime(df_affiliation["dateFin"], errors="raise")
# aviser si jamais besoin un jour de traiter des affiliations encore en cours
# df_affiliation["dateFin"] = df_affiliation["dateFin"].fillna(pd.Timestamp("2100-01-01"))

# indexer par mpId pour lookup rapide
aff_by_mp = {
    mp: g[["dateDebut", "dateFin", "parti_recod"]].to_dict("records")
    for mp, g in df_affiliation.groupby("mpId")
}


# Fonction de recodage temporel des affiliations
def get_parti_for_row(row):
    """
    Retourne l'affiliation partisane recodée correspondant à la date de séance.

    La fonction :
    - lit `id_acteur` (assimilé à `mpId`) et `dateSeance_ts` sur la ligne ;
    - parcourt les périodes d'affiliation de ce député (si présent dans aff_by_mp);
    - renvoie `parti_recod` si `dateSeance_ts` (normalisée au jour) est comprise
    entre `dateDebut` et `dateFin` (bornes incluses).
    """
    mp = row.get("id_acteur")  # correspond au mpId
    # gérer le cas des orateurs non députés ou autre type intervention
    if pd.isna(mp) or mp not in aff_by_mp:
        return None
    # récupérer le ts de l'intervention
    ts = row.get("dateSeance_ts")
    if pd.isna(ts):
        return None
    # retourner l'affiliation qui colle à la date d'intervention
    for rec in aff_by_mp[mp]:
        # attention : .normalize() pour ignorer l'heure car sinon hors des bornes de fin
        if rec["dateDebut"] <= ts.normalize() <= rec["dateFin"]:
            return rec["parti_recod"]
    return None


# application du match temporel
df["affiliation_mandat_députés"] = df.apply(get_parti_for_row, axis=1)

# Pas parfait mais pour avoir une idée :
print(
    "affectés :",
    df["affiliation_mandat_députés"].notna().sum(),
    "| non affectés :",
    df["affiliation_mandat_députés"].isna().sum(),
    "| id_acteur sans affiliation dynamique :",
    df[df["affiliation_mandat_députés"].isna()]["id_acteur"].nunique(),
)


# %% [markdown]
# ### 2.2.3 Ajout des affiliations gouvernementales

# %% [markdown]
# ### Création d'une variable sur-imprimant l'appartenance au gouv

# %%
# =================================================
# CRÉATION VARIABLE AFFILIATION + GOUV
# =================================================
# Ajout des affiliations gouvernementales
# renvoyer les membres du gouv à une catégorie "GOUV" pour les différencier
# le faire avant de forcer les groupeAbrev
# (qui feraient disparaître certains cas limites du gouvernement
# ie : si info affiliation manquante le même jour que d'autres affiliation GOUV)

"""
nb : traçabilité
/!\ ici on veut récup membres du gouv, souvent en sans affiliation
mais on veut aussi forcer leur etiquette gvt même quand ils ont une affiliation de député
(ex : ministre qui est aussi député)

Logique de recodage :
Recoder membres gouv, uniquement si != PA0 (= garder cohérence avec cas précédents)
si une des conditions suivantes est vérifiée,
- ministre -> ok, 96 personnes pour 130 qualités, mais exclure le cas de Justin Trudeau et 19 cas PA0
- garde des sceaux (pas toujours co-qualifié de ministre) : ok, 2 bien Dupond-Moretti / Belloubet (même si 10 PA0)
- secrétaire d’État -> 40 personnes pour 53 qualité correspondantes, OK (2 PA0)
= basé sur la lecture des résultats de :
df["qualite_orateur"].value_counts()

-> mais il faut exclure "Premier ministre du Canada" -> 2 occurences 
Autre option retenue : exclure des PA le PA-107309 = Justin Trudeau, Premier ministre du Canada
"""

# masque condition membres gouvernement
mask_gvt = (
    df["qualite_orateur"].str.contains(
        "ministre|garde des sceaux|secrétaire d[’']État",
        case=False,
        na=False,
        regex=True,
    )
    & (df["id_acteur"] != "PA0")
    & (df["id_acteur"] != "PA-107309")
)  # exclure Justin Trudeau, "Premier ministre du Canada"

# ========== Création nouvelle variable avec GVT ==========
# conserver l'affiliation initiale pour réutilisation future
df["affiliation_et_gouv"] = df["affiliation_mandat_députés"]
# recoder les cas concernés en GOUV
df.loc[mask_gvt, "affiliation_et_gouv"] = "GOUV"

# Vérification des cas affectés recodage GOUV
print("Lignes recodées GOUV :", mask_gvt.sum())
print(
    "Affiliation recodées pour",
    df.loc[mask_gvt, "id_acteur"].nunique(),
    "id_acteur uniques",
)

# %%
# ==========================================================
# RECODAGE CAS LIMITES GOUV :
# valeurs manquantes d'affiliation_et_gouv
# alors que valeurs GOUV le même jour
# ==========================================================

"""nb traçabilité :
Dans notre cas, après vérif manuelle, c'était des ratés
alors qu'on a bien une info gouv le même jour.
On a donc décidé de s'en tenir a cette version stricte.
/!\ D'autres pourraient envisager de recoder aussi les NA
entre une date connue avant et une date connue après,
même si pas le même jour (ex : NA entre 2 dates connues GOUV)
Ici la version conservatrice évite de bourrer des cas limites
de gens qui sortiraient puis reviendraient au gouv
sans que l'on prenne soin de vérifier les périodes.

nb : à appliquer avant de forcer les autres info affiliation dispo dans groupeAbrev (cf. plus bas)
14 cas si on fait l'affiliation gouv après avoir forcé groupeAbrev
67 si c'est bien fait avant == bien FAIRE AVANT !!!
"""

cols_audit = [
    "id_acteur",
    "nom_orateur_clean",
    "dateSeance_ts",
    "affiliation_et_gouv",
    "id_syceron",
]

tmp = df.loc[df["id_acteur"].notna() & (df["id_acteur"] != "PA0"), cols_audit].copy()
tmp = tmp.sort_values(["id_acteur", "dateSeance_ts"]).reset_index(drop=True)
g = tmp.groupby("id_acteur", group_keys=False)

# Valeurs non manquantes les plus proches avant/après
# contre inuitif les ffill et bfill mais c'est ça
tmp["prev_non_na_affil"] = g["affiliation_et_gouv"].ffill()
tmp["next_non_na_affil"] = g["affiliation_et_gouv"].bfill()

# Dates de référence (où affiliation_et_gouv est connue)
tmp["date_affil_connue"] = tmp["dateSeance_ts"].where(
    tmp["affiliation_et_gouv"].notna()
)
tmp["date_connue_avant"] = g["date_affil_connue"].ffill()
tmp["date_connue_apres"] = g["date_affil_connue"].bfill()

# NA entre deux bornes GOUV, même jour que l'une d'elles
# ie : même jour (avec dt.normalize() que la borne avant OU après
mask_a_recoder = (
    tmp["affiliation_et_gouv"].isna()
    & (tmp["prev_non_na_affil"] == "GOUV")
    & (tmp["next_non_na_affil"] == "GOUV")
    & (
        tmp["dateSeance_ts"].dt.normalize().eq(tmp["date_connue_avant"].dt.normalize())
        | tmp["dateSeance_ts"]
        .dt.normalize()
        .eq(tmp["date_connue_apres"].dt.normalize())
    )
)

# recodage dans df principal via id_syceron
ids_a_recoder = tmp.loc[mask_a_recoder, "id_syceron"]
mask_df = df["id_syceron"].isin(ids_a_recoder)
df.loc[mask_df, "affiliation_et_gouv"] = "GOUV"

# mini rapport post recodage
print(f"Lignes recodées GOUV (même jour) : {mask_df.sum()}")
print(f"id_syceron uniques : {df.loc[mask_df, 'id_syceron'].nunique()}")
print(f"id_acteur uniques : {df.loc[mask_df, 'id_acteur'].nunique()}")

print("\nPersonnes concernées :")
print(df.loc[mask_df, "nom_orateur_clean"].unique())

print("\nTop 10 orateurs recodés")
print(df.loc[mask_df, "nom_orateur_clean"].value_counts().head(10))


# %% [markdown]
# ### 2.2.4 Fallback des affiliations manquantes

# %% [markdown]
# #### Forcer le renvoi d'une affiliation si groupeAbrev connu

# %%
# ============================================================
# GESTION AFFILIATIONS MANQUANTES
# - Fallback pour les affiliations manquantes
# - Gestion des cas limites (RN, etc.)
# ============================================================


# %%
# ========= Fallback affiliation manquantes par groupeAbrev ==========

# Ce fallback s'applique désormais à un volume marginal de cas
# suite à la correction et complétion des affiliations (notamment gouvernementales)
# Ici 2 intervenants concernés, donc risque limité.
# Code et masque de diagnostic conservé pour assurer les cas + si le périmètre s'élargit.

# masque pour diagnostic des cas concernés par le fallback groupeAbrev
# (doit le placer avant de faire le combine_first pour avoir l'info)
mask_fallback = df["affiliation_et_gouv"].isna() & df["groupeAbrev"].notna()

# Forcer une affiliation avec le groupe "groupeAbrev" du fichier info députés
df["affiliation_et_gouv"] = df["affiliation_et_gouv"].combine_first(df["groupeAbrev"])
# réutiliser le même recodage que pour les affiliations
df["affiliation_et_gouv"] = df["affiliation_et_gouv"].replace(recodage_affiliation)
# Et gérer les nouvelles dénominations propres groupeAbrev
df["affiliation_et_gouv"] = df["affiliation_et_gouv"].replace(
    {"LES-REP": "LR", "UMP": "LR"}
)


print("=== Cas concernés par le fallback via groupeAbrev ===")
print("Nombre d'interventions concernées :", mask_fallback.sum())
print(
    "Nombre d'id_acteur uniques concernés :",
    df.loc[mask_fallback, "id_acteur"].nunique(dropna=True),
)

print("\nListe des orateurs concernés :")
print(df.loc[mask_fallback, "nom_orateur_clean"].dropna().unique())


# %% [markdown]
# #### Forcer affiliation des RN qui étaient en NI (étaient pas assez pour groupe)

# %%
# ========= Gestion cas limites RN ==========

# Recodage des RN de la XVe législature au bloc RN
# nb = choix = initialement en NI car pas assez nombreux pour former un groupe

liste_NI_RN = [
    "PA720822",  # Bruno Bilde
    "PA720668",  # Sébastien Chenu
    "PA720468",  # Emmanuel Blairy
    "PA720614",  # Marine Le Pen
    "PA719436",  # Nicolas Meizonnet
    "PA720802",  # Catherine Pujol
    "PA719608",  # Emmanuelle Ménard, rattachée au RN entre 2017 et 2022 mais plus entre 2022 et 2024
    "PA720606",  # Ludovic Pajot
    "PA606212",  # Gilbert Collard
    "PA720798",  # Louis Aliot
    "PA720610",  # Myriane Houplain, rattachée au RN entre 2017 et 2022 (Todo resolved car affiliée RN sur période avant de partir Reconquête)
    # TODO : voir si d'autres cas NI/RN ? (cf multi affil)
]

# Date seuil : fin de la 15e législature
date_seuil = pd.Timestamp("2022-06-21")

# Condition combinée :
condition_NI_RN = (df["id_acteur"].isin(liste_NI_RN)) & (
    df["dateSeance_ts"].dt.normalize() < date_seuil
)  # dt.normalize() pour ignorer l'heure et éviter soucis de bornes


# Application de la modalité uniquement pour les lignes correspondant à la condition
df.loc[condition_NI_RN, "affiliation_et_gouv"] = "RN"

# Vérification
print("Lignes recodées RN :", condition_NI_RN.sum())
print(
    "Affiliation recodées pour",
    df.loc[condition_NI_RN, "id_acteur"].nunique(),
    "id_acteur uniques",
)

print("Ceci ne modifie pas nb sans affiliation_et_gouv : simple recodage NI vers RN")


# %%
# Diagnostic des affiliations manquantes
mask_na = df["affiliation_et_gouv"].isna()
na_ids = df.loc[mask_na, "id_acteur"]

print("Interventions restantes sans affiliation :", int(mask_na.sum()))
print(" - dont PA0 :", int((mask_na & df["id_acteur"].eq("PA0")).sum()))
print(" - hors PA0 :", int((mask_na & ~df["id_acteur"].eq("PA0")).sum()))
print(
    "Nombre restant d'id_acteur uniques ayant des affiliations manquantes :",
    na_ids.nunique(dropna=True),
)

# repérage des externes (id_acteur avec '-' = intervenants non-AN)
nb_externes = na_ids.fillna("").str.contains("-", regex=False).sum()
nb_externes_uniques = na_ids[na_ids.fillna("").str.contains("-", regex=False)].nunique()
print(
    f" - dont {nb_externes_uniques} id_acteur unique(s) avec '-' dans PA (probables externes) ({nb_externes} interventions)"
)

# Repérage cas limites PA classiques
mask_na = df["affiliation_et_gouv"].isna()
mask_pa_class = (
    mask_na
    & ~df["id_acteur"].eq("PA0")
    & ~df["id_acteur"].fillna("").str.contains("-", regex=False)
)

print(
    f" - dont {df.loc[mask_pa_class, 'id_acteur'].nunique()} id_acteur unique(s) PA classique sans affiliation"
)
display(
    df.loc[
        mask_pa_class,
        ["id_acteur", "nom_orateur", "nom_orateur_clean", "qualite_orateur"],
    ]
    .value_counts()
    .reset_index()
    .rename(columns={0: "nb_interventions"})
)

# %% [markdown]
# # GESTION DES CAS RESTANTS

# %%
# ==============================================
# TODO: AFFILIATIONS : MATTHIAS EN COURS
# explorer les affiliation manquantes pour identifier les cas limites
# ==============================================

# TODO virer externes si pas tri larmartine
# TODO : virer aussi dans ce cas # ici PA1051 Jean-Paul Delevoye haut-commissaire aux retraites

# %%
# IDENTIFICATION CAS MANQUANTS ET LIMITES AFFILIATION ET GOUV

# Acteurs avec au moins un NA dans affiliation_et_gouv (hors PA0)
restant_affiliation_et_gouv = df[
    (df["affiliation_et_gouv"].isna()) & (df["id_acteur"] != "PA0")
]

# Comptage NA par acteur directement
count_restant_par_acteur = (
    restant_affiliation_et_gouv.groupby(
        ["id_acteur", "nom_orateur_clean"], dropna=False
    )
    .size()
    .reset_index(name="nb_na_interventions")
)

# Répartition NA / renseigné pour ces mêmes acteurs
repartition = (
    df[df["id_acteur"].isin(count_restant_par_acteur["id_acteur"])]
    .groupby("id_acteur")["affiliation_et_gouv"]
    .agg(
        nb_na=lambda s: s.isna().sum(),
        nb_renseigne=lambda s: s.notna().sum(),
    )
    .reset_index()
)

resultat = count_restant_par_acteur.merge(repartition, on="id_acteur").sort_values(
    "nb_renseigne", ascending=False
)

print(f"Nombre d'id_acteur avec au moins un NA : {resultat['id_acteur'].nunique()}")
display(resultat)

resultat.to_csv("../data/temp/count_restant_affiliation_et_gouv.csv", index=False)


# %%
# IDEM AVEC QUALITÉ ORATEUR

# IDENTIFICATION CAS MANQUANTS ET LIMITES AFFILIATION ET GOUV

# Acteurs avec au moins un NA dans affiliation_et_gouv (hors PA0)
restant_affiliation_et_gouv = df[
    (df["affiliation_et_gouv"].isna()) & (df["id_acteur"] != "PA0")
]

# Comptage NA par acteur directement
count_restant_par_acteur = (
    restant_affiliation_et_gouv.groupby(
        ["id_acteur", "nom_orateur_clean", "qualite_orateur"], dropna=False
    )
    .size()
    .reset_index(name="nb_na_interventions")
)

# Répartition NA / renseigné pour ces mêmes acteurs
repartition = (
    df[df["id_acteur"].isin(count_restant_par_acteur["id_acteur"])]
    .groupby("id_acteur")["affiliation_et_gouv"]
    .agg(
        nb_na=lambda s: s.isna().sum(),
        nb_renseigne=lambda s: s.notna().sum(),
    )
    .reset_index()
)

resultat = count_restant_par_acteur.merge(repartition, on="id_acteur").sort_values(
    "nb_renseigne", ascending=False
)

print(f"Nombre d'id_acteur avec au moins un NA : {resultat['id_acteur'].nunique()}")
display(resultat)

resultat.to_csv(
    "../data/temp/count_restant_qualite_affiliation_et_gouv.csv", index=False
)


# %% [markdown]
# ##### LES SOUCIS POSSIBLES multi affil:
#

# %%
# Cas où un même id_acteur a plusieurs valeurs différentes de affiliation_et_gouv
tmp = df[["id_acteur", "nom_orateur_clean", "affiliation_et_gouv"]].copy()
tmp["affiliation_et_gouv_norm"] = tmp["affiliation_et_gouv"].fillna("<<NA>>")

# ids avec au moins 2 modalités différentes (en comptant NA)
ids_multi_affil = (
    tmp.groupby("id_acteur")["affiliation_et_gouv_norm"]
    .nunique()
    .loc[lambda s: s > 1]
    .index
)
cas_diff = tmp[tmp["id_acteur"].isin(ids_multi_affil)].copy()

print(
    "Nombre d'id_acteur avec plusieurs valeurs de affiliation_et_gouv :",
    len(ids_multi_affil),
)
print("Nombre total de lignes concernées :", len(cas_diff))

cas_multi_affil = (
    cas_diff.groupby(["id_acteur", "nom_orateur_clean"])["affiliation_et_gouv_norm"]
    .agg(lambda x: sorted(set(x)))
    .reset_index(name="valeurs_affiliation_et_gouv")
    .sort_values(["nom_orateur_clean", "id_acteur"])
)
display(cas_multi_affil)
cas_multi_affil.to_csv("../data/temp/cas_multi_affiliation_et_gouv.csv", index=False)

# %% [markdown]
# ##### LES SOUCIS POSSIBLES AVEC MEMBRES GOUV :

# %%
# CAS LIMITE GOUV :
# ORATEURS AVEC AFFIL = GOUV + AUTRE CHOSE : identification + comptage des interventions

# LOGIQUE :
# - RENVOYER LES CAS OU AFFIL = GOUV + AUTRE CHOSE
# - identification orateurs et combinaison d'affiliations
# - comptage des interventions

# Interventions des orateurs qui ont plusieurs affiliations dont GVT

# 1) Ne garder que les lignes avec affiliation renseignée
temp = df.loc[
    df["affiliation_et_gouv"].notna(),
    ["id_acteur", "nom_orateur_clean", "affiliation_et_gouv"],
].copy()
# (ça ici permet les cas sans affil forcée, mais marcherait aussi si on fait
# juste après l'affil dynamique pour pas rater les cas)
temp["affiliation_et_gouv_norm"] = temp["affiliation_et_gouv"].fillna("<<NA>>")

# 2) Profils d'affiliation par id_acteur → garder ceux avec affiliations multiples dont GOUV
affil_par_id = temp.groupby("id_acteur")["affiliation_et_gouv_norm"].agg(
    lambda s: sorted(set(s.astype(str)))
)
ids_multi_avec_gvt = affil_par_id[
    affil_par_id.apply(lambda x: len(x) > 1 and "GOUV" in x)
].index

# 3) Comptage GOUV vs AUTRE par orateur
subset = temp[temp["id_acteur"].isin(ids_multi_avec_gvt)].copy()
subset["type_intervention"] = (
    subset["affiliation_et_gouv"].eq("GOUV").map({True: "GOUV", False: "AUTRE"})
)

counts = subset["type_intervention"].value_counts()
nb_gouv = int(counts.get("GOUV", 0))
nb_autre = int(counts.get("AUTRE", 0))
print(f"Interventions comme membre du gouv : {nb_gouv}")
print(f"Interventions dans les autres cas  : {nb_autre}")
print(f"Total                              : {nb_gouv + nb_autre}")

# 4) Tableau fusionné : comptages + affiliations
par_orateur = (
    subset.groupby(["id_acteur", "nom_orateur_clean", "type_intervention"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
par_orateur["TOTAL"] = par_orateur.get("GOUV", 0) + par_orateur.get("AUTRE", 0)

affiliations = (
    subset.groupby(["id_acteur", "nom_orateur_clean"])["affiliation_et_gouv_norm"]
    .agg(lambda s: sorted(set(s.astype(str))))
    .reset_index(name="affiliations")
)

membres_gouv_multi_affil = par_orateur.merge(
    affiliations, on=["id_acteur", "nom_orateur_clean"]
).sort_values("TOTAL", ascending=False)
print(
    f"\nNombre d'orateurs avec affiliations multiples dont GOUV : {len(membres_gouv_multi_affil)}"
)
display(membres_gouv_multi_affil)

membres_gouv_multi_affil.to_csv(
    "../data/temp/membres_gouv_multi_affil.csv", index=False
)


# %%
# NOTE: Désormais géré directement depuis extraction
mask_congres = df["session"].str.contains("Congrès du Parlement", case=False, na=False)

print("Présence de 'Congrès du Parlement' dans session :", mask_congres.any())
print("Nombre de lignes concernées :", int(mask_congres.sum()))

# Optionnel : voir les valeurs de session concernées
if mask_congres.any():
    print("\nValeurs des sessions concernées :")
    print(df.loc[mask_congres, "session"].value_counts())  # Trucs Matthias


# %% [markdown]
# ## Export

# %%
# Export du csv nettoyé
df.to_csv("../data/interim/data_cleaning_full.csv", index=False)

# # NB: certaines col du df_deputes introduisent une erreur à l'import/export
# # Elles ne sont pas utilisées ici, mais si besoin de les utiliser
# # forcer le QUOTE_ALL permet de résoudre
# # (cf : adresses et réseaux sociaux contenant saut de lignes = erreurs de parsing (cas eric.martineau))

# %% [markdown]
# # EXPLORATION

# %%
df["id_acteur"].str.contains("-").sum()

# %%
df_externe = df[df["id_acteur"].str.contains("-", regex=False, na=False)].copy()
df_externe

# %%
resume_externes = (
    df_externe.groupby("id_acteur", dropna=False)
    .agg(
        id_orateur=(
            "id_orateur",
            lambda s: ", ".join(sorted(set(s.dropna().astype(str)))),
        ),
        nom_orateur=(
            "nom_orateur",
            lambda s: ", ".join(sorted(set(s.dropna().astype(str)))),
        ),
        nom_orateur_clean=(
            "nom_orateur_clean",
            lambda s: ", ".join(sorted(set(s.dropna().astype(str)))),
        ),
        qualite_orateur=(
            "qualite_orateur",
            lambda s: ", ".join(sorted(set(s.dropna().astype(str)))),
        ),
        nb_interventions=("id_syceron", "count"),
    )
    .reset_index()
    .sort_values("nb_interventions", ascending=False)
)

display(resume_externes)

# %%
df[
    (df["id_mandat"] == "-1")
    & (df["affiliation_et_gouv"] != "GOUV")
    & (df["id_acteur"] != "PA0")
]["nom_orateur_clean"].value_counts().head(50)

# %%
df[  # (df["id_mandat"] == "-1") &
    (df["affiliation_et_gouv"] != "GOUV")
    & (df["id_acteur"] != "PA0")
    & (df["affiliation_et_gouv"].isna())
]["nom_orateur_clean"].value_counts().head(20)

# %%
