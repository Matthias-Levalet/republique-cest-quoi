# %% [markdown]
# # 1-1 - Extraction des données XML
# Extrait les paragraphes des comptes rendus de l'Assemblée nationale à partir
# des fichiers XML (lxml), pour les 15e et 16e législatures.
# Exclut les uids identifiés comme doublons/congrès et exporte un csv par législature.
# Écrit `extract_15.csv` et `extract_16.csv`, utilisés par l'étape suivante (1-2).

# %%
# TODO: check against NosDéputés/RegardsCitoyens <3
# TODO: exclure lamartine ?

# TODO: plus tard, aviser récupération des points de contexte parents (cf tentative Matthias)
# TODO: est-ce que les séquences d'interruption peuvent être identifiées directement
# depuis xml car elles seraient dans un bloc <interExtraction> ?

# %%
import os
import glob
from lxml import etree
import pandas as pd

PATH_XML_15 = "../data/raw/15-xml/compteRendu/"
PATH_XML_16 = "../data/raw/16-xml/compteRendu/"

PATH_SORTIE_15 = "../data/interim/1_1_extract_15.csv"
PATH_SORTIE_16 = "../data/interim/1_1_extract_16.csv"

# %% [markdown]
# ## Fonctions d'extraction


# %%
# # ==================================================================
# # FONCTIONS D'EXTRACTION DES DONNÉES
# # ==================================================================

# # ======== Fonctions extraction infos depuis fichier XML =========


# # Fonction extraction de la hiérarchie complète des points parents
# def extraire_hierarchie(paragraphe, ns):
#     """
#     Remonte la hiérarchie des points parents d'un paragraphe.
#     Retourne une liste ordonnée du niveau le plus haut au plus bas.
#     """
#     hierarchy = []
#     node = paragraphe.getparent()

#     while node is not None:
#         if node.tag == f"{{{ns['ns']}}}point":
#             # NOTE : encore risque éventuel que des <point> aient plusieurs <texte> ?
#             # pas géré ici tester texte = node.findall("ns:texte", namespaces=ns)
#             texte = node.find("ns:texte", namespaces=ns)
#             hierarchy.append(
#                 {
#                     "niveau": int(node.get("nivpoint", 0)),
#                     "code": node.get("code_grammaire"),
#                     "titre": (
#                         "".join(texte.itertext()).strip() if texte is not None else ""
#                     ),
#                     "valeur_ptsodj": node.get("valeur_ptsodj"),
#                     "art": node.get("art"),
#                     "adt": node.get("adt"),
#                     "bibard": node.get("bibard"),
#                 }
#             )
#         node = node.getparent()

#     hierarchy.reverse()  # du plus haut au plus bas
#     return hierarchy


# # Transformation hiérarchie vers colones
# def _hierarchie_to_colonnes(hierarchy):
#     """
#     Transforme la liste de hiérarchie en colonnes exploitables :
#     - point_structure_complete : "titre1 > titre2 > titre3"
#     - point_niveau_1/2/3 : titres par niveau
#     """
#     titres = [h["titre"] for h in hierarchy if h["titre"]]
#     structure = " > ".join(titres)

#     return {
#         "point_structure_complete": structure,
#         "point_nb_niveaux": len(hierarchy),
#         "point_niveau_1": hierarchy[0]["titre"] if len(hierarchy) > 0 else "",
#         "point_niveau_2": hierarchy[1]["titre"] if len(hierarchy) > 1 else "",
#         "point_niveau_3": hierarchy[2]["titre"] if len(hierarchy) > 2 else "",
#         # parent direct du paragraphe (peut être vide si <point> sans <texte>) : amendements, etc. ?
#         "point_niveau_last": hierarchy[-1]["titre"] if hierarchy else "",
#         # dernier niveau avec un titre non vide (fallback pour amendements etc.)
#         "point_niveau_last_known": next(
#             (h["titre"] for h in reversed(hierarchy) if h["titre"]), ""
#         ),
#         "point_bibard": hierarchy[-1].get("bibard") if hierarchy else None,
#         "point_art": hierarchy[-1].get("art") if hierarchy else None,
#     }


