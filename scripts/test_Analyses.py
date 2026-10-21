# %% [markdown]
# # Analyses statistiques

# %% [markdown]
# ***Structure du fichier***
#
# - (##) Partie thématique
# - (###) (1) Analyse synchronique puis en (2) Analyse diachronique (évolution)
# - (####) Statistiques générales 
# - (####) Tableau et graphique en VA
# - (####) Tableau et graphique en %
# - (####) Tableau et graphique % et VA
#
# ==> ***Nom des variables*** :
# - colonne_condition = variable indépendante "République" analysée 
# - colonne_groupe/député/dpt/genre/etc = variable dépendante 
# - colonne_date 

# %% [markdown]
# ***Règles d'or : Comparer systématiquement statistiques générales, proportions en % et valeurs absolues sur les 2 df afin de pouvoir distinguer ce qui relève du sur ou du sous-investissement.***
#
# *À garder en tête au moment de l'analyse et interprétation des résultats, l'analyse en % dépend de notre unité de mesure (nombre de prises de paroles avec ou sans interruption, phrases). On ne peut pas mesurer en durée de l'intervention ou nombre de mots pour l'intervention donc il ne s'agit pas à proprement parlé d'un % en termes de temps de parole (= un artéfact statistique dont il serait intéressant de comparer les mesures).*
#
# ==> Pour le futur croiser aussi analyse avec données par phrases (utiliser spacy)

# %%
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# %%
df = pd.read_csv(
    "../data/interim/3_1_df_repu_proportion.csv",
    low_memory=False,
    dtype={"ID_orateur": str},
)

# %%
df

# %%
import datetime
import locale

# Active la locale française (nécessaire pour le format)
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

# %%
df["dateSeance_ts"] = pd.to_datetime(df["dateSeanceJour"], format="%A %d %B %Y")
df["dateSeance_day"] = df["dateSeance_ts"].dt.normalize()

# %%
df_repu = df[df["repu_match_valide"] == True]
df_interv = df[df["code_grammaire"] != "INTERRUPTION_1_10"]

# %%
# Correspondances couleurs et affiliations
couleurs_groupes = {
    "LFI": "#B71C1C",  # rouge foncé
    "GDR": "#ea193a",  # rouge vif
    "ECO": "#1FAE70",  # vert
    "SOC-A": "#F05FA8",  # rose
    "LAREM": "#FFD83E",  # jaune
    "DEM": "#F57C00",  # orange
    "HOR": "#6994D6",  # bleu gris
    "LIOT": "#C075C0",  # violet clair repéré sur Wikipédia/instituts de sondages
    "AGIR-E": "#2D769E",  # jaune turquoise
    "UDI": "#439FD1",  # bleu clair
    "LR": "#0D47A1",  # bleu foncé
    "RN": "#412302",  # marron foncé ou noir "#000000"
    # Option Générique par défaut
    "Autres": "#9E9E9E",
}

couleurs_bloc = {
    "Gauche": "#A92424",  # rouge
    "Centre": "#D59629",  # orange
    "Droite": "#1F57AC",  # bleu
    # Valeur par défaut si un parti n'est pas défini
    "Autres": "rgb(160, 160, 160)",
}


# %% [markdown]
# ## Analyses générales temporelles

# %% [markdown]
# ### Fonctions générales 

# %%
def statistiques_générales_temporelles(
    df,
    colonne_condition,
    colonne_nombre="nombre_mentions_repu",
    periode="semaine",
    colonne_date="dateSeance_day",
):
    # Définir la granularité
    if periode == "semaine":
        df["periode"] = (
            df[colonne_date].dt.isocalendar().year.astype(str)
            + "-W"
            + df[colonne_date].dt.isocalendar().week.astype(str)
        )
    elif periode == "jour":
        df["periode"] = df[colonne_date].dt.to_period("D").astype(str)
    elif periode == "mois":
        df["periode"] = df[colonne_date].dt.to_period("M").astype(str)
    elif periode == "annee":
        df["periode"] = df[colonne_date].dt.year.astype(str)
    elif periode == "global":
        df["periode"] = "Global"

    # Compter occurrences par période
    df_counts = (
        df.groupby("periode")
        .agg(
            nb_interventions=(colonne_condition, "count"),
            nb_interventions_repu=(colonne_condition, lambda x: (x == True).sum()),
            nb_occurrences_repu=(colonne_nombre, "sum"),
        )
        .reset_index()
    )

    # Proportion d'interventions true
    df_counts["proportion_interv_repu"] = (
        df_counts["nb_interventions_repu"] / df_counts["nb_interventions"] * 100
    )

    # Occurrences par interventions (/interv_repu)
    df_counts["occ_interv_repu"] = (
        df_counts["nb_occurrences_repu"] / df_counts["nb_interventions_repu"]
    )
    df_counts["occ_interv"] = (
        df_counts["nb_occurrences_repu"] / df_counts["nb_interventions"]
    )

    # Calcul des statistiques pour chaque catégorie
    categories = {
        "nb_interv": df_counts["nb_interventions_repu"],
        "%_interv": df_counts["proportion_interv_repu"],
        "nb_occurrences": df_counts["nb_occurrences_repu"],
        "nb_occ_interv": df_counts["occ_interv"],
        "nb_occ_interv_repu": df_counts["occ_interv_repu"],
    }

    # Liste des statistiques à calculer
    stats_names = [
        "moyenne",
        "médiane",
        "écart-type",
        "variance",
        "coefficient_variation",
    ]
    quantiles = {
        "déciles": [i / 10 for i in range(1, 10)],
        "quartiles": [i / 4 for i in range(1, 4)],
    }

    # Construction du DataFrame de résultats
    results = []
    for category, series in categories.items():
        row = {"Catégorie": category}
        moyenne = round(series.mean(), 2)
        mediane = round(series.median(), 2)
        ecart_type = round(series.std(), 2)
        variance = round(series.var(), 2)
        coefficient_variation = (
            round(ecart_type / moyenne, 2) if moyenne != 0 else float("nan")
        )

        row["moyenne"] = moyenne
        row["médiane"] = mediane
        row["écart-type"] = ecart_type
        row["variance"] = variance
        row["coefficient_variation"] = coefficient_variation

        # Ajout des déciles et quartiles
        for q_name, q_values in quantiles.items():
            q_stats = [round(series.quantile(q).item(), 2) for q in q_values]
            row[f"{q_name}"] = q_stats

        results.append(row)

    # Création du DataFrame final
    df_stats = pd.DataFrame(results)
    df_stats.set_index("Catégorie", inplace=True)

    return {"statistiques": df_stats, "df_counts": df_counts}


# %%
def plot_boxplots_from_stats(
    df,
    colonne_condition,
    colonne_nombre="nombre_mentions_repu",
    periode="semaine",
    colonne_date="dateSeance_day",
):
    # Appel de la fonction pour obtenir les stats et df_counts
    result = statistiques_générales_temporelles(
        df, colonne_condition, colonne_nombre, periode, colonne_date
    )
    df_counts = result["df_counts"]

    # Création de la figure et des sous-graphes (5)
    fig, axes = plt.subplots(3, 2, figsize=(18, 15))

    # Boxplot pour le nombre d'interventions
    sns.boxplot(y=df_counts["nb_interventions_repu"], ax=axes[0, 0], color="lightgreen")
    axes[0, 0].set_title(f"Distribution des interventions par {periode}")
    axes[0, 0].set_ylabel("Nb d'interventions")
    axes[0, 0].grid(True, linestyle="--", alpha=0.7)

    # Boxplot pour la proportion d'interventions
    sns.boxplot(y=df_counts["proportion_interv_repu"], ax=axes[0, 1], color="skyblue")
    axes[0, 1].set_title(f"Distribution de la proportion d'interventions par {periode}")
    axes[0, 1].set_ylabel("Proportion d'interventions)")
    axes[0, 1].grid(True, linestyle="--", alpha=0.7)

    # Boxplot du nombre d'occurrences
    sns.boxplot(y=df_counts["nb_occurrences_repu"], ax=axes[1, 0], color="salmon")
    axes[1, 0].set_title(f"Distribution des occurrences par {periode}")
    axes[1, 0].set_ylabel("Occurrences")
    axes[1, 0].grid(True, linestyle="--", alpha=0.7)

    # Boxplot du nombre d'occurrences par intervention
    sns.boxplot(y=df_counts["occ_interv"], ax=axes[2, 0], color="red")
    axes[2, 0].set_title(f"Distribution des occurrences par intervention par {periode}")
    axes[2, 0].set_ylabel("Occurrences par interventions")
    axes[2, 0].grid(True, linestyle="--", alpha=0.7)

    # Boxplot du nombre d'occurrences par intervention avec république
    sns.boxplot(y=df_counts["occ_interv_repu"], ax=axes[2, 1], color="green")
    axes[2, 1].set_title(
        f"Distribution des occurrences par intervention_répu par {periode}"
    )
    axes[2, 1].set_ylabel("Occurrences par interventions_répu")
    axes[2, 1].grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.show()

    return result


# %%
def diachronique_général(
    df,
    objet,
    suffixe,
    colonne_condition,
    colonne_nombre="nombre_mentions_repu",
    colonne_date="dateSeance_day",
    periode="semaine",
    titre=None,
):
    df = df.copy()

    # 1. Définition des paramètres de période
    if periode == "semaine":
        df["periode"] = (
            df[colonne_date] - pd.to_timedelta(df[colonne_date].dt.dayofweek, unit="d")
        ).dt.strftime("%Y-%m-%d")
        titre_defaut = f"Évolution hebdomadaire de la {objet}"
    elif periode == "jour":
        df["periode"] = df[colonne_date].dt.to_period("D").astype(str)
        titre_defaut = f"Évolution journalière de la {objet}"
    elif periode == "mois":
        df["periode"] = df[colonne_date].dt.to_period("M").astype(str)
        titre_defaut = f"Évolution mensuelle de la {objet}"
    elif periode == "annee":
        df["periode"] = df[colonne_date].dt.year.astype(str)
        titre_defaut = f"Évolution annuelle de la {objet}"

    # 2. Regrouper et compter les occurrences
    counts = (
        df.groupby("periode")
        .agg(
            nb_interventions=(colonne_condition, "count"),
            nb_interventions_repu=(colonne_condition, lambda x: (x == True).sum()),
            nb_occurrences_repu=(colonne_nombre, "sum"),
            date=(colonne_date, "min"),
        )
        .reset_index()
    )
    counts["proportion_interv_repu"] = (
        counts["nb_interventions_repu"] / counts["nb_interventions"] * 100
    ).round(2)
    # Occurrences par interventions (/interv_repu)
    counts["occ_interv_repu"] = (
        counts["nb_occurrences_repu"] / counts["nb_interventions_repu"]
    ).round(2)
    counts["occ_interv"] = (
        counts["nb_occurrences_repu"] / counts["nb_interventions"]
    ).round(2)

    # Gérer les valeurs nulles pour la proportion
    y_proportion = counts["proportion_interv_repu"].copy()
    y_proportion[y_proportion == 0] = None

    # 3. Graphique
    fig = go.Figure()

    # Barre pour true_mentions (bleu)
    fig.add_trace(
        go.Bar(
            x=counts["periode"],
            y=counts["nb_interventions_repu"],
            name="Nb d'interventions",
            marker_color="#1A417B",
            opacity=0.8,
            hovertemplate="<b>Période : %{x}</b><br>Nb interventions : %{y}<extra></extra>",
        )
    )

    # Barre pour somme_mentions_repu (orange)
    fig.add_trace(
        go.Bar(
            x=counts["periode"],
            y=counts["nb_occurrences_repu"],
            name=f"Nb occurrences ({colonne_nombre})",
            marker_color="#9BB2D5",
            opacity=0.8,
            hovertemplate="<b>Période : %{x}</b><br>Nb occurrences : %{y}<extra></extra>",
        )
    )

    # Courbe pour la proportion (optionnelle)
    fig.add_trace(
        go.Scatter(
            x=counts["periode"],
            y=y_proportion,
            mode="markers",
            name="Proportion d'interventions",
            line=dict(color="#080102", width=2.7),
            marker=dict(size=8, symbol="circle"),
            yaxis="y2",
            hovertemplate="<b>Période : %{x}</b><br>Proportion : %{y:.2f}%<extra></extra>",
        )
    )

    # 4. Mise en forme
    fig.update_layout(
        title=(titre if titre else titre_defaut) + (f" ({suffixe})" if suffixe else ""),
        xaxis=dict(title="Période"),
        yaxis=dict(title="Nombre", showgrid=False),
        yaxis2=dict(
            title="Proportion (%)", overlaying="y", side="right", showgrid=False
        ),
        barmode="overlay",  # Superpose les barres
        template="plotly_white",
        legend=dict(x=0.65, y=1.25, bgcolor="rgba(255,255,255,0.7)"),
        bargap=0.4,
    )

    # 5. Tableau
    tableau = counts.drop(columns=["date", "total_mentions"], errors="ignore")
    tableau = tableau.rename(
        columns={
            "periode": "Période",
            "true_mentions": "Nb d'interventions",
            "somme_mentions_repu": "Nb occurrences",
            "proportion_true": "Proportion d'interventions",
            "occ_interv_repu": "Nb occ/interv_répu",
            "occ_interv": "Nb occ/interv",
        }
    )
    tableau.index = range(1, len(tableau) + 1)

    fig.show()
    return tableau


# %% [markdown]
# ### Par ans

# %%
# Stats annuelles
stats_annee = statistiques_générales_temporelles(
    df_interv,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="annee",
)
print(stats_annee["statistiques"])

# %%
# Mise en forme par boxplot
stats = plot_boxplots_from_stats(
    df,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="annee",
)

# %%
# Tableau et graphique des évolutions annuelles
diachronique_général(
    df,
    colonne_nombre="nombre_mentions_repu",
    colonne_condition="repu_match_valide",
    objet="famille du mot République",
    periode="annee",
    suffixe="interv + inters",
)


# %% [markdown]
# ### Par mois

# %%
# Stats mensuelles
stats_mensuelles = statistiques_générales_temporelles(
    df,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="mois",
)
print(stats_mensuelles["statistiques"])

# %%
# Mise en forme par boxplot
stats = plot_boxplots_from_stats(
    df,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="mois",
)

# %%
# Tableau et graphique des évolutions annuelles
diachronique_général(
    df,
    colonne_nombre="nombre_mentions_repu",
    colonne_condition="repu_match_valide",
    objet="famille du mot République",
    periode="mois",
    suffixe="interv + inters",
)


# %% [markdown]
# ### Par semaines

# %%
# Stats hebdo
stats_hebdomadaire = statistiques_générales_temporelles(
    df_interv,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="semaine",
)
print(stats_hebdomadaire["statistiques"])

# %%
# Mise en forme par boxplot
stats = plot_boxplots_from_stats(
    df,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="semaine",
)

# %%
# Tableau et graphique des évolutions hebdomadaires
diachronique_général(
    df,
    colonne_nombre="nombre_mentions_repu",
    colonne_condition="repu_match_valide",
    objet="famille du mot République",
    periode="semaine",
    suffixe="interv + inters",
)

# %% [markdown]
# ### Par jours

# %%
# Tableau et graphique des évolutions hebdomadaires
diachronique_général(
    df,
    colonne_nombre="nombre_mentions_repu",
    colonne_condition="repu_match_valide",
    objet="famille du mot République",
    periode="jour",
    suffixe="interv + inters",
)

# %%
# Stats journalières
stats_journalières = statistiques_générales_temporelles(
    df,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="jour",
)
print(stats_journalières["statistiques"])

# %%
# Mise en forme par boxplot
stats = plot_boxplots_from_stats(
    df,
    colonne_condition="repu_match_valide",
    colonne_nombre="nombre_mentions_repu",
    periode="jour",
)

# %%
# aficher les X dates les plus fréquentes sous forme de tableau
table = df_repu["dateSeance_day"].value_counts()[0:50].reset_index()
table = table.rename(columns={"count": "Nombre de mentions"})
table

# %% [markdown]
# **Remarques**
# - *Le 3 juillet 2017, le 9 juillet 2018, le 4 mars 2024 sont parmis les 5 principales dates car parlement réuni en Congrès*
#
# - *le 1 février 2021, le 28 juin 2021, 5 février 2021, le 23 juillet 2021, le 3 février 2021, 30 juin 2021 (et 5 avril 2023 : bilan de la loi), 1er juillet 2021, le 12 février 2021, renvoient quant à eux à la discussion du projet de loi "confortant le respect des principes de la République". **==> Suivre en détail le processus législatif de ce projet de loi car moment central !!***
#
# - *On a aussi le 22 mars 2020, très courte séance (commencée à 18h30) sur l’urgence du covid et un hommage*
#
# - *6 janvier 2022, 6 juin 2022, 13 mars 2018 : réforme territoriale Nouvelle-Calédonie*
#
# - *25 janvier 2024, 8 juillet 2019 et 16 janvier 2020 : accords internationaux avec présence d'expressions comme "gouvernement de la République française", de pays sous forme adjectivable (ex : "république arménienne") ou avec république en miniscule --> moins présent maintenant que exclus*
#
# - *11 février 2019 sur "l'école de la confiance"*
# - *12 et 13 juillet 2018 sur le  projet de loi constitutionnelle pour une Démocratie plus représentative, responsable et efficace*

# %% [markdown]
# ##### Archives

# %%
# Compter True/False par jour
df_daily = (
    df.groupby(df["dateSeance_day"].dt.date)["repu_match_valide"]
    .value_counts(normalize=True)  # calcule directement les proportions
    .rename("proportion")
    .reset_index()
)

# Garder uniquement les "True"
df_daily_true = df_daily[df_daily["repu_match_valide"] == True]

# Graphique
fig_daily = px.line(
    df_daily_true,
    x="dateSeance_day",
    y="proportion",
    title="Évolution journalier de l'investissement en proportion de la famille du mot 'République' (B)",
    labels={"proportion": "% des occurences", "dateSeance_day": "Date"},
    template="plotly_white",
)

fig_daily.show()

# aficher les 25 dates les plus fréquentes sous forme de tableau
table = df_daily_true.sort_values("proportion", ascending=False).head(20)
table


# %%
# Définir les paramètres
# colonne_condition = "Laïcité-Islam"
# periode = "ME"  # "ME" = mois, "WE" = semaine, "YS" = année.

# S'assurer que la colonne date est bien en datetime
# df["dateSeance_day"] = pd.to_datetime(df["dateSeance_day"])

# Agréger les données par mois
# df_monthly = (
#    df
#    .resample(periode, on="dateSeance_day")[colonne_condition]
#    .agg(
#        total_mentions="count",
#        true_mentions=lambda x: (x == True).sum()
#    )
##    .reset_index()
# )

# Calculer la proportion
# df_monthly["proportion_true"] = df_monthly["true_mentions"] / df_monthly["total_mentions"]

# Créer la figure avec Plotly Graph Objects
# fig = go.Figure()

# Barres : volume total
# fig.add_trace(go.Bar(
#    x=df_monthly["dateSeance_day"],
#    y=df_monthly["true_mentions"],
#    name="Nombre d'interventions avec FDM 'République'",
#    marker_color="rgba(99, 110, 250, 0.6)",
#    yaxis="y1"
# ))

# Courbe : proportion
# fig.add_trace(go.Scatter(
#    x=df_monthly["dateSeance_day"],
#    y=df_monthly["proportion_true"] * 100,  # en pourcentage
#    name="Proportion d'intervention en % avec FDM 'République'",
#    mode="lines+markers",
#    line=dict(color="rgba(239, 85, 59, 0.8)", width=3),
#    yaxis="y2"
# ))

# Mise en forme du graphique
# fig.update_layout(
#    title=f"Évolution hebdomadaire de l'investissement de la famille du mot 'République' (A)",
#    xaxis=dict(title="Mois"),
#    yaxis=dict(
#        title="Valeurs absolue",
#        showgrid=False
#    ),
#    yaxis2=dict(
#        title="Proportion en %",
#        overlaying="y",
#        side="right",
#        showgrid=False
#    ),
#    legend=dict(x=0.65, y=1.14, bgcolor="rgba(255,255,255,0.7)"),
#    template="plotly_white",
#    bargap=0.2
# )
# fig.update_xaxes(
#    dtick="M12",  # un tick par an
#    tickformat="%Y",
#    ticklabelmode="period"  # place les labels entre les périodes
# )

# fig.show()
# df_monthly


# %% [markdown]
# ## Analyse par contexte parlementaire

# %% [markdown]
# ### Analyse par discussions législatives (PPL/PJL)

# %% [markdown]
# ### Analyse par type de discussions législatives 

# %%
# Tri croisé à plat (répu/non-répu "repu_match_valide" + "nombre_repu" par type de discussions législatives "point_type")

## Adapter stat analyse temporelle et y inclure p-value du khi-deux & V de Cramer
## pour objectiver la corrélation entre type de discussion (variable dépendante explicative)
## et utilisation de la République (variable indépendante à expliquer)

# %%
df["point_type"].value_counts()

# %% [markdown]
# ## Par groupes 

# %% [markdown]
# ### Analyse synchronique  

# %% [markdown]
# #### Fonctions générales 

# %%
# Reprendre fonction analyses temporelles + rajouter test de corrélation



