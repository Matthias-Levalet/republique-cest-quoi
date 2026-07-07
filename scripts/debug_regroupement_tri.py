# %% [markdown]
# # Debug - Investigation tri avant regroupement des interventions
# Script d'investigation PONCTUELLE, ne fait PAS partie du pipeline de
# production (pas de numéro, etc.).
# Conservé pour tracer la décision prise dans 1-3 : ne PAS trier le csv
# avant d'appliquer regrouper(), malgré la tentation de trier par
# ordinal_prise/ordre_absolu_seance/id_syceron pour "sécuriser" l'ordre.
#
# Conclusion de cette investigation (à date) :
# le tri change le nombre de lignes regroupées (959660 sans tri vs 981871
# avec tri sur ordre_absolu_seance seul, 960491 avec tri + ordinal_prise,
# 979438 avec tri sur id_syceron seul) sans qu'aucune version ne soit
# clairement "la bonne" -> on garde l'ordre du csv d'entrée (pas de tri)
# en attendant d'élucider complètement l'origine de l'écart.
# TODO non résolu : cas "de Rugy" (CRSANR5L15S2019O1N196) qui ne fusionne
# pas correctement, probablement lié au tri/typage plutôt qu'à un vrai
# changement de code_grammaire/code_parole.

# %%
import pandas as pd

PATH_ENTREE = "../data/interim/extract_15_16_concat.csv"

CODES_INTERRUPTION = {"INTERRUPTION_1_10"}

# %%
df = pd.read_csv(PATH_ENTREE, low_memory=False, dtype={"id_orateur": str})
df["code_parole"] = df["code_parole"].fillna("non_précisé")
print("Shape du df chargé : ", df.shape)


# %% [markdown]
# ## Fonction regrouper (copie de 1-3, nécessaire pour comparer les variantes)
# nb : dupliquée ici volontairement (pas d'utils partagé) - si vous modifiez
# la logique de regroupement dans 1-3, pensez à répercuter ici si vous
# continuez à utiliser ce script de debug.

# %%
COLS_META = [
    "uid", "SeanceRef", "SessionRef", "dateSeance", "dateSeanceJour",
    "numSeanceJour", "numSeance", "typeAssemblee", "legislature", "session",
    "nomFichierJo", "presidentSeance", "point_titre", "point_type",
    "valeur_ptsodj", "ordinal_prise", "ordre_absolu_seance", "id_acteur",
    "id_mandat", "code_grammaire", "code_style", "code_parole", "id_syceron",
    "roledebat", "nom_orateur", "qualite_orateur", "id_orateur", "stime",
]


