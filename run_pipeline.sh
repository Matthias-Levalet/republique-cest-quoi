#!/bin/bash

set -e  # stoppe au premier script qui échoue

ROOT="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$ROOT/scripts"
LOGS="$ROOT/logs"

mkdir -p "$LOGS"

LOGFILE="$LOGS/pipeline_$(date +%Y%m%d_%H%M%S).txt"

exec > >(tee -a "$LOGFILE") 2>&1

echo "Pipeline lancé le $(date)"

etapes=(
    "1_1_extraction.py"
    "1_2_fusion_legislatures.py"
    "1_3_regroupement_interventions.py"
    "2_1_filtrage.py"
    "2_2_identification_acteurs.py"
    "2_3_match_deputes.py"
    "2_4_affiliations.py"
    "3_1_identification_republique.py"
)

cd "$SCRIPTS"

for etape in "${etapes[@]}"; do
    echo
    echo "========================================"
    echo "=== $etape ==="
    echo "========================================"

    python -u "$etape"
done

echo
echo "========================================"
echo "=== Pipeline .sh terminé ! ==="
echo "========================================"

echo "Journal : $LOGFILE"

# to run :
# chmod +x run_pipeline.sh
# ./run_pipeline.sh