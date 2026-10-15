# %%
import pandas as pd
import re
import unicodedata

PATH_COMMISSIONS_MANDATS = "../data/raw/id-dep/datan_mandats.csv"

df = pd.read_csv(
    PATH_COMMISSIONS_MANDATS, low_memory=False, encoding="latin1", sep=";"
)  # format dégueu

df.shape

# %%
df.head()

# %%
df["typeOrgane"].value_counts()

# %%
cols = ["mpId", "organeRef"]  # à adapter

multi = (
    df.dropna(subset=["codeQualite"])
    .groupby(cols)["codeQualite"]
    .nunique()
)
multi = multi[multi > 1]

print(f"{len(multi)} couples député-commission avec plusieurs qualités")

# détail des cas concernés
if len(multi):
    detail = (
        df.set_index(cols)
        .loc[multi.index]
        .reset_index()
        .sort_values(cols)
    )
    display(detail)

# %%
import pandas as pd

d = df.copy()
d["dateDebut"] = pd.to_datetime(d["dateDebut"], errors="coerce")
# dateFin vide = mandat encore en cours
d["dateFin"] = pd.to_datetime(d["dateFin"], errors="coerce").fillna(pd.Timestamp.max)

d = d.sort_values(cols + ["dateDebut"])

# début du mandat suivant < fin du mandat courant => chevauchement
d["debut_suivant"] = d.groupby(cols)["dateDebut"].shift(-1)
d["qualite_suivante"] = d.groupby(cols)["codeQualite"].shift(-1)

chevauchements = d[
    (d["debut_suivant"] < d["dateFin"])
    & (d["qualite_suivante"] != d["codeQualite"])
]

print(f"{len(chevauchements)} chevauchements avec qualités différentes")
display(chevauchements[cols + ["codeQualite", "dateDebut", "dateFin",
                               "qualite_suivante", "debut_suivant"]])

# %%
