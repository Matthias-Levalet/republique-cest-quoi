# %% [markdown]
# # Diagnostics - Affiliations manquantes et cas limites
# Script d'INVESTIGATION, ne fait PAS partie du pipeline de production
# Relit `interventions_nettoyees.csv` (sortie finale de 2-4)
# et produit uniquement des csv de diagnostic dans `data/temp/`,
# sans jamais modifier le csv final.

# %%
import pandas as pd

PATH_ENTREE = "../data/interim/interventions_nettoyees.csv"

# %%
df = pd.read_csv(PATH_ENTREE, low_memory=False, dtype={"id_orateur": str})
print("Shape du df chargé : ", df.shape)

# %% [markdown]
# ## Acteurs avec au moins une affiliation manquante

# %%
restant_affiliation_et_gouv = df[
    (df["affiliation_et_gouv"].isna()) & (df["id_acteur"] != "PA0")
]

count_restant_par_acteur = (
    restant_affiliation_et_gouv.groupby(["id_acteur", "nom_orateur_clean"], dropna=False)
    .size()
    .reset_index(name="nb_na_interventions")
)

repartition = (
    df[df["id_acteur"].isin(count_restant_par_acteur["id_acteur"])]
    .groupby("id_acteur")["affiliation_et_gouv"]
    .agg(nb_na=lambda s: s.isna().sum(), nb_renseigne=lambda s: s.notna().sum())
    .reset_index()
)

resultat = count_restant_par_acteur.merge(repartition, on="id_acteur").sort_values(
    "nb_renseigne", ascending=False
)

print(f"Nombre d'id_acteur avec au moins un NA : {resultat['id_acteur'].nunique()}")
print(resultat)

resultat.to_csv("../data/temp/count_restant_affiliation_et_gouv.csv", index=False)

# %% [markdown]
# ## Idem, avec qualité orateur

# %%
count_restant_par_acteur_qualite = (
    restant_affiliation_et_gouv.groupby(
        ["id_acteur", "nom_orateur_clean", "qualite_orateur"], dropna=False
    )
    .size()
    .reset_index(name="nb_na_interventions")
)

resultat_qualite = count_restant_par_acteur_qualite.merge(
    repartition, on="id_acteur"
).sort_values("nb_renseigne", ascending=False)

print(f"Nombre d'id_acteur avec au moins un NA : {resultat_qualite['id_acteur'].nunique()}")
print(resultat_qualite)

resultat_qualite.to_csv(
    "../data/temp/count_restant_qualite_affiliation_et_gouv.csv", index=False
)

# %% [markdown]
# ## Cas où un même id_acteur a plusieurs valeurs différentes de affiliation_et_gouv

# %%
tmp = df[["id_acteur", "nom_orateur_clean", "affiliation_et_gouv"]].copy()
tmp["affiliation_et_gouv_norm"] = tmp["affiliation_et_gouv"].fillna("<<NA>>")

ids_multi_affil = (
    tmp.groupby("id_acteur")["affiliation_et_gouv_norm"].nunique().loc[lambda s: s > 1].index
)
cas_diff = tmp[tmp["id_acteur"].isin(ids_multi_affil)].copy()

print("Nombre d'id_acteur avec plusieurs valeurs de affiliation_et_gouv :", len(ids_multi_affil))
print("Nombre total de lignes concernées :", len(cas_diff))

cas_multi_affil = (
    cas_diff.groupby(["id_acteur", "nom_orateur_clean"])["affiliation_et_gouv_norm"]
    .agg(lambda x: sorted(set(x)))
    .reset_index(name="valeurs_affiliation_et_gouv")
    .sort_values(["nom_orateur_clean", "id_acteur"])
)
print(cas_multi_affil)
cas_multi_affil.to_csv("../data/temp/cas_multi_affiliation_et_gouv.csv", index=False)

# %% [markdown]
# ## Orateurs avec affiliation GOUV + une autre affiliation

# %%
temp = df.loc[
    df["affiliation_et_gouv"].notna(),
    ["id_acteur", "nom_orateur_clean", "affiliation_et_gouv"],
].copy()
temp["affiliation_et_gouv_norm"] = temp["affiliation_et_gouv"].fillna("<<NA>>")

affil_par_id = temp.groupby("id_acteur")["affiliation_et_gouv_norm"].agg(
    lambda s: sorted(set(s.astype(str)))
)
ids_multi_avec_gvt = affil_par_id[
    affil_par_id.apply(lambda x: len(x) > 1 and "GOUV" in x)
].index

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

print(f"\nNombre d'orateurs avec affiliations multiples dont GOUV : {len(membres_gouv_multi_affil)}")
print(membres_gouv_multi_affil)

membres_gouv_multi_affil.to_csv("../data/temp/membres_gouv_multi_affil.csv", index=False)

# %% [markdown]
# ## Vérification résiduelle "Congrès du Parlement"
# nb : désormais géré directement depuis l'extraction (1-1), conservé ici
# comme garde-fou pour repérer une éventuelle réapparition.

# %%
mask_congres = df["session"].str.contains("Congrès du Parlement", case=False, na=False)

print("Présence de 'Congrès du Parlement' dans session :", mask_congres.any())
print("Nombre de lignes concernées :", int(mask_congres.sum()))

if mask_congres.any():
    print("\nValeurs des sessions concernées :")
    print(df.loc[mask_congres, "session"].value_counts())

# %% [markdown]
# ## Exploration des id_acteur "externes" (contenant '-')

# %%
df_externe = df[df["id_acteur"].str.contains("-", regex=False, na=False)].copy()
print("Nombre de lignes id_acteur externe :", len(df_externe))

resume_externes = (
    df_externe.groupby("id_acteur", dropna=False)
    .agg(
        id_orateur=("id_orateur", lambda s: ", ".join(sorted(set(s.dropna().astype(str))))),
        nom_orateur=("nom_orateur", lambda s: ", ".join(sorted(set(s.dropna().astype(str))))),
        nom_orateur_clean=("nom_orateur_clean", lambda s: ", ".join(sorted(set(s.dropna().astype(str))))),
        qualite_orateur=("qualite_orateur", lambda s: ", ".join(sorted(set(s.dropna().astype(str))))),
        nb_interventions=("id_syceron", "count"),
    )
    .reset_index()
    .sort_values("nb_interventions", ascending=False)
)

print(resume_externes)

# %%
print(
    df[
        (df["id_mandat"] == "-1")
        & (df["affiliation_et_gouv"] != "GOUV")
        & (df["id_acteur"] != "PA0")
    ]["nom_orateur_clean"].value_counts().head(50)
)

# %%
print(
    df[
        (df["affiliation_et_gouv"] != "GOUV")
        & (df["id_acteur"] != "PA0")
        & (df["affiliation_et_gouv"].isna())
    ]["nom_orateur_clean"].value_counts().head(20)
)
