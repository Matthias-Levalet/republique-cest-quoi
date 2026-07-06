# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: myenv_clone
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 1. Extraction des données

# %% [markdown]
# Ce notebook extrait les paragraphes des comptes rendus de l’Assemblée nationale à partir des fichiers XML (en utilisant la bibliothèque lxml) et retourne un csv exploitable dans la suite de l'analyse.
#
# La dernière section (1.4) permet si souhaité de regrouper les interventions interrompues.

# %%
# TODO: plus tard, aviser récupération des points de contexte parents(cf tentative Matthias)
# TODO: est-ce que les séquences d'interruption peuvent être identifiées directement depuis xml car elles seraient dans un bloc <interExtraction> ?

# TODO: check against NosDéputés/RegardsCitoyens <3


# %%
# TODO: refacto
# 1a_extraction_xml.py
# section 1.2 : traite les dossiers 15/16, exclut les uids doublons/congrès, exporte extract_15.csv et extract_16.csv

# 1b_fusion_legislatures.py
# section 1.3 : concat, déduplique sur (id_syceron, texte), exporte extract_15_16_concat.csv

# 1c_regroupement_interventions.py
# section 1.4 : applique regrouper(), exporte interventions_regroupees.csv

# Le reste : virer après test ou l'envoyer dans une vraie section debug pour arreter de polluer

# %% [markdown]
# ## 1.1 définition fonctions d'extraction

# %%
import os
import glob
from lxml import etree
import pandas as pd

# ==================================================================
# FONCTIONS D'EXTRACTION DES DONNÉES
# ==================================================================


