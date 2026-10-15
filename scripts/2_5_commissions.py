# %% [markdown]
# # 2-5 - Mandats en commission
# Lit `2_4_affiliations.csv` (issu de 2_4).
# Associe à chaque intervention la commission du député à cette date
# (colonnes suffixées `_commission`), sur le même principe que le
# match temporel des affiliations en 2_4.
#
# Différence clé avec 2_4 : un député n'a qu'un groupe à la fois, mais peut
# siéger dans plusieurs organes en même temps en cas de prise en compte des
# COMPER + DELEGBUREAU et aussi devoir gérer multi statut dans le même organe
# (ex. COMPER : membre + président).
# Quand plusieurs mandats sont actifs le même jour, leurs valeurs sont
# concaténées avec " | " et `nb_mandats_consideres` donne leur nombre.
#
# Écrit `2_5_interventions_infos.csv`, l'export final du pipeline de nettoyage et d'ajout des infos députés.


# %%
import pandas as pd

PATH_ENTREE = "../data/interim/2_4_affiliations.csv"
PATH_COMMISSIONS_MANDATS = "../data/raw/id-dep/datan_mandats.csv"
PATH_SORTIE = "../data/interim/2_5_interventions_infos.csv"

COL_ID_MP = "mpId"  # clé du député dans le fichier de mandats

# Colonnes du fichier de mandats à rattacher à chaque intervention
COLS_COMMISSION = [
    "typeOrgane",
    "codeQualite",
    "organeRef",
    "libelle",
    "libelleAbrev",
    "libelleAbrege",
]
SUFFIXE_COMMISSION = "_commission"
SEPARATEUR_MULTI = " | "

# Types d'organes retenus (None = tous).
# DELEGBUREAU = délégations, cumulables avec une commission :
# ajouter ici produira des valeurs multiples "A | B"
TYPES_ORGANE_RETENUS = ["COMPER"]  # , "DELEGBUREAU"]
# TODO pour l'instant que COMPER, aviser matthias

# Qualités du plus au moins élevé : sert à choisir, pour une même commission,
# l'enregistrement conservé quand plusieurs sont actifs le même jour.
# (choix à ajuster ; une qualité absente de la liste passe en dernier)
# TODO: vérifier l'ordre et notamment place de "Rapporteur général" vs VP, etc.
# (mais si tout va bien devrait être cumulé que avec membre, ou très rare.)
ORDRE_QUALITE = [
    "Président",
    "Rapporteur général",
    "Vice-Président",
    "Secrétaire",
    "Membre",
]

# %%
# TODO : normalement ok à ce stade pour id_orateur (PA a été ajouté)
df = pd.read_csv(PATH_ENTREE, low_memory=False, dtype={"id_orateur": str})
print("Shape du df chargé : ", df.shape)

# %% [markdown]
# ## Chargement et préparation des mandats

# %%
# ======================================================
# CHARGEMENT DES MANDATS EN COMMISSION
# ======================================================

df_mandats = pd.read_csv(
    PATH_COMMISSIONS_MANDATS, low_memory=False, encoding="latin1", sep=";"
)  # format dégueu
print("Shape du fichier de mandats : ", df_mandats.shape)

print("\nRépartition de typeOrgane :")
print(df_mandats["typeOrgane"].value_counts(dropna=False))

if TYPES_ORGANE_RETENUS is not None:
    df_mandats = df_mandats[df_mandats["typeOrgane"].isin(TYPES_ORGANE_RETENUS)].copy()
    print(f"\nMandats retenus (typeOrgane {TYPES_ORGANE_RETENUS}) :", len(df_mandats))

# préparation des dates df_mandats
df_mandats["dateDebut"] = pd.to_datetime(df_mandats["dateDebut"], errors="raise")
df_mandats["dateFin"] = pd.to_datetime(df_mandats["dateFin"], errors="raise")
print(
    "Mandats sans dateDebut (jamais matchables) :", df_mandats["dateDebut"].isna().sum()
)
sans_fin = df_mandats["dateFin"].isna()
repartition_sans_fin = df_mandats.loc[sans_fin, "typeOrgane"].value_counts()
detail_sans_fin = ", ".join(f"{n} {t}" for t, n in repartition_sans_fin.items())
print(
    f"Mandats sans dateFin : {int(sans_fin.sum())}"
    + (f" (dont {detail_sans_fin})" if sans_fin.any() else "")
)

# vérification des qualités (si on les a bien dans notre liste, sinon classées en dernier)
qualites_inconnues = set(df_mandats["codeQualite"].dropna()) - set(ORDRE_QUALITE)
if qualites_inconnues:
    print(
        "/!\\ codeQualite absents de ORDRE_QUALITE (classés en dernier) :",
        qualites_inconnues,
    )

