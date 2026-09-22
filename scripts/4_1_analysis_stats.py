# %% [markdown]
# # 4.1 Analysis-stats

# %% [markdown]
# - premiers tests à l'arrache

# %%
# TODO: LÉO : REPRENDRE DEPUIS Analyses.ipynb de matthias dans explo.

# %%
import pandas as pd
import plotly.express as px

# %%
# TODO: aviser si vire id_orateur et utiliser id_acteur partout

df = pd.read_csv(
    "../data/interim/df_repu.csv",
    low_memory=False,
    dtype={
        "ID_orateur": str  # désormais géré avant (ajout PA et id_acteur) vire quand mettra au propre
    },
)

# %%
df.shape

# %% [markdown]
# ### dynamique temporelle

# %%
# recréer la colonne DateSeance (dt pas reconnu à l'import)
df["DateSeance_ts"] = pd.to_datetime(df["DateSeance"], format="%Y%m%d%H%M%S%f")
df["DateSeance_day"] = df["DateSeance_ts"].dt.normalize()  # guess it works


# %%
fig_time = px.bar(df.resample("W", on="DateSeance_day").size())

fig_time.update_layout(
    title="Nombre de mentions de la notion de république",  # ajouter un titre
    xaxis_title="Date",
    yaxis_title="Nombre de mentions",  # renommer les étiquettes d'axes
    template="plotly_white",  # changer le style du graphique
    showlegend=False,
)  # masquer la légende

# Afficher le graphique
fig_time.show()

# %%
fig_time.write_html("../reports/figures/fig_time.html")

# %%
# aficher les 25 dates les plus fréquentes sous forme de tableau
table = df["DateSeance_day"].value_counts()[0:20].reset_index()
table = table.rename(columns={"count": "Nombre de mentions"})
table

# %% [markdown]
# ### groupes

# %%
df["groupeAbrev"].value_counts()

# %%
df["parti_affiliation"].value_counts()

# %%
# TODO: use parti_affiliation instead of groupeAbrev

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Calculer les mentions par groupe et par jour/semaine/mois/année
df_grouped = (
    df.groupby([pd.Grouper(key="DateSeance_day", freq="MS"), "groupeAbrev"])
    .size()
    .reset_index(name="mentions")
)

# Trier les groupes par nombre total de mentions
counts = df["groupeAbrev"].value_counts()
groupes = counts.index.tolist()

cols = 4
rows = (len(groupes) + cols - 1) // cols  # nombre de lignes nécessaires

# Calcul de la valeur maximale pour fixer la même échelle Y
max_y = df_grouped["mentions"].max()

fig_group = make_subplots(
    rows=rows, cols=cols, shared_xaxes=True, subplot_titles=groupes
)

for idx, groupe in enumerate(groupes):
    row = idx // cols + 1
    col = idx % cols + 1

    data_groupe = df_grouped[df_grouped["groupeAbrev"] == groupe]
    fig_group.add_trace(
        go.Bar(x=data_groupe["DateSeance_day"], y=data_groupe["mentions"], name=groupe),
        row=row,
        col=col,
    )

fig_group.update_layout(
    height=300 * rows,
    width=1200,
    title_text="Dynamique temporelle des mentions de l'idée de république par groupe parlementaire",
    showlegend=False,
    template="plotly_white",
)

for row in range(1, rows + 1):
    for col in range(1, cols + 1):
        fig_group.update_yaxes(range=[0, max_y], row=row, col=col)

for col in range(1, cols + 1):
    fig_group.update_xaxes(title_text="Date", row=rows, col=col)

for row in range(1, rows + 1):
    fig_group.update_yaxes(title_text="Nombre de mentions", row=row, col=1)

fig_group.show()


# %%
fig_group.write_html("../reports/figures/fig_group.html")

# %% [markdown]
# ### parlementaires

# %%
df["Nom_orateur"].value_counts()[0:20]

# %%
import plotly.express as px

