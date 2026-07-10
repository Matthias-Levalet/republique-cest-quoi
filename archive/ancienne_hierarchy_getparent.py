# ======== Fonctions extraction infos depuis fichier XML =========


# Fonction extraction de la hiérarchie complète des points parents
# NOTE : conservé pour tracabilité, mais marche pas bien en cas
# reprise débats dans nouvelle séance, etc.
# parti sur nouvelle fonction
# IE : approche "ancêtres physiques" (getparent). Remonte les <point>
# qui contiennent RÉELLEMENT ce paragraphe dans l'arbre XML. Le niveau 1
# obtenu ici est donc "le point le plus haut physiquement trouvé pour CE
# paragraphe précis", pas nécessairement le point nivpoint=1 du document,
# si celui-ci est un FRÈRE plutôt qu'un ancêtre (cf. structure où les points
# de haut niveau sont juxtaposés sous <contenu>, pas toujours imbriqués).
# def extraire_hierarchie(paragraphe, ns):
#     """
#     Remonte la hiérarchie PHYSIQUE des points parents d'un paragraphe.
#     Retourne une liste ordonnée du niveau le plus haut au plus bas.
#     """
#     hierarchy = []
#     node = paragraphe.getparent()

#     while node is not None:
#         # NOTE : après test pas de findall nécessaire
#         # si besoin vérif :
#         # if node.tag == f"{{{ns['ns']}}}point":
#         #     textes_directs = node.findall("ns:texte", namespaces=ns)
#         #     if len(textes_directs) > 1:
#         #         print(
#         #             f"⚠️ point id_syceron={node.get('id_syceron')} a {len(textes_directs)} "
#         #             f"<texte> enfants directs (fichier en cours) — vérifier manuellement."
#         #         )
#         #     texte = textes_directs[0] if textes_directs else None
#         if node.tag == f"{{{ns['ns']}}}point":
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

#     hierarchy.reverse()  # du plus haut (physique) au plus bas
#     return hierarchy