# ======== Fonction extraction infos depuis fichier XML =========
def extraire_paragraphes_lxml(fichier_xml: str) -> pd.DataFrame:
    """
    Extrait les paragraphes d'un fichier XML de compte rendu en utilisant lxml.
    """
    try:
        tree = etree.parse(fichier_xml)
        root = tree.getroot()
        ns = {"ns": "http://schemas.assemblee-nationale.fr/referentiel"}

        meta = {
            "uid": root.findtext("ns:uid", namespaces=ns),
            "SeanceRef": root.findtext("ns:seanceRef", namespaces=ns),  # pas partout
            "SessionRef": root.findtext("ns:sessionRef", namespaces=ns),  # pas partout
        }
        meta_tags = [
            "dateSeance",
            "dateSeanceJour",
            "numSeanceJour",
            "numSeance",
            "typeAssemblee",
            "legislature",
            "session",
            "nomFichierJo",
            "presidentSeance",
        ]
        for tag in meta_tags:
            meta[tag] = root.findtext(f".//ns:{tag}", namespaces=ns)

        rows = []

        for paragraphe in root.xpath(".//ns:paragraphe", namespaces=ns):
            # Naviguer vers le <point> parent
            # récupérer les infos
            point = paragraphe.getparent()
            while point is not None and point.tag != f"{{{ns['ns']}}}point":
                point = point.getparent()

            point_type = point.get("code_grammaire") if point is not None else None

            # anciennement : utilisait findtext(), mais ignore les sous-balises donc perte de texte
            # plutôt utiliser itertext() pour reconstruire le contenu complet
            texte_point = (
                point.find("ns:texte", namespaces=ns) if point is not None else None
            )
            point_title = (
                "".join(texte_point.itertext()).strip()
                if texte_point is not None
                else None
            )

            # # Plus pris pour l'instant (ie niveau du point, on a toujours niveau paragraphe plus bas):
            # point_id = point.get("id_syceron") if point is not None else None
            # point_valeur_ptsodj = point.get("valeur_ptsodj") if point is not None else None

            texte_elem = paragraphe.find("ns:texte", namespaces=ns)
            texte = (
                "".join(texte_elem.itertext()).strip()
                if texte_elem is not None
                else None
            )
            stime = texte_elem.get("stime") if texte_elem is not None else None

            # Récupérer les informations de l'orateur
            # ie celles présentes dans la balise <orateur>
            # et pas forcément dans les attributs du paragraphe
            orateur = paragraphe.find(".//ns:orateur", namespaces=ns)
            nom_orateur = (
                orateur.findtext("ns:nom", namespaces=ns)
                if orateur is not None
                else None
            )
            qualite_orateur = (
                orateur.findtext("ns:qualite", namespaces=ns)
                if orateur is not None
                else None
            )
            id_orateur = (
                orateur.findtext("ns:id", namespaces=ns)
                if orateur is not None
                else None
            )

            # toper désormais toutes les infos
            # garder apparent pour éventuels choix ou recodages des noms plutôt que des machins type `**meta`
            rows.append(
                {
                    # ========================
                    # Métadonnées de la séance
                    # ========================
                    "uid": meta["uid"],
                    "SeanceRef": meta["SeanceRef"],
                    "SessionRef": meta["SessionRef"],
                    "dateSeance": meta["dateSeance"],
                    "dateSeanceJour": meta["dateSeanceJour"],
                    "numSeanceJour": meta["numSeanceJour"],
                    "numSeance": meta["numSeance"],
                    "typeAssemblee": meta["typeAssemblee"],
                    "legislature": meta["legislature"],
                    "session": meta["session"],
                    "nomFichierJo": meta["nomFichierJo"],
                    "presidentSeance": meta["presidentSeance"],
                    # ========================
                    # Données du point parent (contexte)
                    # ========================
                    "point_titre": point_title,
                    "point_type": point_type,
                    # 'Sous_titre': '',  # not in this version, get back to original if needed
                    # 'Contexte_hierarchique': '',  # not in this version, get back to original if needed
                    # 'Section_courante': '',  # not in this version, get back to original if needed
                    # 'Sujet_point': '', # not in this version, get back to original if needed
                    # "point_valeur_ptsodj": point_valeur_ptsodj,
                    # "point_id": point_id,
                    # ========================
                    # données du paragraphe
                    # ========================
                    "valeur_ptsodj": paragraphe.get("valeur_ptsodj"),
                    "ordinal_prise": paragraphe.get("ordinal_prise"),
                    "ordre_absolu_seance": paragraphe.get("ordre_absolu_seance"),
                    "id_acteur": paragraphe.get("id_acteur"),
                    "id_mandat": paragraphe.get("id_mandat"),
                    "code_grammaire": paragraphe.get("code_grammaire"),
                    "code_style": paragraphe.get("code_style"),
                    "code_parole": paragraphe.get("code_parole"),
                    "id_syceron": paragraphe.get("id_syceron"),
                    "roledebat": paragraphe.get("roledebat"),
                    # ========================
                    # données orateur + texte
                    # ========================
                    "nom_orateur": nom_orateur,
                    "qualite_orateur": qualite_orateur,
                    "id_orateur": id_orateur,
                    "stime": stime,
                    "texte": texte,
                }
            )

        return pd.DataFrame(rows)

    except Exception as e:
        print(f" Erreur dans {fichier_xml} : {e}")
        return pd.DataFrame()


# ======== Fonction traitement d'un dossier contenant les XML =========
def traiter_dossier_compte_rendu_lxml(
    dossier_path: str, pattern: str = "*.xml"
) -> pd.DataFrame:
    """
    Traite tous les fichiers XML d'un dossier avec la fonction extraire_paragraphes_lxml().
    """
    # fichiers = glob.glob(os.path.join(dossier_path, pattern))
    # lecture des fichiers avec un sorted pour reproductibilité
    fichiers = sorted(glob.glob(os.path.join(dossier_path, pattern)))

    if not fichiers:
        print(f"Aucun fichier XML trouvé dans {dossier_path}")
        return pd.DataFrame()

    df_cumul = []
    total = len(fichiers)
    print(f"Traitement de {total} fichiers XML...\n")

    for i, fichier in enumerate(fichiers, 1):
        nom = os.path.basename(fichier)
        print(f"[{i}/{total}] {nom}...", end=" ")

        df_temp = extraire_paragraphes_lxml(fichier)
        if not df_temp.empty:
            print(f"{len(df_temp)} lignes")
            df_cumul.append(df_temp)
        else:
            print("Vide ou erreur")

    if df_cumul:
        df_extraction = pd.concat(df_cumul, ignore_index=True)
        print(f"\n Extraction terminée : {len(df_extraction)} lignes consolidées")
        return df_extraction
    else:
        return pd.DataFrame()


