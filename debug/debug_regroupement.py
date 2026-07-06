# CE FICHIER EST PAS EXECUTABLE EN L'ÉTAT, IL S'AGIT D'UNE TRACE D'UN BOUT DU NB 1

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
