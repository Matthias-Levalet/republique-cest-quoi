# CE FICHIER EST PAS EXECUTABLE EN L'ÉTAT, IL S'AGIT D'UNE TRACE D'UN BOUT DU NB 2

# ==================================================================
# REGROUPEMENT DES INTERVENTIONS INTERROMPUES
# Fusion des interventions d'un même orateur interrompues par des interruptions
# ==================================================================

# Repartir du df en mémoire
df = df_concat.copy()

# # ou le recharger depuis CSV (lui ou df souhaité)
# # Charger le df concaténé des deux législatures
# df = pd.read_csv(
#     "../data/interim/extract_15_16_concat.csv",
#     low_memory=False,
#     dtype={
#         "id_orateur": str  # éviter identification en float avant d'avoir ajouté le "PA"
#     },
# )

# print("Shape du df chargé : ", df.shape)

# Changer les missing values pour non_précisé (majoritaire) dans Code_parole
df["code_parole"] = df["code_parole"].fillna("non_précisé")

# # NOTE : après test ne semble pas dramatique de ne pas prendre en compte le
# # df["id_orateur"] = "PA" + df["id_orateur"] : seules 0 ou 2 lignes changent (si code parole ou pas)
# # les recodages "manuels" de PA repérés par ailleurs (voir autre notebook)
# # ne changent rien non plus ici
# # cf surtout des interruptions et ne change pas grand chose au regroup d'interventions
# + quand erreur pas forcément de changement d'ID entre ou d'interv.

# TODO :notre regroupement était cassé, le mettre au cas où :
# Mais par principe la trace si on veut garder :
# Stabiliser le id_orateur pour être au format AN
df["id_orateur"] = "PA" + df["id_orateur"]
# Remplacer les valeurs manquantes de id_acteur par id_orateur quand disponible
df["id_acteur_originel"] = df["id_acteur"]  # garder une trace
df["id_acteur"] = df["id_acteur"].combine_first(df["id_orateur"])


"""
==========================
Regroupe les lignes de l'extraction CSV pour fusionner les interventions
d'un même orateur interrompues par des INTERRUPTION_1_10.

Sortie : un CSV entrelacé avec :
  - une ligne par groupe d'intervention fusionnée (texte concaténé)
  - les informations sur le nombre de fragments, d'interruptions reçues, etc.
  - les lignes INTERRUPTION conservées telles quelles, intercalées dans l'ordre
"""

# ---------------------------------------------------------------------------
# Paramètres
# ---------------------------------------------------------------------------

# Codes considérés comme interruptions (conservés tels quels dans la sortie)
CODES_INTERRUPTION = {"INTERRUPTION_1_10"}

# Colonnes invariantes dans un groupe (on garde la valeur de la 1ère ligne)
COLS_META = [
    "uid",
    "SeanceRef",
    "SessionRef",
    "dateSeance",
    "dateSeanceJour",
    "numSeanceJour",
    "numSeance",
    "typeAssemblee",
    "legislature",
    "session",
    "nomFichierJo",
    "presidentSeance",
    "point_titre",
    "point_type",
    "valeur_ptsodj",
    "ordinal_prise",
    "ordre_absolu_seance",
    "id_acteur",
    "id_mandat",
    "code_grammaire",
    "code_style",
    "code_parole",
    "id_syceron",
    "roledebat",
    "nom_orateur",
    "qualite_orateur",
    "id_orateur",
    "stime",
]

# ---------------------------------------------------------------------------
# ========== Fonction principale ==========
# ---------------------------------------------------------------------------