# %% [markdown]
# ## 1.2 Extraction des données des XML et export CSV

# %%
# ==================================================================
# TRAITEMENT DES LÉGISLATURES SOUHAITÉES
# ==================================================================

# ========== Traitement des législatures ==========

# Traitement de la 16° législature
df_16 = traiter_dossier_compte_rendu_lxml("../data/raw/16-xml/compteRendu/")

# Traitement de la 15° législature
df_15 = traiter_dossier_compte_rendu_lxml("../data/raw/15-xml/compteRendu/")

# ========== Nettoyage fichiers doublons et congrès ==========

# UIDs à exclure (doublons / congrès)
"""
# nb tracabilité :
# NOTE: ici en manuel, mais pourrait imaginer une exclusion auto
# sur base de str.contains("Congrès du Parlement") dans session
# + ajouter deduplication sur base id_syceron + texte
# NOTE : la déduplication serait pas parfaite vs supr de fichier (voir dessous)
"""

uids_a_exclure = {
    "CRSANR5L16S2021O1N144",  # "faux" fichier en 16e (doublon de "CRSANR5L15S2021O1N144" de 2021)
    "CRSJOCGR5L15S2017E1N001",  # JO "Congrès du Parlement du 3 juillet 2017"
    "CRSANR5L15S2017O1N001",  # doublon AN JO "Congrès du Parlement du 3 juillet 2017"
    "CRSJOCGR5L15S2018E1N001",  # JO "Congrès du Parlement du 9 juillet 2018"
    "CRSCGR5L16S2024O1N001",  # CG "Congrès du Parlement du 4 mars 2024"
}

# Pour affichage (pas indispensable)
uids_trouvees_15 = uids_a_exclure & set(df_15["uid"])
uids_trouvees_16 = uids_a_exclure & set(df_16["uid"])

print(
    f"UIDs à exclure trouvés en df_15 : {len(uids_trouvees_15)}/{len(uids_a_exclure)}"
)
for uid in uids_trouvees_15:
    print(f"  - {uid}")

print(
    f"UIDs à exclure trouvés en df_16 : {len(uids_trouvees_16)}/{len(uids_a_exclure)}"
)
for uid in uids_trouvees_16:
    print(f"  - {uid}")

# puis suppression des lignes correspondantes
n15_avant, n16_avant = len(df_15), len(df_16)
df_15 = df_15[~df_15["uid"].isin(uids_a_exclure)]
df_16 = df_16[~df_16["uid"].isin(uids_a_exclure)]

print(f"Suppression UID ciblés - df_15 : {n15_avant - len(df_15)} ligne(s)")
print(f"Suppression UID ciblés - df_16 : {n16_avant - len(df_16)} ligne(s)")

# exports
df_16.to_csv("../data/interim/extract_16.csv", index=False, encoding="utf-8")
print(f"\n Export CSV df_16: ({df_16.shape[0]} lignes)")

df_15.to_csv("../data/interim/extract_15.csv", index=False, encoding="utf-8")
print(f"\n Export CSV df_15: ({df_15.shape[0]} lignes)")


# %% [markdown]
# ## 1.3 Fusion des législatures

# %%
# ==================================================================
# FUSION DES LÉGISLATURES
# concaténation de df_15 et df_16 (ou lecture depuis CSV si nécessaire)
# ==================================================================

# # si déjà en mémoire : utiliser df_15, df_16 ; sinon :
# df_15 = pd.read_csv("../data/interim/extract_15.csv", encoding="utf-8")
# df_16 = pd.read_csv("../data/interim/extract_16.csv", encoding="utf-8")

# si besoin de vérifier et aligner les colonnes
# Mais overkill ici, on est propre normalement

