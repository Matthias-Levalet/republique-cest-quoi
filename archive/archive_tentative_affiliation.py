######################################################################
# GARDE POUR TRACE MAIS A CHANGÉ LOGIQUE POUR TRUC PLUS SIMPLE/ROBUSTE
######################################################################

# EN cours : créer une fonction de renvoi du parti dans le temps
# Et donc galérer avec les dates d'intervention vs date de début et fin affiliation ?

# TODO: trouver ce qui merde car pour l'instant fait avec les pieds
# pistes : cas des sans id_orateur ? cas des interv sans date ?
# souci : tous ceux qui ont pas d'ID député > pas de renvoi de date début ou fin, etc.
# Changer la logique ? > au final pas gros fichier
# On peut partir sur lookup


print("shape avant merge: ", df.shape)
# Garder uniquement les colonnes utiles
df_affiliation = df_affiliation[["mpId", "dateDebut", "dateFin", "parti_recod"]].copy()

# Conversion des dates affiliation en datetime
df_affiliation["dateDebut"] = pd.to_datetime(
    df_affiliation["dateDebut"], errors="raise"
)
df_affiliation["dateFin"] = pd.to_datetime(df_affiliation["dateFin"], errors="raise")


# Conversion date intervention
df["DateSeance_ts"] = pd.to_datetime(df["DateSeance"], format="%Y%m%d%H%M%S%f")

# merge sur l'identifiant (ID_orateur vs mpId)
df_merged = df.merge(df_affiliation, left_on="ID_orateur", right_on="mpId", how="left")

# Garder uniquement les affiliations valides à la date de l’intervention
df_match_affiliation = df_merged[
    (df_merged["DateSeance_ts"] >= df_merged["dateDebut"])
    & (df_merged["DateSeance_ts"] <= df_merged["dateFin"])
]

print("shape après merge:", df_match_affiliation.shape)