def regrouper(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prend un DataFrame trié par (uid, ordre_absolu_seance) et retourne
    un DataFrame entrelacé :
      - lignes d'intervention fusionnées (nb_fragments >= 1)
      - lignes d'interruption conservées telles quelles (nb_fragments = NaN)
    """
    cols_utiles = list(dict.fromkeys(COLS_META + ["texte"]))
    work = df[cols_utiles].copy()

    work["uid_norm"] = work["uid"].fillna("").astype(str)
    work["id_acteur_norm"] = work["id_acteur"].fillna("").astype(str)
    work["code_grammaire_norm"] = work["code_grammaire"].fillna("").astype(str)
    work["code_parole_norm"] = work["code_parole"].fillna("").astype(str)
    work["texte_norm"] = work["texte"].fillna("").astype(str)

    # # TODO : Ancien bug car faisait pas de conversion numérique et donc tri lexicographique sur les ordres de séance
    # TODO : tester avec id syceron pour ordre et voir ce qui casse ?
    # FIXME : repérérer cause de l'écart de lignes entre avec et sans tri avant regroupement
    # -> du a ordinal prise qui est absent pour le plus gros, mais reste un truc
    # avec le tri sans ordinal prise : Shape du df regroupé :  (981871, 33)
    # avec le tri et ordinal prise : Shape du df regroupé :  (960491, 33)
    # avec le tri seulement sur id_syceron : Shape du df regroupé :  (979438, 33)
    # Sans le tri : Shape du df regroupé :  (959660, 33)

    # NOTE : donc encore un écart, semble mieux de pas faire le tri, mais si le fait convertir en numérique
    # work['ordinal_prise_num'] = pd.to_numeric(work['ordinal_prise'], errors="coerce")
    # work['ordre_absolu_seance_num'] = pd.to_numeric(work['ordre_absolu_seance'], errors="coerce")
    # work = work.sort_values(['uid_norm', 'ordinal_prise_num', 'ordre_absolu_seance_num']).reset_index(drop=True)
    # et un autre test (PIRE) par ordre id_syceron pour voir :
    # work["id_syceron"] = pd.to_numeric(work["id_syceron"], errors="coerce")
    # n_nan = work["id_syceron"].isna().sum()
    # if n_nan > 0:
    #     raise ValueError(f"id_syceron manquant/non numérique sur {n_nan} ligne(s)")
    # work = work.sort_values(["id_syceron"]).reset_index(drop=True)

    resultats = []  # liste finale (interventions + interruptions)
    groupe = None  # groupe en cours d'accumulation
    buffer_interruptions = []  # interruptions entre deux fragments du même orateur

    def ligne_sortie_depuis_base(base_row: dict) -> dict:
        r = {col: base_row[col] for col in cols_utiles}
        r["nb_fragments"] = pd.NA
        r["nb_interruptions_recues"] = pd.NA
        r["a_ete_interrompu"] = pd.NA
        r["id_syceron_fragments"] = pd.NA
        # r["codes_gram_fragments"] = pd.NA # ie pour traçabilité si enlève condition
        # r["codes_parole_fragments"] = pd.NA # ie pour traçabilité si enlève condition
        # r["changement_code_grammaire"] = pd.NA # ie pour traçabilité si enlève condition
        # r["changement_code_parole"] = pd.NA # ie pour traçabilité si enlève condition
        return r

    def clore_groupe(g: dict) -> dict:
        """
        Finalise un groupe. Les interruptions du buffer seront émises APRÈS dans le flux.
        """
        row = g["premiere_ligne"].copy()
        row["texte"] = " ".join(
            g["textes"]
        )  # on prend les textes norm pour éviter les NaN
        row["nb_fragments"] = g["nb_fragments"]
        row["nb_interruptions_recues"] = g["nb_interruptions_recues"]
        row["a_ete_interrompu"] = g["nb_interruptions_recues"] > 0
        row["id_syceron_fragments"] = "|".join(g["codes_syceron"])
        # row["codes_gram_fragments"] = "|".join(g["codes_grammaire"]) # ie pour traçabilité si enlève condition
        # row["codes_parole_fragments"] = "|".join(g["codes_parole"]) # ie pour traçabilité si enlève condition
        # row["changement_code_grammaire"] = len(set(g["codes_grammaire"])) > 1 # ie pour traçabilité si enlève condition
        # row["changement_code_parole"] = len(set(g["codes_parole"])) > 1 # ie pour traçabilité si enlève condition
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
                # L'interruption est dans le contexte d'un groupe ouvert :
                # on l'ajoute au buffer (elle sera émise si le même orateur reprend)
                buffer_interruptions.append(row)
                groupe["nb_interruptions_recues"] += 1
            else:
                # Interruption hors contexte (cas rare) : on l'émet directement
                resultats.append(ligne_sortie_depuis_base(row))
            continue

        # --- Cas 2 : intervention principale ---
        if (
            groupe is not None
            and buffer_interruptions  # on regroupe que si bien interrompu (et pas parle 2 fois de suite)
            and acteur_str != ""  # cf les nan convertis en ""
            and groupe["id_acteur"] == acteur_str
            and groupe["uid"] == uid_str
            and groupe["codes_grammaire"][-1] == cg
            and groupe["codes_parole"][-1] == cp
        ):
            # Même orateur, même séance, mêmes codes, avec interruption -> on fusionne
            groupe["textes"].append(row["texte_norm"])
            groupe["codes_grammaire"].append(cg)
            groupe["codes_parole"].append(cp)
            groupe["codes_syceron"].append(syc)
            groupe["nb_fragments"] += 1
        else:
            # Nouvel orateur ou nouvelle séance ou changement de codes
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


df_interv_regroupe = regrouper(df)
print("Shape du df regroupé : ", df_interv_regroupe.shape)

df_interv_regroupe.to_csv("../data/interim/interventions_regroupees.csv", index=False)