# # Fonction d'extraction des infos pour les paragraphes
# def extraire_paragraphes_lxml(fichier_xml: str) -> pd.DataFrame:
#     """
#     Extrait les paragraphes d'un fichier XML de compte rendu en utilisant lxml.
#     """
#     try:
#         tree = etree.parse(fichier_xml)
#         root = tree.getroot()
#         ns = {"ns": "http://schemas.assemblee-nationale.fr/referentiel"}

#         meta = {
#             "uid": root.findtext("ns:uid", namespaces=ns),
#             "SeanceRef": root.findtext("ns:seanceRef", namespaces=ns),  # pas partout
#             "SessionRef": root.findtext("ns:sessionRef", namespaces=ns),  # pas partout
#         }
#         meta_tags = [
#             "dateSeance",
#             "dateSeanceJour",
#             "numSeanceJour",
#             "numSeance",
#             "typeAssemblee",
#             "legislature",
#             "session",
#             "nomFichierJo",
#             "presidentSeance",
#         ]
#         for tag in meta_tags:
#             meta[tag] = root.findtext(f".//ns:{tag}", namespaces=ns)

#         rows = []

#         for paragraphe in root.xpath(".//ns:paragraphe", namespaces=ns):
#             # TODO : check cet ajout de la hiérarchie complète
#             hierarchy = extraire_hierarchie(paragraphe, ns)
#             hier_cols = _hierarchie_to_colonnes(hierarchy)

#             # point_type = code_grammaire du <point> parent direct (= dernier niveau hiérarchie)
#             point_type = hierarchy[-1]["code"] if hierarchy else None

#             texte_elem = paragraphe.find("ns:texte", namespaces=ns)
#             texte = (
#                 "".join(texte_elem.itertext()).strip()
#                 if texte_elem is not None
#                 else None
#             )
#             stime = texte_elem.get("stime") if texte_elem is not None else None

#             # Récupérer les informations de l'orateur
#             # (= celles présentes dans la balise <orateur>, pas forcément dans les attributs du paragraphe)
#             orateur = paragraphe.find(".//ns:orateur", namespaces=ns)
#             nom_orateur = (
#                 orateur.findtext("ns:nom", namespaces=ns)
#                 if orateur is not None
#                 else None
#             )
#             qualite_orateur = (
#                 orateur.findtext("ns:qualite", namespaces=ns)
#                 if orateur is not None
#                 else None
#             )
#             id_orateur = (
#                 orateur.findtext("ns:id", namespaces=ns)
#                 if orateur is not None
#                 else None
#             )

