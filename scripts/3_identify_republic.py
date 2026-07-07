# %% [markdown]
# # Identifier les textes évoquant la République

# %%
import pandas as pd
import re

# TODO: aviser si vire id_orateur et utiliser id_acteur partout
df = pd.read_csv(
    "../data/interim/interventions_nettoyees.csv",
    low_memory=False,
)
df.shape


# %% [markdown]
# ## INTRODUIRE PRÉ-TRAITEMENT TEXTE

# %% [markdown]
# Pour simplifier la vie et faciliter aussi possibles perf d'un futur modèle, virer les parenthèses et balises ici pour s'économiser pas mal de choses du côté des noms de groupes

# %%
# TODO : remarque matthias -> aviser possibles soucis accents etc. ?

# nettoyage basique du texte
# après test pas de diff avec normalisation unicode nfc (voir plus bas)
def nettoyer_texte(texte):
    if not isinstance(texte, str):
        return texte
    # Supprimer les balises HTML/XML
    texte = re.sub(r"<[^>]+>", "", texte)
    # Supprimer contenu entre parenthèses
    texte = re.sub(r"\([^)]*\)", "", texte)
    # Supprimer les espaces multiples
    texte = re.sub(r"\s+", " ", texte).strip()
    # uniformise pour avoir les bons apostrophes (nécessaire pour regex)
    texte = texte.replace("’", "'")
    return texte


df["texte_brut"] = df["texte"]  # garder une version brute du texte
df["texte"] = df["texte"].apply(nettoyer_texte)

# Si pas géré avant (devrait le faire dans le 2 sinon, mais possible perte avec nettoyage)
# Supprimer les lignes où "texte" est manquant
# pas déconnant de le garder là avec éventuelles suppressions dues au nettoyage

# df = df.dropna(subset=["texte"])
# en fait plutôt ça (sinon on vire pas les lignes avec texte vide après nettoyage)
df = df[df["texte"].notna() & (df["texte"] != "")]
df.shape

# %% [markdown]
# ## Regex

# %% [markdown]
# Logique de la tentative :
# - regex
# - mais exclure certains termes
# - mais comme les termes exclus peuvent apparaitre aussi avec les termes voulus, éviter de chainer et finir par virer des trucs qu'on aurait voulu (les idées républicaines sont menacées par Les Républicains)

# %%
# préparer les pays à exclure
with open("../data/raw/liste_pays_republique_stable.txt", "r", encoding="utf-8") as f:
    liste_pays = [line.strip() for line in f]

# créer un pattern regex pour les pays, plus bas on rendra le groupe non capturant
pattern_pays = r"|".join(re.escape(p) for p in liste_pays)


# Regex de la famille du mot République (simplifié ici)

pattern_lexical = re.compile(
    r"républi",  # même au milieu des mots
    re.I,
)

# Regex des expressions à exclure
# logique : création de groupes (?:…) non capturant
# car utilisé juste pour les positions, pas besoin de les récupérer

# Expressions à exclure - casse exacte
# possible cas du féminin… mais pas d'occurrence dans la base avec nos exclusions
pattern_excl_case_sensitive = re.compile(
    # Exclusion des occurences liées au parti les Républicains
    r"(?:\b[LlDd]es Républicains\b)"  # garde la casse pour identifier le parti (et pas un adjectif)
    r"|(?:\baux Républicains\b)"  # idem majuscule pour le groupe
    r"|(?:\b[Cc]ollègues? Républicains?\b)"  # cas avec et sans maj pour collègues
    r"|(?:\bsénateurs? Républicains?\b)"  # pas de maj sénateurs ou féminin dans la base après exclu, mais aviser
    r"|(?:\bdéputés? Républicains?\b)"  # pas de maj députés ou féminin dans la base après exclu, mais aviser
    # spécifique corpus AN choisi
    r"|(?:\bLes Républicain\b)"  # typo manque s = spécifique corpus AN (4 occurrences)
    r"|(?:\bentre Républicains?\b)"  # spécifique corpus AN (4 occurrences)
    r"|(?:\bex-Républicains?\b)"  # spécifique corpus AN (4 occurrences)
    r"|(?:\banciens? Républicains?\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bseuls Républicains\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bparlementaires Républicains\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bélus Républicains\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bgroupeLes Républicains\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\b[Nn]ous Républicains\b)"  # spécifique corpus AN (2 occurrences)
    r"|(?:\bcertains Républicains\b)"  # spécifique corpus AN (4 occurrences)
    r"|(?:\bamis Républicains\b)"  # spécifique corpus AN (1 occurrence)
    # occurrences plusieurs partis
    r"|(?:\bdroite, Républicains et macronistes\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bRépublicains-Front national\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bMacronistes, Républicains, lepénistes\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bRassemblement national, Républicains et macronistes\b)"  # spécifique corpus AN (1 occurrence)
    r"|(?:\bparti Républicain\b)"  # spécifique corpus AN (1 occurrence : US)
    # titre presse
    r"|(?:\bL[’']Est républicain\b)"  # le journal
    r"|(?:\bLa Nouvelle République\b)"  # le journal
)