# cols15 = set(df_15.columns)
# cols16 = set(df_16.columns)
# for c in sorted((cols15 | cols16) - cols15):
#     df_15[c] = pd.NA
# for c in sorted((cols15 | cols16) - cols16):
#     df_16[c] = pd.NA

# concat
df_concat = pd.concat([df_15, df_16], ignore_index=True, sort=False)

# ==================================================================
# DÉDUPLICATION
# ici utilisée en fallback après suppression ciblée de fichiers
# ==================================================================
"""
# NOTE : Pourrait supr la déduplication car ici = 0
# mais parce qu'on est allé identifier et supr les fichier doublons !
# On garde si évolution des données ou de choix de clé déduplication
# et pour repérage si ajout données
# NOTE : la deduplication est pas parfaite vs supr de fichier
# = des lignes qui passent le filtre car pas des vrais doublons
# (entête fichier, sans texte, etc. ?)
# par ex 7 lignes d'écart sur le fichier CRSANR5L16S2021O1N144
# donc autant virer les fichiers proprement quand on identifie
# et utiliser la déduplication en fallback
"""

# conservation de la clé texte pour éviter de supprimer certaines lignes
# qui ont même id_syceron mais texte différent (didascalies, etc.)
# ici le faire sans l'uid puisque l'enjeu c'est possiblement des fichiers pas nommés pareil !
# NOTE : enjeu identification = parfois mêmes "mauvais" uid pour les fichiers doublons
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
        f"concat {len(df_15)} + {len(df_16)} -> {df_concat_before} lignes ; après déduplication {len(df_concat)} lignes"
    )

# export
df_concat.to_csv(
    "../data/interim/extract_15_16_concat.csv", index=False, encoding="utf-8"
)
print(f"\n Export CSV : ({df_concat.shape[0]} lignes)")

# %% [markdown]
# # 1.4 regroupement des interventions interrompues

# %%
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

# %%
# TODO: check les ordres obsolu seances et si ils marchent ou pas (str vs int etc.)
# TODO : check pq de rugy marche pas ? CRSANR5L15S2019O1N196. Pb question au gouv comme ministre ? -> nope sans doute ordre de tri mauvais typage

# %% [markdown]
# # Tests bug regroup interventions

# %%
# =========================
# A) Profil des clés de tri
# =========================
w = df.copy()

w["ordinal_prise_num"] = pd.to_numeric(w["ordinal_prise"], errors="coerce")
w["ordre_absolu_seance_num"] = pd.to_numeric(w["ordre_absolu_seance"], errors="coerce")

print("Lignes totales:", len(w))
print("NaN ordinal_prise:", w["ordinal_prise_num"].isna().sum())
print("NaN ordre_absolu_seance:", w["ordre_absolu_seance_num"].isna().sum())

# UID les plus "sales"
uid_diag = (
    w.groupby("uid", dropna=False)
    .agg(
        n=("uid", "size"),
        n_nan_ord=("ordinal_prise_num", lambda s: s.isna().sum()),
        n_nan_abs=("ordre_absolu_seance_num", lambda s: s.isna().sum()),
        n_acteurs_vides=("id_acteur", lambda s: s.fillna("").eq("").sum()),
    )
    .sort_values(["n_nan_ord", "n_nan_abs", "n_acteurs_vides"], ascending=False)
)
print(uid_diag.head(20))

# %%
# ===========================================
# B) Cas "interruption puis reprise" non fusionnés
# ===========================================
# On cherche le motif local:
# ligne i = intervention
# i+1 = INTERRUPTION_1_10
# i+2 = intervention même uid + même acteur
# mais un critère bloque la fusion

tmp = df.copy()
tmp["uid_norm"] = tmp["uid"].fillna("").astype(str)
tmp["id_acteur_norm"] = tmp["id_acteur"].fillna("").astype(str)
tmp["code_grammaire_norm"] = tmp["code_grammaire"].fillna("").astype(str)
tmp["code_parole_norm"] = tmp["code_parole"].fillna("non_précisé").astype(str)
tmp = tmp.reset_index(drop=True)