#             # toper désormais toutes les infos
#             # garder apparent pour éventuels choix ou recodages des noms plutôt que des machins type `**meta`
#             rows.append(
#                 {
#                     # ===== Métadonnées de la séance =====
#                     "uid": meta["uid"],
#                     "SeanceRef": meta["SeanceRef"],
#                     "SessionRef": meta["SessionRef"],
#                     "dateSeance": meta["dateSeance"],
#                     "dateSeanceJour": meta["dateSeanceJour"],
#                     "numSeanceJour": meta["numSeanceJour"],
#                     "numSeance": meta["numSeance"],
#                     "typeAssemblee": meta["typeAssemblee"],
#                     "legislature": meta["legislature"],
#                     "session": meta["session"],
#                     "nomFichierJo": meta["nomFichierJo"],
#                     "presidentSeance": meta["presidentSeance"],
#                     # ===== données contexte - points parents / Hiérarchie complète =====
#                     "point_structure_complete": hier_cols["point_structure_complete"],
#                     "point_nb_niveaux": hier_cols["point_nb_niveaux"],
#                     "point_niveau_1": hier_cols["point_niveau_1"],
#                     "point_niveau_2": hier_cols["point_niveau_2"],
#                     "point_niveau_3": hier_cols["point_niveau_3"],
#                     "point_niveau_last": hier_cols["point_niveau_last"],
#                     "point_niveau_last_known": hier_cols["point_niveau_last_known"],
#                     "point_type": point_type,
#                     "point_bibard": hier_cols["point_bibard"],  # TODO : virer ?
#                     "point_art": hier_cols["point_art"],  # TODO : virer ?
#                     # ===== données du paragraphe =====
#                     "valeur_ptsodj": paragraphe.get("valeur_ptsodj"),
#                     "ordinal_prise": paragraphe.get("ordinal_prise"),
#                     "ordre_absolu_seance": paragraphe.get("ordre_absolu_seance"),
#                     "id_acteur": paragraphe.get("id_acteur"),
#                     "id_mandat": paragraphe.get("id_mandat"),
#                     "code_grammaire": paragraphe.get("code_grammaire"),
#                     "code_style": paragraphe.get("code_style"),
#                     "code_parole": paragraphe.get("code_parole"),
#                     "id_syceron": paragraphe.get("id_syceron"),
#                     "roledebat": paragraphe.get("roledebat"),
#                     # ===== données orateur + texte =====
#                     "nom_orateur": nom_orateur,
#                     "qualite_orateur": qualite_orateur,
#                     "id_orateur": id_orateur,
#                     "stime": stime,
#                     "texte": texte,
#                 }
#             )

#         return pd.DataFrame(rows)

#     except Exception as e:
#         print(f" Erreur dans {fichier_xml} : {e}")
#         return pd.DataFrame()


# # ======== Fonction traitement d'un dossier contenant les XML =========
# def traiter_dossier_compte_rendu_lxml(
#     dossier_path: str, pattern: str = "*.xml"
# ) -> pd.DataFrame:
#     """
#     Traite tous les fichiers XML d'un dossier avec la fonction extraire_paragraphes_lxml().
#     """
#     # lecture des fichiers avec un sorted pour reproductibilité
#     fichiers = sorted(glob.glob(os.path.join(dossier_path, pattern)))

#     if not fichiers:
#         print(f"Aucun fichier XML trouvé dans {dossier_path}")
#         return pd.DataFrame()

#     df_cumul = []
#     total = len(fichiers)
#     print(f"Traitement de {total} fichiers XML...\n")

#     for i, fichier in enumerate(fichiers, 1):
#         nom = os.path.basename(fichier)
#         print(f"[{i}/{total}] {nom}...", end=" ")

#         df_temp = extraire_paragraphes_lxml(fichier)
#         if not df_temp.empty:
#             print(f"{len(df_temp)} lignes")
#             df_cumul.append(df_temp)
#         else:
#             print("Vide ou erreur")

#     if df_cumul:
#         df_extraction = pd.concat(df_cumul, ignore_index=True)
#         print(f"\n Extraction terminée : {len(df_extraction)} lignes consolidées")
#         return df_extraction
#     else:
#         return pd.DataFrame()

# %%
# TEST ALTERNATIF

# ==================================================================
# FONCTIONS D'EXTRACTION DES DONNÉES
# ==================================================================

# ======== Fonctions extraction infos depuis fichier XML =========


