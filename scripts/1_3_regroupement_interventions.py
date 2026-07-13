# %% [markdown]
# # 1-3 - Regroupement des interventions interrompues
# Lit `1_2_extract_15_16_concat.csv` (issu de 1_2).
# Fusionne les interventions d'un même orateur interrompues par des INTERRUPTION_1_10,
# en conservant les interruptions elles-mêmes intercalées dans l'ordre.
# Exporte `1_3_interventions_regroupees.csv`, utilisé par le pipeline de nettoyage (voir 2_1).

# %%
import pandas as pd

PATH_ENTREE = "../data/interim/1_2_extract_15_16_concat.csv"
PATH_SORTIE = "../data/interim/1_3_interventions_regroupees.csv"

# %%
df = pd.read_csv(
    PATH_ENTREE,
    low_memory=False,
    dtype={
        "id_orateur": str
    },  # éviter identification en float avant d'avoir ajouté le "PA"
)
print("Shape du df chargé : ", df.shape)

# Changer les missing values pour non_précisé (majoritaire) dans code_parole
df["code_parole"] = df["code_parole"].fillna("non_précisé")

# Stabiliser le id_orateur pour être au format AN
# NOTE : pas indispensable ici mais permet de stabiliser les id dès ici
df["id_orateur"] = "PA" + df["id_orateur"]
# Remplacer les valeurs manquantes de id_acteur par id_orateur quand disponible
df["id_acteur_originel"] = df["id_acteur"]  # garder une trace
df["id_acteur"] = df["id_acteur"].combine_first(df["id_orateur"])

# %% [markdown]
# ## Fonction de regroupement

# %%
# ==================================================================
# REGROUPEMENT DES INTERVENTIONS INTERROMPUES
# Fusion des interventions d'un même orateur interrompues par des interruptions
# ==================================================================

# ========== Paramètres ==========

# Codes considérés comme interruptions (conservés tels quels dans la sortie)
CODES_INTERRUPTION = {"INTERRUPTION_1_10"}

# Colonnes invariantes dans un groupe (on garde la valeur de la 1ère ligne)
COLS_META = [c for c in df.columns if c != "texte"]

# NOTE : La liste explicite permet : 1/ d'exclure certaines colonnes du df
# de sortie, ou 2/ d'exclure une colonne qui ne serait pas invariante au sein
# d'un groupe – elle ne doit alors pas rester en méta, sous peine de perdre
# silencieusement sa variation intra-groupe (sauf choix conscient et assumé).

# NOTE : Pas véritablement utilisé ici : on garde en réalité toutes les cols
# sauf texte, qui est réintroduite dès cols_utiles — aucune n'est filtrée.
# Choix volontaire de garder l'info de la 1ère ligne (utile pour trace), les
# cas particuliers étant gérés à part : id_syceron par ex. renvoie la liste
# de ceux rencontrés dans les fragments, tout en gardant l'originel en méta
# (cf. id_syceron_fragments).

# ========== Fonction principale ==========