issues = []

for i in range(len(tmp) - 2):
    a = tmp.iloc[i]
    b = tmp.iloc[i + 1]
    c = tmp.iloc[i + 2]

    if b["code_grammaire_norm"] != "INTERRUPTION_1_10":
        continue
    if (
        a["code_grammaire_norm"] == "INTERRUPTION_1_10"
        or c["code_grammaire_norm"] == "INTERRUPTION_1_10"
    ):
        continue

    # reprise même orateur/séance attendue
    if (
        a["uid_norm"] == c["uid_norm"]
        and a["id_acteur_norm"] == c["id_acteur_norm"]
        and a["id_acteur_norm"] != ""
    ):
        blockers = []
        if a["code_grammaire_norm"] != c["code_grammaire_norm"]:
            blockers.append("code_grammaire_change")
        if a["code_parole_norm"] != c["code_parole_norm"]:
            blockers.append("code_parole_change")

        if blockers:
            issues.append(
                {
                    "uid": a["uid"],
                    "i": i,
                    "id_acteur": a["id_acteur"],
                    "nom_orateur": a.get("nom_orateur", None),
                    "ord_a": a.get("ordre_absolu_seance", None),
                    "ord_b": b.get("ordre_absolu_seance", None),
                    "ord_c": c.get("ordre_absolu_seance", None),
                    "id_syceron_a": a.get("id_syceron", None),
                    "id_syceron_b": b.get("id_syceron", None),
                    "id_syceron_c": c.get("id_syceron", None),
                    "blockers": "|".join(blockers),
                }
            )

issues_df = pd.DataFrame(issues)
print("Cas problématiques détectés:", len(issues_df))
display(issues_df.head(30))

# %%
# ======================================
# C) Comparaison avant/après tri (audit)
# ======================================
# Exécute regrouper 2 fois: sans tri, puis avec tri robuste, et compare.


def prepare_sorted_for_regroup(df_in):
    w = df_in.copy()
    w["uid_norm"] = w["uid"].fillna("").astype(str)

    w = w.reset_index(drop=False).rename(columns={"index": "_row_order"})
    w["ordinal_prise_num"] = pd.to_numeric(w["ordinal_prise"], errors="coerce")
    w["ordre_absolu_seance_num"] = pd.to_numeric(
        w["ordre_absolu_seance"], errors="coerce"
    )

    w = w.sort_values(
        by=["uid_norm", "ordinal_prise_num", "ordre_absolu_seance_num", "_row_order"],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True)

    return w.drop(
        columns=["ordinal_prise_num", "ordre_absolu_seance_num", "_row_order"]
    )


# 1) sans tri
out_no_sort = regrouper(df.copy())

# 2) avec tri robuste
df_sorted = prepare_sorted_for_regroup(df.copy())
out_sort = regrouper(df_sorted)

print("Shape sans tri:", out_no_sort.shape)
print("Shape avec tri robuste:", out_sort.shape)

# Où ça change le plus (par uid)
a = out_no_sort.groupby("uid", dropna=False).size().rename("n_no_sort")
b = out_sort.groupby("uid", dropna=False).size().rename("n_sort")
delta = pd.concat([a, b], axis=1).fillna(0)
delta["delta"] = delta["n_sort"] - delta["n_no_sort"]
delta = delta.sort_values("delta", ascending=False)
display(delta.head(30))

# %%
import pandas as pd


