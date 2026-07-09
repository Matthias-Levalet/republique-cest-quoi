# %% [markdown]
# # 2-1 - Filtrage des interventions et nettoyage des textes
# Lit `interventions_regroupees.csv` (issu de 1-3).
# Exclut les interventions non exploitables (président.e, styles non NORMAL,
# codes grammaires inutiles), nettoie les textes et exclut les vides/parasites.
# Écrit `2_1_filtrage_nettoyage.csv`, utilisé par l'étape suivante (2-2).

# %%
import re
import html
import unicodedata
import pandas as pd

PATH_ENTREE = "../data/interim/interventions_regroupees.csv"
PATH_SORTIE = "../data/interim/2_1_filtrage_nettoyage.csv"

# Codes grammaires à exclure après les premiers filtres
# (peut varier selon les choix de filtrage en amont)
EXCLUSION_CODE_GRAMMAIRE = [
    "OUV_SEAN_2_1",
    "FUSION",
    "FIN_SEAN_2_1",
    "DISC_ARTICLES_3_9_1",  # interv président.es mal identifiées
    "DISC_ARTICLES_3_1",
    "ANN_SCR_AUTRE_1_0",
]

# %%
df = pd.read_csv(PATH_ENTREE, low_memory=False, dtype={"id_orateur": str})
print("Shape du df chargé : ", df.shape)

# %% [markdown]
# ## Filtrage des interventions
# nb pour exclusion président.e : role_debat n'est pas toujours bien identifié,
# on utilise aussi nom_orateur
# (avant de le recoder/nettoyer, sinon risque de perte par remplacement).

# %%
# ===========================================================
# FILTRAGE DES INTERVENTIONS
# ===========================================================

# Exclure les prises de parole de la présidence
df = df[~df["nom_orateur"].str.strip().isin(["M. le président", "Mme la présidente"])]
df = df[~df["roledebat"].str.strip().isin(["president"])]

# Exclure les lignes pour lesquelles on n'a pas d'info orateurs (pas exploitable)
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

# %%
# ========== Gestion codes grammaires ==========

# Exclusion des codes grammaires inutiles restants après les premiers filtres
mask_excl_code_grammaire = df["code_grammaire"].isin(EXCLUSION_CODE_GRAMMAIRE)
print(f"Lignes à exclure (code_grammaire) : {mask_excl_code_grammaire.sum()}")

df = df[~mask_excl_code_grammaire]
print(f"Shape après exclusion code_grammaire : {df.shape}")

# %% [markdown]
# ## Nettoyage des textes puis exclusion des vides et parasites


# %%
# ===========================================================
# NETTOYAGE DES TEXTES PUIS EXCLUSION DES VIDES ET PARASITES
# ===========================================================

# ========== Nettoyer les textes et supprimer les lignes vides ==========


# nettoyage basique du texte


def nettoyer_texte(texte):
    if not isinstance(texte, str):
        return ""
    # Normaliser les caractères Unicode
    texte = unicodedata.normalize("NFC", texte)
    # Décoder les entités HTML
    texte = html.unescape(texte)
    # Supprimer les balises HTML/XML > espace (éviter collage de mots)
    texte = re.sub(r"<[^>]+>", " ", texte)
    # Supprimer contenu entre parenthèses
    # NOTE : CHOIX FORT SELON CE QUI VEUT ÊTRE ÉTUDIÉ
    # Supprime des didascalies ("Applaudissements", etc.)
    # mais aussi tout autre contenu entre parenthèses
    # ne gère pas les parenthèses imbriquées mais sont extrêmement rares (parfois sur (e))
    texte = re.sub(r"\([^()]*\)", "", texte)
    # Uniformiser apostrophes (utile pour regex)
    texte = texte.replace("’", "'").replace("\u02bc", "'")
    # Normaliser les espaces (après unescape(), couvre \xa0, \t, \n)
    # et supprimer les espaces multiples
    texte = re.sub(r"\s+", " ", texte).strip()

    return texte


df["texte_brut"] = df["texte"]  # garder une version brute du texte
df["texte"] = df["texte"].apply(nettoyer_texte)

# supprimer les lignes où "texte" est manquant ou vide
mask_texte_vide = df["texte"].isna() | (df["texte"] == "")
print(f"Lignes supprimées pour texte vide : {mask_texte_vide.sum()}")
df = df[~mask_texte_vide]

# %%
# ========== Gestion textes parasites ==========

# Varie selon les choix de filtrage en amont (sur les président.es) mais il
# peut y avoir quelques cas spécifiques de textes parasites, ex :
# "……………………………………………………………."
# "------------------Cette partie de la séance est en cours de finalisation---------------------------------------------"


# identification textes parasites
def est_texte_parasite(texte):
    """Détecte les textes parasites (points de suspension, séance en cours de finalisation)."""
    if not isinstance(texte, str):
        return False
    nettoye = re.sub(
        r"Cette partie de la séance est en cours de finalisation", "", texte
    )
    nettoye = re.sub(r"[-–—.…\s]+", "", nettoye)
    return nettoye == ""


mask_parasite = df["texte"].apply(est_texte_parasite)
print(f"Lignes parasites supprimées : {mask_parasite.sum()}")
df = df[~mask_parasite]

print("Shape du df après nettoyage et exclusion des textes : ", df.shape)

# %% [markdown]
# ## Export

# %%
# ========== Export ==========
df.to_csv(PATH_SORTIE, index=False)
print("Export vers :", PATH_SORTIE)
