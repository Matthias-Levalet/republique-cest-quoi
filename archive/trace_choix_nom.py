# ========== Comparaison nom_orateur brut vs nom_orateur_clean ==========
# Repérer les cas où le nom le plus fréquent assigné à un id_acteur
# diffère du nom brut de l'intervention -> signe possible d'une erreur d'id_acteur
# (ex : ministre ou invité avec un PA qui appartient à un autre)
# Passage par un rapidfuzz pour avoir un score de similarité

# CE FICHIER EST PAS EXECUTABLE EN L'ÉTAT, IL S'AGIT D'UNE TRACE D'UN BOUT DU NB 2

from rapidfuzz import fuzz


def normaliser_nom_fuzzy(x):
    if not isinstance(x, str):
        return x
    x = nettoyer_nom(x).lower().strip()
    # retire ponctuation pour éviter de flag juste une virgule/point
    x = re.sub(r"[^\w\s'-]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


# Noms normalisés
# pour nom orateur = appliquer aussi le nettoyage standard pour comparabilité
nom_brut_norm = df["nom_orateur"].apply(normaliser_nom_fuzzy)
nom_clean_norm = df["nom_orateur_clean"].apply(normaliser_nom_fuzzy)

# Score fuzzy (0-100)
score_fuzzy = [
    fuzz.ratio(a, b) if isinstance(a, str) and isinstance(b, str) else None
    for a, b in zip(nom_brut_norm, nom_clean_norm)
]
df["score_nom_fuzzy"] = score_fuzzy

# Seuil: plus haut = plus strict
seuil_similarite = 96

cols_fuzz = [
    "id_acteur",
    "id_acteur_originel",
    "id_orateur",
    "nom_orateur",
    "nom_orateur_clean",
    "id_syceron",
    "score_nom_fuzzy",
]
mask_nom_diff_significatif = (
    (df["id_acteur"] != "PA0")
    & nom_brut_norm.notna()
    & nom_clean_norm.notna()
    & (nom_brut_norm != nom_clean_norm)
    & (df["score_nom_fuzzy"] < seuil_similarite)
)

deduplication_pb_fuzz = (
    df.loc[mask_nom_diff_significatif, cols_fuzz]
    .value_counts()
    .rename("n")
    .reset_index()
    .sort_values("score_nom_fuzzy")
)

deduplication_pb_fuzz.to_csv("../data/temp/deduplication_pb_fuzz.csv", index=False)
deduplication_pb_fuzz

77.27272727272727
# aller cut à 77.27272727272727 -> dessous que les cas chelous, au dessus que les memes gens mais changement noms.
# et même si "différent" ici c'est bien la meme personne Mme Christine Cloarec,Mme Christine Le Nabour
# PA720046,PA720046,PA720046,Mme Audrey Dufeu,Mme Audrey Dufeu Schubert,2326880,78.04878048780488,1