def build_triplets(df: pd.DataFrame) -> pd.DataFrame:
    t = df.copy().reset_index(drop=True)

    # Normalisations alignées avec regrouper
    t["uid_norm"] = t["uid"].fillna("").astype(str)
    t["id_acteur_norm"] = t["id_acteur"].fillna("").astype(str)
    t["code_grammaire_norm"] = t["code_grammaire"].fillna("").astype(str)
    t["code_parole_norm"] = t["code_parole"].fillna("non_précisé").astype(str)

    rows = []
    for i in range(len(t) - 2):
        a = t.iloc[i]
        b = t.iloc[i + 1]
        c = t.iloc[i + 2]

        # motif local: intervention -> interruption -> intervention
        if b["code_grammaire_norm"] != "INTERRUPTION_1_10":
            continue
        if a["code_grammaire_norm"] == "INTERRUPTION_1_10":
            continue
        if c["code_grammaire_norm"] == "INTERRUPTION_1_10":
            continue
        if a["uid_norm"] != c["uid_norm"]:
            continue

        same_actor = (a["id_acteur_norm"] != "") and (
            a["id_acteur_norm"] == c["id_acteur_norm"]
        )
        same_cg = a["code_grammaire_norm"] == c["code_grammaire_norm"]
        same_cp = a["code_parole_norm"] == c["code_parole_norm"]

        if same_actor and same_cg and same_cp:
            status = "fusion_attendue"
            reason = "ok_regles_fusion"
        else:
            status = "non_fusion"
            blockers = []
            if not same_actor:
                blockers.append("acteur_diff_ou_manquant")
            if not same_cg:
                blockers.append("code_grammaire_change")
            if not same_cp:
                blockers.append("code_parole_change")
            reason = "|".join(blockers)

        rows.append(
            {
                # clé de comparaison assez stable
                "triplet_key": f"{a.get('uid', '')}|{a.get('id_syceron', '')}|{b.get('id_syceron', '')}|{c.get('id_syceron', '')}",
                "uid": a.get("uid"),
                "nom_orateur_avant": a.get("nom_orateur"),
                "nom_orateur_reprise": c.get("nom_orateur"),
                "id_acteur_avant": a.get("id_acteur"),
                "id_acteur_reprise": c.get("id_acteur"),
                "ordre_avant": a.get("ordre_absolu_seance"),
                "ordre_interrupt": b.get("ordre_absolu_seance"),
                "ordre_reprise": c.get("ordre_absolu_seance"),
                "id_syceron_avant": a.get("id_syceron"),
                "id_syceron_interrupt": b.get("id_syceron"),
                "id_syceron_reprise": c.get("id_syceron"),
                "status": status,
                "reason": reason,
                "txt_avant": (a.get("texte") or "")[:180],
                "txt_interrupt": (b.get("texte") or "")[:180],
                "txt_reprise": (c.get("texte") or "")[:180],
            }
        )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.drop_duplicates(subset=["triplet_key"]).reset_index(drop=True)
    return out


def prepare_sorted_for_regroup(df_in: pd.DataFrame) -> pd.DataFrame:
    w = df_in.copy()
    w["uid_norm"] = w["uid"].fillna("").astype(str)
    w = w.reset_index(drop=False).rename(columns={"index": "_row_order"})
    w["ordinal_prise_num"] = pd.to_numeric(w["ordinal_prise"], errors="coerce")
    w["ordre_absolu_seance_num"] = pd.to_numeric(
        w["ordre_absolu_seance"], errors="coerce"
    )

    w = w.sort_values(
        by=["uid_norm", "ordinal_prise_num", "ordre_absolu_seance_num", "_row_order"],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True)

    return w.drop(
        columns=["ordinal_prise_num", "ordre_absolu_seance_num", "_row_order"]
    )


# 1) Cas sans tri
cas_no_sort = build_triplets(df).rename(
    columns={"status": "status_no_sort", "reason": "reason_no_sort"}
)

# 2) Cas avec tri robuste
df_sorted = prepare_sorted_for_regroup(df)
cas_sort = build_triplets(df_sorted).rename(
    columns={"status": "status_sort", "reason": "reason_sort"}
)

# 3) Alignement et détection des changements
cols_common = [
    "triplet_key",
    "uid",
    "nom_orateur_avant",
    "nom_orateur_reprise",
    "id_acteur_avant",
    "id_acteur_reprise",
    "ordre_avant",
    "ordre_interrupt",
    "ordre_reprise",
    "id_syceron_avant",
    "id_syceron_interrupt",
    "id_syceron_reprise",
    "txt_avant",
    "txt_interrupt",
    "txt_reprise",
]

