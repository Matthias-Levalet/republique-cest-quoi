# %% [markdown]
# # 2-4 - Affiliations parlementaires et gouvernementales
# Lit `2_3_match_deputes.csv` (issu de 2-3). Logique suivie :
# 1. récupérer le groupe à la date d'intervention si dispo
#    -> var affiliation_mandat_députés
# 2. ajouter les affiliations gouvernementales
#    -> var affiliation_et_gouv
#    - corriger les données manquantes gouv quand entre des bornes gouv même jour
# 3. fallback sur dernière affiliation connue (groupe/groupeAbrev)
#    -> var affiliation_et_gouv complétée
#    - correction des affiliations NI/RN
# Écrit `data_cleaning_full.csv`, l'export final du pipeline de nettoyage.

# %%
import pandas as pd
from IPython.display import display  # ruff casse les pieds

PATH_ENTREE = "../data/interim/2_3_match_deputes.csv"
PATH_AFFILIATIONS = "../data/raw/id-dep/datan_affiliations.csv"
PATH_SORTIE = "../data/interim/2_4_interventions_nettoyees.csv"


# nb : ici choix de recoder avec les principaux noms sur la législature des
# groupes parlementaires (objet d'étude), et non nom de parti car plus
# restreint que les cas ici étudiés.
RECODAGE_AFFILIATION = {
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
}

RECODAGE_GROUPE_ABREV = {"LES-REP": "LR", "UMP": "LR"}

REGEX_QUALITE_GOUV = r"ministre|garde des sceaux|secrétaire d[’']État"
ID_ACTEUR_JUSTIN_TRUDEAU = (
    "PA-107309"  # "Premier ministre du Canada", à exclure du GOUV
)