def regrouper(df: pd.DataFrame) -> pd.DataFrame:
    """Voir 1_3_regroupement_interventions.py pour la version documentée."""
    cols_utiles = list(dict.fromkeys(COLS_META + ["texte"]))
    work = df[cols_utiles].copy()
    work["uid_norm"] = work["uid"].fillna("").astype(str)
    work["id_acteur_norm"] = work["id_acteur"].fillna("").astype(str)
    work["code_grammaire_norm"] = work["code_grammaire"].fillna("").astype(str)
    work["code_parole_norm"] = work["code_parole"].fillna("").astype(str)
    work["texte_norm"] = work["texte"].fillna("").astype(str)

    resultats, groupe, buffer_interruptions = [], None, []

    def ligne_sortie_depuis_base(base_row):
        r = {col: base_row[col] for col in cols_utiles}
        r["nb_fragments"] = pd.NA
        r["nb_interruptions_recues"] = pd.NA
        r["a_ete_interrompu"] = pd.NA
        r["id_syceron_fragments"] = pd.NA
        return r

    def clore_groupe(g):
        row = g["premiere_ligne"].copy()
        row["texte"] = " ".join(g["textes"])
        row["nb_fragments"] = g["nb_fragments"]
        row["nb_interruptions_recues"] = g["nb_interruptions_recues"]
        row["a_ete_interrompu"] = g["nb_interruptions_recues"] > 0
        row["id_syceron_fragments"] = "|".join(g["codes_syceron"])
        return row

    for row in work.to_dict("records"):
        cg, cp = row["code_grammaire_norm"], row["code_parole_norm"]
        acteur_str, uid_str = row["id_acteur_norm"], row["uid_norm"]
        syc = str(row["id_syceron"]) if pd.notna(row["id_syceron"]) else ""

        if cg in CODES_INTERRUPTION:
            if groupe is not None:
                buffer_interruptions.append(row)
                groupe["nb_interruptions_recues"] += 1
            else:
                resultats.append(ligne_sortie_depuis_base(row))
            continue

        if (
            groupe is not None and buffer_interruptions and acteur_str != ""
            and groupe["id_acteur"] == acteur_str and groupe["uid"] == uid_str
            and groupe["codes_grammaire"][-1] == cg and groupe["codes_parole"][-1] == cp
        ):
            groupe["textes"].append(row["texte_norm"])
            groupe["codes_grammaire"].append(cg)
            groupe["codes_parole"].append(cp)
            groupe["codes_syceron"].append(syc)
            groupe["nb_fragments"] += 1
        else:
            if groupe is not None:
                resultats.append(clore_groupe(groupe))
                for irr in buffer_interruptions:
                    resultats.append(ligne_sortie_depuis_base(irr))
                buffer_interruptions = []
            groupe = {
                "uid": uid_str, "id_acteur": acteur_str,
                "premiere_ligne": {col: row[col] for col in cols_utiles},
                "textes": [row["texte_norm"]], "codes_grammaire": [cg],
                "codes_parole": [cp], "codes_syceron": [syc],
                "nb_fragments": 1, "nb_interruptions_recues": 0,
            }

    if groupe is not None:
        resultats.append(clore_groupe(groupe))
        for irr in buffer_interruptions:
            resultats.append(ligne_sortie_depuis_base(irr))

    return pd.DataFrame(resultats)


# %% [markdown]
# ## A) Profil des clés de tri

# %%
w = df.copy()
w["ordinal_prise_num"] = pd.to_numeric(w["ordinal_prise"], errors="coerce")
w["ordre_absolu_seance_num"] = pd.to_numeric(w["ordre_absolu_seance"], errors="coerce")

print("Lignes totales:", len(w))
print("NaN ordinal_prise:", w["ordinal_prise_num"].isna().sum())
print("NaN ordre_absolu_seance:", w["ordre_absolu_seance_num"].isna().sum())

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

# %% [markdown]
# ## B) Comparaison avant/après tri (audit global)

# %%
def prepare_sorted_for_regroup(df_in):
    w = df_in.copy()
    w["uid_norm"] = w["uid"].fillna("").astype(str)
    w = w.reset_index(drop=False).rename(columns={"index": "_row_order"})
    w["ordinal_prise_num"] = pd.to_numeric(w["ordinal_prise"], errors="coerce")
    w["ordre_absolu_seance_num"] = pd.to_numeric(w["ordre_absolu_seance"], errors="coerce")
    w = w.sort_values(
        by=["uid_norm", "ordinal_prise_num", "ordre_absolu_seance_num", "_row_order"],
        kind="mergesort", na_position="last",
    ).reset_index(drop=True)
    return w.drop(columns=["ordinal_prise_num", "ordre_absolu_seance_num", "_row_order"])


out_no_sort = regrouper(df.copy())
df_sorted = prepare_sorted_for_regroup(df.copy())
out_sort = regrouper(df_sorted)

print("Shape sans tri:", out_no_sort.shape)
print("Shape avec tri robuste:", out_sort.shape)

a = out_no_sort.groupby("uid", dropna=False).size().rename("n_no_sort")
b = out_sort.groupby("uid", dropna=False).size().rename("n_sort")
delta = pd.concat([a, b], axis=1).fillna(0)
delta["delta"] = delta["n_sort"] - delta["n_no_sort"]
delta = delta.sort_values("delta", ascending=False)
print(delta.head(30))

