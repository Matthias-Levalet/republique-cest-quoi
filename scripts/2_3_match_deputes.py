# %% [markdown]
# # 2-3 - Match des infos générales des députés (données datan)
# Lit `2_2_identification_acteurs.csv` (issu de 2_2). Fusionne avec les
# données générales des députés (nom, groupe, mandat...) sur id_acteur.
# Écrit `2_3_match_deputes.csv`, utilisé par l'étape suivante (2_4).

# %%
import pandas as pd

PATH_ENTREE = "../data/interim/2_2_identification_acteurs.csv"
PATH_SORTIE = "../data/interim/2_3_match_deputes.csv"
PATH_DEPUTES = "../data/raw/id-dep/deputes-historique(datan-datagouv).csv"

# %%
# TODO : normalement ok à ce stade pour id_orateur (PA a été ajouté)
df = pd.read_csv(PATH_ENTREE, low_memory=False, dtype={"id_orateur": str})
print("Shape du df chargé : ", df.shape)

# %%
# ==============================
# MATCH DONNÉES DÉPUTÉS
# ==============================

df_deputes = pd.read_csv(PATH_DEPUTES)

# Suppression des colonnes non utiles qui introduisent des soucis de parsing
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

# %% [markdown]
# ## Fusion des données députés

# %%
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
# ## Export

# %%
print("\nShape du df en sortie : ", df.shape)

df.to_csv(PATH_SORTIE, index=False)
print("Export vers :", PATH_SORTIE)
