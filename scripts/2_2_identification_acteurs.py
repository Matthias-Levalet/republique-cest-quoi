# %% [markdown]
# # 2-2 - Fusion des identifiants d'acteurs et correction des erreurs
# Lit `2_1_filtrage_nettoyage.csv` (issu de 2-1).
# Fusionne id_acteur et id_orateur, calcule le nom le plus fréquent par acteur,
# corrige les erreurs d'identification détectées par comparaison directe
# puis par similarité fuzzy.
# Écrit `2_2_identification_acteurs.csv`, utilisé par l'étape suivante (2-3).

# %%
import re
import pandas as pd
from rapidfuzz import fuzz

PATH_ENTREE = "../data/interim/2_1_filtrage_nettoyage.csv"
PATH_SORTIE = "../data/interim/2_2_identification_acteurs.csv"
PATH_TRACE_CORRECTION_NOM = "../data/temp/trace_correction_diff_nom.csv"

COLS_CHECK = [
    "id_acteur",
    "id_orateur",
    "nom_orateur",
    "nom_orateur_clean",
    "id_syceron",
]

# Seuil optimisé après inspection manuelle des cas limites.
# Derniers cas retenus dans ce seuil :
# - Mme Audrey Dufeu vs Mme Audrey Dufeu Schubert (78.05)
# - Mme Christine Cloarec vs Mme Christine Le Nabour (77.27...) -> même personne
SEUIL_CORRECTION = 77.27272727272727

# %%
df = pd.read_csv(PATH_ENTREE, low_memory=False, dtype={"id_orateur": str})
print("Shape du df chargé : ", df.shape)

# %% [markdown]
# ## Fusion id_acteur et id_orateur
# nb : certains cas (~3000) ont un id_orateur plus précis (un vrai PA) que
# id_acteur (PA0). Ce sont presque toujours des interruptions à plusieurs
# locuteurs, qu'id_orateur attribue (mal) à une seule personne. On préfère
# donc garder PA0 (neutre) et n'utiliser id_orateur que pour combler les
# id_acteur manquants.

# %%
# ===========================================================
# FUSION DES IDENTIFIANTS D'ACTEURS,
# RÉCUPÉRATION ET NETTOYAGE DU NOM LE PLUS FRÉQUENT
# (et correction d'erreurs id_acteur)
# ===========================================================

# ========== Fusion id_acteur et id_orateur ==========

# # Si pas fait avant :
# # (ici déjà réalisé dans le regroupement des interruptions, cf. 1-2)
# # Stabiliser le id_orateur pour être au format AN
# df["id_orateur"] = "PA" + df["id_orateur"]
# # Remplacer les valeurs manquantes de id_acteur par id_orateur quand disponible
# df["id_acteur_originel"] = df["id_acteur"]  # garder une trace
# df["id_acteur"] = df["id_acteur"].combine_first(df["id_orateur"])
# %% [markdown]
# ## Récupération et nettoyage du nom le plus fréquent


# %%
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
def get_most_frequent_name(row):
    """
    Renvoie le nom le plus fréquent pour cet id_acteur, sauf si l'acteur
    est PA0 ou manquant (nom brut conservé dans ce cas).

    /!\\ Limite : 1/ invisibilise les rares interventions mal identifiées par
    leur PA mais qui portent le bon nom (le nom majoritaire l'emporte) ;
    2/ dépend de `most_frequent_name`, à recalculer après toute correction
    d'id_acteur; 3/ pourrait poser soucis avec les président.es de séance
    si on avait voulu les garder.
    """
    if row["id_acteur"] == "PA0" or pd.isna(row["id_acteur"]):
        return row["nom_orateur"]
    return most_frequent_name.get(row["id_acteur"], row["nom_orateur"])