# %% [markdown]
# ## C) Détail des triplets intervention -> interruption -> reprise
# Repère les cas où une reprise après interruption ne fusionne pas, et
# compare le statut (fusion attendue / non fusion) avant et après tri.

# %%
def build_triplets(df: pd.DataFrame) -> pd.DataFrame:
    t = df.copy().reset_index(drop=True)
    t["uid_norm"] = t["uid"].fillna("").astype(str)
    t["id_acteur_norm"] = t["id_acteur"].fillna("").astype(str)
    t["code_grammaire_norm"] = t["code_grammaire"].fillna("").astype(str)
    t["code_parole_norm"] = t["code_parole"].fillna("non_précisé").astype(str)

    rows = []
    for i in range(len(t) - 2):
        a, b, c = t.iloc[i], t.iloc[i + 1], t.iloc[i + 2]

        if b["code_grammaire_norm"] != "INTERRUPTION_1_10":
            continue
        if a["code_grammaire_norm"] == "INTERRUPTION_1_10":
            continue
        if c["code_grammaire_norm"] == "INTERRUPTION_1_10":
            continue
        if a["uid_norm"] != c["uid_norm"]:
            continue

        same_actor = (a["id_acteur_norm"] != "") and (a["id_acteur_norm"] == c["id_acteur_norm"])
        same_cg = a["code_grammaire_norm"] == c["code_grammaire_norm"]
        same_cp = a["code_parole_norm"] == c["code_parole_norm"]

        if same_actor and same_cg and same_cp:
            status, reason = "fusion_attendue", "ok_regles_fusion"
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

        rows.append({
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
        })

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.drop_duplicates(subset=["triplet_key"]).reset_index(drop=True)
    return out


cas_no_sort = build_triplets(df).rename(columns={"status": "status_no_sort", "reason": "reason_no_sort"})
cas_sort = build_triplets(df_sorted).rename(columns={"status": "status_sort", "reason": "reason_sort"})

cols_common = [
    "triplet_key", "uid", "nom_orateur_avant", "nom_orateur_reprise",
    "id_acteur_avant", "id_acteur_reprise", "ordre_avant", "ordre_interrupt",
    "ordre_reprise", "id_syceron_avant", "id_syceron_interrupt",
    "id_syceron_reprise", "txt_avant", "txt_interrupt", "txt_reprise",
]

cmp = cas_no_sort[cols_common + ["status_no_sort", "reason_no_sort"]].merge(
    cas_sort[["triplet_key", "status_sort", "reason_sort"]], on="triplet_key", how="outer",
)
cmp["status_no_sort"] = cmp["status_no_sort"].fillna("absent")
cmp["status_sort"] = cmp["status_sort"].fillna("absent")
cmp["reason_no_sort"] = cmp["reason_no_sort"].fillna("")
cmp["reason_sort"] = cmp["reason_sort"].fillna("")

changes = cmp[cmp["status_no_sort"] != cmp["status_sort"]].copy()

print("Triplets sans tri :", len(cas_no_sort))
print("Triplets avec tri :", len(cas_sort))
print("Triplets dont le statut change :", len(changes))
print(changes.sort_values(["uid", "ordre_avant"]).head(100))

changes.to_csv("../data/temp/cas_statut_change_apres_tri.csv", index=False, encoding="utf-8")
print("Export (debug uniquement, hors pipeline) : ../data/temp/cas_statut_change_apres_tri.csv")

# %% [markdown]
# ## Cas particulier : "de Rugy" (TODO non résolu)

# %%
print(
    changes[changes["nom_orateur_avant"].fillna("").str.contains("rugy", case=False)][
        [
            "uid", "status_no_sort", "status_sort", "reason_no_sort", "reason_sort",
            "ordre_avant", "ordre_interrupt", "ordre_reprise",
            "id_syceron_avant", "id_syceron_interrupt", "id_syceron_reprise",
        ]
    ].head(100)
)