# %%
def statistiques_générales_groupes(df, colonne_condition, periode="semaine"):
    # Définir la granularité
    if periode == "semaine":
        df["periode"] = (
            df["dateSeance_day"].dt.isocalendar().year.astype(str)
            + "-W"
            + df["dateSeance_day"].dt.isocalendar().week.astype(str)
        )
    elif periode == "mois":
        df["periode"] = df["dateSeance_day"].dt.to_period("M").astype(str)
    elif periode == "annee":
        df["periode"] = df["dateSeance_day"].dt.year.astype(str)
    elif periode == "global":
        df["periode"] = "Global"

    # Compter occurrences par période (proportion et True)
    df_counts = (
        df.groupby(["affiliation_et_gouv", "periode"])[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # Proportion de True
    df_counts["proportion_true"] = (
        df_counts["true_mentions"] / df_counts["total_mentions"]
    )

    # Statistiques
    stats = {
        "moyenne_proportion": df_counts["proportion_true"].mean(),
        "médiane_proportion": df_counts["proportion_true"].median(),
        "moyenne_valeur": df_counts["true_mentions"].mean(),
        "médiane_valeur": df_counts["true_mentions"].median(),
        "deciles_proportion": df_counts["proportion_true"].quantile(
            [i / 100 for i in range(1, 100)]
        )
        * 100,
        "deciles_valeur": df_counts["true_mentions"].quantile(
            [i / 100 for i in range(1, 100)]
        ),
    }

    return stats


# %%
df

# %%
# Sur toute la période
stats_global = statistiques_générales_groupes(
    df, colonne_condition="repu_match_valide", periode="global"
)  # remplacer df par df_regroup pour avoir le corpus B
print("Statistiques sur 2017-2024")
print(f"Moyenne (VA) : {stats_global['moyenne_valeur']:.2f}")
print(f"Médiane (VA) : {stats_global['médiane_valeur']:.2f}")
print(f"Déciles (VA)  : {stats_global['deciles_valeur']}")
print(f"Moyenne (%)  : {stats_global['moyenne_proportion']:.2%}")
print(f"Médiane (%) : {stats_global['médiane_proportion']:.2f}")
print(f"Déciles (%)  : {stats_global['deciles_proportion']}")

# --- Par année ---
# stats_annee = statistiques_générales_groupes(df, periode="annee")
# print("Par Année :")
# print(f"Moyenne (VA) : {stats_annee['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_annee['médiane_valeur']:.2f}")
# print(f"Déciles (VA)  : {stats_annee['deciles_valeur']}")
# print(f"Moyenne (%)  : {stats_annee['moyenne_proportion']:.2%}")
# print(f"Médiane (%) : {stats_annee['médiane_proportion']:.2f}")
# print(f"Déciles (%)  : {stats_annee['deciles_proportion']}")

# --- Par mois ---
# stats_mois = statistiques_générales_groupes(df, periode="mois")
# print("Par Mois :")
# print(f"Moyenne (VA) : {stats_mois['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_mois['médiane_valeur']:.2f}")
# print(f"Déciles (VA)  : {stats_mois['deciles_valeur']}")
# print(f"Moyenne (%)  : {stats_mois['moyenne_proportion']:.2%}")
# print(f"Médiane (%) : {stats_mois['médiane_proportion']:.2f}")
# print(f"Déciles (%)  : {stats_mois['deciles_proportion']}")

# --- Par semaine ---
# stats_sem = statistiques_générales_groupes(df, periode="semaine")
# print("Par Semaine :")
# print(f"Moyenne (VA) : {stats_sem['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_sem['médiane_valeur']:.2f}")
# print(f"Déciles (VA)  : {stats_sem['deciles_valeur']}")
# print(f"Moyenne (%)  : {stats_sem['moyenne_proportion']:.2%}")
# print(f"Médiane (%) : {stats_sem['médiane_proportion']:.2f}")
# print(f"Déciles (%)  : {stats_sem['deciles_proportion']}")


# %% [markdown]
# #### En VA (à faire)

# %%
# Sous format fonction et nommer diachronique_groupes_VA

# %% [markdown]
# #### En proportion (à coloriser)

# %%
# Sous format fonction et nommer diachronique_groupes_%

# %%
# Compter le nombre de fois où chaque groupe parlementaire dit "République"
counts = (
    df.groupby("affiliation_et_gouv")["repu_match_valide"]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

# Filtrer les orateurs avec au moins 10 mentions True
filtered = counts[counts["true_mentions"] >= 250]

# Trier par proportion décroissante et garder les 40 premiers
df_toppartis = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(40)
    .reset_index(drop=True)
)

# Graphique
fig_toppartis = px.bar(
    df_toppartis,
    x="groupe_députés_affiliation",
    y="proportion_true",
    title="Proportions des occurrences de la 'République' par groupe parlementaire (<250 occurrences)",
    labels={
        "groupe_députés_affiliation": "Groupe parlementaire",
        "proportion_true": "% 'République'",
    },
    template="plotly_white",
)

fig_toppartis.update_layout(xaxis_tickangle=-45)

fig_toppartis.show()
df_toppartis

# %% [markdown]
# #### En proportion + VA 

# %%
# Sous format fonction et nommer diachronique_groupes_total

# %%
df

# %%
# Paramètres
colonne_condition = "interv_mythe_"
colonne_groupe = "affiliation_et_gouv"

# Compter le nombre de fois où chaque groupe parlementaire dit "République"
df_groupes = (
    df.groupby(colonne_groupe)[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calculer la proportion
df_groupes["proportion_true"] = (
    df_groupes["true_mentions"] / df_groupes["total_mentions"] * 100
)  # en %

# Filtrage des 10 premiers (en % ou en valeur absolue)
df_groupes = (
    df_groupes.sort_values("true_mentions", ascending=False)
    .head(10)
    .reset_index(drop=True)
)


# Créer la figure
fig = go.Figure()

# Nombre d'occurrences de la "République"
fig.add_trace(
    go.Bar(
        x=df_groupes[colonne_groupe],
        y=df_groupes["true_mentions"],
        name="Nombre d'interventions avec FDM 'République'",
        marker_color="rgba(99, 110, 250, 0.6)",
        yaxis="y1",
    )
)

# Proportion des occurrences de la "République"
fig.add_trace(
    go.Scatter(
        x=df_groupes[colonne_groupe],
        y=df_groupes["proportion_true"],
        name="Proportion d'intervention en % avec FDM 'République'",
        mode="markers",
        marker=dict(color="rgba(239, 85, 59, 0.9)", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en forme
fig.update_layout(
    title="Investissement de la famille du mot 'République' des dix principaux groupes parlementaires (A)",
    xaxis=dict(title="Groupe parlementaire"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(
        title="Proportion en %",
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(x=0.63, y=-0.28, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.25,
)

# Afficher la figure
fig.show()
df_groupes


# %%
df

# %%
# Graphique avec couleurs spécifiques par parti

# Agréger les données par parti
colonne_condition = "repu_match_valide"
colonne_groupe = "affiliation_mandat_députés"
suffixe = "FDM"

df_groupes = (
    df.groupby(colonne_groupe)[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

df_groupes["proportion_true"] = (
    df_groupes["true_mentions"] / df_groupes["total_mentions"] * 100
)

# Si certains partis ne sont pas dans ton dictionnaire, leur attribuer "Autres"
df_groupes["couleur"] = (
    df_groupes[colonne_groupe].map(couleurs_groupes).fillna(couleurs_groupes["Autres"])
)

# Trier les groupes par volume
df_groupes = (
    df_groupes.sort_values("true_mentions", ascending=False)
    .head(11)
    .reset_index(drop=True)
)

# Créer la figure
fig = go.Figure()

# Barres : volume total (couleur spécifique par parti)
for _, row in df_groupes.iterrows():
    fig.add_trace(
        go.Bar(
            x=[row[colonne_groupe]],
            y=[row["true_mentions"]],
            name=row[colonne_groupe],
            marker_color=row["couleur"],
            yaxis="y1",
            showlegend=False,  # On affiche la légende séparément si besoin
        )
    )

# Points : proportion
fig.add_trace(
    go.Scatter(
        x=df_groupes[colonne_groupe],
        y=df_groupes["proportion_true"],
        name=f"Proportion d'intervention en %",
        mode="markers",
        marker=dict(color="black", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en page
fig.update_layout(
    title=f"Investissement de la famille du mot République (Corpus Assemblée nationale : 2017-2024)",
    xaxis=dict(title="Groupe parlementaire"),
    yaxis=dict(title="Nombre d'interventions", showgrid=False),
    yaxis2=dict(
        title="Proportion d'interventions",
        showgrid=False,
        overlaying="y",
        side="right",
    ),
    legend=dict(x=0.65, y=1.17, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.35,
)

fig.show()


# %%
# Graphique avec couleurs spécifiques par parti

# Agréger les données par parti
colonne_condition = "repu_match_valide"
colonne_groupe = "affiliation_et_gouv"
suffixe = "FDM"

df_groupes = (
    df_interv.groupby(colonne_groupe)[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

df_groupes["proportion_true"] = (
    df_groupes["true_mentions"] / df_groupes["total_mentions"] * 100
)

# Si certains partis ne sont pas dans ton dictionnaire, leur attribuer "Autres"
df_groupes["couleur"] = (
    df_groupes[colonne_groupe].map(couleurs_groupes).fillna(couleurs_groupes["Autres"])
)

# Trier les groupes par volume
df_groupes = (
    df_groupes.sort_values("true_mentions", ascending=False)
    .head(11)
    .reset_index(drop=True)
)

# Créer la figure
fig = go.Figure()

# Barres : volume total (couleur spécifique par parti)
for _, row in df_groupes.iterrows():
    fig.add_trace(
        go.Bar(
            x=[row[colonne_groupe]],
            y=[row["true_mentions"]],
            name=row[colonne_groupe],
            marker_color=row["couleur"],
            yaxis="y1",
            showlegend=False,  # On affiche la légende séparément si besoin
        )
    )

# Points : proportion
fig.add_trace(
    go.Scatter(
        x=df_groupes[colonne_groupe],
        y=df_groupes["proportion_true"],
        name=f"Proportion d'intervention en % de {colonne_condition}",
        mode="markers",
        marker=dict(color="black", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en page
fig.update_layout(
    title=f"Investissement de {colonne_condition} par les dix principaux groupes parlementaires ({suffixe})",
    xaxis=dict(title="Groupe parlementaire"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(
        title="Proportion en %",
        showgrid=False,
        overlaying="y",
        side="right",
    ),
    legend=dict(x=0.65, y=1.17, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.35,
)

fig.show()


# %% [markdown]
# ### Analyses diachroniques (Évolutions)

# %% [markdown]
# #### En valeur absolue

# %%
def evolution_groupes_va(
    df,
    colonne_condition,
    préfixe,
    top_n,
    colonne_date="dateSeance_day",
    colonne_groupe="affiliation_et_gouv",
):
    # 1. Calcul par groupe
    counts = (
        df.groupby(colonne_groupe)[colonne_condition]
        .apply(lambda x: (x == True).sum())
        .reset_index(name="true_mentions")
    )

    # 2. Trier les groupes par volume pour ne garder que les X premiers
    top_groupes = (
        counts.sort_values("true_mentions", ascending=False)
        .head(top_n)[colonne_groupe]
        .tolist()
    )

    # 3. Filtrer le DF
    df_groupes = df[
        df[colonne_groupe].isin(top_groupes) & (df[colonne_condition] == True)
    ].copy()

    # 4. Agrégation annuelle
    df_groupes = (
        df_groupes.groupby([pd.Grouper(key=colonne_date, freq="YS"), colonne_groupe])[
            colonne_condition
        ]
        .apply(lambda x: (x == True).sum())
        .reset_index(name="true_mentions")
    )

    # 5. Extraire l'année
    df_groupes["Année"] = df_groupes[colonne_date].dt.year

    # 6. Construire la figure avec Graph objects
    fig = go.Figure()

    for groupe in df_groupes[colonne_groupe].unique():
        subset = df_groupes[df_groupes[colonne_groupe] == groupe]

        couleur = couleurs_groupes.get(groupe, couleurs_groupes["Autres"])

        fig.add_trace(
            go.Scatter(
                x=subset["Année"],
                y=subset["true_mentions"],
                mode="lines+markers",
                name=groupe,
                line=dict(color=couleur, width=2),
                marker=dict(size=6, color=couleur),
                hovertemplate="<b>%{x}</b><br>%{y} occurences<extra>"
                + groupe
                + "</extra>",
            )
        )

    # 7. Mise en forme du graphique
    fig.update_layout(
        title=f"Évolution de l'investissement de la {préfixe} ''{colonne_condition}'' des {top_n} principaux groupes parlementaires en VA",
        xaxis=dict(title="Année", tickmode="linear", dtick=1, showgrid=True),
        yaxis=dict(title="Valeur absolue", showgrid=True, gridcolor="#D7D6D6"),
        legend=dict(title="Groupes", x=1.02, y=0.95, bgcolor="rgba(255,255,255,0.8)"),
        template="plotly_white",
        hovermode="x unified",
        font=dict(size=12),
    )

    fig.show()



# %%
evolution_groupes_va(df, colonne_condition="repu_match_valide", préfixe="FDM", top_n=11)


# %% [markdown]
# #### En proportion

# %%
def evolution_groupes_proportion(
    df,
    colonne_condition,
    préfixe,
    top_n,
    date_col="dateSeance_day",
    colonne_groupe="affiliation_et_gouv",
):
    # 1. Calcul global des proportions par groupe
    counts = (
        df.groupby(colonne_groupe)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 2. Trier les groupes par volume pour ne garder que les X premiers
    top_groupes = (
        counts.sort_values("true_mentions", ascending=False)
        .head(top_n)[colonne_groupe]
        .tolist()
    )

    # 3. Filtrer le DF
    df_groupes = df[df[colonne_groupe].isin(top_groupes)].copy()

    # 4. Agrégation annuelle
    df_groupes = (
        df_groupes.groupby([pd.Grouper(key=date_col, freq="YS"), colonne_groupe])[
            colonne_condition
        ]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 5. Calcul du pourcentage annuel
    df_groupes["proportion_true"] = (
        df_groupes["true_mentions"] / df_groupes["total_mentions"]
    )
    df_groupes["Année"] = df_groupes[date_col].dt.year

    # 6. Construire la figure avec Graph objects
    fig = go.Figure()

    for groupe in df_groupes[colonne_groupe].unique():
        subset = df_groupes[df_groupes[colonne_groupe] == groupe]

        couleur = couleurs_groupes.get(groupe, couleurs_groupes["Autres"])

        fig.add_trace(
            go.Scatter(
                x=subset["Année"],
                y=subset["proportion_true"] * 100,
                mode="lines+markers",
                name=groupe,
                line=dict(color=couleur, width=2),
                marker=dict(size=6, color=couleur),
                hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra>" + groupe + "</extra>",
            )
        )

    # 7. Mise en forme du graphique
    fig.update_layout(
        title=f"Évolution de l'investissement de la {préfixe} ''{colonne_condition}'' des {top_n} principaux groupes parlementaires en %",
        xaxis=dict(title="Année", tickmode="linear", dtick=1, showgrid=True),
        yaxis=dict(title="% d'utilisation", showgrid=True, gridcolor="#D7D6D6"),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(title="Groupes", x=1.02, y=0.95),
        font=dict(size=12),
    )

    fig.show()
    df_groupes



# %%
evolution_groupes_proportion(
    df, colonne_condition="repu_match_valide", préfixe="FDM", top_n=4
)

# %% [markdown]
# ### Par groupe

# %% [markdown]
# #### En valeur absolue (à faire)

# %%
# diachronique_groupe_va

# %% [markdown]
# #### En proportion 

# %%
# diachronique_groupe_proportion

# %% [markdown]
# #### En VA + %

# %%
# diachronique_groupe_total


def diachronique_groupe_total(
    df,
    colonne_condition,
    préfixe,
    groupe,
    colonne_groupe,
    colonne_date="dateSeance_day",
    periode="semaine",
):
    # 1. Filtrer les données pour le groupe
    df_groupe = df[df[colonne_groupe] == groupe].copy()

    # 2. Définition des paramètres de période
    if periode == "semaine":
        df_groupe["periode"] = (
            df_groupe[colonne_date].dt.isocalendar().year.astype(str)
            + "-W"
            + df_groupe[colonne_date].dt.isocalendar().week.astype(str)
        )
        titre_defaut = f"Évolution hebdomadaire de l'investissement de la {préfixe} ''{colonne_condition}'' du groupe {groupe}"

    elif periode == "jour":
        df["periode"] = df[colonne_date].dt.to_period("D").astype(str)
        titre_defaut = f"Évolution journalier de l'investissement de la {préfixe} ''{colonne_condition}'' du groupe {groupe}"

    elif periode == "mois":
        df_groupe["periode"] = df_groupe[colonne_date].dt.to_period("M").astype(str)
        titre_defaut = f"Évolution mensuelle de l'investissement de la {préfixe} ''{colonne_condition}'' du groupe {groupe}"

    elif periode == "annee":
        df_groupe["periode"] = df_groupe[colonne_date].dt.year.astype(str)
        titre_defaut = f"Évolution annuelle de l'investissement de la {préfixe} ''{colonne_condition}'' du groupe {groupe}"

    # 3. Regrouper et compter les occurrences de la colonne condition
    counts = (
        df_groupe.groupby("periode")
        .agg(
            total_mentions=(colonne_condition, "count"),
            true_mentions=(colonne_condition, lambda x: (x == True).sum()),
            date=(colonne_date, "min"),
        )
        .reset_index()
    )

    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"] * 100

    # Couleur du parti
    couleur_parti = couleurs_groupes.get(groupe, couleurs_groupes["Autres"])

    # Gérer l'enjeu des courbes pleines
    y_proportion = counts["proportion_true"].copy()
    y_proportion[y_proportion == 0] = None

    # 4. Graphique
    fig = go.Figure()

    # Barres pour valeur absolue
    fig.add_trace(
        go.Bar(
            x=counts["periode"],
            y=counts["true_mentions"],
            name="Occurrences en valeur absolue",
            marker_color=couleur_parti,
            opacity=0.5,
            yaxis="y1",
            hovertemplate="<b>Période : %{x}</b><br>Occurrences : %{y}",
        )
    )
    # Courbe pour proportion

    fig.add_trace(
        go.Scatter(
            x=counts["periode"],
            y=y_proportion,
            mode="markers",
            name="Proportion en %",
            line=dict(color="#080102", width=2.7),
            marker=dict(size=8, symbol="circle"),
            yaxis="y2",
            hovertemplate="<b>Période : %{x}</b><br>Proportion : %{y:.2f}%<br>",
        )
    )

    # 4. Mise en forme
    fig.update_layout(
        title=titre_defaut,
        xaxis=dict(title="Période"),
        yaxis=dict(title="Occurrences absolues", showgrid=False),
        yaxis2=dict(
            title="Proportion (%)", overlaying="y", side="right", showgrid=False
        ),
        template="plotly_white",
        legend=dict(x=0.75, y=1.15, bgcolor="rgba(255,255,255,0.7)"),
        bargap=0.4,
    )

    fig.show()
    return counts


# %%
diachronique_groupe_total(
    df,
    periode="annee",
    colonne_condition="repu_match_valide",
    préfixe="FDM",
    groupe="RN",
    colonne_groupe="affiliation_et_gouv",
)

# %%
# Définir les paramètres
colonne_groupe = "REN"
colonne_condition = "repu_match_valide"
periode = "YS"  # "M" = mois, "W" = semaine, "YS" = début d'année

# Filtrage
df_parti = df[df["groupe_députés_affiliation"] == colonne_groupe].copy()

# Agrégation par période
df_period = (
    df_parti.resample(periode, on="dateSeance_day")[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
df_period["proportion_true"] = df_period["true_mentions"] / df_period["total_mentions"]

# === 2. Couleur du parti ===
couleur_parti = couleurs_groupes.get(colonne_groupe, couleurs_groupes["Autres"])

# === 3. Création de la figure ===
fig = go.Figure()

# Barres : volume total
fig.add_trace(
    go.Bar(
        x=df_period["dateSeance_day"],
        y=df_period["true_mentions"],
        name="Nombre total des occurrences",
        marker_color=couleur_parti,
        opacity=0.7,
        yaxis="y1",
    )
)

# Courbe : proportion (%)
fig.add_trace(
    go.Scatter(
        x=df_period["dateSeance_day"],
        y=df_period["proportion_true"] * 100,
        name="Proportion des occurrences",
        mode="lines+markers",
        line=dict(color="#000000", width=3, dash="solid"),
        marker=dict(size=8, color="#000000", line=dict(width=1, color="white")),
        yaxis="y2",
    )
)

# === 4. Mise en forme ===
fig.update_layout(
    title=f"Évolution annuelle de l'investissement de la famille du mot 'République' au {colonne_groupe} (A)",
    xaxis=dict(title="Années"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(title="Proportion en %", overlaying="y", side="right", showgrid=False),
    legend=dict(x=0.75, y=1.2, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.2,
)

fig.show()
df_period


# %%
# À faire : tableau avec évolution des thématiques par groupe

# %% [markdown]
# ## Par personnel politique / individuellement

# %% [markdown]
# ### Analyse diachronique

# %% [markdown]
# #### Statistiques générales

# %%
def diachronique_personnelpo_statistiques(
    df, colonne_condition, colonne_date="dateSeance_day", periode="semaine"
):
    # Définir la granularité
    if periode == "semaine":
        df["periode"] = (
            df[colonne_date].dt.isocalendar().year.astype(str)
            + "-W"
            + df[colonne_date].dt.isocalendar().week.astype(str)
        )
    elif periode == "jour":
        df["periode"] = df[colonne_date].dt.to_period("D").astype(str)
    elif periode == "mois":
        df["periode"] = df[colonne_date].dt.to_period("M").astype(str)
    elif periode == "annee":
        df["periode"] = df[colonne_date].dt.year.astype(str)
    elif periode == "global":
        df["periode"] = "Global"

    # Compter occurrences par période et par personnel politique (proportion et True)
    df_counts = (
        df.groupby(["nom_orateur_clean", "periode"])[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # Proportion de True
    df_counts["proportion_true"] = (
        df_counts["true_mentions"] / df_counts["total_mentions"]
    )

    # Statistiques
    stats = {
        "moyenne_proportion": df_counts["proportion_true"].mean(),
        "médiane_proportion": df_counts["proportion_true"].median(),
        "moyenne_valeur": df_counts["true_mentions"].mean(),
        "médiane_valeur": df_counts["true_mentions"].median(),
        "deciles_proportion": df_counts["proportion_true"].quantile(
            [i / 10 for i in range(1, 10)]
        )
        * 100,
        "deciles_valeur": df_counts["true_mentions"].quantile(
            [i / 100 for i in range(75, 100)]
        ),
    }

    # Calcul de la distribution cumulative pour true_mentions
    valeurs_triees = np.sort(df_counts["true_mentions"].values)
    distribution_cumulee = (
        100 * (np.arange(len(valeurs_triees)) + 1) / len(valeurs_triees)
    )
    stats["distribution_cumulee_true_mentions"] = {
        "valeurs": valeurs_triees,
        "distribution": distribution_cumulee,
    }

    # Calcul de la distribution cumulative pour proportion_true
    valeurs_triees_prop = np.sort(df_counts["proportion_true"].values)
    distribution_cumulee_prop = (
        100 * (np.arange(len(valeurs_triees_prop)) + 1) / len(valeurs_triees_prop)
    )
    stats["distribution_cumulee_proportion_true"] = {
        "valeurs": valeurs_triees_prop,
        "distribution": distribution_cumulee_prop,
    }
    return stats


# %%
nom_orateur = "M. Gérald Darmanin"
df_test = df[df["nom_orateur_clean"] == nom_orateur]
df_test["nombre_mentions_repu"].sum()
df_test["nombre_mentions_repu"].mean()


# %%
def stats_occurrences_orateur(
    df_repu,
    nom_orateur,
    colonne_nom="nom_orateur_clean",
    colonne_mentions="nombre_mentions_repu",
):
    # Filtrer les données pour l'orateur spécifié
    df_orateur = df_repu[df_repu[colonne_nom] == nom_orateur]
    # Calculer la moyenne et la médiane
    somme = df_repu[colonne_mentions].sum()
    moyenne = df_repu[colonne_mentions].mean()
    mediane = df_repu[colonne_mentions].median()

    return {"somme": somme, "moyenne": moyenne, "médiane": mediane}



# %%
resultat = stats_occurrences_orateur(df_repu, "M. Gérald Darmanin")
print(resultat)

# %%
# Sur toute la période
stats_global = diachronique_personnelpo_statistiques(
    df, colonne_condition="repu_match_valide", periode="global"
)  # remplacer df par df_regroup
print("Statistiques sur X")
print(f"Moyenne (VA) : {stats_global['moyenne_valeur']:.2f}")
print(f"Médiane (VA) : {stats_global['médiane_valeur']:.2f}")
print(f"Déciles (VA)  : {stats_global['deciles_valeur']}")
print(f"Moyenne (%)  : {stats_global['moyenne_proportion']:.2%}")
print(f"Médiane (%) : {stats_global['médiane_proportion']:.2f}")
print(f"Déciles (%)  : {stats_global['deciles_proportion']}")

# --- Par année ---
# stats_annee = diachronique_personnelpo_statistiques(df, periode="annee")
# print("Par Année :")
# print(f"Moyenne (VA) : {stats_annee['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_annee['médiane_valeur']:.2f}")
# print(f"Déciles (VA)  : {stats_annee['deciles_valeur']}")
# print(f"Moyenne (%)  : {stats_annee['moyenne_proportion']:.2%}")
# print(f"Médiane (%) : {stats_annee['médiane_proportion']:.2f}")
# print(f"Déciles (%)  : {stats_annee['deciles_proportion']}")

# --- Par mois ---
# stats_mois = diachronique_personnelpo_statistiques(df, periode="mois")
# print("Par Mois :")
# print(f"Moyenne (VA) : {stats_mois['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_mois['médiane_valeur']:.2f}")
# print(f"Déciles (VA)  : {stats_mois['deciles_valeur']}")
# print(f"Moyenne (%)  : {stats_mois['moyenne_proportion']:.2%}")
# print(f"Médiane (%) : {stats_mois['médiane_proportion']:.2f}")
# print(f"Déciles (%)  : {stats_mois['deciles_proportion']}")

# --- Par semaine ---
# stats_sem = diachronique_personnelpo_statistiques(df, periode="semaine")
# print("Par Semaine :")
# print(f"Moyenne (VA) : {stats_sem['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_sem['médiane_valeur']:.2f}")
# print(f"Déciles (VA)  : {stats_sem['deciles_valeur']}")
# print(f"Moyenne (%)  : {stats_sem['moyenne_proportion']:.2%}")
# print(f"Médiane (%) : {stats_sem['médiane_proportion']:.2f}")
# print(f"Déciles (%)  : {stats_sem['deciles_proportion']}")

# stats_journalières = diachronique_personnelpo_statistiques(df_CRPR, colonne_condition="repu_match_valide", periode="jour") #remplacer df par df_regroup
# print("Statistiques journalier sur X")
# print(f"Moyenne (VA) : {stats_journalières['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_journalières['médiane_valeur']:.2f}")
# print(f"Déciles (VA)  : {stats_journalières['deciles_valeur']}")
# print(f"Moyenne (%)  : {stats_journalières['moyenne_proportion']:.2%}")
# print(f"Médiane (%) : {stats_journalières['médiane_proportion']:.2f}")
# print(f"Déciles (%)  : {stats_journalières['deciles_proportion']}")

# %%
# Récupérer les données pour true_mentions
data_true_mentions = stats_global["distribution_cumulee_true_mentions"]

fig = px.line(
    x=data_true_mentions["distribution"],
    y=data_true_mentions["valeurs"],
    title="Distribution cumulative des personnes utilisant la 'République' lors de CRPR",
    labels={"x": "Distribution (%)", "y": "Nombre de true_mentions"},
    width=800,
    height=500,
)
fig.show()

# %%
df_CRPR["id_orateur"].nunique()


# %% [markdown]
# #### Tableau(x) et graphique(s)

# %% [markdown]
# ##### En valeur absolue

# %%
def diachronique_personnelpo_va(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    préfixe,
    top_n,
    colonne_député="nom_orateur_clean",
):
    # 1. Déterminer le groupe dominant de chaque personnel politique (le plus fréquent)
    groupe_dominant = (
        df.groupby([colonne_député, colonne_groupe])
        .size()
        .reset_index(name="nb_mentions")
        .sort_values(["nom_orateur_clean", "nb_mentions"], ascending=[True, False])
        .drop_duplicates(subset=colonne_député)
        .set_index(colonne_député)[colonne_groupe]
    )

    # 2. Compter le nombre de mobilisation de l'objet d'étude pour chaque personnel politique
    counts = (
        df.groupby(colonne_député)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Ajouter la colonne du groupe dominant
    counts[colonne_groupe] = counts[colonne_député].map(groupe_dominant)

    # 4. Ajouter la couleur correspondante
    counts["couleur"] = (
        counts[colonne_groupe].map(couleurs_groupes).fillna(couleurs_groupes["Autres"])
    )

    # 5. Trier les députés par le nombre de mentions "True"
    df_personnelpo_va = (
        counts.sort_values("true_mentions", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    # 6. Créer le graphique
    fig = go.Figure()

    for _, row in df_personnelpo_va.iterrows():
        fig.add_trace(
            go.Bar(
                x=[row[colonne_député]],
                y=[row["true_mentions"]],
                name=row[colonne_député],  # essayer d'enlever
                marker_color=row["couleur"],
                hovertemplate=f"<b>{row[colonne_député]}</b><br>"
                f"Groupe : {row[colonne_député]}<br>"
                f"Occurrences : {row['true_mentions']}",
                showlegend=False,
            )
        )

    # 7. Mise en forme
    fig.update_layout(
        title=f"Top {top_n} du personnel politique investissant le plus la {préfixe} '{colonne_condition}' à l'AN en valeur absolue (A)",
        xaxis=dict(title="Député·es -- Ministres", tickangle=-45),
        yaxis=dict(title="Valeur absolue", showgrid=False),
        template="plotly_white",
        bargap=0.25,
    )

    fig.show()
    return df_personnelpo_va


# %%
table = df_repu["nom_orateur_clean"].value_counts()[0:20].reset_index()
table = table.rename(columns={"count": "Nombre de mentions"})
table

# %%
df_repu

# %%
diachronique_personnelpo_va(
    df,
    couleurs_groupes,
    top_n=20,
    colonne_condition="repu_match_valide",
    colonne_groupe="affiliation_et_gouv",
    préfixe="thématique",
)


# %% [markdown]
# ##### En proportion 

# %%
def diachronique_personnelpo_proportion(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    préfixe,
    min_true,
    top_n,
    colonne_député="nom_orateur_clean",
):
    # 1. Déterminer le groupe dominant de chaque orateur (le plus fréquent)
    groupe_dominant = (
        df.groupby([colonne_député, colonne_groupe])
        .size()
        .reset_index(name="nb_mentions")
        .sort_values(["nom_orateur_clean", "nb_mentions"], ascending=[True, False])
        .drop_duplicates(subset=colonne_député)
        .set_index(colonne_député)[colonne_groupe]
    )

    # 2. Compter le nombre total et de "True" pour chaque orateur
    counts = (
        df.groupby(colonne_député)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Calcul de la proportion
    counts["proportion_true"] = round(
        counts["true_mentions"] / counts["total_mentions"] * 100, 2
    )

    # 4. Ajouter la colonne du groupe dominant
    counts[colonne_groupe] = counts[colonne_député].map(groupe_dominant)

    # 5. Ajouter la couleur correspondante
    counts["couleur"] = (
        counts[colonne_groupe].map(couleurs_groupes).fillna(couleurs_groupes["Autres"])
    )

    # Filtrer les orateurs avec au moins X mentions True
    filtered = counts[counts["total_mentions"] >= min_true]

    # 5. Trier les députés par le nombre de mentions de la FDM "République"
    df_personnelpo_proportion = (
        filtered.sort_values("proportion_true", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    # 6. Créer le graphique
    fig = go.Figure()

    for _, row in df_personnelpo_proportion.iterrows():
        fig.add_trace(
            go.Bar(
                x=[row[colonne_député]],
                y=[row["proportion_true"]],
                name=row[colonne_député],  # essayer d'enlever
                marker_color=row["couleur"],
                hovertemplate=f"<b>{row[colonne_député]}</b><br>"
                f"Groupe : {row[colonne_groupe]}<br>"
                f"Proportions en % : {row['proportion_true']}",
                showlegend=False,
            )
        )

    # 7. Mise en forme
    fig.update_layout(
        title=f"Top {top_n} du personnel politique investissant le plus la {préfixe} '{colonne_condition}' à l'AN en % (seuil {min_true})",
        xaxis=dict(title="Député·es -- Ministres", tickangle=-45),
        yaxis=dict(title="Proportion en %", showgrid=False),
        template="plotly_white",
        bargap=0.25,
    )

    fig.show()
    return df_personnelpo_proportion


# %%
diachronique_personnelpo_proportion(
    df_interv,
    couleurs_groupes,
    colonne_condition="repu_match_valide",
    colonne_groupe="affiliation_et_gouv",
    préfixe="thématique",
    top_n=20,
    min_true=30,
)


# %% [markdown]
# ##### En VA et %

# %%
def diachronique_personnelpo_total(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    préfixe,
    min_true,
    top_n,
    colonne_député="nom_orateur_clean",
    mode="Double",
):
    # 1. Déterminer le groupe le plus fréquent pour chaque personnel politique
    groupe_dominant = (
        df.groupby([colonne_député, colonne_groupe])
        .size()
        .reset_index(name="nb_mentions")
        .sort_values([colonne_député, "nb_mentions"], ascending=[True, False])
        .drop_duplicates(subset=colonne_député)
        .set_index(colonne_député)[colonne_groupe]
    )

    # 2. Compter le nombre d'occurrences de la FDM pour chaque personnel politique
    counts = (
        df.groupby(colonne_député)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Calcul de la proportion (%)
    counts["proportion_true"] = round(
        counts["true_mentions"] / counts["total_mentions"] * 100, 2
    )

    # 4. Ajouter le groupe dominant et la couleur
    counts[colonne_groupe] = counts[colonne_député].map(groupe_dominant)
    counts["couleur"] = (
        counts[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )

    # 5. Filtrer le personnel politique à partir d'un minimum d'occurrences
    filtered = counts[counts["true_mentions"] >= min_true]
    df_personnelpo_total = (
        filtered.sort_values("true_mentions", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    # 6. Créer la figure Plotly
    fig = go.Figure()

    # --- Mode "absolu" ou "double" : afficher les barres ---
    if mode in ["absolu", "double"]:
        for _, row in df_personnelpo_total.iterrows():
            fig.add_trace(
                go.Bar(
                    x=[row[colonne_député]],
                    y=[row["true_mentions"]],
                    name=row[colonne_député],
                    marker_color=row["couleur"],
                    yaxis="y1",
                    hovertemplate=f"<b>{row[colonne_député]}</b><br>"
                    f"Groupe : {row[colonne_groupe]}<br>"
                    f"Valeur absolue : {row['true_mentions']}<br>"
                    f"Proportion : {row['proportion_true']:.1f} %",
                    showlegend=False,
                )
            )

    # --- Mode "proportion" ou "double" : afficher les points ---
    if mode in ["proportion", "double"]:
        fig.add_trace(
            go.Scatter(
                x=df_personnelpo_total[colonne_député],
                y=df_personnelpo_total["proportion_true"],
                name="Proportion d'intervention en % avec FDM 'République'",
                mode="markers",
                marker=dict(color="black", size=8, symbol="circle"),
                line=dict(width=1, dash="dot", color="black"),
                yaxis="y2",
            )
        )

    # 7. Mise en forme du graphique
    fig.update_layout(
        title=(
            f"Top {top_n} du personnel politique investissant le plus la République lors de CRPR"
        ),
        xaxis=dict(title="Député·es / Ministres", tickangle=-45),
        yaxis=dict(title="Valeur absolue", showgrid=False),
        yaxis2=dict(
            title="Proportion en %",
            overlaying="y",
            side="right",
            showgrid=False,
            range=[
                0,
                max(df_personnelpo_total["proportion_true"].max() * 1.1, 10),
            ],  # marge auto
        ),
        legend=dict(x=0.6, y=1.2, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    # 8. Ajustement du titre selon le mode
    if mode == "absolu":
        fig.update_layout(title=fig.layout.title.text + " — en valeur absolue")
    elif mode == "proportion":
        fig.update_layout(title=fig.layout.title.text + " — en proportion (%)")
    else:
        fig.update_layout(title=fig.layout.title.text + "")

    fig.show()

    return df_personnelpo_total



# %%
diachronique_personnelpo_total(
    df_interv,
    couleurs_groupes,
    colonne_condition="repu_match_valide",
    colonne_groupe="affiliation_et_gouv",
    préfixe="thématique",
    top_n=20,
    min_true=10,
    mode="double",
)

# %%
nom_orateur = "M. Sébastien Jumel"
df_test = df[df["nom_orateur_clean"] == nom_orateur]
df_test["nombre_mentions_repu"].sum()
df_test["nombre_mentions_repu"].mean()

# %%
diachronique_personnelpo_total(
    df_interv,
    couleurs_groupes,
    colonne_condition="repu_match_valide",
    colonne_groupe="affiliation_et_gouv",
    préfixe="thématique",
    top_n=15,
    min_true=10,
    mode="double",
)


# %% [markdown]
# ### Analyse synchronique

# %% [markdown]
# #### En valeur absolue 

# %%
def synchronique_personnel_va(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    préfixe,
    top_n,
    colonne_député="nom_orateur_clean",
    date_col="dateSeance_day",
):
    # 1. Déterminer le groupe dominant pour chaque personnel politique
    groupe_dominant = (
        df.groupby([colonne_député, colonne_groupe])
        .size()
        .reset_index(name="n")
        .sort_values(["nom_orateur_clean", "n"], ascending=[True, False])
        .drop_duplicates(subset=colonne_député)
        .set_index(colonne_député)[colonne_groupe]
    )

    # 2. Calcul du total de mentions True par personnel politique
    counts = (
        df.groupby(colonne_député)[colonne_condition]
        .apply(lambda x: (x == True).sum())
        .reset_index(name="true_mentions")
    )

    # 3. Sélection des Top N personnel politique
    top_députés = (
        counts.sort_values("true_mentions", ascending=False)
        .head(top_n)[colonne_député]
        .tolist()
    )

    # 4. Filtrer les données correspondantes
    df_top = df[df[colonne_député].isin(top_députés)].copy()

    # 5. Ajouter groupe dominant et couleur
    df_top[colonne_groupe] = df_top[colonne_député].map(groupe_dominant)
    df_top["couleur"] = (
        df_top[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )

    # 6. Agrégation annuelle (YS = début d’année)
    df_agg = (
        df_top.groupby([pd.Grouper(key=date_col, freq="YS"), colonne_député])[
            colonne_condition
        ]
        .apply(lambda x: (x == True).sum())
        .reset_index(name="true_mentions")
    )

    # 7. Ajouter le groupe et la couleur
    df_agg[colonne_groupe] = df_agg[colonne_député].map(groupe_dominant)
    df_agg["couleur"] = (
        df_agg[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )

    # 8. Liste de symboles pour différencier les députés d’un même groupe
    symboles_possibles = [
        "circle",
        "square",
        "diamond",
        "cross",
        "triangle-up",
        "triangle-down",
        "triangle-left",
        "triangle-right",
        "x",
        "star",
        "hexagram",
        "pentagon",
    ]

    # 9. Attribution automatique des symboles par groupe
    symbol_mapping = {}
    for groupe, sous_df in df_agg.groupby(colonne_groupe):
        députés_groupe = sous_df[colonne_député].unique()
        for i, député in enumerate(députés_groupe):
            symbol_mapping[député] = symboles_possibles[i % len(symboles_possibles)]

    # 10. Création du graphique
    fig = go.Figure()

    for député in top_députés:
        couleur = df_agg.loc[df_agg[colonne_député] == député, "couleur"].iloc[0]
        symbole = symbol_mapping.get(député, "circle")
        df_temp = df_agg[df_agg[colonne_député] == député]

        fig.add_trace(
            go.Scatter(
                x=df_temp[date_col],
                y=df_temp["true_mentions"],
                mode="lines+markers",
                name=député,
                line=dict(color=couleur, width=1.75),
                marker=dict(size=8, symbol=symbole),
                hovertemplate=(f"<b>{député}</b><br>%{{x|%Y}}<br>Occurrences : %{{y}}"),
            )
        )

    # 11. Mise en forme
    fig.update_layout(
        title=f"Évolution du Top {top_n} du personnel politique investissant le plus la {préfixe} '{colonne_condition}' à l'AN",
        xaxis=dict(title="Année", tickformat="%Y"),
        yaxis=dict(title="Occurrences (valeur absolue)", showgrid=False),
        legend=dict(x=0.85, y=1.15, bgcolor="#E3E1E1"),
        bargap=0.2,
        template="plotly_white",
    )

    fig.show()
    return df_agg



# %%
synchronique_personnel_va(
    df,
    couleurs_groupes,
    colonne_condition="repu_match_valide",
    colonne_groupe="affiliation_et_gouv",
    préfixe="thématique",
    top_n=5,
)


# %% [markdown]
# #### En proportion

# %%
def synchronique_personnel_proportion(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    préfixe,
    top_n,
    min_true,
    colonne_député="nom_orateur_clean",
    date_col="dateSeance_day",
):
    # 1. Déterminer le groupe dominant pour chaque personnel politique
    groupe_dominant = (
        df.groupby([colonne_député, colonne_groupe])
        .size()
        .reset_index(name="n")
        .sort_values([colonne_député, "n"], ascending=[True, False])
        .drop_duplicates(subset=colonne_député)
        .set_index(colonne_député)[colonne_groupe]
    )

    # 2. Calculer total et True par personnel politique
    counts = (
        df.groupby(colonne_député)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Ajouter la proportion globale (%)
    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"] * 100

    # 4.  Ajouter le groupe dominant et la couleur
    counts[colonne_groupe] = counts[colonne_député].map(groupe_dominant)
    counts["couleur"] = (
        counts[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )

    # 5. Filtrer les orateurs avec un nombre minimum d’occurrences True
    filtered = counts[counts["true_mentions"] >= min_true]

    # 6. Sélectionner les top N selon la proportion
    top_députés = (
        filtered.sort_values("proportion_true", ascending=False)
        .head(top_n)[colonne_député]
        .tolist()
    )

    # 7. Filtrer le DF pour ces top N
    df_top = df[df[colonne_député].isin(top_députés)].copy()

    # 8. Agrégation annuelle : total & true
    df_agg = (
        df_top.groupby([pd.Grouper(key=date_col, freq="YS"), colonne_député])[
            colonne_condition
        ]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 9. Ajouter la proportion annuelle (%)
    df_agg["proportion_true"] = df_agg["true_mentions"] / df_agg["total_mentions"] * 100

    # 10. Ajouter le groupe, la couleur et l’année
    df_agg[colonne_groupe] = df_agg[colonne_député].map(groupe_dominant)
    df_agg["couleur"] = (
        df_agg[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )
    df_agg["Année"] = df_agg[date_col].dt.year

    # 11. Définir des symboles distincts pour différencier les personnalités d’un même groupe
    symboles_possibles = [
        "circle",
        "square",
        "diamond",
        "cross",
        "triangle-up",
        "triangle-down",
        "triangle-left",
        "triangle-right",
        "x",
        "star",
        "hexagram",
        "pentagon",
    ]

    symbol_mapping = {}
    for g, sous_df in df_agg.groupby(colonne_groupe):
        députés_groupe = sous_df[colonne_député].unique()
        for i, député in enumerate(députés_groupe):
            symbol_mapping[député] = symboles_possibles[i % len(symboles_possibles)]

    # 12. Création du graphique
    fig = go.Figure()

    for député in top_députés:
        df_temp = df_agg[df_agg[colonne_député] == député]
        couleur = df_temp["couleur"].iloc[0]
        symbole = symbol_mapping.get(député, "circle")

        fig.add_trace(
            go.Scatter(
                x=df_temp["Année"],
                y=df_temp["proportion_true"],
                mode="lines+markers",
                name=député,
                line=dict(color=couleur, width=2),
                marker=dict(size=8, symbol=symbole),
                hovertemplate=(
                    f"<b>{député}</b><br>Année : %{{x}}<br>Proportion : %{{y:.1f}}%"
                ),
            )
        )

    # 13. Mise en forme finale
    fig.update_layout(
        title=f"Évolution des {top_n} principaux personnel politique investissant la {préfixe} '{colonne_condition}' à l'AN (en %, seuil {min_true})",
        xaxis=dict(title="Année", tickformat="%Y"),
        yaxis=dict(title="Proportion d’occurrences (%)", showgrid=False),
        legend=dict(x=0.75, y=1.15, bgcolor="#E3E1E1"),
        template="plotly_white",
    )

    fig.show()
    return df_agg



# %%
synchronique_personnel_proportion(
    df,
    couleurs_groupes,
    colonne_condition="Territoires métropolitains",
    colonne_groupe="groupe&gvt_affiliation",
    préfixe="thématique",
    top_n=5,
    min_true=10,
)


# %% [markdown]
# #### En VA et % (trop complexe)

# %%
def synchronique_personnels_proportion(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    préfixe,
    top_n,
    min_true,
    colonne_député="nom_orateur_clean",
    date_col="dateSeance_day",
):
    # 1. Déterminer le groupe dominant pour chaque personnel politique
    groupe_dominant = (
        df.groupby([colonne_député, colonne_groupe])
        .size()
        .reset_index(name="n")
        .sort_values([colonne_député, "n"], ascending=[True, False])
        .drop_duplicates(subset=colonne_député)
        .set_index(colonne_député)[colonne_groupe]
    )

    # 2. Calculer total et True par personnel politique
    counts = (
        df.groupby(colonne_député)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Ajouter la proportion globale (%)
    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"] * 100

    # 4. Ajouter le groupe dominant et la couleur
    counts[colonne_groupe] = counts[colonne_député].map(groupe_dominant)
    counts["couleur"] = (
        counts[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )

    # 5. Filtrer les orateurs avec un nombre minimum d’occurrences True
    filtered = counts[counts["true_mentions"] >= min_true]

    # 6. Sélectionner les top N selon la proportion
    top_députés = (
        filtered.sort_values("proportion_true", ascending=False)
        .head(top_n)[colonne_député]
        .tolist()
    )

    # 7. Filtrer le DF pour ces top N
    df_top = df[df[colonne_député].isin(top_députés)].copy()

    # 8. Agrégation annuelle : total & true
    df_agg = (
        df_top.groupby([pd.Grouper(key=date_col, freq="YS"), colonne_député])[
            colonne_condition
        ]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 9. Ajouter la proportion annuelle (%)
    df_agg["proportion_true"] = df_agg["true_mentions"] / df_agg["total_mentions"] * 100

    # 10. Ajouter le groupe, la couleur et l’année
    df_agg[colonne_groupe] = df_agg[colonne_député].map(groupe_dominant)
    df_agg["couleur"] = (
        df_agg[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )
    df_agg["Année"] = df_agg[date_col].dt.year

    # 11. Symboles distincts pour différencier les personnalités d’un même groupe
    symboles_possibles = [
        "circle",
        "square",
        "diamond",
        "cross",
        "triangle-up",
        "triangle-down",
        "triangle-left",
        "triangle-right",
        "x",
        "star",
        "hexagram",
        "pentagon",
    ]

    symbol_mapping = {}
    for g, sous_df in df_agg.groupby(colonne_groupe):
        députés_groupe = sous_df[colonne_député].unique()
        for i, député in enumerate(députés_groupe):
            symbol_mapping[député] = symboles_possibles[i % len(symboles_possibles)]

    # 12. Création du graphique
    fig = go.Figure()

    for député in top_députés:
        df_temp = df_agg[df_agg[colonne_député] == député]
        couleur = df_temp["couleur"].iloc[0]
        symbole = symbol_mapping.get(député, "circle")

        # Courbe principale : proportion (%)
        fig.add_trace(
            go.Scatter(
                x=df_temp["Année"],
                y=df_temp["proportion_true"],
                mode="lines+markers",
                name=f"{député} (%)",
                line=dict(color=couleur, width=2),
                marker=dict(size=8, symbol=symbole),
                yaxis="y1",
                hovertemplate=(
                    f"<b>{député}</b><br>"
                    "Année : %{x}<br>"
                    "Proportion : %{y:.1f}%<extra></extra>"
                ),
            )
        )

        # Deuxième trace : valeur absolue (barres fines)
        fig.add_trace(
            go.Bar(
                x=df_temp["Année"],
                y=df_temp["true_mentions"],
                name=f"{député} (VA)",
                marker_color=couleur,
                opacity=0.5,
                yaxis="y2",
                hovertemplate=(
                    f"<b>{député}</b><br>"
                    "Année : %{x}<br>"
                    "Occurrences : %{y}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    # 13 Mise en forme finale
    fig.update_layout(
        title=f"Évolution des {top_n} principaux personnel politique investissant la {préfixe} '{colonne_condition}' à l'AN (seuil {min_true})",
        xaxis=dict(title="Année", tickformat="%Y"),
        yaxis=dict(title="Proportion d’occurrences (%)", side="right", showgrid=False),
        yaxis2=dict(
            title="Valeur absolue (occurrences)",
            overlaying="y",
            side="left",
            showgrid=False,
        ),
        legend=dict(x=0.70, y=1.15, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    fig.show()
    return df_agg



# %%
synchronique_personnels_proportion(
    df,
    couleurs_groupes,
    colonne_condition="Territoires métropolitains",
    colonne_groupe="groupe&gvt_affiliation",
    top_n=5,
    min_true=10,
)


# %% [markdown]
# ### Analyses par personnes 

# %% [markdown]
# #### Topic

# %%
def topics_par_orateur(df, nom_orateur):
    # Filtrer pour l'orateur sélectionné
    df_orateur = df[df["nom_orateur_clean"] == nom_orateur].copy()

    # Compter les occurrences de chaque topic
    topic_counts = (
        df_orateur["topic"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "topic", "topic": "occurrences"})
    )

    # Trier par nombre d'occurrences (décroissant)
    topic_counts = topic_counts.sort_values(by="occurrences", ascending=False)

    return topic_counts



# %%
df

# %%
resultat = topics_par_orateur(df, "M. Xavier Breton")
print(resultat)


# %% [markdown]
# #### Statistiques 

# %%
def stat_test(
    df,
    colonne_condition,
    colonne_orateur,
    personnel_po="nom_orateur_clean",
    commission="commission_député",
):
    # 1. Filtrer pour la personne choisie
    df_personne = df[df[colonne_orateur] == personnel_po].copy()

    # 2. Déterminer la commission dominante de la personne
    commission_dominante = (
        df_personne.groupby(commission)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .iloc[0][commission]
    )

    # 3. Compter le nombre d'interventions avec la République
    total_interventions = len(df_personne)
    interventions_avec_republique = df_personne[colonne_condition].sum()

    # 4. Calculer la proportion d'interventions utilisant la République
    proportion_republique = (
        (interventions_avec_republique / total_interventions * 100)
        if total_interventions > 0
        else 0
    )

    # 5. Calculer le nombre total d'occurrences de la République
    total_occurrences_republique = df_personne["nombre_mentions_repu"].sum()

    # 6. Calculer la moyenne des occurrences de la République
    moyenne_occurrences_republique = df_personne["nombre_mentions_repu"].mean()

    # 7. Créer un tableau avec les résultats
    resultats = {
        "Commission principale": [commission_dominante],
        "Proportion d'interventions avec la République (%)": [proportion_republique],
        "Nombre d'interventions avec la République": [interventions_avec_republique],
        "Nombre total d'occurrences de la République": [total_occurrences_republique],
        "Moyenne des occurrences de la République": [moyenne_occurrences_republique],
    }

    return resultats


# %%
resultats = stat_test(
    df=df_interv,
    colonne_condition="repu_match_valide",
    colonne_orateur="nom_orateur_clean",  # Remplace si nécessaire
    personnel_po="M. Yves Jégo",
)

resultats_df = pd.DataFrame(resultats)

print(resultats_df)

# %%
df[df["nom_orateur_clean"] == "M. Éric Poulliat"].topic


# %%
def statistiques_personnelpo(df, personnel_po, colonne_condition, periode="semaine"):
    # Filtrer sur la personne voulue
    df_personnel = df[df["nom_orateur_clean"] == personnel_po].copy()
    if df_personnel.empty:
        raise ValueError(
            f"Aucune donnée trouvée pour le personnel politique : {personnel_po}"
        )

    # Définir la granularité
    if periode == "semaine":
        df_personnel["periode"] = (
            df_personnel["dateSeance_day"].dt.isocalendar().year.astype(str)
            + "-W"
            + df_personnel["dateSeance_day"].dt.isocalendar().week.astype(str)
        )
    elif periode == "mois":
        df_personnel["periode"] = (
            df_personnel["dateSeance_day"].dt.to_period("M").astype(str)
        )
    elif periode == "annee":
        df_personnel["periode"] = df_personnel["dateSeance_day"].dt.year.astype(str)
    elif periode == "global":
        df_personnel["periode"] = "Global"

    # Compter occurrences par période (proportion et True)
    df_counts = (
        df_personnel.groupby("periode")[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # Proportion de True
    df_counts["proportion_true"] = (
        df_counts["true_mentions"] / df_counts["total_mentions"]
    )

    # Statistiques
    stats = {
        "moyenne_proportion": df_counts["proportion_true"].mean(),
        "médiane_proportion": df_counts["proportion_true"].median(),
        "moyenne_valeur": df_counts["true_mentions"].mean(),
        "médiane_valeur": df_counts["true_mentions"].median(),
        "deciles_proportion": df_counts["proportion_true"].quantile(
            [i / 10 for i in range(0, 10)]
        )
        * 100,
        "deciles_valeur": df_counts["true_mentions"].quantile(
            [i / 10 for i in range(0, 10)]
        ),
    }

    return stats


# %%
def statistiques_personnelpo_moyenne(
    df, personnel_po, colonne_condition, periode="semaine"
):
    # Filtrer sur la personne voulue
    df_personnel = df[df["nom_orateur_clean"] == personnel_po].copy()
    if df_personnel.empty:
        raise ValueError(
            f"Aucune donnée trouvée pour le personnel politique : {personnel_po}"
        )

    # Définir la granularité
    if periode == "semaine":
        df_personnel["periode"] = (
            df_personnel["dateSeance_day"].dt.isocalendar().year.astype(str)
            + "-W"
            + df_personnel["dateSeance_day"].dt.isocalendar().week.astype(str)
        )
    elif periode == "mois":
        df_personnel["periode"] = (
            df_personnel["dateSeance_day"].dt.to_period("M").astype(str)
        )
    elif periode == "annee":
        df_personnel["periode"] = df_personnel["dateSeance_day"].dt.year.astype(str)
    elif periode == "global":
        df_personnel["periode"] = "Global"

    # Calculer la moyenne par période
    df_counts = (
        df_personnel.groupby("periode")[colonne_condition]
        .agg(
            total_interventions="count",
            moyenne_par_intervention="mean",
            somme_totale="sum",
        )
        .reset_index()
    )

    # Statistiques
    stats = {
        "moyenne_globale": df_counts["moyenne_par_intervention"].mean(),
        "médiane_globale": df_counts["moyenne_par_intervention"].median(),
        "moyenne_totale_par_période": df_counts["somme_totale"].mean(),
        "médiane_totale_par_période": df_counts["somme_totale"].median(),
        "déciles_moyenne": df_counts["moyenne_par_intervention"].quantile(
            [i / 10 for i in range(0, 10)]
        ),
        "déciles_totale": df_counts["somme_totale"].quantile(
            [i / 10 for i in range(0, 10)]
        ),
    }

    return stats



# %%
stats = statistiques_personnelpo_moyenne(
    df, "M. Éric Poulliat", "repu_match_valide", "mois"
)


# %%
personnel_po = "M. Guillaume Vuilletet"
colonne_condition = "repu_match_valide"

# Sur toute la période
stats_global = statistiques_personnelpo_moyenne(
    df, personnel_po, colonne_condition, periode="global"
)
print(f"Statistiques de {personnel_po} sur 2017-2024")
print(f"Moyenne d'utilisation par intervention : {stats_global['moyenne_globale']:.2f}")
print(f"Médiane d'utilisation par intervention : {stats_global['médiane_globale']:.2f}")
# print(f"Médiane (VA) : {stats_global['médiane_valeur']:.2f}")

# --- Par année ---
stats_annee = statistiques_personnelpo_moyenne(
    df, personnel_po, colonne_condition, periode="annee"
)
# print(f"Statistiques de {personnel_po} par années")
# print(f"Moyenne (VA) : {stats_annee['moyenne_globale']:.2f}")
# print(f"Médiane (VA) : {stats_annee['médiane_globale']:.2f}")
# print(f"Répartition (VA)  : {stats_annee['description_valeur']:}")
# print(f"Répartition (%)  : {stats_annee['description_proportion']:}")
# print(f"Déciles (VA)  : {stats_annee['deciles_valeur']}")
# print(f"Déciles (%)  : {stats_annee['deciles_proportion']}")

# --- Par mois ---
stats_mois = statistiques_personnelpo_moyenne(
    df, personnel_po, colonne_condition, periode="mois"
)
# print(f"Statistiques de {personnel_po} par mois")
# print(f"Moyenne (VA) : {stats_mois['moyenne_globale']:.2f}")
# print(f"Médiane (VA) : {stats_mois['médiane_globale']:.2f}")
# print(f"Répartition (VA)  : {stats_mois['description_valeur']}")
# print(f"Répartition (%)  : {stats_mois['description_proportion']:}")


# --- Par semaine ---
# stats_sem = statistiques_personnelpo(df, personnel_po, periode="semaine")
# print(f"Statistiques de {personnel_po} par semaines")
# print(f"Moyenne (VA) : {stats_sem['moyenne_valeur']:.2f}")
# print(f"Moyenne (%)  : {stats_sem['moyenne_proportion']:.2%}")
# print(f"Répartition (VA)  : {stats_sem['description_valeur']}")
# print(f"Répartition (%)  : {stats_sem['description_proportion']}")
# print(f"Déciles (VA)  : {stats_sem['deciles_valeur']}")
# print(f"Déciles (%)  : {stats_sem['deciles_proportion']}")


# %%
def synchronique_personnel(
    df,
    couleurs_groupes,
    colonne_condition,
    personnel_po,
    colonne_groupe,
    préfixe,
    periode,
    colonne_député="nom_orateur_clean",
    date_col="dateSeance_day",
):
    # 1. Filtrer pour la personne choisie
    df = df[df[colonne_député] == personnel_po].copy()

    # 2. Déterminer le groupe dominant de la personne
    groupe_dominant = (
        df.groupby(colonne_groupe)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .iloc[0][colonne_groupe]
    )

    # 3. Rajouter la couleur du groupe/personne (secondaire)
    couleur = couleurs_groupes.get(
        groupe_dominant, couleurs_groupes.get("Autres", "grey")
    )

    # 4. Déterminer la fréquence temporelle selon la période choisie
    freq_mapping = {
        "D": ("D", "Jour", "%D"),
        "A": ("YS", "Année", "%Y"),
        "M": ("MS", "Mois", "%b %Y"),
        "Q": ("Q", "Trimestre", "T%q %Y"),
    }
    if periode not in freq_mapping:
        raise ValueError("periode doit être 'A' (année), 'M' (mois) ou 'Q' (trimestre)")

    freq, label_x, tickformat = freq_mapping[periode]

    # 5. Agrégation temporelle
    df_agg = (
        df.groupby(pd.Grouper(key=date_col, freq=freq))[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 6. Calcul de la proportion et de l’année
    df_agg["proportion_true"] = df_agg["true_mentions"] / df_agg["total_mentions"] * 100
    df_agg["Période"] = df_agg[date_col]

    # 7. Création du graphique
    fig = go.Figure()

    # Courbe principale (%)
    fig.add_trace(
        go.Scatter(
            x=df_agg["Période"],
            y=df_agg["proportion_true"],
            mode="lines+markers",
            name=f"{personnel_po} (%)",
            line=dict(color=couleur, width=3),
            marker=dict(size=8, symbol="circle"),
            yaxis="y1",
            hovertemplate=(
                f"<b>{personnel_po}</b><br>"
                "Année : %{x}<br>"
                "Proportion : %{y:.1f}%<extra></extra>"
            ),
        )
    )

    # Barres = valeurs absolues
    fig.add_trace(
        go.Bar(
            x=df_agg["Période"],
            y=df_agg["true_mentions"],
            name=f"{personnel_po} (VA)",
            marker_color=couleur,
            opacity=0.4,
            yaxis="y2",
            hovertemplate=(
                f"<b>{personnel_po}</b><br>"
                "Année : %{x}<br>"
                "Occurrences : %{y}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    # 7. Mise en forme finale
    fig.update_layout(
        title=f"Évolution annuelle de la {préfixe} '{colonne_condition}' par {personnel_po} ({groupe_dominant}) à l'AN",
        xaxis=dict(title=label_x, tickformat=tickformat),
        yaxis=dict(title="Proportion(%)", side="right", showgrid=False),
        yaxis2=dict(
            title="Valeur absolue", overlaying="y", side="left", showgrid=False
        ),
        legend=dict(x=0.83, y=1.25, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    fig.show()
    return df_agg



# %%
personnel_po = "M. Guillaume Vuilletet"
colonne_condition = "repu_match_valide"

# Sur toute la période
stats_global = statistiques_personnelpo(
    df, personnel_po, colonne_condition, periode="global"
)
print(f"Statistiques de {personnel_po} sur 2017-2024")
print(f"Nombre total d'occurrences en VA : {stats_global['moyenne_valeur']:.2f}")
# print(f"Médiane (VA) : {stats_global['médiane_valeur']:.2f}")

# --- Par année ---
stats_annee = statistiques_personnelpo(
    df, personnel_po, colonne_condition, periode="annee"
)
print(f"Statistiques de {personnel_po} par années")
print(f"Moyenne (VA) : {stats_annee['moyenne_valeur']:.2f}")
print(f"Médiane (VA) : {stats_annee['médiane_valeur']:.2f}")
print(f"Moyenne (%)  : {stats_annee['moyenne_proportion']:.2%}")
print(f"Médiane (%)  : {stats_annee['médiane_proportion']:.2%}")
# print(f"Répartition (VA)  : {stats_annee['description_valeur']:}")
# print(f"Répartition (%)  : {stats_annee['description_proportion']:}")
# print(f"Déciles (VA)  : {stats_annee['deciles_valeur']}")
# print(f"Déciles (%)  : {stats_annee['deciles_proportion']}")

# --- Par mois ---
stats_mois = statistiques_personnelpo(
    df, personnel_po, colonne_condition, periode="mois"
)
print(f"Statistiques de {personnel_po} par mois")
print(f"Moyenne (VA) : {stats_mois['moyenne_valeur']:.2f}")
print(f"Médiane (VA) : {stats_mois['médiane_valeur']:.2f}")
print(f"Moyenne (%)  : {stats_mois['moyenne_proportion']:.2%}")
print(f"Médiane (%)  : {stats_mois['médiane_proportion']:.2%}")
# print(f"Répartition (VA)  : {stats_mois['description_valeur']}")
# print(f"Répartition (%)  : {stats_mois['description_proportion']:}")
print(f"Déciles (VA)  : {stats_mois['deciles_valeur']}")
print(f"Déciles (%)  : {stats_mois['deciles_proportion']}")

# --- Par semaine ---
# stats_sem = statistiques_personnelpo(df, personnel_po, periode="semaine")
# print(f"Statistiques de {personnel_po} par semaines")
# print(f"Moyenne (VA) : {stats_sem['moyenne_valeur']:.2f}")
# print(f"Moyenne (%)  : {stats_sem['moyenne_proportion']:.2%}")
# print(f"Répartition (VA)  : {stats_sem['description_valeur']}")
# print(f"Répartition (%)  : {stats_sem['description_proportion']}")
# print(f"Déciles (VA)  : {stats_sem['deciles_valeur']}")
# print(f"Déciles (%)  : {stats_sem['deciles_proportion']}")


# %% [markdown]
# #### Tableau(x) et graphique(s)

# %%
def synchronique_personnel(
    df,
    couleurs_groupes,
    colonne_condition,
    personnel_po,
    colonne_groupe,
    préfixe,
    periode,
    colonne_député="nom_orateur_clean",
    date_col="dateSeance_day",
):
    # 1. Filtrer pour la personne choisie
    df = df[df[colonne_député] == personnel_po].copy()

    # 2. Déterminer le groupe dominant de la personne
    groupe_dominant = (
        df.groupby(colonne_groupe)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .iloc[0][colonne_groupe]
    )

    # 3. Rajouter la couleur du groupe/personne (secondaire)
    couleur = couleurs_groupes.get(
        groupe_dominant, couleurs_groupes.get("Autres", "grey")
    )

    # 4. Déterminer la fréquence temporelle selon la période choisie
    freq_mapping = {
        "D": ("D", "Jour", "%D"),
        "A": ("YS", "Année", "%Y"),
        "M": ("MS", "Mois", "%b %Y"),
        "W": ("W", "Semaine", "%Y-%m-%d"),
        "Q": ("Q", "Trimestre", "T%q %Y"),
    }
    if periode not in freq_mapping:
        raise ValueError("periode doit être 'A' (année), 'M' (mois) ou 'Q' (trimestre)")

    freq, label_x, tickformat = freq_mapping[periode]

    # 5. Agrégation temporelle
    df_agg = (
        df.groupby(pd.Grouper(key=date_col, freq=freq))[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 6. Calcul de la proportion et de l’année
    df_agg["proportion_true"] = df_agg["true_mentions"] / df_agg["total_mentions"] * 100
    df_agg["Période"] = df_agg[date_col]

    # 7. Création du graphique
    fig = go.Figure()

    # Courbe principale (%)
    fig.add_trace(
        go.Scatter(
            x=df_agg["Période"],
            y=df_agg["proportion_true"],
            mode="lines+markers",
            name=f"{personnel_po} (%)",
            line=dict(color=couleur, width=3),
            marker=dict(size=8, symbol="circle"),
            yaxis="y1",
            hovertemplate=(
                f"<b>{personnel_po}</b><br>"
                "Année : %{x}<br>"
                "Proportion : %{y:.1f}%<extra></extra>"
            ),
        )
    )

    # Barres = valeurs absolues
    fig.add_trace(
        go.Bar(
            x=df_agg["Période"],
            y=df_agg["true_mentions"],
            name=f"{personnel_po} (VA)",
            marker_color=couleur,
            opacity=0.4,
            yaxis="y2",
            hovertemplate=(
                f"<b>{personnel_po}</b><br>"
                "Année : %{x}<br>"
                "Occurrences : %{y}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    # 7. Mise en forme finale
    fig.update_layout(
        title=f"Évolution annuelle de la {préfixe} '{colonne_condition}' par {personnel_po} ({groupe_dominant}) à l'AN",
        xaxis=dict(title=label_x, tickformat=tickformat),
        yaxis=dict(title="Proportion(%)", side="right", showgrid=False),
        yaxis2=dict(
            title="Valeur absolue", overlaying="y", side="left", showgrid=False
        ),
        legend=dict(x=0.83, y=1.25, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    fig.show()
    return df_agg



# %%
df

# %%
synchronique_personnel(
    df,
    couleurs_groupes,
    colonne_condition="repu_match_valide",
    personnel_po="M. Roger Chudeau",
    colonne_groupe="affiliation_et_gouv",
    periode="M",
    préfixe="thématique",
)


# %%
def synchronique_personnel_moyenne(
    df,
    couleurs_groupes,
    colonne_condition,
    personnel_po,
    colonne_groupe,
    préfixe,
    periode,
    colonne_député="nom_orateur_clean",
    date_col="dateSeance_day",
):
    # 1. Filtrer pour la personne choisie
    df = df[df[colonne_député] == personnel_po].copy()

    # 2. Déterminer le groupe dominant de la personne
    groupe_dominant = (
        df.groupby(colonne_groupe)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .iloc[0][colonne_groupe]
    )

    # 3. Rajouter la couleur du groupe/personne (secondaire)
    couleur = couleurs_groupes.get(
        groupe_dominant, couleurs_groupes.get("Autres", "grey")
    )

    # 4. Déterminer la fréquence temporelle selon la période choisie
    freq_mapping = {
        "D": ("D", "Jour", "%D"),
        "A": ("YS", "Année", "%Y"),
        "M": ("MS", "Mois", "%b %Y"),
        "Q": ("Q", "Trimestre", "T%q %Y"),
    }
    if periode not in freq_mapping:
        raise ValueError("periode doit être 'A' (année), 'M' (mois) ou 'Q' (trimestre)")

    freq, label_x, tickformat = freq_mapping[periode]

    # 5. Agrégation temporelle : calcul de la moyenne
    df_agg = (
        df.groupby(pd.Grouper(key=date_col, freq=freq))[colonne_condition]
        .agg(total_interventions="count", moyenne_par_intervention="mean")
        .reset_index()
    )

    # 6. Préparation des données pour le graphique
    df_agg["Période"] = df_agg[date_col]

    # 7. Création du graphique
    fig = go.Figure()

    # Courbe principale : moyenne par intervention
    fig.add_trace(
        go.Scatter(
            x=df_agg["Période"],
            y=df_agg["moyenne_par_intervention"],
            mode="lines+markers",
            name=f"{personnel_po} (moyenne)",
            line=dict(color=couleur, width=3),
            marker=dict(size=8, symbol="circle"),
            yaxis="y1",
            hovertemplate=(
                f"<b>{personnel_po}</b><br>"
                "Période : %{x}<br>"
                "Moyenne : %{y:.2f}<extra></extra>"
            ),
        )
    )

    # Barres : nombre total d'interventions
    fig.add_trace(
        go.Bar(
            x=df_agg["Période"],
            y=df_agg["total_interventions"],
            name=f"{personnel_po} (interventions)",
            marker_color=couleur,
            opacity=0.4,
            yaxis="y2",
            hovertemplate=(
                f"<b>{personnel_po}</b><br>"
                "Période : %{x}<br>"
                "Interventions : %{y}<extra></extra>"
            ),
            showlegend=False,
        )
    )

    # 8. Mise en forme finale
    fig.update_layout(
        title=f"Évolution de la {préfixe} '{colonne_condition}' par {personnel_po} ({groupe_dominant}) à l'AN",
        xaxis=dict(title=label_x, tickformat=tickformat),
        yaxis=dict(title="Moyenne par intervention", side="right", showgrid=False),
        yaxis2=dict(
            title="Nombre d'interventions", overlaying="y", side="left", showgrid=False
        ),
        legend=dict(x=0.83, y=1.25, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    fig.show()
    return df_agg



# %%
synchronique_personnel_moyenne(
    df,
    couleurs_groupes,
    colonne_condition="nombre_correspondances",
    personnel_po="M. Éric Poulliat",
    colonne_groupe="groupe&gvt_affiliation",
    periode="D",
    préfixe="thématique",
)

# %%
# À faire : tableau avec évolution des thématiques par individu (réfléchir au préalable à la logique)
# logique = remplacer la présence de plusieurs personnes par plusieurs thématiques = reprendre évolution personnelpo

# Préalable : quoi faire avec bruit ? mettre hors bruit ?




# %%
# à adapter
def synchronique_personnel_va(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    préfixe,
    top_n,
    colonne_député="nom_orateur_clean",
    date_col="dateSeance_day",
):
    # 1. Déterminer le groupe dominant pour chaque personnel politique
    groupe_dominant = (
        df.groupby([colonne_député, colonne_groupe])
        .size()
        .reset_index(name="n")
        .sort_values(["nom_orateur_clean", "n"], ascending=[True, False])
        .drop_duplicates(subset=colonne_député)
        .set_index(colonne_député)[colonne_groupe]
    )

    # 2. Calcul du total de mentions True par personnel politique
    counts = (
        df.groupby(colonne_député)[colonne_condition]
        .apply(lambda x: (x == True).sum())
        .reset_index(name="true_mentions")
    )

    # 3. Sélection des Top N personnel politique
    top_députés = (
        counts.sort_values("true_mentions", ascending=False)
        .head(top_n)[colonne_député]
        .tolist()
    )

    # 4. Filtrer les données correspondantes
    df_top = df[df[colonne_député].isin(top_députés)].copy()

    # 5. Ajouter groupe dominant et couleur
    df_top[colonne_groupe] = df_top[colonne_député].map(groupe_dominant)
    df_top["couleur"] = (
        df_top[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )

    # 6. Agrégation annuelle (YS = début d’année)
    df_agg = (
        df_top.groupby([pd.Grouper(key=date_col, freq="YS"), colonne_député])[
            colonne_condition
        ]
        .apply(lambda x: (x == True).sum())
        .reset_index(name="true_mentions")
    )

    # 7. Ajouter le groupe et la couleur
    df_agg[colonne_groupe] = df_agg[colonne_député].map(groupe_dominant)
    df_agg["couleur"] = (
        df_agg[colonne_groupe]
        .map(couleurs_groupes)
        .fillna(couleurs_groupes.get("Autres", "grey"))
    )

    # 8. Liste de symboles pour différencier les députés d’un même groupe
    symboles_possibles = [
        "circle",
        "square",
        "diamond",
        "cross",
        "triangle-up",
        "triangle-down",
        "triangle-left",
        "triangle-right",
        "x",
        "star",
        "hexagram",
        "pentagon",
    ]

    # 9. Attribution automatique des symboles par groupe
    symbol_mapping = {}
    for groupe, sous_df in df_agg.groupby(colonne_groupe):
        députés_groupe = sous_df[colonne_député].unique()
        for i, député in enumerate(députés_groupe):
            symbol_mapping[député] = symboles_possibles[i % len(symboles_possibles)]

    # 10. Création du graphique
    fig = go.Figure()

    for député in top_députés:
        couleur = df_agg.loc[df_agg[colonne_député] == député, "couleur"].iloc[0]
        symbole = symbol_mapping.get(député, "circle")
        df_temp = df_agg[df_agg[colonne_député] == député]

        fig.add_trace(
            go.Scatter(
                x=df_temp[date_col],
                y=df_temp["true_mentions"],
                mode="lines+markers",
                name=député,
                line=dict(color=couleur, width=1.75),
                marker=dict(size=8, symbol=symbole),
                hovertemplate=(f"<b>{député}</b><br>%{{x|%Y}}<br>Occurrences : %{{y}}"),
            )
        )

    # 11. Mise en forme
    fig.update_layout(
        title=f"Évolution du Top {top_n} du personnel politique investissant le plus la {préfixe} '{colonne_condition}' à l'AN",
        xaxis=dict(title="Année", tickformat="%Y"),
        yaxis=dict(title="Occurrences (valeur absolue)", showgrid=False),
        legend=dict(x=0.85, y=1.15, bgcolor="#E3E1E1"),
        bargap=0.2,
        template="plotly_white",
    )

    fig.show()
    return df_agg



# %% [markdown]
# ## Analyse par commission parlementaire

# %% [markdown]
# #### Analyses générales

# %%
df = df.drop(df["commission_député"] == "RI et GE")


# %%
df["commission_député"].value_counts()

# %%
df_repu["commission_député"].value_counts()

# %%
# Paramètres
colonne_condition = "repu_match_valide"
colonne_discussion = "commission_député"

# Compter le nombre de fois où la FDM "République" est utilisée par type de discussion
df_groupes = (
    df.groupby(colonne_discussion)[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calculer la proportion
df_groupes["proportion_true"] = (
    df_groupes["true_mentions"] / df_groupes["total_mentions"] * 100
)  # en %

# Filtrage des 10 premiers (en % ou en valeur absolue)
df_groupes = (
    df_groupes.sort_values("true_mentions", ascending=False)
    .head(20)
    .reset_index(drop=True)
)


# Créer la figure
fig = go.Figure()

# Nombre d'occurrences de la "République"
fig.add_trace(
    go.Bar(
        x=df_groupes[colonne_discussion],
        y=df_groupes["true_mentions"],
        name="Nombre d'interventions avec FDM 'République'",
        marker_color="rgba(99, 110, 250, 0.6)",
        yaxis="y1",
    )
)

# Proportion des occurrences de la "République"
fig.add_trace(
    go.Scatter(
        x=df_groupes[colonne_discussion],
        y=df_groupes["proportion_true"],
        name="Proportion d'intervention en % avec FDM 'République'",
        mode="markers",
        marker=dict(color="rgba(239, 85, 59, 0.9)", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en forme
fig.update_layout(
    title="Comparaison des types de discours dans lesquels apparait la FDM République",
    xaxis=dict(title="Type de discours"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(
        title="Proportion en %",
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(x=0.60, y=-0.65, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.25,
)

# Afficher la figure
fig.show()
df_groupes


# %% [markdown]
# #### Analyses croisées

# %%
def synchronique_personnelpo_groupe(
    df,
    groupe,
    colonne_condition,
    colonne_groupe,
    préfixe,
    min_true,
    top_n,
    colonne_commission="commission_député",
    mode="Double",
):
    # 1. Filtrer pour ne garder que le groupe parlementaire en question
    df_parti = df[df[colonne_groupe] == groupe].copy()

    # 2. Compter le nombre d'occurrences de la condition pour chaque personnel politique de ce parti
    counts = (
        df_parti.groupby(colonne_commission)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Calcul de la proportion (%)
    counts["proportion_true"] = (
        counts["true_mentions"] / counts["total_mentions"]
    ) * 100

    # 4. Filtrer le personnel politique à partir d'un minimum d'occurrences
    filtered = counts[counts["true_mentions"] >= min_true]
    df_personnelpo_groupe = (
        filtered.sort_values("true_mentions", ascending=False)
        .head(int(top_n))
        .reset_index(drop=True)
    )

    # 5. Créer la figure Plotly
    fig = go.Figure()

    # --- Mode "absolu" ou "double" : afficher les barres ---
    if mode in ["absolu", "Double"]:
        for _, row in df_personnelpo_groupe.iterrows():
            fig.add_trace(
                go.Bar(
                    x=[row[colonne_commission]],
                    y=[row["true_mentions"]],
                    name=row[colonne_commission],
                    marker_color=row.get(
                        "couleur", "#91AACF"
                    ),  # Couleur par défaut si absente
                    yaxis="y1",
                    hovertemplate=f"<b>{row[colonne_commission]}</b><br>"
                    f"Groupe : {groupe}<br>"
                    f"Valeur absolue : {row['true_mentions']}<br>"
                    f"Proportion : {row['proportion_true']:.1f} %",
                    showlegend=False,
                )
            )

    # --- Mode "proportion" ou "double" : afficher les points ---
    if mode in ["proportion", "Double"]:
        fig.add_trace(
            go.Scatter(
                x=df_personnelpo_groupe[colonne_commission],
                y=df_personnelpo_groupe["proportion_true"],
                name="Proportion d'intervention en %",
                mode="markers",
                marker=dict(color="black", size=8, symbol="circle"),
                line=dict(width=1, dash="dot", color="black"),
                yaxis="y2",
            )
        )

    # 7. Mise en forme du graphique
    fig.update_layout(
        title=(
            f"Top {top_n} des députés {groupe} investissant le plus la {préfixe} '{colonne_condition}' à l'AN"
            f" (≥ {min_true} occurrences)"
        ),
        xaxis=dict(title="Député·es / Ministres", tickangle=-45),
        yaxis=dict(title="Valeur absolue", showgrid=False),
        yaxis2=dict(
            title="Proportion en %",
            overlaying="y",
            side="right",
            showgrid=False,
            range=[0, max(df_personnelpo_groupe["proportion_true"].max() * 1.1, 10)],
        ),
        legend=dict(x=0.6, y=1.2, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    # 8. Ajustement du titre selon le mode
    if mode == "absolu":
        fig.update_layout(title=fig.layout.title.text + " — en valeur absolue")
    elif mode == "proportion":
        fig.update_layout(title=fig.layout.title.text + " — en proportion (%)")
    else:
        fig.update_layout(title=fig.layout.title.text)

    fig.show()
    return df_personnelpo_groupe



# %%
synchronique_personnelpo_groupe(
    df,
    groupe="SOC-A",
    colonne_condition="repu_match_valide",
    colonne_groupe="affiliation_mandat_députés",
    préfixe="FDM",
    min_true=1,
    top_n=9,
    mode="absolu",
)


# %% [markdown]
# ## Personnel politique par groupes

# %% [markdown]
# ### Analyse synchronique 

# %% [markdown]
# #### Statistiques moyennes

# %%
def statistiques_députés_groupes(
    df, groupe, periode="semaine", colonne_condition="repu_match_valide"
):
    # Filtrer sur le parti choisi
    df_groupe = df[df["groupe_députés_affiliation"] == groupe].copy()
    if df_groupe.empty:
        raise ValueError(f"Aucune donnée trouvée pour le groupe : {groupe}")

    # Définir la granularité
    if periode == "semaine":
        df_groupe["periode"] = (
            df_groupe["dateSeance_day"].dt.isocalendar().year.astype(str)
            + "-W"
            + df_groupe["dateSeance_day"].dt.isocalendar().week.astype(str)
        )
    elif periode == "mois":
        df_groupe["periode"] = df_groupe["dateSeance_day"].dt.to_period("M").astype(str)
    elif periode == "annee":
        df_groupe["periode"] = df_groupe["dateSeance_day"].dt.year.astype(str)
    elif periode == "global":
        df_groupe["periode"] = "Global"

    # Compter occurrences par période (proportion et True)
    df_counts = (
        df_groupe.groupby(["nom_orateur_clean", "periode"])[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # Proportion de True
    df_counts["proportion_true"] = (
        df_counts["true_mentions"] / df_counts["total_mentions"]
    )

    # Statistiques
    stats = {
        "moyenne_proportion": df_counts["proportion_true"].mean(),
        "médiane_proportion": df_counts["proportion_true"].median(),
        "moyenne_valeur": df_counts["true_mentions"].mean(),
        "médiane_valeur": df_counts["true_mentions"].median(),
        "deciles_proportion": df_counts["proportion_true"].quantile(
            [i / 100 for i in range(90, 100)]
        )
        * 100,
        "deciles_valeur": df_counts["true_mentions"].quantile(
            [i / 100 for i in range(90, 100)]
        ),
    }

    return stats


# %%
groupe = "LR"

# Sur toute la période
stats_global = statistiques_députés_groupes(df, groupe, periode="global")
print("Statistiques sur 2017-2024")
print(f"Moyenne (VA) : {stats_global['moyenne_valeur']:.2f}")
print(f"Médiane (VA) : {stats_global['médiane_valeur']:.2f}")
print(f"Déciles (VA)  : {stats_global['deciles_valeur']}")
print(f"Moyenne (%)  : {stats_global['moyenne_proportion']:.2%}")
print(f"Médiane (%) : {stats_global['médiane_proportion']:.2f}")
print(f"Déciles (%)  : {stats_global['deciles_proportion']}")

# --- Par année ---
# stats_annee = statistiques_députés_groupes(df, groupe, periode="annee")
# print("Par Année :")
# print(f"Moyenne (VA) : {stats_annee['moyenne_valeur']:.2f}")
# print(f"Moyenne (%)  : {stats_annee['moyenne_proportion']:.2%}")
# print(f"Répartition (VA)  : {stats_annee['description_valeur']:}")
# print(f"Répartition (%)  : {stats_annee['description_proportion']:}")
# print(f"Déciles (VA)  : {stats_annee['deciles_valeur']}")
# print(f"Déciles (%)  : {stats_annee['deciles_proportion']}")

# --- Par mois ---
# stats_mois = statistiques_députés_groupes(df, groupe, periode="mois")
# print("Par Mois :")
# print(f"Moyenne (VA) : {stats_mois['moyenne_valeur']:.2f}")
# print(f"Moyenne (%)  : {stats_mois['moyenne_proportion']:.2%}")
# print(f"Répartition (VA)  : {stats_mois['description_valeur']}")
# print(f"Répartition (%)  : {stats_mois['description_proportion']:}")

# --- Par semaine ---
# stats_sem = statistiques_députés_groupes(df, groupe, periode="semaine")
# print("Par Semaine :")
# print(f"Moyenne (VA) : {stats_sem['moyenne_valeur']:.2f}")
# print(f"Moyenne (%)  : {stats_sem['moyenne_proportion']:.2%}")
# print(f"Répartition (VA)  : {stats_sem['description_valeur']}")
# print(f"Répartition (%)  : {stats_sem['description_proportion']}")


# %% [markdown]
# #### Fonction générale 

# %%
def synchronique_personnelpo_groupe(
    df,
    groupe,
    colonne_condition,
    colonne_groupe,
    préfixe,
    min_true,
    top_n,
    colonne_député="nom_orateur_clean",
    mode="Double",
):
    # 1. Filtrer pour ne garder que le groupe parlementaire en question
    df_parti = df[df[colonne_groupe] == groupe].copy()

    # 2. Compter le nombre d'occurrences de la condition pour chaque personnel politique de ce parti
    counts = (
        df_parti.groupby(colonne_député)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Calcul de la proportion (%)
    counts["proportion_true"] = (
        counts["true_mentions"] / counts["total_mentions"]
    ) * 100

    # 4. Filtrer le personnel politique à partir d'un minimum d'occurrences
    filtered = counts[counts["true_mentions"] >= min_true]
    df_personnelpo_groupe = (
        filtered.sort_values("true_mentions", ascending=False)
        .head(int(top_n))
        .reset_index(drop=True)
    )

    # 5. Créer la figure Plotly
    fig = go.Figure()

    # --- Mode "absolu" ou "double" : afficher les barres ---
    if mode in ["absolu", "Double"]:
        for _, row in df_personnelpo_groupe.iterrows():
            fig.add_trace(
                go.Bar(
                    x=[row[colonne_député]],
                    y=[row["true_mentions"]],
                    name=row[colonne_député],
                    marker_color=row.get(
                        "couleur", "#91AACF"
                    ),  # Couleur par défaut si absente
                    yaxis="y1",
                    hovertemplate=f"<b>{row[colonne_député]}</b><br>"
                    f"Groupe : {groupe}<br>"
                    f"Valeur absolue : {row['true_mentions']}<br>"
                    f"Proportion : {row['proportion_true']:.1f} %",
                    showlegend=False,
                )
            )

    # --- Mode "proportion" ou "double" : afficher les points ---
    if mode in ["proportion", "Double"]:
        fig.add_trace(
            go.Scatter(
                x=df_personnelpo_groupe[colonne_député],
                y=df_personnelpo_groupe["proportion_true"],
                name="Proportion d'intervention en %",
                mode="markers",
                marker=dict(color="black", size=8, symbol="circle"),
                line=dict(width=1, dash="dot", color="black"),
                yaxis="y2",
            )
        )

    # 7. Mise en forme du graphique
    fig.update_layout(
        title=(
            f"Top {top_n} des députés {groupe} investissant le plus la {préfixe} '{colonne_condition}' à l'AN"
            f" (≥ {min_true} occurrences)"
        ),
        xaxis=dict(title="Député·es / Ministres", tickangle=-45),
        yaxis=dict(title="Valeur absolue", showgrid=False),
        yaxis2=dict(
            title="Proportion en %",
            overlaying="y",
            side="right",
            showgrid=False,
            range=[0, max(df_personnelpo_groupe["proportion_true"].max() * 1.1, 10)],
        ),
        legend=dict(x=0.6, y=1.2, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    # 8. Ajustement du titre selon le mode
    if mode == "absolu":
        fig.update_layout(title=fig.layout.title.text + " — en valeur absolue")
    elif mode == "proportion":
        fig.update_layout(title=fig.layout.title.text + " — en proportion (%)")
    else:
        fig.update_layout(title=fig.layout.title.text)

    fig.show()
    return df_personnelpo_groupe



# %%
synchronique_personnelpo_groupe(
    df_CRPR,
    groupe="RN",
    colonne_condition="repu_match_valide",
    colonne_groupe="groupe&gvt_affiliation",
    préfixe="FDM",
    min_true=1,
    top_n=20,
    mode="absolu",
)


# %%
# Faire une fonction pour voir par député quelles thématiques

# %% [markdown]
# #### Autres fonctions 

# %% [markdown]
# ##### En proportion (non nécessaire, fonction datée)

# %%
# Définir les paramètres
groupe = "LR"
colonne_condition = "Immigration"
min_true = 5
top_n = 20

# 1. Filtrer pour ne garder que le groupe en question
df_groupe = df[df["groupe_députés_affiliation"] == groupe].copy()

# 2. Compter le nombre de fois où chaque orateur du groupe dit "République"
counts = (
    df_groupe.groupby("nom_orateur_clean")[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# 3. Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"] * 100

# 4. Couleur du groupe
couleur_groupe = couleurs_groupes.get(groupe, couleurs_groupes["Autres"])

# Filtrer les orateurs avec au moins X mentions True
filtered = counts[counts["true_mentions"] >= min_true]

# 5. Trier les députés par le nombre de mentions de la FDM "République"
df_counts = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(top_n)
    .reset_index(drop=True)
)

# 6. Créer la figure
fig = go.Figure()

# Barres : volume total
for _, row in df_counts.iterrows():
    fig.add_trace(
        go.Bar(
            x=[row["nom_orateur_clean"]],
            y=[row["proportion_true"]],
            name=row["nom_orateur_clean"],
            marker_color=couleur_groupe,
            yaxis="y1",
            showlegend=False,  # On affiche la légende séparément si besoin
        )
    )


# Mise en forme
fig.update_layout(
    title=f"Top{top_n} des député.es {groupe} investissant le plus la famille du mot 'République' en proportion (A)",
    xaxis=dict(title="Député.es"),
    yaxis=dict(title="En %", showgrid=False),
    yaxis2=dict(),
    template="plotly_white",
    bargap=0.2,
)

fig.show()
df_counts


# %% [markdown]
# ##### En VA et % (fonction datée)

# %%
# Définir les paramètres
groupe = "REN"
colonne_condition = "Laïcité-Islam"
top_n = 10

# 1. Filtrer pour ne garder que le groupe en question
df_groupe = df[df["groupe_députés_affiliation"] == groupe].copy()

# 2. Compter le nombre de fois où chaque orateur du groupe dit "République"
counts = (
    df_groupe.groupby("nom_orateur_clean")[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# 3. Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"] * 100

# 4. Couleur du groupe
couleur_parti = couleurs_groupes.get(groupe, couleurs_groupes["Autres"])

# 5. Trier les députés par le nombre de mentions de la FDM "République"
df_counts = (
    counts.sort_values("true_mentions", ascending=False)
    .head(top_n)
    .reset_index(drop=True)
)

# 6. Créer la figure
fig = go.Figure()

# Barres : volume total
for _, row in df_counts.iterrows():
    fig.add_trace(
        go.Bar(
            x=[row["nom_orateur_clean"]],
            y=[row["true_mentions"]],
            name=row["nom_orateur_clean"],
            marker_color=couleur_parti,
            yaxis="y1",
            showlegend=False,  # On affiche la légende séparément si besoin
        )
    )

# Points : proportion
fig.add_trace(
    go.Scatter(
        x=df_counts["nom_orateur_clean"],
        y=df_counts["proportion_true"],
        name="Proportion d'intervention en % avec FDM 'République'",
        mode="markers",
        marker=dict(color="black", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en forme
fig.update_layout(
    title=f"Top {top_n} des député.es {groupe} investissant le plus la famille du mot 'République' (A)",
    xaxis=dict(title="Député.es"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(title="Proportion en %", overlaying="y", side="right", showgrid=False),
    legend=dict(x=0.65, y=1.15, bgcolor="#E3E1E1"),
    template="plotly_white",
    bargap=0.2,
)

fig.show()
df_counts


# %% [markdown]
# ### Évolutions

# %% [markdown]
# #### En valeur absolue

# %%
def evolution_députés_groupes_va(
    df,
    colonne_condition,
    groupe,
    top_n,
    colonne_groupe,
    préfixe,
    date_col="dateSeance_day",
    colonne_député="nom_orateur_clean",
):
    # 1. Filtrer pour ne garder que le groupe en question
    df_groupe = df[df[colonne_groupe] == groupe].copy()

    # 2. Calcul des proportions de chaque député par groupe
    counts = (
        df_groupe.groupby(colonne_député)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Trier les député.s par volume pour ne garder que les X premiers
    top_députés = (
        counts.sort_values("true_mentions", ascending=False)
        .head(top_n)[colonne_député]
        .tolist()
    )

    # 4. Filtrer le DF
    df_groupes = df[
        df[colonne_député].isin(top_députés) & (df[colonne_condition] == True)
    ].copy()

    # 4. Agrégation annuelle
    df_groupes = (
        df_groupes.groupby([pd.Grouper(key=date_col, freq="YS"), colonne_député])[
            colonne_condition
        ]
        .apply(lambda x: (x == True).sum())
        .reset_index(name="true_mentions")
    )

    # 5. Extraire l'année
    df_groupes["Année"] = df_groupes[date_col].dt.year

    # Tracer l'évolution du % dans le temps
    fig = px.line(
        df_groupes,
        x="Année",
        y="true_mentions",
        color=colonne_député,
        markers=True,
        title=f"Évolution du Top {top_n} des député.es {groupe} investissant le plus la {préfixe} {colonne_condition}",
        labels={"true_mentions": "Valeur absolue", colonne_député: "Député.s"},
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        hovermode="x unified",
        template="plotly_white",
        legend_title_text="Député.s",
        yaxis_tickformat="",
    )

    fig.show()



# %%
evolution_députés_groupes_va(
    df_thématique,
    groupe="REN",
    colonne_condition="Laïcité-Islam",
    colonne_groupe="groupe&gvt_affiliation",
    préfixe="thématique",
    top_n=5,
)


# %% [markdown]
# #### En proportion (fonction à résoudre)

# %%
def evolution_députés_groupes_pourcentage(
    df,
    groupe=None,
    date_col="dateSeance_day",
    colonne_groupe="groupe_députés_affiliation",
    colonne_député="nom_orateur_clean",
    colonne_condition="repu_match_valide",
    top_n=None,
):
    # 1. Filtrer pour ne garder que le groupe en question
    df_groupe = df[df[colonne_groupe] == groupe].copy()

    # 2. Trier les député.s par volume pour ne garder que les X premiers
    top_députés = (
        df_groupe.sort_values("true_mentions", ascending=False)
        .head(top_n)[colonne_député]
        .tolist()
    )

    # 3. Filtrer le DF
    df_groupes = df[
        df[colonne_député].isin(top_députés) & (df[colonne_condition] == True)
    ].copy()

    # 4. Agrégation annuelle
    df_groupes = (
        df_groupes.groupby([pd.Grouper(key=date_col, freq="YS"), colonne_député])[
            colonne_condition
        ]
        .apply(lambda x: (x == True).sum())
        .reset_index()
    )

    # 5. Ajouter la proportion annuelle (% d'utilisation)
    df_groupes["proportion_true"] = (
        df_groupes["true_mentions"] / df_groupes["total_mentions"]
    )

    # 6. Extraire l'année
    df_groupes["Année"] = df_groupes[date_col].dt.year

    # Tracer l'évolution du % dans le temps
    fig = px.line(
        df_groupes,
        x="Année",
        y="proportion_true",
        color=colonne_député,
        markers=True,
        title=f"Évolution du Top {top_n} des député.es {groupe} investissant le plus la famille du mot 'République' (A)",
        labels={"proportion_true": "En %", colonne_député: "Député.s"},
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        hovermode="x unified",
        template="plotly_white",
        legend_title_text="Député.s",
        yaxis_tickformat="",
    )

    fig.show()



# %%
evolution_députés_groupes_pourcentage(df, groupe="LR", top_n=5)

# %%
# TODO : changer manuellement les couleurs des graphiques


def evolution_députés_groupes_pourcentage(
    df,
    groupe=None,
    date_col="dateSeance_day",
    personnel_col="nom_orateur_clean",
    match_col="repu_match_valide",
    min_true_mentions=50,
    top_n=6,
):
    # 1. Filtrer pour ne garder que le groupe en question
    df_groupe = df[df["groupe_députés_affiliation"] == groupe].copy()

    # Calcul global des proportions par groupe
    counts = (
        df_groupe.groupby(personnel_col)[match_col]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # Ajouter la proportion globale
    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

    # Filtrer les partis avec au moins min_true_mentions
    filtered = counts[counts["true_mentions"] >= min_true_mentions]

    # Sélectionner les top_n groupes selon la proportion
    top_personnel = (
        filtered.sort_values("proportion_true", ascending=False)
        .head(top_n)[personnel_col]
        .tolist()
    )

    # Filtrer les données pour ces groupes
    df_top = df[df[personnel_col].isin(top_personnel)].copy()

    # Calculer les stats annuelles : mentions totales et vraies
    df_grouped = (
        df_top.groupby([pd.Grouper(key=date_col, freq="Y"), personnel_col])[match_col]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # Ajouter la proportion annuelle (% d'utilisation)
    df_grouped["proportion_true"] = (
        df_grouped["true_mentions"] / df_grouped["total_mentions"]
    )

    # Extraire l'année pour affichage
    df_grouped["Année"] = df_grouped[date_col].dt.year

    # Tracer l'évolution du % dans le temps
    fig = px.line(
        df_grouped,
        x="Année",
        y="proportion_true",
        color=personnel_col,
        markers=True,
        title=f"Évolution du Top {top_n} des député.es {groupe} investissant le plus en proportion la famille du mot 'République' (A)",
        labels={
            "proportion_true": "% d'utilisation",
            personnel_col: "Groupe parlementaire",
        },
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        hovermode="x unified",
        template="plotly_white",
        legend_title_text="Député.es",
        yaxis_tickformat=".0%",
    )

    fig.show()



# %%
evolution_députés_groupes_pourcentage(df, groupe="LR")

# %% [markdown]
# ## Analyse de périodes spécifiques (à faire)

# %% [markdown]
# ### Analyse de séquences législatives (à faire)

# %% [markdown]
# #### Construire les DF des séquences

# %% [markdown]
# Faire des df par séquence législative en prenant exactement les jours où la loi a été discuté 
# // Attention, un proxy approximatif car 1 jour n'est pas égal à une PPL, mais s'en rapproche le plus ? // 
# ==> si possible aller récupérer uniquement les bonnes séances et point à l'odj. 

# %%
# Pour pouvoir utiliser la colonne numSeanceJour, nécessaire de changer la modalité unique en variable numérique
df["numSeanceJour"] = df["numSeanceJour"].replace("Unique", "0")
# Puis de changer les numéros en vraies variables numériques
df["numSeanceJour"] = pd.to_numeric(df["numSeanceJour"], errors="coerce")


# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2020-12-17", "numSeanceJour": 0, "valeur_ptsodj": 1},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_test = pd.concat(dfs_filtres, ignore_index=True)


# %%
df_test

# %% [markdown]
# ##### Df CRPR (loi dite séparatisme)

# %%
# Loi séparatisme --> ne récupérer que les jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_CRPR_extensif = [
    "2021-02-01",
    "2021-02-02",
    "2021-02-03",
    "2021-02-04",
    "2021-02-05",
    "2021-02-08",
    "2021-02-10",
    "2021-02-11",
    "2021-02-12",
    "2021-02-13",
    "2021-02-16",
    "2021-06-28",
    "2021-06-29",
    "2021-06-30",
    "2021-07-01",
    "2021-07-23",
]

df_CRPR_extensif = df[df["dateSeance_day"].isin(jour_CRPR_extensif)]

# %%
# Étape 1 : prendre tous les jours où on ne parle que de cette loi
jour_entier_CRPR = [
    "2021-02-01",
    "2021-02-03",
    "2021-02-04",
    "2021-02-08",
    "2021-02-10",
    "2021-02-11",
    "2021-02-12",
    "2021-02-13",
    "2021-06-28",
    "2021-06-30",
    "2021-07-01",
]

df_CRPR_entier = df[df["dateSeance_day"].isin(jour_entier_CRPR)]

# %%
# Étape 2 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2021-02-02", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2021-02-05", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2021-02-05", "numSeanceJour": 2, "valeur_ptsodj": None},
    {
        "dateSeance_day": "2021-02-05",
        "numSeanceJour": 3,
        "valeur_ptsodj": None,
    },  # Pour avoir tous les points de cette séance
    {"dateSeance_day": "2021-02-16", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2021-06-29", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2021-06-29", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2021-07-23", "numSeanceJour": 1, "valeur_ptsodj": 2},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_filtres = pd.concat(dfs_filtres, ignore_index=True)


# %%
# Étape 3 : fusionner les 2 df
df_CRPR = pd.concat([df_CRPR_entier, df_filtres], ignore_index=True)

# %%
df_repu_CRPR = df_CRPR[df_CRPR["repu_match_valide"] == True]

# %%
df_CRPR

# %%
# Étape 4 : créer une colonne booléenne

# Ajouter une colonne temporaire dans B pour identifier les lignes
df_CRPR["CRPR"] = True

# Fusionner A et B sur les colonnes clés, en gardant toutes les lignes de A
df = pd.merge(df, df_CRPR[["id_syceron", "CRPR"]], on=["id_syceron"], how="left")

# Remplacer les valeurs NaN par False
df["CRPR"] = df["CRPR"].fillna(False)

# vérifier résultats avant utilisations car 1000 se mettent en faux...

# %% [markdown]
# ##### Df "démocratie plus représentative"

# %%
# Démocratie + représentative trop large
jour_représentative_extensif = [
    "2018-07-10",
    "2018-07-11",
    "2018-07-12",
    "2018-07-13",
    "2018-07-10",
    "2018-07-16",
    "2018-07-17",
    "2018-07-18",
    "2018-07-19",
    "2018-07-20",
    "2018-07-21",
    "2018-07-22",
]

df_représentative_extensif = df[df["dateSeance_day"].isin(jour_représentative_extensif)]

# %%
# Étape 1 : prendre tous les jours où on ne parle que de cette loi
jour_représentative_entier = [
    "2018-07-11",
    "2018-07-16",
    "2018-07-18",
    "2018-07-19",
    "2018-07-20",
    "2018-07-21",
    "2018-07-22",
]

df_représentative_entier = df[df["dateSeance_day"].isin(jour_représentative_entier)]

# %%
# Étape 2 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2018-07-10", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2018-07-10", "numSeanceJour": 2, "valeur_ptsodj": None},
    {
        "dateSeance_day": "2018-07-12",
        "numSeanceJour": 2,
        "valeur_ptsodj": None,
    },  # Pour avoir tous les points de cette séance
    {"dateSeance_day": "2018-07-12", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-07-13", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2018-07-13", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-07-17", "numSeanceJour": 1, "valeur_ptsodj": 4},
    {"dateSeance_day": "2018-07-17", "numSeanceJour": 1, "valeur_ptsodj": 6},
    {"dateSeance_day": "2018-07-17", "numSeanceJour": 2, "valeur_ptsodj": None},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_filtres = pd.concat(dfs_filtres, ignore_index=True)


# %%
# Étape 3 : fusionner les 2 df
df_représentative = pd.concat([df_représentative_entier, df_filtres], ignore_index=True)

# %%
df_représentative

# %%
# Étape 4 : créer une colonne booléenne

# Ajouter une colonne temporaire dans B pour identifier les lignes
df_représentative["Représentative"] = True

# Fusionner A et B sur les colonnes clés, en gardant toutes les lignes de A
df = pd.merge(
    df,
    df_représentative[["id_syceron", "Représentative"]],
    on=["id_syceron"],
    how="left",
)

# Remplacer les valeurs NaN par False
df["Représentative"] = df["Représentative"].fillna(False)

# %% [markdown]
# ##### Projet de loi « pour une école de la confiance »

# %%
# Loi pour une école de la confiance --> ne récupérer que les jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_PUEDLC_extensif = [
    "2019-02-11",
    "2019-02-12",
    "2019-02-13",
    "2019-02-14",
    "2019-02-15",
    "2019-02-19",
]

df_PUEDLC_extensif = df[df["dateSeance_day"].isin(jour_PUEDLC_extensif)]

# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2019-02-11", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-11", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-12", "numSeanceJour": 1, "valeur_ptsodj": 4},
    {"dateSeance_day": "2019-02-12", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-13", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2019-02-14", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-14", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-15", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-15", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-15", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-19", "numSeanceJour": 2, "valeur_ptsodj": 3},
    {"dateSeance_day": "2019-07-02", "numSeanceJour": 1, "valeur_ptsodj": 4},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_PUEDLC = pd.concat(dfs_filtres, ignore_index=True)


# %%
df_PUEDLC

# %%
# Étape 2 : créer une colonne booléenne

# Ajouter une colonne temporaire dans B pour identifier les lignes
df_PUEDLC["PUEDLC"] = True

# Fusionner A et B sur les colonnes clés, en gardant toutes les lignes de A
df = pd.merge(df, df_PUEDLC[["id_syceron", "PUEDLC"]], on=["id_syceron"], how="left")

# Remplacer les valeurs NaN par False
df["PUEDLC"] = df["PUEDLC"].fillna(False)

# %% [markdown]
# ##### Projet de loi pour une immigration maîtrisée et un droit d'asile effectif

# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2018-04-16", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-17", "numSeanceJour": 2, "valeur_ptsodj": 3},
    {"dateSeance_day": "2018-04-17", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-18", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-19", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-19", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-19", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-20", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-20", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2018-04-20", "numSeanceJour": 3, "valeur_ptsodj": 1},
    {"dateSeance_day": "2018-04-21", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-21", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-21", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-04-22", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2018-07-26", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-07-26", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-07-26", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2018-08-01", "numSeanceJour": 1, "valeur_ptsodj": 3},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_IMDAEF = pd.concat(dfs_filtres, ignore_index=True)


# %%
# Étape 2 : créer une colonne booléenne

# Ajouter une colonne temporaire dans B pour identifier les lignes
df_IMDAEF["IMDAEF"] = True

# Fusionner A et B sur les colonnes clés, en gardant toutes les lignes de A
df = pd.merge(df, df_IMDAEF[["id_syceron", "IMDAEF"]], on=["id_syceron"], how="left")

# Remplacer les valeurs NaN par False
df["IMDAEF"] = df["IMDAEF"].fillna(False)

# %% [markdown]
# ##### Projet de loi d’orientation et de programmation du ministère de la justice 2023-2027

# %%
# Jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_OPMJ_extensif = ["2018-07-09"]

df_OPMJ_extensif = df[df["dateSeance_day"].isin(jour_OPMJ_extensif)]

# %%
df_OPMJ_extensif

# %%
# Jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_OPMJ_extensif = [
    "2023-07-03",
    "2023-07-04",
    "2023-07-05",
    "2023-07-06",
    "2023-07-10",
    "2023-07-11",
    "2023-07-12",
    "2023-07-13",
    "2023-07-18",
    "2023-10-10",
]

df_OPMJ_extensif = df[df["dateSeance_day"].isin(jour_OPMJ_extensif)]

# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2023-07-03", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2023-07-03", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-04", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2023-07-04", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-05", "numSeanceJour": 1, "valeur_ptsodj": 4},
    {"dateSeance_day": "2023-07-05", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-06", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-06", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-06", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-10", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-10", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-11", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2023-07-11", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-11", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2023-07-12", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2023-07-12", "numSeanceJour": 2, "valeur_ptsodj": 1},
    {"dateSeance_day": "2023-10-18", "numSeanceJour": 1, "valeur_ptsodj": 4},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_OPMJ = pd.concat(dfs_filtres, ignore_index=True)


# %%
df_OPMJ

# %% [markdown]
# ##### Projet de loi renforçant la sécurité intérieure et la lutte contre le terrorisme

# %%
# Loi pour une école de la confiance --> ne récupérer que les jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_SILT_extensif = [
    "2017-09-25",
    "2017-09-26",
    "2017-09-27",
    "2017-09-28",
    "2017-10-03",
    "2017-11-03",
]

df_SILT_extensif = df[df["dateSeance_day"].isin(jour_SILT_extensif)]

# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2017-09-25", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-09-25", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-09-26", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2017-09-26", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-09-27", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-09-27", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-09-28", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-09-28", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-10-03", "numSeanceJour": 1, "valeur_ptsodj": 4},
    {"dateSeance_day": "2017-10-11", "numSeanceJour": 1, "valeur_ptsodj": 2},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_SILT = pd.concat(dfs_filtres, ignore_index=True)


# %%
df_SILT

# %% [markdown]
# ##### Projet de loi Maintenir l'ordre dans les manifestations publiques

# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2019-01-29", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-01-30", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2019-01-30", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-02-01", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2019-02-05", "numSeanceJour": 1, "valeur_ptsodj": 5},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_MOMP = pd.concat(dfs_filtres, ignore_index=True)


# %%
df_MOMP

# %% [markdown]
# ##### Projet de loi pour la confiance dans la vie publique

# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2017-07-24", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2017-07-24", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-07-28", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-07-28", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-08-03", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-08-03", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2017-08-09", "numSeanceJour": 0, "valeur_ptsodj": 3},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_CVP = pd.concat(dfs_filtres, ignore_index=True)


# %%
# Jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_OPMI_extensif = [
    "2023-07-03",
    "2023-07-04",
    "2023-07-05",
    "2023-07-06",
    "2023-07-10",
    "2023-07-11",
    "2023-07-12",
    "2023-07-13",
    "2023-07-18",
    "2023-10-10",
]

df_OPMI_extensif = df[df["dateSeance_day"].isin(jour_OPMI_extensif)]

# %%
df_OPMI_extensif

# %% [markdown]
# ##### Proposition de loi relative à la sécurité globale 

# %%
# Filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2020-11-17", "numSeanceJour": 2, "valeur_ptsodj": 1},
    {"dateSeance_day": "2020-11-18", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2020-11-18", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-19", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-19", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-19", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-20", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-20", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-20", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-24", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2021-04-15", "numSeanceJour": 1, "valeur_ptsodj": 5},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_sécurité_globale = pd.concat(dfs_filtres, ignore_index=True)


# %%
# Étape 2 : créer une colonne booléenne

# Ajouter une colonne temporaire dans B pour identifier les lignes
df_sécurité_globale["Sécurité_gloable"] = True

# Fusionner A et B sur les colonnes clés, en gardant toutes les lignes de A
df = pd.merge(
    df,
    df_sécurité_globale[["id_syceron", "Sécurité_gloable"]],
    on=["id_syceron"],
    how="left",
)

# Remplacer les valeurs NaN par False
df["Sécurité_gloable"] = df["Sécurité_gloable"].fillna(False)

# %% [markdown]
# ##### Compétences de la Collectivité européenne d’Alsace 

# %%
# Jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_CEA_extensif = ["2019-06-24", "2019-06-25", "2019-06-26", "2019-07-25"]

df_CEA_extensif = df[df["dateSeance_day"].isin(jour_CEA_extensif)]

# %%
# Étape 1 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2019-06-24", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-06-24", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-06-25", "numSeanceJour": 1, "valeur_ptsodj": 4},
    {"dateSeance_day": "2019-06-25", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2019-06-26", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2019-07-25", "numSeanceJour": 0, "valeur_ptsodj": 2},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_CEA = pd.concat(dfs_filtres, ignore_index=True)


# %%
df_CEA

# %% [markdown]
# ##### Projet de loi d’orientation et de programmation du ministère de l’intérieur

# %%
# Jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_OPMI_extensif = [
    "2022-11-14",
    "2022-11-15",
    "2022-11-16",
    "2022-11-17",
    "2022-11-18",
    "2022-11-22",
    "2022-12-07",
]

df_OPMI_extensif = df[df["dateSeance_day"].isin(jour_OPMI_extensif)]

# %%
# Étape 2 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2022-11-14", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2022-11-14", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-15", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2022-11-15", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-16", "numSeanceJour": 1, "valeur_ptsodj": 1},
    {"dateSeance_day": "2022-11-16", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-17", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2022-11-17", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-17", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-18", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-18", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-18", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2022-11-22", "numSeanceJour": 2, "valeur_ptsodj": 3},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_OPMI = pd.concat(dfs_filtres, ignore_index=True)


# %%
# Jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_OPMI_extensif = ["2017-07-24", "2017-07-28", "2017-08-03", "2017-08-09"]

df_OPMI_extensif = df[df["dateSeance_day"].isin(jour_OPMI_extensif)]

# %%
df_OPMI_extensif

# %% [markdown]
# ##### Proposition de loi constitutionnelle visant à garantir la prééminence des lois de la République

# %%
# Étape 2 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2020-12-03", "numSeanceJour": 1, "valeur_ptsodj": 2},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_LREP = pd.concat(dfs_filtres, ignore_index=True)

# %%
df_LREP

# %%
# Loi pour une école de la confiance --> ne récupérer que les jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_LREM_extensif = ["2020-12-03"]

df_LREM_extensif = df[df["dateSeance_day"].isin(jour_LREM_extensif)]

# %%
df_LREM_extensif

# %% [markdown]
# ##### Projet de loi finance 2021

# %%
# Étape 2 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2020-10-12", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-12", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-13", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2020-10-13", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-14", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-14", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-15", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-15", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-16", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-16", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-16", "numSeanceJour": 2, "valeur_ptsodj": 1},
    {"dateSeance_day": "2020-10-19", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-19", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-20", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2020-10-26", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-26", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-26", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-27", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2020-10-27", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-28", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2020-10-28", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-29", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-29", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-30", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-30", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2020-10-30", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-02", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-02", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-02", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-04", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-05", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-05", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-05", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-06", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-06", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2020-11-06", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-07", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-07", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2020-11-09", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-09", "numSeanceJour": 2, "valeur_ptsodj": 2},
    {"dateSeance_day": "2020-11-09", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-12", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-12", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-12", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-13", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-13", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-13", "numSeanceJour": 3, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-17", "numSeanceJour": 0, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-12-14", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-12-14", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-12-15", "numSeanceJour": 1, "valeur_ptsodj": 3},
    {"dateSeance_day": "2020-12-15", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-12-17", "numSeanceJour": 0, "valeur_ptsodj": 1},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_PLF2021 = pd.concat(dfs_filtres, ignore_index=True)

# %%
df_PLF2021

# %% [markdown]
# ##### Loi Prorogation de l’état d’urgence sanitaire

# %%
# Étape 2 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2020-10-24", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-10-24", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-03", "numSeanceJour": 1, "valeur_ptsodj": 4},
    {"dateSeance_day": "2020-11-03", "numSeanceJour": 1, "valeur_ptsodj": 6},
    {"dateSeance_day": "2020-11-03", "numSeanceJour": 2, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-04", "numSeanceJour": 1, "valeur_ptsodj": None},
    {"dateSeance_day": "2020-11-07", "numSeanceJour": 2, "valeur_ptsodj": 1},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_Urgence_sanitaire = pd.concat(dfs_filtres, ignore_index=True)

# %%
df_Urgence_sanitaire

# %% [markdown]
# ##### Souveraineté de la France, nationalité, immigration et asile

# %%
# Loi pour une école de la confiance --> ne récupérer que les jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_SFNIA_extensif = ["2023-12-07"]

df_SFNIA_extensif = df[df["dateSeance_day"].isin(jour_SFNIA_extensif)]

# %%
# Étape 2 : filtrer les bonnes séances et point à l'odj des autres jours où il y a également QAG ou autre loi discutée

# Liste des critères de filtrage
filtres = [
    {"dateSeance_day": "2023-12-07", "numSeanceJour": 1, "valeur_ptsodj": 2},
    {"dateSeance_day": "2023-12-07", "numSeanceJour": 2, "valeur_ptsodj": None},
]

# Initialiser une liste pour stocker les DataFrames filtrés
dfs_filtres = []

# Appliquer les filtres
for filtre in filtres:
    date = filtre["dateSeance_day"]
    num_seance = filtre["numSeanceJour"]
    valeur_pt = filtre["valeur_ptsodj"]

    # Filtrer par date et numéro de séance
    df_temp = df[(df["dateSeance_day"] == date) & (df["numSeanceJour"] == num_seance)]

    # Si une valeur de point est spécifiée, filtrer aussi par cette valeur
    if valeur_pt is not None:
        df_temp = df_temp[df_temp["valeur_ptsodj"] == valeur_pt]

    # Ajouter le DataFrame filtré à la liste
    dfs_filtres.append(df_temp)

# Concaténer tous les DataFrames filtrés
df_filtres = pd.concat(dfs_filtres, ignore_index=True)


# %%
df_filtres

# %%
# Loi pour une école de la confiance --> ne récupérer que les jours où ils en parlent (mais attention ne concerne pas toutes les séances ou point à l'odj de ces séances)
jour_test_extensif = ["2019-01-29", "2019-01-30", "2019-02-01", "2019-02-05"]

df_test_extensif = df[df["dateSeance_day"].isin(jour_test_extensif)]

# %%
df_test_extensif

# %% [markdown]
# #### Quelle utilisation de la 'République' ? 

# %%
# 1. Regarder combien de repu_match_valide = true sur le df
# df_séparatisme # 782 soit 15% des discours lors de ces échanges parlementaires
# df_séparatisme_extensif
# df_représentative
# df_représentative_extensif
# df_PUEDLC
df_CEA


# %% [markdown]
# #### Quelles thématiques ? 

# %%
# Code à réaliser en réfléchissant d'abord à la logique à suivre

# %% [markdown]
# #### Quel partis ?

# %%
def diachronique_séquences_partis(
    df,
    couleurs_groupes,
    colonne_condition,
    colonne_groupe,
    seuil_min_true,
    top_n,
    jours=None,
    periode="intervalle",
    date_debut=None,
    date_fin=None,
    date_col="dateSeance_day",
    titre=None,
):
    # 1. Filtrage selon la période
    if periode == "intervalle":
        debut = pd.to_datetime(date_debut)
        fin = pd.to_datetime(date_fin)
        df_filtered = df[(df[date_col] >= debut) & (df[date_col] <= fin)]
        titre_defaut = f"Groupes mobilisant le plus la FDM 'République' du {debut.date()} au {fin.date()} (≥ {seuil_min_true} occurrences)"
    elif periode == "jours":
        jours_dt = [pd.to_datetime(j).date() for j in jours]
        df_filtered = df[df[date_col].dt.date.isin(jours_dt)]
        titre_defaut = f"Groupes mobilisant le plus la FDM 'République' lors d'évènements sélectionnés (≥ {seuil_min_true} occurrences)"
    else:
        raise ValueError("La période doit être 'intervalle' ou 'jours'.")

    # 2. Comptage des occurrences
    counts = (
        df_filtered.groupby(colonne_groupe)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )
    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

    # 3. Filtrage par seuil et tri
    filtered = counts[counts["true_mentions"] >= seuil_min_true]
    df_top = (
        filtered.sort_values("true_mentions", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    # 4. Création de la figure
    fig = go.Figure()

    for _, row in df_top.iterrows():
        groupe = row[colonne_groupe]
        couleur = couleurs_groupes.get(groupe, couleurs_groupes.get("Autres", "grey"))

        fig.add_trace(
            go.Bar(
                x=[groupe],
                y=[row["true_mentions"]],
                name=f"{groupe} (VA)",
                marker_color=couleur,
                opacity=0.5,
                yaxis="y1",
                hovertemplate="<b>"
                + groupe
                + "</b><br>Occurrences : %{y}<extra></extra>",
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[groupe],
                y=[row["proportion_true"] * 100],
                name=f"{groupe} (%)",
                line=dict(color=couleur, width=3),
                marker=dict(size=10, symbol="circle"),
                yaxis="y2",
                hovertemplate="<b>"
                + groupe
                + "</b><br>Proportion : %{y}<extra></extra>",
            )
        )

    # --- 5. Mise en forme ---
    fig.update_layout(
        title=titre if titre else titre_defaut,
        xaxis=dict(title="Parti / Groupe politique"),
        yaxis=dict(title="Occurrences absolues", showgrid=False),
        yaxis2=dict(
            title="Proportion (%)", overlaying="y", side="right", showgrid=False
        ),
        template="plotly_white",
        legend=dict(x=0.75, y=1.15, bgcolor="rgba(255,255,255,0.7)"),
        bargap=0.4,
    )

    fig.show()
    return df_top



# %% [markdown]
# ##### Projet de loi "séparatisme"

# %%
diachronique_séquences_partis(
    df_thématique,
    couleurs_groupes=couleurs_groupes,
    date_debut="2021-02-01",
    date_fin="2021-02-16",
    periode="intervalle",
    seuil_min_true=10,
    top_n=5,
    colonne_condition="Laïcité-Islam",
    colonne_groupe="groupe&gvt_affiliation",
)

# %%
diachronique_séquences_partis(
    df,
    couleurs_groupes=couleurs_groupes,
    jours=[
        "2021-02-01",
        "2021-02-02",
        "2021-02-03",
        "2021-02-04",
        "2021-02-05",
        "2021-02-08",
        "2021-02-10",
        "2021-02-11",
        "2021-02-12",
        "2021-02-13",
        "2021-02-16",
    ],
    periode="jours",
    seuil_min_true=10,
    top_n=5,
    titre="Groupes mobilisant la FDM de 'République' lors de la 1ère discussion du projet de loi séparatisme",
)


# %%
diachronique_séquences_partis(
    df,
    couleurs_groupes=couleurs_groupes,
    jours=["2021-06-28", "2021-06-29", "2021-06-30", "2021-07-01", "2021-01-23"],
    periode="jours",
    seuil_min_true=10,
    top_n=5,
    titre="Groupes mobilisant la FDM de 'République' lors de la 2e phase de discussion du projet de loi séparatisme",
)


# %%
diachronique_séquences_partis(
    df_regroup,
    couleurs_groupes=couleurs_groupes,
    jours=[
        "2021-02-01",
        "2021-02-02",
        "2021-02-03",
        "2021-02-04",
        "2021-02-05",
        "2021-02-08",
        "2021-02-10",
        "2021-02-11",
        "2021-02-12",
        "2021-02-13",
        "2021-02-16",
        "2021-06-28",
        "2021-06-29",
        "2021-06-30",
        "2021-07-01",
        "2021-01-23",
    ],
    periode="jours",
    seuil_min_true=10,
    top_n=5,
    titre="Groupes mobilisant la FDM de 'République' lors de la  discussion du projet de loi séparatisme",
)


# %% [markdown]
# ##### Projet de loi organique « pour une démocratie plus représentative, responsable et efficace »

# %%
diachronique_séquences_partis(
    df_regroup,
    couleurs_groupes=couleurs_groupes,
    date_debut="2018-07-10",
    date_fin="2018-07-22",
    periode="intervalle",
    seuil_min_true=10,
    top_n=10,
    titre="Groupes mobilisant le plus la FDM de la 'République' (discussion du projet de loi organique démocratie)",
)

# %% [markdown]
# ##### Projet de loi "pour une école de la confiance"

# %%
diachronique_séquences_partis(
    df,
    couleurs_groupes=couleurs_groupes,
    date_debut="2019-02-11",
    date_fin="2019-02-19",
    periode="intervalle",
    seuil_min_true=10,
    top_n=10,
    titre="Groupes mobilisant le plus la FDM de la 'République' lors de la discussion « pour une école de la confiance »",
)

# %%
diachronique_séquences_partis(
    df,
    couleurs_groupes=couleurs_groupes,
    jours=[
        "2018-04-16",
        "2018-04-17",
        "2018-04-18",
        "2018-04-19",
        "2018-04-20",
        "2018-04-21",
        "2018-07-26",
        "2018-07-31",
        "2018-08-01",
    ],
    periode="jours",
    seuil_min_true=3,
    top_n=5,
    titre="Groupes mobilisant la FDM de 'République' lors de X",
)


# %%
diachronique_séquences_partis(
    df_regroup,
    couleurs_groupes=couleurs_groupes,
    date_debut="2017-07-24",
    date_fin="2017-07-28",
    periode="intervalle",
    seuil_min_true=5,
    top_n=10,
    titre="Groupes mobilisant le plus la FDM de la 'République' lors de X",
)


# %% [markdown]
# #### Quelles personnes ?

# %%
def diachronique_séquences_personnel(
    df,
    couleurs_groupes,
    jours=None,
    periode="intervalle",
    date_debut=None,
    date_fin=None,
    seuil_min_true=5,
    top_n=10,
    date_col="dateSeance_day",
    colonne_condition="repu_match_valide",
    colonne_personnel="nom_orateur_clean",
    colonne_groupe="groupe&gvt_affiliation",
    titre=None,
):
    # 1. Filtrage selon la période
    if periode == "intervalle":
        debut = pd.to_datetime(date_debut)
        fin = pd.to_datetime(date_fin)
        df_filtered = df[(df[date_col] >= debut) & (df[date_col] <= fin)]
        titre_defaut = f"Personnels mobilisant le plus la FDM 'République' du {debut.date()} au {fin.date()} (≥ {seuil_min_true} occurrences)"
    elif periode == "jours":
        jours_dt = [pd.to_datetime(j).date() for j in jours]
        df_filtered = df[df[date_col].dt.date.isin(jours_dt)]
        titre_defaut = f"Personnels mobilisant le plus la FDM 'République' lors d'évènements sélectionnés (≥ {seuil_min_true} occurrences)"
    else:
        raise ValueError("La période doit être 'intervalle' ou 'jours'.")

    # 2. Comptage des occurrences par personnel
    counts = (
        df_filtered.groupby(colonne_personnel)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )
    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

    # 3. Ajouter le groupe dominant du personnel pour la couleur
    groupes = (
        df.groupby(colonne_personnel)[colonne_groupe]
        .agg(lambda x: x.value_counts().index[0])  # le groupe le plus fréquent
        .reset_index()
    )
    counts = counts.merge(groupes, on=colonne_personnel, how="left")

    # 4. Filtrage et tri
    filtered = counts[counts["true_mentions"] >= seuil_min_true]
    df_top = (
        filtered.sort_values("true_mentions", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    # 5. Création de la figure
    fig = go.Figure()

    for _, row in df_top.iterrows():
        personnel = row[colonne_personnel]
        groupe = row[colonne_groupe]
        couleur = couleurs_groupes.get(groupe, couleurs_groupes.get("Autres", "grey"))

        fig.add_trace(
            go.Bar(
                x=[personnel],
                y=[row["true_mentions"]],
                name=f"{personnel} (VA)",
                marker_color=couleur,
                opacity=0.5,
                yaxis="y1",
                hovertemplate="<b>"
                + colonne_personnel
                + "</b><br>Occurrences : %{y}<extra></extra>",
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[personnel],
                y=[row["proportion_true"] * 100],
                name=f"{personnel} (%)",
                line=dict(color=couleur, width=3),
                marker=dict(size=10, symbol="circle"),
                yaxis="y2",
                hovertemplate="<b>"
                + colonne_personnel
                + "</b><br>Proportion : %{y}<extra></extra>",
                showlegend=False,
            )
        )

    # 6. Mise en forme
    fig.update_layout(
        title=titre if titre else titre_defaut,
        xaxis=dict(title="Personnel politique"),
        yaxis=dict(title="Valeurs absolues", showgrid=False),
        yaxis2=dict(
            title="Proportion en %", overlaying="y", side="right", showgrid=False
        ),
        template="plotly_white",
        legend=dict(x=0.75, y=1.15, bgcolor="rgba(255,255,255,0.7)"),
        bargap=0.4,
    )

    fig.show()
    return df_top


# %%
diachronique_séquences_personnel(
    df_CRPR,
    couleurs_groupes=couleurs_groupes,
    jours=[
        "2021-02-01",
        "2021-02-02",
        "2021-02-03",
        "2021-02-04",
        "2021-02-05",
        "2021-02-08",
        "2021-02-10",
        "2021-02-11",
        "2021-02-12",
        "2021-02-13",
        "2021-02-16",
    ],
    periode="jours",
    seuil_min_true=5,
    top_n=20,
    titre="Top 10 du personnel politique sur la FDM de la 'République' lors de la 1ère discussion du projet de loi séparatisme",
)


# %%
diachronique_séquences_personnel(
    df_CRPR,
    couleurs_groupes=couleurs_groupes,
    jours=["2021-06-28", "2021-06-29", "2021-06-30", "2021-07-01", "2021-01-23"],
    periode="jours",
    seuil_min_true=5,
    top_n=10,
    titre="Top du personnel politique sur la FDM de 'République' lors de la 2e phase de discussion du projet de loi séparatisme",
)


# %%
diachronique_séquences_personnel(
    df_CRPR,
    couleurs_groupes=couleurs_groupes,
    jours=[
        "2021-02-01",
        "2021-02-02",
        "2021-02-03",
        "2021-02-04",
        "2021-02-05",
        "2021-02-08",
        "2021-02-10",
        "2021-02-11",
        "2021-02-12",
        "2021-02-13",
        "2021-02-16",
        "2021-06-28",
        "2021-06-29",
        "2021-06-30",
        "2021-07-01",
        "2021-01-23",
    ],
    periode="jours",
    seuil_min_true=3,
    top_n=60,
    titre="Top du personnel politique sur la FDM de la 'République' lors de la discussion du projet de loi séparatisme",
)

# %%
diachronique_séquences_personnel(
    df_regroup,
    couleurs_groupes=couleurs_groupes,
    date_debut="2018-07-10",
    date_fin="2018-07-22",
    periode="intervalle",
    seuil_min_true=10,
    top_n=10,
    titre="Top du personnel politique sur la FDM de la 'République' lors de la discussion du projet de loi organique pour une démocratie ...",
)

# %% [markdown]
# ##### Projet de loi "pour une école de la confiance"

# %%
diachronique_séquences_personnel(
    df,
    couleurs_groupes=couleurs_groupes,
    date_debut="2024-01-09",
    date_fin="2024-09-05",
    periode="intervalle",
    seuil_min_true=5,
    top_n=10,
    titre="Personnel mobilisant le plus la famille de mot 'République' lors du Gouvernement Attal (A)",
)

# %%
diachronique_séquences_personnel(
    df_regroup,
    couleurs_groupes=couleurs_groupes,
    jours=["2019-04-03"],
    periode="jours",
    seuil_min_true=1,
    top_n=10,
    titre="Top du personnel politique sur la FDM de la 'République' lors de X",
)

# %%
diachronique_séquences_personnel(
    df,
    couleurs_groupes=couleurs_groupes,
    date_debut="2019-06-24",
    date_fin="2019-06-26",
    periode="intervalle",
    seuil_min_true=5,
    top_n=10,
    titre="Personnel mobilisant le plus la FDM de la 'République' lors de X",
)

# %% [markdown]
# ### Analyse par type de discussion

# %%
# Paramètres
colonne_condition = "repu_match_valide"
colonne_discussion = "point_type"

# Compter le nombre de fois où la FDM "République" est utilisée par type de discussion
df_groupes = (
    df.groupby(colonne_discussion)[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calculer la proportion
df_groupes["proportion_true"] = (
    df_groupes["true_mentions"] / df_groupes["total_mentions"] * 100
)  # en %

# Filtrage des 10 premiers (en % ou en valeur absolue)
df_groupes = (
    df_groupes.sort_values("true_mentions", ascending=False)
    .head(20)
    .reset_index(drop=True)
)


# Créer la figure
fig = go.Figure()

# Nombre d'occurrences de la "République"
fig.add_trace(
    go.Bar(
        x=df_groupes[colonne_discussion],
        y=df_groupes["true_mentions"],
        name="Nombre d'interventions avec FDM 'République'",
        marker_color="rgba(99, 110, 250, 0.6)",
        yaxis="y1",
    )
)

# Proportion des occurrences de la "République"
fig.add_trace(
    go.Scatter(
        x=df_groupes[colonne_discussion],
        y=df_groupes["proportion_true"],
        name="Proportion d'intervention en % avec FDM 'République'",
        mode="markers",
        marker=dict(color="rgba(239, 85, 59, 0.9)", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en forme
fig.update_layout(
    title="Comparaison des types de discours dans lesquels apparait la FDM République",
    xaxis=dict(title="Type de discours"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(
        title="Proportion en %",
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(x=0.60, y=-0.65, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.25,
)

# Afficher la figure
fig.show()
df_groupes


# %% [markdown]
# ### Analyse par type de prise de parole

# %%
df_repu["code_grammaire"].value_counts()

# %%
df["code_grammaire"].value_counts()

# %%
# Paramètres
colonne_condition = "code_grammaire"
colonne_discussion = "point_type"

# Compter le nombre de fois où la FDM "République" est utilisée par type de discussion
df_groupes = (
    df.groupby(colonne_discussion)[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calculer la proportion
df_groupes["proportion_true"] = (
    df_groupes["true_mentions"] / df_groupes["total_mentions"] * 100
)  # en %

# Filtrage des 10 premiers (en % ou en valeur absolue)
df_groupes = (
    df_groupes.sort_values("true_mentions", ascending=False)
    .head(20)
    .reset_index(drop=True)
)


# Créer la figure
fig = go.Figure()

# Nombre d'occurrences de la "République"
fig.add_trace(
    go.Bar(
        x=df_groupes[colonne_discussion],
        y=df_groupes["true_mentions"],
        name="Nombre d'interventions avec FDM 'République'",
        marker_color="rgba(99, 110, 250, 0.6)",
        yaxis="y1",
    )
)

# Proportion des occurrences de la "République"
fig.add_trace(
    go.Scatter(
        x=df_groupes[colonne_discussion],
        y=df_groupes["proportion_true"],
        name="Proportion d'intervention en % avec FDM 'République'",
        mode="markers",
        marker=dict(color="rgba(239, 85, 59, 0.9)", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en forme
fig.update_layout(
    title="Comparaison des types de discours dans lesquels apparait la FDM République",
    xaxis=dict(title="Type de discours"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(
        title="Proportion en %",
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(x=0.60, y=-0.65, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.25,
)

# Afficher la figure
fig.show()
df_groupes


# %% [markdown]
# ### Analyses par législatures

# %%
df_16e = df[df["legislature"] == 16]
df_15e = df[df["legislature"] == 15]

# Compter le nombre de fois où chaque orateur dit "République"
counts = (
    df_16e.groupby("nom_orateur_clean")["repu_match_valide"]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

# Filtrer les orateurs avec au moins 10 mentions True
filtered = counts[counts["true_mentions"] >= 40]

# Trier par proportion décroissante et garder les 40 premiers
df16_top20 = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(40)
    .reset_index(drop=True)
)

# Graphique
fig16_top20 = px.bar(
    df16_top20,
    x="nom_orateur_clean",
    y="proportion_true",
    title="Top 20 orateurs par proportion de mentions de 'République > 40, 16e législature'",
    labels={
        "nom_orateur_clean": "Personnel politique",
        "proportion_true": "% 'République'",
    },
    template="plotly_white",
)

fig16_top20.update_layout(xaxis_tickangle=-45)

fig16_top20.show()
df16_top20

# Compter le nombre de fois où chaque orateur dit "République"
counts = (
    df_15e.groupby("nom_orateur_clean")["repu_match_valide"]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

# Filtrer les orateurs avec au moins 10 mentions True
filtered = counts[counts["true_mentions"] >= 100]

# Trier par proportion décroissante et garder les 40 premiers
df15_top20 = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(40)
    .reset_index(drop=True)
)

# Graphique
fig15_top20 = px.bar(
    df15_top20,
    x="nom_orateur_clean",
    y="proportion_true",
    title="Top 20 orateurs par proportion de mentions de 'République > 40 15e législature'",
    labels={
        "nom_orateur_clean": "Personnel politique",
        "proportion_true": "% 'République'",
    },
    template="plotly_white",
)

fig15_top20.update_layout(xaxis_tickangle=-45)

fig15_top20.show()
df15_top20


# %%
def top_orateurs_periodique(
    df,
    periode="annee",
    annee=None,
    semaine=None,
    jour=None,
    date_debut=None,
    date_fin=None,
    jours=None,
    colonne_condition="repu_match_valide",
    seuil_min_true=None,
    top_n=20,
):
    # --- Filtrage selon la période ---
    if periode == "annee":
        if annee is None:
            raise ValueError("Il faut préciser l'année pour periode='annee'")
        df_filtered = df[df["dateSeance_day"].dt.year == annee]
        titre = f"Personnel politique mobilisant en % le plus la 'République' en {annee} à l'Assemblée Nationale (Seuil de {seuil_min_true} occurences)"

    elif periode == "semaine":
        if annee is None or semaine is None:
            raise ValueError(
                "Il faut préciser l'année et la semaine pour periode='semaine'"
            )
        df_filtered = df[
            (df["dateSeance_day"].dt.isocalendar().year == annee)
            & (df["dateSeance_day"].dt.isocalendar().week == semaine)
        ]
        titre = f"Personnel politique mobilisant en % le plus la 'République' la {semaine} semaine {annee} à l'Assemblée Nationale (Seuil de {seuil_min_true})"

    elif periode == "jour":
        if jour is None:
            raise ValueError("Il faut préciser la date pour periode='jour'")
        jour_dt = pd.to_datetime(jour).date()
        df_filtered = df[df["dateSeance_day"].dt.date == jour_dt]
        titre = f"Personnel politique mobilisant le plus en % la 'République' le {jour_dt} (Seuil de {seuil_min_true} occurences)"

    elif periode == "intervalle":
        if date_debut is None or date_fin is None:
            raise ValueError(
                "Il faut préciser date_debut et date_fin pour periode='intervalle'"
            )
        debut = pd.to_datetime(date_debut)
        fin = pd.to_datetime(date_fin)
        df_filtered = df[
            (df["dateSeance_day"] >= debut) & (df["dateSeance_day"] <= fin)
        ]
        titre = f"Personnel politique mobilisant le plus en % la 'République' du {debut.date()} au {fin.date()} (Seuil de {seuil_min_true} occurences)"

    elif periode == "jours":
        if jours is None or not isinstance(jours, (list, tuple)):
            raise ValueError("Il faut fournir une liste de dates pour periode='jours'")
        jours_dt = [pd.to_datetime(j).date() for j in jours]
        df_filtered = df[df["dateSeance_day"].dt.date.isin(jours_dt)]
        titre = f"Personnel politique mobilisant le plus la 'République' en % lors de X évènement (Seuil de {seuil_min_true} occurences)"

    else:
        raise ValueError(
            "periode doit être 'annee', 'semaine', 'jour', 'intervalle' ou 'jours'"
        )

    # --- Comptage des occurrences ---
    counts = (
        df_filtered.groupby("nom_orateur_clean")[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )
    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

    # --- Filtrage par seuil ---
    filtered = counts[counts["true_mentions"] >= seuil_min_true]

    # --- Trier par proportion décroissante et garder top_n ---
    df_top = (
        filtered.sort_values("proportion_true", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    # --- Graphique ---
    fig = px.bar(
        df_top,
        x="nom_orateur_clean",
        y="proportion_true",
        hover_data=["true_mentions", "total_mentions"],
        title=titre,
        template="plotly_white",
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        yaxis_title="Proportion des interventions totales",
        xaxis_title="Personnel politique",
    )
    fig.show()

    return df_top



# %%
# Top 10 orateurs en % par année
top_orateurs_periodique(df, periode="annee", annee=2024, seuil_min_true=20)
# Top 10 orateurs sur la semaine X de X
top_orateurs_periodique(df, periode="semaine", annee=2021, semaine=6, seuil_min_true=10)
# Top 10 orateurs en % (tel jour) le X
top_orateurs_periodique(df, periode="jour", jour="2021-02-01", seuil_min_true=10)

# %% [markdown]
# ### Quelles évolutions sur la période

# %%
# TODO : changer manuellement les couleurs des graphiques + changer dates pour ressembler plus aux 2 options définies plus haut (intervalle, jours spécifiques)


def evolutions_séquences(
    df,
    date_col="dateSeance_day",
    parti_col="groupe_députés_affiliation",
    match_col="repu_match_valide",
    min_true_mentions=100,
    top_n=7,
    start_year=2021,  # changer les dates
    end_year=2021,
):
    # Filtrer par période si spécifiée
    if start_year or end_year:
        mask = pd.Series(True, index=df.index)
        if start_year:
            mask &= df[date_col].dt.year >= start_year
        if end_year:
            mask &= df[date_col].dt.year <= end_year
        df = df.loc[mask].copy()

    # Calcul global des proportions par groupe
    counts = (
        df.groupby(parti_col)[match_col]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

    # Filtrer les groupes pertinents
    filtered = counts[counts["true_mentions"] >= min_true_mentions]

    # Sélectionner les top groupes selon la proportion
    top_partis = (
        filtered.sort_values("proportion_true", ascending=False)
        .head(top_n)[parti_col]
        .tolist()
    )

    # Filtrer les données pour ces groupes
    df_top = df[df[parti_col].isin(top_partis)].copy()

    # Calcul annuel des proportions
    df_grouped = (
        df_top.groupby([pd.Grouper(key=date_col, freq="M"), parti_col])[match_col]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    df_grouped["proportion_true"] = (
        df_grouped["true_mentions"] / df_grouped["total_mentions"]
    )
    df_grouped["Année"] = df_grouped[date_col].dt.year
    df_grouped["Mois"] = df_grouped[date_col].dt.strftime("%Y-%m")

    # Tracé du graphique (% d’utilisation par année)
    fig = px.line(
        df_grouped,
        x="Mois",
        y="proportion_true",
        color=parti_col,
        markers=True,
        title=(
            f"Évolution mensuelle du % d'utilisation du mot 'République' "
            f"(Des {top_n} principaux groupes parlementaires, {start_year or df_grouped['Année'].min()}–{end_year or df_grouped['Année'].max()})"
        ),
        labels={
            "proportion_true": "% d'utilisation",
            parti_col: "Groupe parlementaire",
        },
    )

    fig.update_layout(
        xaxis=dict(dtick="M1", tickangle=45),
        hovermode="x unified",
        template="plotly_white",
        legend_title_text="Groupe",
        yaxis_tickformat=".0%",
    )

    fig.show()



# %%
evolutions_séquences(df)

# %% [markdown]
# ## Autres variables
#
# --> en réalité ce qui serait utile ce serait de faire des vraies stats/régressions pour mesurer le poids de chacune de ces variables sur la probabilité d'utiliser la république. À voir comment faire 

# %%
df["civ"] = df["civ"].replace({"M.": "Homme", "Mme": "Femme"})

# %%
df.to_csv(
    "../data/interim/df_identification_republi_simple.csv",
    index=False,
)

# %%
fig = px.bar(df["civ"].value_counts())
fig.update_layout(
    title="Répartition des genres (civ)", template="plotly_white", showlegend=False
)
fig.show()


# %%
def diachronique_genre_total(
    df,
    genre="civ",
    colonne_condition="repu_match_valide",
    min_true=50,
    top_n=50,
    mode="Double",
):
    # 2. Compter le nombre d'occurrences de la FDM pour chaque genre
    counts = (
        df.groupby(genre)[colonne_condition]
        .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
        .reset_index()
    )

    # 3. Calcul de la proportion (%)
    counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"] * 100

    # 6. Créer la figure Plotly
    fig = go.Figure()

    # --- Mode "absolu" ou "double" : afficher les barres ---
    if mode in ["absolu", "double"]:
        for _, row in counts.iterrows():
            fig.add_trace(
                go.Bar(
                    x=[row[genre]],
                    y=[row["true_mentions"]],
                    name=row[genre],
                    marker_color="#6D0606",
                    yaxis="y1",
                    hovertemplate=f"<b>{row[genre]}</b><br>"
                    f"Valeur absolue : {row['true_mentions']}<br>"
                    f"Proportion : {row['proportion_true']:.1f} %",
                    showlegend=False,
                )
            )

    # --- Mode "proportion" ou "double" : afficher les points ---
    if mode in ["proportion", "double"]:
        fig.add_trace(
            go.Scatter(
                x=counts[genre],
                y=counts["proportion_true"],
                name="Proportion d'intervention en % avec FDM 'République'",
                mode="markers",
                marker=dict(color="black", size=8, symbol="circle"),
                line=dict(width=1, dash="dot", color="black"),
                yaxis="y2",
            )
        )

    # 7. Mise en forme du graphique
    fig.update_layout(
        title=(
            f"Top {top_n} du personnel politique investissant le plus la famille du mot 'République' (B) "
            f"(≥ {min_true} occurrences)"
        ),
        xaxis=dict(title="Député·es / Ministres", tickangle=-45),
        yaxis=dict(title="Valeur absolue", showgrid=False),
        yaxis2=dict(
            title="Proportion en %",
            overlaying="y",
            side="right",
            showgrid=False,
            range=[0, max(counts["proportion_true"].max() * 1.1, 10)],  # marge auto
        ),
        legend=dict(x=0.6, y=1.2, bgcolor="#E3E1E1"),
        template="plotly_white",
        bargap=0.25,
    )

    # 8. Ajustement du titre selon le mode
    if mode == "absolu":
        fig.update_layout(title=fig.layout.title.text + " — en valeur absolue")
    elif mode == "proportion":
        fig.update_layout(title=fig.layout.title.text + " — en proportion (%)")
    else:
        fig.update_layout(title=fig.layout.title.text + "")

    fig.show()

    return diachronique_genre_total



# %%
diachronique_genre_total(df, mode="double")

# %% [markdown]
# ### Autres variables 

# %%
# Paramètres
colonne_condition = "repu_match_valide"
colonne_groupe = "departementCode"

# Compter le nombre de fois où chaque groupe parlementaire dit "République"
df_groupes = (
    df.groupby(colonne_groupe)[colonne_condition]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calculer la proportion
df_groupes["proportion_true"] = (
    df_groupes["true_mentions"] / df_groupes["total_mentions"] * 100
)  # en %

# Filtrage des 10 premiers (en % ou en valeur absolue)
df_groupes = (
    df_groupes.sort_values("proportion_true", ascending=False)
    .head(10)
    .reset_index(drop=True)
)


# Créer la figure
fig = go.Figure()

# Nombre d'occurrences de la "République"
fig.add_trace(
    go.Bar(
        x=df_groupes[colonne_groupe],
        y=df_groupes["true_mentions"],
        name="Nombre d'interventions avec FDM 'République'",
        marker_color="rgba(99, 110, 250, 0.6)",
        yaxis="y1",
    )
)

# Proportion des occurrences de la "République"
fig.add_trace(
    go.Scatter(
        x=df_groupes[colonne_groupe],
        y=df_groupes["proportion_true"],
        name="Proportion d'intervention en % avec FDM 'République'",
        mode="markers",
        marker=dict(color="rgba(239, 85, 59, 0.9)", size=10, symbol="circle"),
        yaxis="y2",
    )
)

# Mise en forme
fig.update_layout(
    title="Investissement de la famille du mot 'République' des dix principaux groupes parlementaires (A)",
    xaxis=dict(title="Groupe parlementaire"),
    yaxis=dict(title="Valeur absolue", showgrid=False),
    yaxis2=dict(
        title="Proportion en %",
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(x=0.63, y=-0.28, bgcolor="rgba(255,255,255,0.7)"),
    template="plotly_white",
    bargap=0.25,
)

# Afficher la figure
fig.show()
df_groupes


# %%
# Nécessité ici de transformer l'âge en chiffre pour l'ordonner.

# Compter le nombre de fois où chaque orateur dit "République"
counts = (
    df.groupby("experienceDepute")["repu_match_valide"]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

# Filtrer les orateurs avec au moins 10 mentions True
filtered = counts[counts["true_mentions"] >= 50]

# Trier par proportion décroissante et garder les 40 premiers
df_experience_top20 = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(40)
    .reset_index(drop=True)
)

df_experience_top20

# Graphique
fig_experience = px.bar(
    df_experience_top20,
    x="experienceDepute",
    y="proportion_true",
    title="Évolution de la proportion d'utilisation de la 'République avec l'expérience",
    labels={"experienceDepute": "Expérience", "proportion_true": "% 'République'"},
    template="plotly_white",
)

fig_experience.update_layout(xaxis_tickangle=-45)

fig_experience.show()

df_experience_top20

# %%
# Compter le nombre de fois où chaque orateur dit "République"
counts = (
    df.groupby("age")["repu_match_valide"]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

# Filtrer les orateurs avec au moins 10 mentions True
filtered = counts[counts["true_mentions"] >= 50]

# Trier par proportion décroissante et garder les 40 premiers
df_experienceb_top20 = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(40)
    .reset_index(drop=True)
)

# Graphique
fig_experienceb = px.bar(
    df_experienceb_top20,
    x="age",
    y="proportion_true",
    title="Évolution de la proportion d'utilisation de la 'République avec l'âge",
    labels={"age": "Age", "proportion_true": "% 'République'"},
    template="plotly_white",
)

fig_experienceb.update_layout(xaxis_tickangle=-45)

fig_experienceb.show()

df_experienceb_top20

# %%
# Compter le nombre de fois où chaque orateur d'un département dit "République"
counts = (
    df.groupby("departementCode")["repu_match_valide"]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

# Filtrer les orateurs avec au moins 10 mentions True
filtered = counts[counts["true_mentions"] >= 50]

# Trier par proportion décroissante et garder les 40 premiers
df_dpt_top20 = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(40)
    .reset_index(drop=True)
)

df_dpt_top20

# Graphique
fig_dpt = px.bar(
    df_dpt_top20,
    x="departementCode",
    y="proportion_true",
    title="Évolution de la proportion d'utilisation de la 'République par département",
    labels={"departementCode": "Departement", "proportion_true": "% 'République'"},
    template="plotly_white",
)

fig_dpt.update_layout(xaxis_tickangle=-45)

fig_dpt.show()

df_dpt_top20

# %% [markdown]
# ==> en VA ce sont les départements IDF et surtout le 93 de LFI qui reviennent le plus, mais en % ce sont les territoires d'outre-mers

# %%
# Compter le nombre de fois où chaque orateur/genre dit "République"
counts = (
    df.groupby("civ")["repu_match_valide"]
    .agg(total_mentions="count", true_mentions=lambda x: (x == True).sum())
    .reset_index()
)

# Calcul de la proportion
counts["proportion_true"] = counts["true_mentions"] / counts["total_mentions"]

# Filtrer les orateurs avec au moins 10 mentions True
filtered = counts[counts["true_mentions"] >= 50]

# Trier par proportion décroissante et garder les 40 premiers
df_genre_top20 = (
    filtered.sort_values("proportion_true", ascending=False)
    .head(40)
    .reset_index(drop=True)
)

df_genre_top20

# %% [markdown]
# ## Test de régressions linéaires 

# %% [markdown]
# ### Étape 1 : restructuration des variables 

# %%
# Réfléchir à recoder l'âge en génération (reprendre celles de VT ?)

# %%
df["genre"] = df["civ"].replace({"Homme": "1", "Femme": "0"})

# %%
df["repu"] = df["repu_match_valide"].replace({"True": "1", "False": "0"})

# %%
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def regression_lineaire(df, y_col, x_cols):
    # Définir X et y
    X = df[x_cols]
    y = df[y_col]

    # Encoder les colonnes catégorielles si nécessaire
    X = pd.get_dummies(X, drop_first=True)

    # Forcer en 2D si une seule variable explicative
    if X.shape[1] == 1:
        X = X.values.reshape(-1, 1)
    else:
        X = X.values

    # y doit être 1D
    y = y.values

    # Créer et entraîner le modèle
    model = LinearRegression()
    model.fit(X, y)

    # Prédictions
    y_pred = model.predict(X)

    # Résultats
    print("Coefficient(s):", model.coef_)
    print("Intercept:", model.intercept_)
    print("Score R²:", model.score(X, y))

    # Graphique si une seule variable explicative
    if X.shape[1] == 1:
        plt.scatter(X, y, color="blue", label="Données réelles")
        plt.plot(X, y_pred, color="red", label="Régression")
        plt.xlabel(x_cols[0])
        plt.ylabel(y_col)
        plt.legend()
        plt.show()

    return model



# %%
modele = regression_lineaire(
    df, y_col="repu_match_valide", x_cols=["parti_affiliation"]
)

# %%
modele = regression_lineaire(df, y_col="repu_match_valide", x_cols=["experienceDepute"])

# %%
modele = regression_lineaire(
    df,
    y_col="repu_match_valide",
    x_cols=["parti_affiliation", "civ", "experienceDepute"],
)

# %%
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm


def regression_lineaire_df(df, y_col, x_cols, summary=False):
    # Définir X (variable à expliquer) et y (variable explicatives)
    X = df[x_cols]
    y = df[y_col]

    # Encoder les colonnes catégorielles si nécessaire
    X = pd.get_dummies(X, drop_first=True)

    # Forcer en numpy array
    X_values = X.values
    y_values = y.values

    # ----- Version scikit-learn -----
    model = LinearRegression()
    model.fit(X_values, y_values)
    y_pred = model.predict(X_values)

    print("Régression (scikit-learn)")
    print("Coefficient(s):", model.coef_)
    print("Intercept:", model.intercept_)
    print("Score R²:", model.score(X_values, y_values))

    # Graphique si une seule variable explicative
    if X.shape[1] == 1:
        plt.scatter(X_values, y_values, color="blue", label="Données réelles")
        plt.plot(X_values, y_pred, color="red", label="Régression")
        plt.xlabel(x_cols[0])
        plt.ylabel(y_col)
        plt.legend()
        plt.show()

    # ----- Version statsmodels -----
    if summary:
        X_sm = sm.add_constant(X)  # ajoute la constante pour l'intercept
        model_sm = sm.OLS(y, X_sm).fit()
        print("Résumé statistique (statsmodels):")
        print(model_sm.summary())
        return model, model_sm

    return model



# %%
modele_sklearn, modele_stats = regression_lineaire_df(
    df, y_col="repu_match_valide", x_cols=["parti_affiliation", "civ"], summary=True
)