# Fonction nettoyage des noms d'orateurs
def nettoyer_nom(texte):
    """
    Nettoyage d'un nom d'orateur : proche de nettoyer_texte (2-1) mais
    supprime aussi les virgules.
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

# %% [markdown]
# ## Correction automatique et manuelle des erreurs id_acteur
# nb : cas problématiques id_acteur != id_orateur & nom_orateur !=
# nom_orateur_clean -> on considère que le texte du CR fait foi, donc que
# id_orateur est le bon identifiant, qu'on utilise pour écraser id_acteur.
# Si id_acteur != id_orateur mais que les noms sont similaires, l'erreur
# porte sur id_orateur (non utilisé ensuite, donc sans conséquence ici).
# Cas manuels : quelques cas limites identifiés par inspection manuelle,
# ici des intervenants mal identifiés en PA externes.

# %%
# ========== Correction automatique des erreurs id_acteur =============

# Mask auto des cas problématiques id_acteur vs id_orateur et noms différents
mask_pb_id = (
    df["id_acteur"].notna()
    & df["id_orateur"].notna()
    & (df["id_acteur"] != "PA0")
    & (df["id_orateur"] != "PA0")
    & (df["id_acteur"] != df["id_orateur"])
    & (df["nom_orateur"].apply(nettoyer_nom) != df["nom_orateur_clean"])
)  # nettoyer pour commensurabilité

print("\nSituations problématiques id_acteur vs id_orateur avant correction auto :\n")
print(df.loc[mask_pb_id, COLS_CHECK].sort_values("id_syceron").to_string(index=False))

# Correction auto : id_acteur <- id_orateur
df.loc[mask_pb_id, "id_acteur"] = df.loc[mask_pb_id, "id_orateur"]
print(f"\nLignes corrigées auto dans df : {mask_pb_id.sum()}")

# ========== Correction manuelle des erreurs id_acteur =============

# Identification manuelle des cas limites mal identifiés avec PA externe
corrections_manuelles = {
    "PA-121339": "PA721764",  # Olivia Grégoire (quand présidente d’une commission spéciale)
    "PA-107289": "PA719930",  # Boris Vallaud
    "PA-1260": "PA332523",  # Marie-Christine Dalloz (quand rapporteure spéciale)
    "PA-125019": "PA736201",  # Sophie Taillé-Polian
}

# Appliquer les corrections manuelles (on touche pas à id_orateur, juste id_acteur)
mask_manuel_all = df["id_acteur"].isin(
    corrections_manuelles.keys()
)  # pour affichage log
print("\nCorrections manuelles à appliquer :\n", corrections_manuelles)

for ancien_id, nouvel_id in corrections_manuelles.items():
    mask_manuel = df["id_acteur"] == ancien_id
    if mask_manuel.any():
        # Récupérer tous les noms uniques associés à cet ancien_id
        noms_associes = df.loc[mask_manuel, "nom_orateur"].unique()
        # Appliquer la correction manuelle
        df.loc[mask_manuel, "id_acteur"] = nouvel_id
        print(
            f"Correction manuelle : {ancien_id} -> {nouvel_id} "
            f"→ {mask_manuel.sum()} ligne(s) modifiée(s) "
            f"(noms associés : {', '.join(noms_associes)})"
        )
    else:
        print(f"Aucune ligne trouvée pour l'ID {ancien_id} (correction ignorée)")

# ========== Re-calcul nom_orateur_clean =============

# Recalculer le nom le plus fréquent après correction des identifiants acteurs
# = réactualiser (puisqu'on en a modifié, pourrait changer le plus fréquent)
most_frequent_name = calculer_nom_plus_frequent(df)
# et ré-appliquer la récup (= la fonction change pas)
df["nom_orateur_clean"] = df.apply(get_most_frequent_name, axis=1).apply(nettoyer_nom)

# Affichage diag
print("\nSituations après correction auto :\n")
print(
    df.loc[mask_pb_id, COLS_CHECK]
    .drop_duplicates("id_syceron")
    .sort_values("id_syceron")
    .to_string(index=False)
)

print("\nSituations après correction manuelle :\n")
print(
    df.loc[mask_manuel_all, COLS_CHECK]
    .drop_duplicates("id_syceron")
    .sort_values("id_syceron")
    .to_string(index=False)
)

# %% [markdown]
# ## Détection et correction des erreurs probables d'identification (fuzzy)
# Contrairement au cas précédent, id_acteur et id_orateur ne diffèrent pas
# nécessairement ici. On compare le nom brut à nom_orateur_clean via un score
# de similarité fuzzy. Sous le seuil optimisé, on considère qu'il s'agit
# d'une véritable erreur d'identification (et non d'une simple variante du
# même nom) -> réaffectation à PA0 + surimpression du nom brut.


# %%
# ========================================================================
# DÉTECTION ET CORRECTION DES ERREURS PROBABLES D'IDENTIFICATION
# (comparaison nom_orateur brut vs nom identifié, via score de similarité fuzzy)
# ========================================================================

# ========== identification des cas où l'identification semble erronée/problématique ==========


def normaliser_nom_fuzzy(x):
    """Normalisation d'un nom en vue de la comparaison par similarité fuzzy."""
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

# Score fuzzy (0-100) : ratio plutôt que WRatio/token car après tests montrent
# des écarts importants sur de simples différences d'accents avec les
# alternatives token.
df["score_nom_fuzzy"] = [
    fuzz.ratio(a, b) if isinstance(a, str) and isinstance(b, str) else None
    for a, b in zip(nom_brut_norm, nom_clean_norm)
]

mask_a_corriger = (
    (df["id_acteur"] != "PA0")
    & nom_brut_norm.notna()
    & nom_clean_norm.notna()
    & (nom_brut_norm != nom_clean_norm)
    & (df["score_nom_fuzzy"] < SEUIL_CORRECTION)
)

# Trace des cas affectés, avant écrasement, pour audit manuel
df.loc[mask_a_corriger, COLS_CHECK + ["score_nom_fuzzy"]].copy().to_csv(
    PATH_TRACE_CORRECTION_NOM, index=False
)

print("\nSituations problématiques nom_orateur vs nom_orateur_clean :")
print("(similarité fuzzy nom_orateur brut vs nom_orateur_clean identifié)")
print(f"Nombre de cas à corriger erreur identification : {mask_a_corriger.sum()}")

# ===== Correction (réaffectation à PA0 + correction nom_orateur_clean) =====
df.loc[mask_a_corriger, "id_acteur"] = "PA0"
df.loc[mask_a_corriger, "nom_orateur_clean"] = df.loc[mask_a_corriger, "nom_orateur"]

print("\nShape du df en sortie : ", df.shape)

# %% [markdown]
# ## Export

# %%
# ========== Export ==========
df.to_csv(PATH_SORTIE, index=False)
print("Export vers :", PATH_SORTIE)

# TODO: syceron 2827575 2827576 2827577 = M. Lionel Tivoli = PA793298
# (alors qu'ici en neutre non identifié et sous PA0)
# (on s'en cogne vu le nb et doit y en avoir d'autres ?)