def regrouper(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prend un DataFrame et retourne un DataFrame entrelacé :
      - lignes d'intervention fusionnées (nb_fragments >= 1)
      - lignes d'interruption conservées telles quelles (nb_fragments = NaN)

    NOTE :nb traçabilité : plusieurs tentatives de tri préalable (par ordinal_prise,
    ordre_absolu_seance, id_syceron convertis en numérique) ont été testées
    et donnaient des résultats différents (et pas nécessairement meilleurs :
    voir investigation dédiée hors pipeline). Le choix retenu ici est de ne
    PAS trier avant regroupement et de garder l'ordre du csv d'entrée.
    TODO : AVISER !!!!!
    """
    cols_utiles = list(dict.fromkeys(COLS_META + ["texte"]))
    work = df[cols_utiles].copy()

    work["uid_norm"] = work["uid"].fillna("").astype(str)
    work["id_acteur_norm"] = work["id_acteur"].fillna("").astype(str)
    work["code_grammaire_norm"] = work["code_grammaire"].fillna("").astype(str)
    work["code_parole_norm"] = work["code_parole"].fillna("").astype(str)
    work["texte_norm"] = work["texte"].fillna("").astype(str)

    resultats = []  # liste finale (interventions + interruptions)
    groupe = None  # groupe en cours d'accumulation
    buffer_interruptions = []  # interruptions entre deux fragments du même orateur

    def ligne_sortie_depuis_base(base_row: dict) -> dict:
        r = {col: base_row[col] for col in cols_utiles}
        r["nb_fragments"] = pd.NA
        r["nb_interruptions_recues"] = pd.NA
        r["a_ete_interrompu"] = pd.NA
        r["id_syceron_fragments"] = pd.NA
        return r

    def clore_groupe(g: dict) -> dict:
        """Finalise un groupe. Les interruptions du buffer seront émises APRÈS dans le flux."""
        row = g["premiere_ligne"].copy()
        row["texte"] = " ".join(g["textes"])  # textes norm pour éviter les NaN
        row["nb_fragments"] = g["nb_fragments"]
        row["nb_interruptions_recues"] = g["nb_interruptions_recues"]
        row["a_ete_interrompu"] = g["nb_interruptions_recues"] > 0
        row["id_syceron_fragments"] = "|".join(g["codes_syceron"])
        return row

    records = work.to_dict("records")

    for row in records:
        cg = row["code_grammaire_norm"]
        cp = row["code_parole_norm"]
        acteur_str = row["id_acteur_norm"]
        uid_str = row["uid_norm"]
        syc = str(row["id_syceron"]) if pd.notna(row["id_syceron"]) else ""

        # --- Cas 1 : interruption ---
        if cg in CODES_INTERRUPTION:
            if groupe is not None:
                # l'interruption est dans le contexte d'un groupe ouvert :
                # on l'ajoute au buffer (elle sera émise si le même orateur reprend)
                buffer_interruptions.append(row)
                groupe["nb_interruptions_recues"] += 1
            else:
                # interruption hors contexte (cas rare) : émise directement
                resultats.append(ligne_sortie_depuis_base(row))
            continue

        # --- Cas 2 : intervention principale ---
        if (
            groupe is not None
            and buffer_interruptions  # on regroupe seulement si bien interrompu (et pas parle 2 fois de suite)
            and acteur_str != ""  # cf les nan convertis en ""
            and groupe["id_acteur"] == acteur_str
            and groupe["uid"] == uid_str
            and groupe["codes_grammaire"][-1] == cg
            and groupe["codes_parole"][-1] == cp
        ):
            # Même orateur, même séance, mêmes codes, avec interruption -> fusion
            groupe["textes"].append(row["texte_norm"])
            groupe["codes_grammaire"].append(cg)
            groupe["codes_parole"].append(cp)
            groupe["codes_syceron"].append(syc)
            groupe["nb_fragments"] += 1
        else:
            # Nouvel orateur, nouvelle séance, ou changement de codes
            if groupe is not None:
                # Clore le groupe précédent
                resultats.append(clore_groupe(groupe))
                # Et les interruptions en buffer suivent le groupe
                for irr in buffer_interruptions:
                    resultats.append(ligne_sortie_depuis_base(irr))
                buffer_interruptions = []

            groupe = {
                "uid": uid_str,
                "id_acteur": acteur_str,
                "premiere_ligne": {col: row[col] for col in cols_utiles},
                "textes": [row["texte_norm"]],
                "codes_grammaire": [cg],
                "codes_parole": [cp],
                "codes_syceron": [syc],
                "nb_fragments": 1,
                "nb_interruptions_recues": 0,
            }

    # Clore le dernier groupe
    if groupe is not None:
        resultats.append(clore_groupe(groupe))
        for irr in buffer_interruptions:
            resultats.append(ligne_sortie_depuis_base(irr))

    return pd.DataFrame(resultats)


# %% [markdown]
# ## Application et export

# %%
# ========== Application regroupement ==========
df_interv_regroupe = regrouper(df)
print("Shape du df regroupé : ", df_interv_regroupe.shape)

# ========== Export ==========

df_interv_regroupe.to_csv(PATH_SORTIE, index=False)
print("Export vers :", PATH_SORTIE)