# %% [markdown]
# ## Fermeture des mandats sans dateFin
# ie : un mandat sans dateFin n'est pas "éternel" : la comparaison avec NaT
# serait toujours fausse (jamais matché), et le prolonger indéfiniment peut
# créer de fausses appartenances simultanées.
# Distinction ici des cas COMPER et DELEGBUREAU.

# %%
# ======================================================
# FERMETURE ET NETTOYAGE DES MANDATS SANS DATEFIN
# NOTE : logique valable pour les commissions permanentes (COMPER) :
# un député ne siège que dans une commission permanente à la fois, donc un mandat
# sans dateFin est fermé au début de la commission suivante (même typeOrgane,
# autre organeRef) ou, à défaut, à la fin de la législature.
#
# NOTE: Ne convient possiblement pas directement aux DELEGBUREAU.
# Pas de DELEGBUREAU sans date de fin dans nos donénes, mais si jamais :
# si on peut avoir plusieurs délégations en parallèle, un mandat serait
# alors fermé trop tôt.
# Pour l'instant ajout d'une option TYPE_FERMETURE = "COMPER"
# pour ne pas fermer les mandats DELEGBUREAU (ou autres) par défaut.
# (sécurité si DELEGBUREAU est ajouté à TYPES_ORGANE_RETENUS)
#
# TODO: aviser matthias + check si j'ai la bonne règle aussi pour COMPER
# ======================================================

# TODO: modifier et affiner si on ajoute DELEGBUREAU = quelles règles cumuls ?

TYPE_FERMETURE = "COMPER"  # fermeture par "commission suivante" valable seulement ici


# fonction pour fermer les mandats ouverts (dateFin manquante) selon TYPE_FERMETURE retenu
def fermer_mandats_ouverts(df_m):
    """Renvoie une copie de df_m dont les dateFin manquantes sont fermées, et le journal des fermetures."""
    df_m = df_m.copy()
    fin_legislature = df_m.groupby("legislature")["dateFin"].max()
    journal = []

    ouverts = df_m.index[
        df_m["dateFin"].isna() & (df_m["typeOrgane"] == TYPE_FERMETURE)
    ]
    for i in ouverts:
        m = df_m.loc[i]
        borne, raison = fin_legislature[m["legislature"]], "fin de législature"

        suivantes = df_m.loc[
            (df_m[COL_ID_MP] == m[COL_ID_MP])
            & (df_m["typeOrgane"] == m["typeOrgane"])
            & (df_m["organeRef"] != m["organeRef"])
            & (df_m["legislature"] == m["legislature"])
            & (df_m["dateDebut"] > m["dateDebut"]),
            "dateDebut",
        ]
        if len(suivantes) and suivantes.min() < borne:
            borne, raison = suivantes.min(), "début d'une autre commission"

        df_m.loc[i, "dateFin"] = borne
        journal.append(
            {
                COL_ID_MP: m[COL_ID_MP],
                "libelleAbrev": m["libelleAbrev"],
                "dateDebut": m["dateDebut"].date(),
                "dateFin_attribuee": borne.date(),
                "raison": raison,
            }
        )
    return df_m, pd.DataFrame(journal)


# Appliquer la fermeture des mandats ouverts
df_mandats, journal_fermetures = fermer_mandats_ouverts(df_mandats)

# ================================
# Diagnostic journal de fermeture
# ================================

print(f"Mandats sans dateFin fermés : {len(journal_fermetures)}")
if len(journal_fermetures):
    print(journal_fermetures["raison"].value_counts().to_string())
    print("\nDétail (à vérifier) :")
    print(journal_fermetures.to_string(index=False))

# vérification des cas restants
# (notamment si TYPES_ORGANE_RETENUS diffère de TYPE_FERMETURE, ex. DELEGBUREAU)
restants = df_mandats["dateFin"].isna()
if restants.any():
    print(
        f"/!\\ {restants.sum()} mandat(s) sans dateFin non fermés "
        f"(typeOrgane : {df_mandats.loc[restants, 'typeOrgane'].unique().tolist()}) :"
        " jamais actifs tant qu'ils restent sans dateFin."
    )

# # Si besoin, nuclear bouton pour forcer les restants à la date de fin max du fichier
# # (ie législature en cours)
# # NOTE: peut convenir dans le cas DELGBUREAU, mais pas forcément pour COMPER
# date_fin_max = df_mandats["dateFin"].max()
# df_mandats.loc[restants, "dateFin"] = date_fin_max
# print(
#     f"\nMandats forcés à la dateFin max du fichier ({date_fin_max.date()}) : {int(restants.sum())}"
# )
# if restants.any():
#     print(df_mandats.loc[restants, "typeOrgane"].value_counts().to_string())