# Fonction extraction de la hiérarchie complète des points parents
# NOTE : approche "ancêtres physiques" (getparent). Remonte les <point>
# qui contiennent RÉELLEMENT ce paragraphe dans l'arbre XML. Le niveau 1
# obtenu ici est donc "le point le plus haut physiquement trouvé pour CE
# paragraphe précis" -- pas nécessairement le point nivpoint=1 du document,
# si celui-ci est un FRÈRE plutôt qu'un ancêtre (cf. structure où les points
# de haut niveau sont juxtaposés sous <contenu>, pas toujours imbriqués).
def extraire_hierarchie(paragraphe, ns):
    """
    Remonte la hiérarchie PHYSIQUE des points parents d'un paragraphe.
    Retourne une liste ordonnée du niveau le plus haut au plus bas.
    """
    hierarchy = []
    node = paragraphe.getparent()

    while node is not None:
        # NOTE : après test pas de findall nécessaire
        # si besoin vérif :
        # if node.tag == f"{{{ns['ns']}}}point":
        #     textes_directs = node.findall("ns:texte", namespaces=ns)
        #     if len(textes_directs) > 1:
        #         print(
        #             f"⚠️ point id_syceron={node.get('id_syceron')} a {len(textes_directs)} "
        #             f"<texte> enfants directs (fichier en cours) — vérifier manuellement."
        #         )
        #     texte = textes_directs[0] if textes_directs else None
        if node.tag == f"{{{ns['ns']}}}point":
            texte = node.find("ns:texte", namespaces=ns)
            hierarchy.append(
                {
                    "niveau": int(node.get("nivpoint", 0)),
                    "code": node.get("code_grammaire"),
                    "titre": (
                        "".join(texte.itertext()).strip() if texte is not None else ""
                    ),
                    "valeur_ptsodj": node.get("valeur_ptsodj"),
                    "art": node.get("art"),
                    "adt": node.get("adt"),
                    "bibard": node.get("bibard"),
                }
            )
        node = node.getparent()

    hierarchy.reverse()  # du plus haut (physique) au plus bas
    return hierarchy


# Fonction alternative : hiérarchie LOGIQUE via nivpoint, pré-calculée une
# fois par fichier (ordre du document), pas par remontée d'ancêtres.
# NOTE : contrairement à extraire_hierarchie(), ceci capture le vrai
# nivpoint=1 du document même quand il s'agit d'un FRÈRE physique du point
# où se trouve le paragraphe (cf. tests sur CRSANR5L16S2023O1N087.xml :
# 832/835 paragraphes avaient un niveau_1 physique différent du niveau_1
# logique réel). nivpoint="99" (suspensions) n'affecte pas ce contexte.
def construire_contexte_nivpoint(root, ns):
    """
    Parcourt <contenu> en DFS, dans l'ordre du document, et associe à
    chaque paragraphe (par id_syceron) sa hiérarchie logique de points
    actifs à ce moment, indexée par nivpoint plutôt que par imbrication
    physique. Retourne {id_syceron: hierarchy_list}, hierarchy_list ayant
    le même format que extraire_hierarchie() pour rester compatible avec
    _hierarchie_to_colonnes().
    """
    contenu = root.find("ns:contenu", namespaces=ns)
    if contenu is None:
        return {}

    contexte_par_niveau = {}
    resultat = {}

    def walk(elem):
        for child in elem:
            tag = etree.QName(child).localname

            if tag == "point":
                niv_str = child.get("nivpoint")
                niv = int(niv_str) if niv_str and niv_str.isdigit() else None

                if niv is not None and niv != 99:
                    texte_elem = child.find("ns:texte", namespaces=ns)
                    titre = (
                        "".join(texte_elem.itertext()).strip()
                        if texte_elem is not None
                        else ""
                    )
                    # un nouveau point de niveau N invalide tout contexte >= N
                    for k in [k for k in contexte_par_niveau if k >= niv]:
                        del contexte_par_niveau[k]
                    contexte_par_niveau[niv] = {
                        "niveau": niv,
                        "code": child.get("code_grammaire"),
                        "titre": titre,
                        "valeur_ptsodj": child.get("valeur_ptsodj"),
                        "art": child.get("art"),
                        "adt": child.get("adt"),
                        "bibard": child.get("bibard"),
                    }

                walk(child)  # gère à la fois sous-points imbriqués ET paragraphe direct

            elif tag == "paragraphe":
                id_syc = child.get("id_syceron")
                if id_syc:
                    resultat[id_syc] = [
                        contexte_par_niveau[k] for k in sorted(contexte_par_niveau)
                    ]
            else:
                walk(child)  # interExtraction, ouvertureSeance, finSeance, etc.

    walk(contenu)
    return resultat


