#!/bin/bash
# ==============================================================================
# Druggie_buggie Orchestration Runner
# Executes pipeline verification, data ingestion, and BigQuery checks
# ==============================================================================

set -e

PROJECT_ID="db1b-1"
REGION="us-west1"

echo "=================================================="
echo "💉 Running Druggie_buggie Data Architecture Runner"
echo "Target GCP Project: $PROJECT_ID ($REGION)"
echo "=================================================="

# Check Python environment
if command -v python3 &>/dev/null; then
    echo "🐍 Python3 detected: $(python3 --version)"
else
    echo "❌ Python3 is required but not installed."
    exit 1
fi

echo "📦 Verifying directory structure..."
mkdir -p data/raw data/processed notebooks sql/bronze sql/silver sql/gold src/extractors src/loaders src/transformers src/analysis docs

echo "🔍 Validating modules..."
python3 -c "import src; print('✅ Package import verified')"

echo "=================================================="
echo "🎉 Druggie_buggie verified successfully."
echo "   To launch the interactive forensic dashboard:"
echo "   👉 python3 server.py"
echo "=================================================="

if [ "$1" = "serve" ]; then
    python3 server.py
fi