# Expressions à exclure - ignorer la casse
pattern_excl_case_insensitive = re.compile(
    # partis et groupes politiques
    r"(?:\bgauche démocrate et républicaine\b)"  # premier sans |
    r"|(?:\bgauche démocrate et républicaine-NUPES\b)"
    r"|(?:\brépublique en marche\b)"
    r"|(?:\bsocialiste, écologiste et républicain\b)"
    # fonctions et institutions
    r"|(?:\bprésidents? de la république\b)"
    r"|(?:\bprésidences? de la république\b)"
    r"|(?:\bprocureurs? de la république\b)"
    r"|(?:\bcours? de justice de la république\b)"  # nb : cours de sûreté est lui gardé car projet loi LR et pas une institution
    r"|(?:\badministration générale de la république\b)"
    r"|(?:\bgouvernement de la république française\b)"  # pas de pluriel dans corpus
    r"|(?:\bInstitut supérieur des langues de la République française\b)"
    r"|(?:\bHaut-commissariat de la République\b)"  # expression utilisée pour parler des préfets en Kanaky et Polynésie française uniquement
    r"|(?:\bHaut-commissaire de la République\b)"  # ibid
    r"|(?:\bcompagnies? républicaines? de sécurité\b)"
    r"|(?:\bgarde républicaine\b)"
    r"|(?:\bgardes? républicains?\b)"
    r"|(?:\buniversités? de la République\b)"  # sur corpus 2017-2024 réf à une commission d'enquête
    r"|(?:\binstitut Famille et République\b)"  # institut privé de la galaxie LMPT
    # titres de loi
    r"|(?:\bnouvelle organisation territoriale de la République\b)"
    r"|(?:\bconfortant le respect des principes de la République\b)"
    r"|(?:\bpour une république numérique\b)"
    # expression et législations
    # NOTE: Le choix a été fait de ne pas exclure ces formes qui sont pertinentes à conserver
    # Elles sont conservées ici en commentaires pour traçabilité
    # r"|(?:\bcontrat d[’']engagement républicain\b)"
    # r"|(?:\bcontrat d[’']engagement au respect des principes de la République\b)"
    # r"|(?:\bcontrat d[’']intégration républicaine\b)"
    # r"|(?:\bquartier[s]? de reconquête républicaine\b)"
    # pays
    r"|(?:\brépubliques? soviétiques?\b)"
    r"|(?:\bex-républiques? soviétiques?\b)"
    r"|(?:\brépublique de Weimar\b)"
    r"|(?:\b(?:" + pattern_pays + r")\b)",  # ajout des exclusions de pays
    re.I,
)

# TODO : ajouter les dernières exclusions et cas limites
# place de la république = 45
# république du Haut-Karabakh = 3
# république d’Artsakh (selon forme de l’Artsakh) = 16
# république islamique (iran) = ~9 ?????
# république des Fidji =1
# République de Chine = 1
# républiques du Donbass = 2
# république de Crimée = 1
# République yougoslave
# République démocratique d'Arménie
# Républiques du Bénin et du Sénégal = 2
# République romaine = 5 ????


def contains_lexical_outside_excl(text):
    # NOTE : on pourrait utiliser spans triés et bisect pour optimiser la vérification des positions,
    # et on pourrait merger les positions de spans d'exclusions pour accélérer,
    # mais pas indispensable ici et plus compliqué

    # si pas de match lexical inutile d'aller plus loin
    if not pattern_lexical.search(text):
        return False

    # Collecter les spans exclus
    # en ajoutant les exclusions sensibles et insensibles à la casse
    excl_positions = [m.span() for m in pattern_excl_case_sensitive.finditer(text)] + [
        m.span() for m in pattern_excl_case_insensitive.finditer(text)
    ]

    # Fonction pour vérifier si une position est dans une zone exclue
    # (ici optimisable avec bisect si besoin)
    def in_excl(pos):
        # return any(start <= pos < end for start, end in excl_positions) # equivalent mais moins clair
        for start, end in excl_positions:
            if start <= pos < end:
                return True
        return False

    # Chercher toutes les occurrences du champ lexical
    for match in pattern_lexical.finditer(text):
        start_pos = match.start()
        if not in_excl(start_pos):
            return True
    return False