# Transformation hiérarchie vers colonnes (inchangée, réutilisée pour les 2 approches)
def _hierarchie_to_colonnes(hierarchy):
    """
    Transforme une liste de hiérarchie (physique OU logique, même format)
    en colonnes exploitables.
    """
    titres = [h["titre"] for h in hierarchy if h["titre"]]
    structure = " > ".join(titres)

    return {
        "point_structure_complete": structure,
        "point_nb_niveaux": len(hierarchy),
        "point_niveau_1": hierarchy[0]["titre"] if len(hierarchy) > 0 else "",
        "point_niveau_2": hierarchy[1]["titre"] if len(hierarchy) > 1 else "",
        "point_niveau_3": hierarchy[2]["titre"] if len(hierarchy) > 2 else "",
        "point_niveau_last": hierarchy[-1]["titre"] if hierarchy else "",
        "point_niveau_last_known": next(
            (h["titre"] for h in reversed(hierarchy) if h["titre"]), ""
        ),
        "point_bibard": hierarchy[-1].get("bibard") if hierarchy else None,
        "point_art": hierarchy[-1].get("art") if hierarchy else None,
    }


# Fonction d'extraction des infos pour les paragraphes
def extraire_paragraphes_lxml(fichier_xml: str) -> pd.DataFrame:
    """
    Extrait les paragraphes d'un fichier XML de compte rendu en utilisant lxml.
    Calcule les DEUX hiérarchies en parallèle (physique et nivpoint) pour
    permettre une comparaison directe sur votre jeu de données réel, avant
    de trancher laquelle garder (ou si les deux sont utiles ensemble).
    """
    try:
        tree = etree.parse(fichier_xml)
        root = tree.getroot()
        ns = {"ns": "http://schemas.assemblee-nationale.fr/referentiel"}

        meta = {
            "uid": root.findtext("ns:uid", namespaces=ns),
            "SeanceRef": root.findtext("ns:seanceRef", namespaces=ns),
            "SessionRef": root.findtext("ns:sessionRef", namespaces=ns),
        }
        meta_tags = [
            "dateSeance", "dateSeanceJour", "numSeanceJour", "numSeance",
            "typeAssemblee", "legislature", "session", "nomFichierJo", "presidentSeance",
        ]
        for tag in meta_tags:
            meta[tag] = root.findtext(f".//ns:{tag}", namespaces=ns)

        # pré-calcul de la hiérarchie nivpoint (une seule passe par fichier)
        contexte_nivpoint = construire_contexte_nivpoint(root, ns)

        rows = []

        for paragraphe in root.xpath(".//ns:paragraphe", namespaces=ns):
            # --- Hiérarchie physique (votre approche existante) ---
            hierarchy_physique = extraire_hierarchie(paragraphe, ns)
            cols_physique = _hierarchie_to_colonnes(hierarchy_physique)
            point_type = hierarchy_physique[-1]["code"] if hierarchy_physique else None

            # --- Hiérarchie nivpoint (nouvelle approche, par comparaison) ---
            id_syc = paragraphe.get("id_syceron")
            hierarchy_nivpoint = contexte_nivpoint.get(id_syc, [])
            cols_nivpoint = _hierarchie_to_colonnes(hierarchy_nivpoint)

            texte_elem = paragraphe.find("ns:texte", namespaces=ns)
            texte = (
                "".join(texte_elem.itertext()).strip() if texte_elem is not None else None
            )
            stime = texte_elem.get("stime") if texte_elem is not None else None

            orateur = paragraphe.find(".//ns:orateur", namespaces=ns)
            nom_orateur = orateur.findtext("ns:nom", namespaces=ns) if orateur is not None else None
            qualite_orateur = orateur.findtext("ns:qualite", namespaces=ns) if orateur is not None else None
            id_orateur = orateur.findtext("ns:id", namespaces=ns) if orateur is not None else None

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
                    # ===== Hiérarchie PHYSIQUE (getparent, votre approche) =====
                    "point_structure_complete": cols_physique["point_structure_complete"],
                    "point_nb_niveaux": cols_physique["point_nb_niveaux"],
                    "point_niveau_1": cols_physique["point_niveau_1"],
                    "point_niveau_2": cols_physique["point_niveau_2"],
                    "point_niveau_3": cols_physique["point_niveau_3"],
                    "point_niveau_last": cols_physique["point_niveau_last"],
                    "point_niveau_last_known": cols_physique["point_niveau_last_known"],
                    "point_type": point_type,
                    "point_bibard": cols_physique["point_bibard"],
                    "point_art": cols_physique["point_art"],
                    # ===== Hiérarchie NIVPOINT (nouvelle, pour comparaison) =====
                    "point_structure_complete_nivpoint": cols_nivpoint["point_structure_complete"],
                    "point_nb_niveaux_nivpoint": cols_nivpoint["point_nb_niveaux"],
                    "point_niveau_1_nivpoint": cols_nivpoint["point_niveau_1"],
                    "point_niveau_2_nivpoint": cols_nivpoint["point_niveau_2"],
                    "point_niveau_3_nivpoint": cols_nivpoint["point_niveau_3"],
                    "point_niveau_last_nivpoint": cols_nivpoint["point_niveau_last"],
                    "point_niveau_last_known_nivpoint": cols_nivpoint["point_niveau_last_known"],
                    "point_bibard_nivpoint": cols_nivpoint["point_bibard"],
                    "point_art_nivpoint": cols_nivpoint["point_art"],
                    # ===== Données du paragraphe =====
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
                    # ===== Données orateur + texte =====
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
# ==================================================================
# TRAITEMENT DES LÉGISLATURES SOUHAITÉES
# ==================================================================