fig_top_orateurs = px.bar(
    df["Nom_orateur"].value_counts()[0:10],
    # x=top_counts.index,
    # y=top_counts.values,
    labels={"value": "Nombre de mentions", "Nom_orateur": "Orateur"},
    title="Top 20 orateurs par nombre de mentions",
    template="plotly_white",
)
fig_top_orateurs.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,
)
fig_top_orateurs.show()

# %%
fig_top_orateurs.write_html("../reports/figures/fig_top_orateurs.html")

# %%
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Top 20 orateurs
top_orateurs = df["Nom_orateur"].value_counts().index[:20].tolist()

# Grouper par semaine et orateur
df_orateur = df[df["Nom_orateur"].isin(top_orateurs)]
df_grouped_orateur = (
    df_orateur.groupby([pd.Grouper(key="DateSeance_day", freq="MS"), "Nom_orateur"])
    .size()
    .reset_index(name="mentions")
)

cols = 4
rows = (len(top_orateurs) + cols - 1) // cols
max_y = df_grouped_orateur["mentions"].max()

fig_orateurs_time = make_subplots(
    rows=rows, cols=cols, shared_xaxes=True, subplot_titles=top_orateurs
)

for idx, orateur in enumerate(top_orateurs):
    row = idx // cols + 1
    col = idx % cols + 1
    data_orateur = df_grouped_orateur[df_grouped_orateur["Nom_orateur"] == orateur]
    fig_orateurs_time.add_trace(
        go.Bar(
            x=data_orateur["DateSeance_day"], y=data_orateur["mentions"], name=orateur
        ),
        row=row,
        col=col,
    )

fig_orateurs_time.update_layout(
    height=300 * rows,
    width=1200,
    title_text="Dynamique temporelle des mentions par orateur",
    showlegend=False,
    template="plotly_white",
)

for row in range(1, rows + 1):
    for col in range(1, cols + 1):
        fig_orateurs_time.update_yaxes(range=[0, max_y], row=row, col=col)

for col in range(1, cols + 1):
    fig_orateurs_time.update_xaxes(title_text="Date", row=rows, col=col)

for row in range(1, rows + 1):
    fig_orateurs_time.update_yaxes(title_text="Nombre de mentions", row=row, col=1)

fig_orateurs_time.show()


# %%
fig_orateurs_time.write_html("../reports/figures/fig_orateurs_time.html")

# %%
# # BOF
# # Grouper par date et orateur
# # Top XX orateurs
# top_orateurs = df["Nom_orateur"].value_counts().index[:10].tolist()

# df_orateur_grouped = (
#     df[df["Nom_orateur"].isin(top_orateurs)]
#     .groupby([pd.Grouper(key="DateSeance_day", freq="W"), "Nom_orateur"])
#     .size()
#     .reset_index(name="mentions")
# )

# fig = px.line(
#     df_orateur_grouped,
#     x="DateSeance_day",
#     y="mentions",
#     color="Nom_orateur",
#     title="Évolution temporelle des mentions par orateur",
#     labels={"DateSeance_day": "Date", "mentions": "Nombre de mentions", "Nom_orateur": "Orateur"},
#     template="plotly_white",
# )

# fig.show()

# %% [markdown]
# ### Genre

# %%
df["civ"] = df["civ"].replace({"M.": "Homme", "Mme": "Femme"})

# %%
df["civ"].value_counts()

# %%
fig = px.bar(df["civ"].value_counts())
fig.update_layout(
    title="Répartition des genres (civ)", template="plotly_white", showlegend=False
)
fig.show()

# %%
# Grouper par semaine et genre
df_civ_grouped = (
    df.groupby([pd.Grouper(key="DateSeance_day", freq="W"), "civ"])
    .size()
    .reset_index(name="mentions")
)

fig_gender = px.line(
    df_civ_grouped,
    x="DateSeance_day",
    y="mentions",
    color="civ",
    title="Évolution temporelle des mentions selon le genre",
    labels={"DateSeance_day": "Date", "mentions": "Nombre de mentions", "civ": "Genre"},
    template="plotly_white",
)

fig_gender.show()

# %%
fig_gender.write_html("../reports/figures/fig_gender.html")