# %%
# bloc d'essai
mon_texte = "Les députés Républicains ont voté une loi grâce à l'institut de la famille et république."
contains_lexical_outside_excl(mon_texte)


# %%
# Appliquer sur la colonne
df["repu_match_valide"] = df["texte"].apply(contains_lexical_outside_excl)

# %%
df["repu_match_valide"].value_counts()

# %%
# NOTE : après tests pas de différence côté accents (normalisation unicodedata NFC)
# Recherche après normalisation NFC
# import unicodedata
# df["texte_nfc"] = df["texte"].apply(lambda x: unicodedata.normalize("NFC", x))
# df["repu_match_valide_nfc"] = df["texte_nfc"].apply(contains_lexical_outside_excl)
# df["repu_match_valide_nfc"].value_counts()

# %%
# Match lexical simple (sans exclusions)
pattern_lexical = re.compile(r"républi", re.I)

df["repu_match"] = df["texte"].str.contains(pattern_lexical, na=False)

df["repu_match"].value_counts()

# %%
# dans fichier nos députés (sans regroupement donc)
# repu_match_valide
# False    1377276
# True       13924
# Name: count, dtype: int64

# dans fichier brut extraction sans regroupement :
# repu_match_valide
# False    1016076
# True       13333
# Name: count, dtype: int64

# dans fichier maison avec regroupement :
# repu_match_valide
# False    506104
# True      10922
# Name: count, dtype: int64

# TODO -> ALLER VOIR LES ~600 manquants !!!!!!!!!!

# --------------------------------------
# Et le match "républi" sans exclusions :
# ie :
# pattern_lexical = re.compile(
#     r"républi",  # même au milieu des mots
#     re.I,
# )

# Sur fichier interv groupées :
# repu_match
# False    392747
# True      30949
# Name: count, dtype: int64

# Idem avec NFC normalisation :
# repu_match_nfc
# False    392747
# True      30949
# Name: count, dtype: int64

# Sur extraction brute sans groupement :
# repu_match
# False    1083748
# True       44090
# Name: count, dtype: int64

# Sur nosdeputés 15+16
# repu_match
# False    1345638
# True       45569
# Name: count, dtype: int64

# sur https://an-4931d4.gitpages.huma-num.fr/debats-AN#tableau-complet
#  ✓ 2 010 738 interventions en mémoire (2011–2026) — recherches instantanées
# 33 694 interventions
# -> mehhh il en manque alors que période plus longue


# %%
# TODO : À VÉRIFIER POUR INTÉGRER nb de mentions
# TODO : pourrait fusionner avec la fonction précédente pour éviter de parcourir le texte deux fois,
# mais pour l'instant on garde séparé pour clarté et test

# # Rajout en test d'une autre colonne avec le nombre de fois où la République apparait
# # À tester/voir si fonctionne bien mais en tout cas absence de cas avec false et au moins 1


def count_lexical_outside_excl(text):
    if pd.isna(text):
        return 0

    # Trouver les positions des expressions exclues
    excl_positions = []
    excl_positions.extend(
        [m.span() for m in pattern_excl_case_sensitive.finditer(text)]
    )
    excl_positions.extend(
        [m.span() for m in pattern_excl_case_insensitive.finditer(text)]
    )

    # Fonction pour vérifier si une position est dans une zone exclue
    def in_excl(pos):
        for start, end in excl_positions:
            if start <= pos < end:
                return True
        return False

    # Compter les occurrences valides
    count = 0
    for match in pattern_lexical.finditer(text):
        start_pos = match.start()
        if not in_excl(start_pos):
            count += 1

    return count


# Appliquer la fonction pour compter les mentions valides de "république" dans le texte
df["nombre_mentions_repu"] = df["texte"].apply(count_lexical_outside_excl)

# %%
# ============
# EXPORTS
# ============

# Exporter fichier avec colone match pour calcul avec proportions
df.to_csv(
    "../data/interim/df_repu_proportion.csv",
    index=False,
)

# export des seuls cas contenant république

df_match = df[df["repu_match_valide"]]

df_match.to_csv(
    "../data/interim/df_repu.csv",
    index=False,
    # quoting=csv.QUOTE_ALL,  # not needed anymore ?
)

