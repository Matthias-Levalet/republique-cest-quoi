# %% [markdown]
# # 1-2 - Fusion des législatures
# Lit `extract_15.csv` et `extract_16.csv` (issus de 1-1), les concatène,
# déduplique en fallback, et exporte `extract_15_16_concat.csv` utilisé par
# l'étape suivante (1-3).

# %%
import pandas as pd

PATH_ENTREE_15 = "../data/interim/1_1_extract_15.csv"
PATH_ENTREE_16 = "../data/interim/1_1_extract_16.csv"
PATH_SORTIE = "../data/interim/1_2_extract_15_16_concat.csv"

# %% [markdown]
# ## Concaténation

# %%
# ==================================================================
# FUSION DES LÉGISLATURES
# concaténation de df_15 et df_16
# ==================================================================

df_15 = pd.read_csv(
    PATH_ENTREE_15,
    low_memory=False,
    dtype={
        "id_orateur": str
    },  # éviter identification en float avant d'avoir ajouté le "PA"
)

df_16 = pd.read_csv(
    PATH_ENTREE_16,
    low_memory=False,
    dtype={
        "id_orateur": str
    },  # éviter identification en float avant d'avoir ajouté le "PA"
)


# %%
df_concat = pd.concat([df_15, df_16], ignore_index=True, sort=False)

# %% [markdown]
# ## Déduplication
# nb traçabilité : utilisée ici en fallback après suppression ciblée de
# fichiers doublons en 1-1. Devrait donner 0 doublon si l'exclusion de
# fichiers a bien couvert tous les cas ; on la garde pour repérage en cas
# d'évolution des données ou d'ajout de nouveaux fichiers.
# nb : la déduplication seule n'est pas parfaite vs suppression de fichier
# (des lignes peuvent passer le filtre car pas de vrais doublons :
# en-tête fichier, sans texte, etc.) -> d'où l'exclusion de fichiers en 1-1,
# la déduplication n'intervenant qu'en filet de sécurité.

# %%
# ==================================================================
# DÉDUPLICATION
# ici utilisée en fallback après suppression ciblée de fichiers
# ==================================================================

# conservation de la clé texte pour éviter de supprimer des lignes qui ont
# un même id_syceron mais texte différent (didascalies, etc.).
# on ne garde pas l'uid dans la clé, car l'enjeu concerne parfois des
# fichiers doublons portant le même (mauvais) uid.
# ie : on peut pas juste aller regarder les noms de fichier avec l'iud, il correspond pas

dup_key = ["id_syceron", "texte"]

# mask pour les lignes qui seraient supprimées par drop_duplicates
mask_removed = df_concat.duplicated(subset=dup_key, keep="first")

if mask_removed.sum() == 0:
    print("Pas de doublons avec les clés choisies")
    print(f"concat {len(df_15)} + {len(df_16)} -> {len(df_concat)} lignes")
else:
    # lignes que l'on vire
    removed = df_concat[mask_removed].copy()
    # # si besoin investigation :
    # # toutes les lignes impliquées dans un doublon, y compris celle qu'on garde
    # mask_any = df_concat.duplicated(subset=dup_key, keep=False)
    # # groupes doublons = lignes dupliquées regroupées et triées
    # dupe_groups = df_concat[mask_any].sort_values(by=dup_key)
    # # les survivants (si jamais on veut les voir, pas utilisé directement ici)
    # kept_in_groups = df_concat[~mask_removed & mask_any]

    print(f"Groupes dupliqués distincts  : {mask_removed.sum()}")
    print(f"Lignes supprimées prévues : {len(removed)}")
    # nb : si nb groupe = nb lignes c'est ok = paires doublons et pas triples etc.
    print("UIDs des lignes concernées (pas parfait pour retrouver fichier) :")
    for uid in sorted(removed["uid"].dropna().unique()):
        print(f"  - {uid}")

    df_concat_before = len(df_concat)
    df_concat = df_concat.drop_duplicates(subset=dup_key, keep="first")
    print(
        f"concat {len(df_15)} + {len(df_16)} -> {df_concat_before} lignes ; "
        f"après déduplication {len(df_concat)} lignes"
    )

# %% [markdown]
# ## Export

# %%
# ========== Exports ==========
df_concat.to_csv(PATH_SORTIE, index=False, encoding="utf-8")
print(f"\n Export CSV : ({df_concat.shape[0]} lignes) -> {PATH_SORTIE}")
