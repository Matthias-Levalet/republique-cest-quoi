# # ========== Possible correction manuelle des erreurs id_acteur =============

# CE FICHIER EST PAS EXECUTABLE EN L'ÉTAT, IL S'AGIT D'UNE TRACE D'UN BOUT DU NB 2


# NOTE: ce nettoyage est fait plus haut par une solution automatique
# Une trace manuelle est conservée ici pour information
# et pour de possibles volontés de réutilisations manuelles

# # Cas identifiés où id_acteur != id_orateur ET les noms diffèrent
# # -> on considère que le texte (et donc le nom inscrit) du CR fait foi
# # -> l'id_orateur est le bon, on l'utilise pour écraser id_acteur
# # (liste établie a posteriori via diagnostic id_pb, figée ici pour éviter de recalculer)

# ID_SYCERON_A_CORRIGER = {
#     3024324,  # "M. Hadrien Clouet"  -> identifié sous PA Tavel (PA794166)
#     3048161,  # "Mme Lisa Belluco"   -> identifié sous PA Trouvé (PA795164)
#     3180585,  # "M. Benjamin Lucas"  -> identifié sous PA Guedj (PA1567)
#     3182770,  # "M. Sacha Houlié"    -> identifié sous PA Dupond-Moretti (PA773443)
#     3204694,  # "M. Matthias Tavel"  -> identifié sous PA Trouvé (PA795164)
#     3205482,  # "M. Bruno Millienne" -> identifié sous PA Croizier (PA793716)
#     3243209,  # "M. Guillaume Kasbarian" -> identifié sous PA Grégoire (PA721764)
#     3260505,  # "M. Jean-René Cazeneuve" -> identifié sous PA Cazenave (PA793940)
#     3275233,  # "M. Frédéric Cabrolier"  -> identifié sous PA Minot (PA720630)
#     3286452,  # "M. Jean-René Cazeneuve" -> identifié sous PA Cazenave (PA793940)
#     3315478,  # "M. Hadrien Ghomi"   -> identifié sous PA Pellerin (PA795926)
#     3321985,  # "M. Manuel Bompard"  -> identifié sous PA Lecoq (PA335612)
#     3378626,  # "M. André Chassaigne"-> identifié sous PA Molac (PA607619)
#     3471389,  # "M. Grégoire de Fournas" -> identifié sous PA Prud'homme (PA719578)
# }

# # Identifier les cas (mask) et écraser id_acteur par id_orateur
# mask_syceron_pb = df["id_syceron"].isin(ID_SYCERON_A_CORRIGER)
# df.loc[mask_syceron_pb, "id_acteur"] = df.loc[mask_syceron_pb, "id_orateur"]

# # ========== FIN Correction manuelle si nécessaire =============