cmp = cas_no_sort[cols_common + ["status_no_sort", "reason_no_sort"]].merge(
    cas_sort[["triplet_key", "status_sort", "reason_sort"]],
    on="triplet_key",
    how="outer",
)

# classification lisible
cmp["status_no_sort"] = cmp["status_no_sort"].fillna("absent")
cmp["status_sort"] = cmp["status_sort"].fillna("absent")
cmp["reason_no_sort"] = cmp["reason_no_sort"].fillna("")
cmp["reason_sort"] = cmp["reason_sort"].fillna("")

changes = cmp[cmp["status_no_sort"] != cmp["status_sort"]].copy()

print("Triplets sans tri :", len(cas_no_sort))
print("Triplets avec tri :", len(cas_sort))
print("Triplets dont le statut change :", len(changes))

display(changes.sort_values(["uid", "ordre_avant"]).head(100))

# Export
changes.to_csv(
    "../data/interim/cas_statut_change_apres_tri.csv", index=False, encoding="utf-8"
)
print("Export:", "../data/interim/cas_statut_change_apres_tri.csv")

# %%
changes[changes["nom_orateur_avant"].fillna("").str.contains("rugy", case=False)][
    [
        "uid",
        "status_no_sort",
        "status_sort",
        "reason_no_sort",
        "reason_sort",
        "ordre_avant",
        "ordre_interrupt",
        "ordre_reprise",
        "id_syceron_avant",
        "id_syceron_interrupt",
        "id_syceron_reprise",
    ]
].head(100)

# %%
# a tester :

import pandas as pd

# 1) ID stable pour tracer les mêmes lignes dans tous les scénarios
base = df.copy().reset_index(drop=True)
base["_row_id"] = base.index
base["uid_norm"] = base["uid"].fillna("").astype(str)

# 2) variantes de tri
v_no = base.copy()

v_ord = base.copy()
v_ord["ordinal_prise_num"] = pd.to_numeric(v_ord["ordinal_prise"], errors="coerce")
v_ord["ordre_abs_num"] = pd.to_numeric(v_ord["ordre_absolu_seance"], errors="coerce")
v_ord = v_ord.sort_values(
    ["uid_norm", "ordinal_prise_num", "ordre_abs_num", "_row_id"],
    kind="mergesort",
    na_position="last",
).reset_index(drop=True)

v_syc = base.copy()
v_syc["id_syceron_num"] = pd.to_numeric(v_syc["id_syceron"], errors="coerce")
n_nan = v_syc["id_syceron_num"].isna().sum()
if n_nan:
    raise ValueError(f"id_syceron manquant/non numérique: {n_nan}")
v_syc = v_syc.sort_values(["id_syceron_num", "_row_id"], kind="mergesort").reset_index(
    drop=True
)


# 3) où l'ordre diverge, par uid
def first_divergence_by_uid(a, b):
    out = []
    au = a.groupby("uid_norm")["_row_id"].apply(list)
    bu = b.groupby("uid_norm")["_row_id"].apply(list)
    for uid in sorted(set(au.index).intersection(bu.index)):
        la, lb = au[uid], bu[uid]
        m = min(len(la), len(lb))
        k = next((i for i in range(m) if la[i] != lb[i]), None)
        if k is not None or len(la) != len(lb):
            out.append(
                {
                    "uid": uid,
                    "len_a": len(la),
                    "len_b": len(lb),
                    "first_diff_pos": -1 if k is None else k,
                    "row_a_at_diff": None if k is None else la[k],
                    "row_b_at_diff": None if k is None else lb[k],
                }
            )
    return pd.DataFrame(out).sort_values(["first_diff_pos", "uid"])


diff_no_vs_ord = first_divergence_by_uid(v_no, v_ord)
diff_no_vs_syc = first_divergence_by_uid(v_no, v_syc)

print("UID avec divergence ordre (no vs ord):", len(diff_no_vs_ord))
print("UID avec divergence ordre (no vs syc):", len(diff_no_vs_syc))
display(diff_no_vs_ord.head(20))
display(diff_no_vs_syc.head(20))

# %%

# %%