# RN de la XVe législature initialement classés NI (pas assez nombreux pour un groupe)
LISTE_NI_RN = [
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

DATE_SEUIL_FIN_15E_LEGISLATURE = "2022-06-21"

# %%
df = pd.read_csv(PATH_ENTREE, low_memory=False, dtype={"id_orateur": str})
print("Shape du df chargé : ", df.shape)

# %% [markdown]
# ## Match temporel des affiliations parlementaires
# nb : plutôt qu'un merge foireux (pb des orateurs non députés absents,
# etc.), on part sur un lookup ligne à ligne. Le fichier est suffisamment
# réduit pour que le surplus de calcul ne soit pas un problème.
# nb : attention aux bornes temporelles (cf. .normalize() pour ignorer l'heure).

# %%
# ======================================================
# RECODAGE ET MATCH TEMPOREL DES AFFILIATIONS PARLEMENTAIRES
# cf. affiliation lors de telle prise de parole
# ======================================================


# ========== Recodage des dénominations de groupes ==========

df_affiliation = pd.read_csv(
    PATH_AFFILIATIONS, encoding="latin1", sep=";"
)  # format dégueu

# ========== Match temporel des affiliations ==========

# préparation des dates
df_affiliation["libelleAbrev"] = df_affiliation["libelleAbrev"].astype(str).str.strip()
df_affiliation["parti_recod"] = df_affiliation["libelleAbrev"].replace(
    RECODAGE_AFFILIATION
)

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
    Parcourt les périodes d'affiliation du député (si présent dans aff_by_mp)
    et renvoie parti_recod si dateSeance_ts (normalisée au jour) est comprise
    entre dateDebut et dateFin (bornes incluses).
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
# ## Ajout des affiliations gouvernementales
# nb : on récupère les membres du gouv (souvent sans affiliation) mais on
# force aussi leur étiquette gouv même quand ils ont une affiliation de
# député (ex : ministre qui est aussi député). À faire avant de forcer
# groupeAbrev (qui ferait disparaître certains cas limites du gouvernement).
# Logique de recodage : ministre / garde des sceaux / secrétaire d'État,
# uniquement si id_acteur != PA0. Exclusion de Justin Trudeau
# ("Premier ministre du Canada", pas un cas français à recoder GOUV).

# %%
# =================================================
# CRÉATION VARIABLE AFFILIATION + GOUV
# =================================================

# masque condition membres gouvernement
mask_gvt = (
    df["qualite_orateur"].str.contains(
        REGEX_QUALITE_GOUV, case=False, na=False, regex=True
    )
    & (df["id_acteur"] != "PA0")
    & (df["id_acteur"] != ID_ACTEUR_JUSTIN_TRUDEAU)
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

# %% [markdown]
# ### Recodage des cas limites GOUV : NA le même jour qu'une affiliation GOUV
# nb : après vérif manuelle, c'était des ratés alors qu'on a bien une info
# gouv le même jour. Version conservatrice retenue : on ne comble pas les NA
# entre deux dates GOUV connues si elles ne sont pas le même jour.
# /!\ à appliquer avant de forcer groupeAbrev (14 cas après vs 67 avant = bien FAIRE AVANT).

# %%
# ==========================================================
# RECODAGE CAS LIMITES GOUV :
# valeurs manquantes d'affiliation_et_gouv
# alors que valeurs GOUV le même jour
# ==========================================================

# TODO : décider si on veut recoder les cas limites GOUV sur plusieurs jours
# (ex : 1 jour avant et 1 jour après ou plus)
# ie si on veut quelque chose de moins conservateur

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

# Valeurs non manquantes les plus proches avant/après (contre-intuitif : ffill/bfill inversés)
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
# ## Fallback des affiliations manquantes
# Volume marginal après correction des affiliations gouvernementales.
# Diagnostic conservé pour surveiller le périmètre si les données évoluent.

# %%
# ============================================================
# GESTION AFFILIATIONS MANQUANTES
# - Fallback pour les affiliations manquantes
# - Gestion des cas limites (RN, etc.)
# ============================================================

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
df["affiliation_et_gouv"] = df["affiliation_et_gouv"].replace(RECODAGE_AFFILIATION)
# Et gérer les nouvelles dénominations propres groupeAbrev
df["affiliation_et_gouv"] = df["affiliation_et_gouv"].replace(RECODAGE_GROUPE_ABREV)

print("\n=== Cas concernés par le fallback via groupeAbrev ===")
print("Nombre d'interventions concernées :", mask_fallback.sum())
print(
    "Nombre d'id_acteur uniques concernés :",
    df.loc[mask_fallback, "id_acteur"].nunique(dropna=True),
)
print("Liste des orateurs concernés :")
print(df.loc[mask_fallback, "nom_orateur_clean"].dropna().unique())

# %% [markdown]
# ## Cas limites RN (XVe législature, initialement classés NI)
# nb : ces députés RN étaient trop peu nombreux pour former un groupe et
# ont donc été enregistrés en NI ; on les recode explicitement en RN avant
# la fin de la 15e législature.

# %%
# ========= Gestion cas limites RN ==========

# Recodage des RN de la XVe législature au bloc RN
# nb = choix = initialement en NI car pas assez nombreux pour former un groupe

condition_NI_RN = (df["id_acteur"].isin(LISTE_NI_RN)) & (
    df["dateSeance_ts"].dt.normalize() < pd.Timestamp(DATE_SEUIL_FIN_15E_LEGISLATURE)
)  # dt.normalize() pour ignorer l'heure et éviter soucis de bornes

df.loc[condition_NI_RN, "affiliation_et_gouv"] = "RN"

print("\nLignes recodées RN :", condition_NI_RN.sum())
print(
    "Affiliation recodées pour",
    df.loc[condition_NI_RN, "id_acteur"].nunique(),
    "id_acteur uniques",
)
print("Ceci ne modifie pas le nb sans affiliation_et_gouv : simple recodage NI vers RN")

# %% [markdown]
# ## Diagnostic des affiliations manquantes restantes

# %%
# ========== Diagnostic des affiliations manquantes ==========

mask_na = df["affiliation_et_gouv"].isna()
na_ids = df.loc[mask_na, "id_acteur"]

print("\nInterventions restantes sans affiliation :", int(mask_na.sum()))
print(" - dont PA0 :", int((mask_na & df["id_acteur"].eq("PA0")).sum()))
print(" - hors PA0 :", int((mask_na & ~df["id_acteur"].eq("PA0")).sum()))
print(
    "Nombre restant d'id_acteur uniques ayant des affiliations manquantes :",
    na_ids.nunique(dropna=True),
)

# repérage des (propables) externes (id_acteur avec '-' = intervenants non-AN)
nb_externes = na_ids.fillna("").str.contains("-", regex=False).sum()
nb_externes_uniques = na_ids[na_ids.fillna("").str.contains("-", regex=False)].nunique()
print(
    f" - dont {nb_externes_uniques} id_acteur unique(s) avec '-' dans PA (probables externes) ({nb_externes} interventions)"
)

# Repérage cas limites PA classiques
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
# ## Export

# %%
df.to_csv(PATH_SORTIE, index=False)
print("Export vers :", PATH_SORTIE)

# NB : certaines colonnes de df_deputes introduisent une erreur à l'import/export
# (adresses/réseaux sociaux contenant des sauts de ligne). Non utilisées ici,
# mais si besoin : forcer QUOTE_ALL au to_csv résout le problème.

# TODO : check des derniers cas sans affil
# TODO : possible exclusion des externes + PA1051 (ancien dep mais externe)
