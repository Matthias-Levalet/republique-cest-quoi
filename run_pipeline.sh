#!/bin/bash
set -e  # stoppe si une étape échoue

cd "$(dirname "$0")/scripts"   # ← correct si le .sh est à la racine

etapes=(
    "1_1_extraction.py"
    "1_2_fusion_legislatures.py"
    "1_3_regroupement_interventions.py"
    "2_1_filtrage.py"
    "2_2_identification_acteurs.py"
    "2_3_match_deputes.py"
    "2_4_affiliations.py"
)

for etape in "${etapes[@]}"; do
    echo ""
    echo "=============================="
    echo "=== $etape ==="
    echo "=============================="
    python "$etape"
done

echo ""
echo "Pipeline complet"

# Pour exécuter : 
# chmod +x run_pipeline.sh
# ./run_pipeline.sh