# %% [markdown]
# # 1-1 - Extraction des données XML
# Extrait les paragraphes des comptes rendus de l'Assemblée nationale à partir
# des fichiers XML (lxml), pour les 15e et 16e législatures.
# Exclut les uids identifiés comme doublons/congrès et exporte un csv par législature.
# Écrit `extract_15.csv` et `extract_16.csv`, utilisés par l'étape suivante (1-2).

# %%
# TODO: plus tard, aviser récupération des points de contexte parents (cf tentative Matthias)
# TODO: est-ce que les séquences d'interruption peuvent être identifiées directement
#       depuis xml car elles seraient dans un bloc <interExtraction> ?
# TODO: check against NosDéputés/RegardsCitoyens <3

# %%
import os
import glob
from lxml import etree
import pandas as pd

PATH_XML_16 = "../data/raw/16-xml/compteRendu/"
PATH_XML_15 = "../data/raw/15-xml/compteRendu/"

PATH_SORTIE_16 = "../data/interim/extract_16.csv"
PATH_SORTIE_15 = "../data/interim/extract_15.csv"

# %% [markdown]
# ## Fonctions d'extraction


# %%


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
            # Naviguer vers le <point> parent et récupérer les infos
            point = paragraphe.getparent()
            while point is not None and point.tag != f"{{{ns['ns']}}}point":
                point = point.getparent()

            point_type = point.get("code_grammaire") if point is not None else None

            # utiliser itertext() pour reconstruire le contenu complet
            # (findtext() ignore les sous-balises et perd du texte)
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
            # (= celles présentes dans la balise <orateur>, pas forcément dans les attributs du paragraphe)
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
                    # ===== Métadonnées de la séance =====
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
                    # ===== Données du point parent (contexte) =====
                    "point_titre": point_title,
                    "point_type": point_type,
                    # 'Sous_titre': '',  # not in this version, get back to original if needed
                    # 'Contexte_hierarchique': '',  # not in this version, get back to original if needed
                    # 'Section_courante': '',  # not in this version, get back to original if needed
                    # 'Sujet_point': '', # not in this version, get back to original if needed
                    # "point_valeur_ptsodj": point_valeur_ptsodj,
                    # "point_id": point_id,
                    # ===== données du paragraphe =====
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
                    # ===== données orateur + texte =====
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
# ## Traitement des législatures souhaitées

# %%
df_16 = traiter_dossier_compte_rendu_lxml(PATH_XML_16)
df_15 = traiter_dossier_compte_rendu_lxml(PATH_XML_15)

# %% [markdown]
# ## Nettoyage fichiers doublons et congrès
# nb traçabilité : exclusion manuelle ici, mais pourrait s'automatiser sur base
# de str.contains("Congrès du Parlement") dans `session`, complétée par une
# déduplication sur id_syceron + texte (imparfaite par rapport à l'exclusion
# ciblée de fichiers, voir 1-2).

# %%
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

n15_avant, n16_avant = len(df_15), len(df_16)
df_15 = df_15[~df_15["uid"].isin(uids_a_exclure)]
df_16 = df_16[~df_16["uid"].isin(uids_a_exclure)]

print(f"Suppression UID ciblés - df_15 : {n15_avant - len(df_15)} ligne(s)")
print(f"Suppression UID ciblés - df_16 : {n16_avant - len(df_16)} ligne(s)")

# %% [markdown]
# ## Export

# %%
df_16.to_csv(PATH_SORTIE_16, index=False, encoding="utf-8")
print(f"\n Export CSV df_16: ({df_16.shape[0]} lignes) -> {PATH_SORTIE_16}")

df_15.to_csv(PATH_SORTIE_15, index=False, encoding="utf-8")
print(f"\n Export CSV df_15: ({df_15.shape[0]} lignes) -> {PATH_SORTIE_15}")