# ========== Traitement des législatures ==========

df_16 = traiter_dossier_compte_rendu_lxml(PATH_XML_16)
df_15 = traiter_dossier_compte_rendu_lxml(PATH_XML_15)


# %% [markdown]
# ## Nettoyage fichiers doublons et congrès
# nb traçabilité : exclusion manuelle ici, mais pourrait s'automatiser sur base
# de str.contains("Congrès du Parlement") dans `session`, complétée par une
# déduplication sur id_syceron + texte (imparfaite par rapport à l'exclusion
# ciblée de fichiers, voir 1-2).

# %%
# ========== Nettoyage fichiers doublons et congrès ==========

uids_a_exclure = {
    "CRSANR5L16S2021O1N144",  # "faux" fichier en 16e (doublon de "CRSANR5L15S2021O1N144" de 2021)
    "CRSJOCGR5L15S2017E1N001",  # JO "Congrès du Parlement du 3 juillet 2017"
    "CRSANR5L15S2017O1N001",  # doublon AN JO "Congrès du Parlement du 3 juillet 2017"
    "CRSJOCGR5L15S2018E1N001",  # JO "Congrès du Parlement du 9 juillet 2018"
    "CRSCGR5L16S2024O1N001",  # CG "Congrès du Parlement du 4 mars 2024"
    "CRSANR5L15S2022O1N168",  # séance spéciale congrès intervention Zelensky
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

# %% [markdown]
# ## Export

# %%
# ========== Exports ==========
df_15.to_csv(PATH_SORTIE_15, index=False, encoding="utf-8")
print(f"\n Export CSV df_15: ({df_15.shape[0]} lignes) -> {PATH_SORTIE_15}")

df_16.to_csv(PATH_SORTIE_16, index=False, encoding="utf-8")
print(f"\n Export CSV df_16: ({df_16.shape[0]} lignes) -> {PATH_SORTIE_16}")