# %% [markdown]
# ## Match temporel des mandats
# nb : même logique qu'en 2_4 (lookup par député, bornes incluses,
# .normalize() pour ignorer l'heure), avec une adaptation : le calcul se fait
# par couple unique (id_acteur, jour) puis est rapporté aux interventions (un
# même député intervient souvent plusieurs fois le même jour).
# Pour un jour donné on garde UNE ligne par commission (la qualité la plus
# élevée (membre vs président par ex)).
# Si plusieurs mandats (commission + deleg bureau, cas limites multi commission ?),
# ils sont alors concaténés avec " | ".

# %%
# ============================================================
# MATCH TEMPOREL DES MANDATS EN COMMISSION
# Gestion possible des multi qualités et multi mandats
# (cf. si prend COMPER + DELEGBUREAU dans TYPES_ORGANE_RETENUS
# ============================================================

# prépa dates df originel (plus haut pour df_mandats)
df["dateSeance_ts"] = pd.to_datetime(
    df["dateSeance"], format="%Y%m%d%H%M%S%f", errors="raise"
)
# attention : .normalize() pour ignorer l'heure car sinon hors des bornes de fin
df["date_seance_jour"] = df["dateSeance_ts"].dt.normalize()

rang_qualite = {q: i for i, q in enumerate(ORDRE_QUALITE)}
df_mandats["_rang_qualite"] = (
    df_mandats["codeQualite"].map(rang_qualite).fillna(len(ORDRE_QUALITE))
)

# indexer par député pour lookup rapide
mandats_by_mp = {
    mp: g.sort_values(["dateDebut", "organeRef"])[
        ["dateDebut", "dateFin", "_rang_qualite"] + COLS_COMMISSION
    ].to_dict("records")
    for mp, g in df_mandats.groupby(COL_ID_MP)
}


# ========== Match temporel des mandats commission ==========


# fonction de récupération temporelle des mandats commission (le jour donné)
def get_mandats_actifs(mp, jour):
    """
    Retourne la liste des mandats du député `mp` actifs le jour `jour`
    (dateDebut <= jour <= dateFin, bornes incluses). Liste vide si le
    député est absent du fichier (non député, PA0...) ou si l'identifiant
    ou la date sont manquants.
    """
    if pd.isna(mp) or pd.isna(jour) or mp not in mandats_by_mp:
        return []
    return [
        rec for rec in mandats_by_mp[mp] if rec["dateDebut"] <= jour <= rec["dateFin"]
    ]


# fonction agrégation des mandats (si plusieurs qualités ou mandats (COMPER + DELEGBUREAU))
def agreger_mandats(mandats):
    """
    Réduit les mandats actifs à une ligne par commission (celle à la qualité
    la plus élevée), puis les transforme en colonnes `<col>_commission` et
    `nb_mandats_consideres` (permet vérif erreur commission ou si mutli si on
    veut prendre en compte DELEGBUREAU).
    S'il y a plusieurs mandats (COMPER, DELEGBUREAU), les valeurs sont
    concaténées avec SEPARATEUR_MULTI.
    Valeur manquante -> chaîne vide, pour garder l'alignement.
    Sans mandat actif : None et 0.
    """
    par_organe = {}
    # tri stable : à qualité égale, on garde l'enregistrement le plus ancien
    for m in sorted(mandats, key=lambda m: m["_rang_qualite"]):
        par_organe.setdefault(str(m["organeRef"]), m)
    commissions = sorted(
        par_organe.values(), key=lambda m: (m["dateDebut"], str(m["organeRef"]))
    )

    resultat = {"nb_mandats_consideres": len(commissions)}
    for col in COLS_COMMISSION:
        if commissions:
            resultat[col + SUFFIXE_COMMISSION] = SEPARATEUR_MULTI.join(
                "" if pd.isna(m[col]) else str(m[col]) for m in commissions
            )
        else:
            resultat[col + SUFFIXE_COMMISSION] = None
    return resultat


# calcul sur les couples uniques (id_acteur, jour), puis rattachement au df
paires = df[["id_acteur", "date_seance_jour"]].drop_duplicates().reset_index(drop=True)
print(
    f"Couples (id_acteur, jour) uniques : {len(paires)} (pour {len(df)} interventions)"
)

resultats = pd.DataFrame(
    [
        agreger_mandats(get_mandats_actifs(mp, jour))
        for mp, jour in zip(paires["id_acteur"], paires["date_seance_jour"])
    ]
)
paires = pd.concat([paires, resultats], axis=1)

n_avant = len(df)
df = df.merge(
    paires, on=["id_acteur", "date_seance_jour"], how="left", validate="many_to_one"
)
assert len(df) == n_avant, "Le rattachement a modifié le nombre de lignes !"
df = df.drop(columns=["date_seance_jour"])

# %% [markdown]
# ## Diagnostic mandats en commission (et plus si DELEGBUREAU pris en compte)

# %%
# ============================================================
# DIAGNOSTICS SUR LES MANDATS EN COMMISSION
# (+ DELEGBUREAU SI PRIS EN COMPTE)
# ============================================================

# ========== Diagnostics des cas multi qualité (avant gestion par fonction agreger_mandats) ==========

print("\nDiagnostics multi qualité (avant gestion fonctions `agreger_mandats` : \n")
cumuls = []
for mp, jour in zip(paires["id_acteur"], paires["date_seance_jour"]):
    par_organe = {}
    for m in get_mandats_actifs(mp, jour):
        par_organe.setdefault(str(m["organeRef"]), []).append(m)
    for organe, recs in par_organe.items():
        if len(recs) > 1:
            cumuls.append(
                {
                    "id_acteur": mp,
                    "jour": jour.date(),
                    "organeRef": organe,
                    "n_mandats": len(recs),
                    "qualites": " + ".join(sorted(str(r["codeQualite"]) for r in recs)),
                }
            )

df_cumuls = pd.DataFrame(cumuls)
print(f"{len(df_cumuls)} cas (acteur, jour, commission) avec plusieurs mandats actifs")

print(f"{df_cumuls['id_acteur'].nunique()} id_acteur (PA) uniques concernés")

# acteurs et jours concernés par combinaison
print("\nPar combinaison (nb de cas, d'acteurs, de commissions) :")
print(
    df_cumuls.groupby("qualites")
    .agg(
        n_cas=("id_acteur", "size"),
        n_acteurs=("id_acteur", "nunique"),
        n_commissions=("organeRef", "nunique"),
    )
    .sort_values("n_cas", ascending=False)
    .to_string()
)

# noms pour lisibilité
noms = df.drop_duplicates("id_acteur").set_index("id_acteur")["nom_orateur_clean"]
df_cumuls["nom"] = df_cumuls["id_acteur"].map(noms)

# exemples : 3 par combinaison (un par acteur différent)
print("\nExemples par combinaison :")
print(
    df_cumuls.drop_duplicates(["qualites", "id_acteur"])
    .groupby("qualites")
    .head(3)
    .sort_values(["qualites", "id_acteur"])[
        ["qualites", "id_acteur", "nom", "organeRef", "jour"]
    ]
    .to_string(index=False)
)


# ========== Diagnostics final des mandats en commission ==========

print("\nDiagnostics final des mandats en commission (post traitements) : \n")

a_une_commission = df["nb_mandats_consideres"] > 0
ids_dans_fichier = df["id_acteur"].isin(mandats_by_mp.keys())
est_gouv = df["affiliation_et_gouv"].eq("GOUV")  # NaN -> False

print(
    "Interventions avec un mandat (commission, deleg si pris en compte) :",
    int(a_une_commission.sum()),
)
print(
    " - dont plusieurs le même jour (attendu : si DELEGBUREAU pris en compte) :",
    int((df["nb_mandats_consideres"] > 1).sum()),
)
print(
    "Interventions sans mandat (commission, deleg si pris en compte) :",
    int((~a_une_commission).sum()),
)
print(
    " - dont membres du GOUV (attendu : pas de commission) :",
    int((~a_une_commission & est_gouv).sum()),
)
print(
    " - dont membres du GOUV présents dans le fichier de mandats (= élus par ailleurs):",
    int((~a_une_commission & ids_dans_fichier & est_gouv).sum()),
    f"({df.loc[~a_une_commission & ids_dans_fichier & est_gouv, 'id_acteur'].nunique()} id_acteur uniques)",
)
print(
    " - dont id_acteur absent du fichier de mandats (hors GOUV, attendu : PA0, externes)) :",
    int((~a_une_commission & ~ids_dans_fichier & ~est_gouv).sum()),
)
print(
    " - (VRAI CAS LIMITE) dont id_acteur présent dans le fichier mais sans mandat à la date (hors GOUV) :",
    int((~a_une_commission & ids_dans_fichier & ~est_gouv).sum()),
    f"({df.loc[~a_une_commission & ids_dans_fichier & ~est_gouv, 'id_acteur'].nunique()} id_acteur uniques)",
)

print("\nExemples de plusieurs mandats le même jour :")
print(
    df.loc[
        df["nb_mandats_consideres"] > 1,
        ["id_acteur", "nom_orateur_clean", "dateSeance_ts", "libelleAbrev_commission"],
    ]
    .drop_duplicates(["id_acteur", "libelleAbrev_commission"])
    .head(10)
    .to_string(index=False)
)


# %% [markdown]
# ## Export

# %%
print("\nShape du df en sortie : ", df.shape)

df.to_csv(PATH_SORTIE, index=False)
print("Export vers :", PATH_SORTIE)
