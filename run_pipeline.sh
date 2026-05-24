#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run_pipeline.sh
#   ./run_pipeline.sh --offline
#   ./run_pipeline.sh --keywords "large language model,transformer,multimodal ai" --max-results 10 --days 365 --max-papers 5

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

SOURCE="openalex"
KEYWORDS="large language model,transformer,multimodal ai"
MAX_RESULTS=10
DAYS=365
MAX_PAPERS=5
OFFLINE="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --offline)
      OFFLINE="true"
      shift
      ;;
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --keywords)
      KEYWORDS="$2"
      shift 2
      ;;
    --max-results)
      MAX_RESULTS="$2"
      shift 2
      ;;
    --days)
      DAYS="$2"
      shift 2
      ;;
    --max-papers)
      MAX_PAPERS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "==> Step 0: Clean generated files"
rm -f data/papers.json data/summaries.json data/papers_offline.json
find articles -maxdepth 1 -type f \( -name '*.md' -o -name '*.json' \) -delete

echo "==> Step 1: Fetch papers"
if [[ "$OFFLINE" == "true" ]]; then
  python .github/skills/paper-research-skill/scripts/fetch_papers.py --offline --output data/papers.json
else
  python .github/skills/paper-research-skill/scripts/fetch_papers.py \
    --source "$SOURCE" \
    --keywords "$KEYWORDS" \
    --max-results "$MAX_RESULTS" \
    --days "$DAYS" \
    --output data/papers.json
fi

echo "==> Step 2: Summarize papers"
python .github/skills/paper-summarization-skill/scripts/summarize_papers.py \
  --input data/papers.json \
  --output data/summaries.json \
  --max-papers "$MAX_PAPERS"

echo "==> Step 3: Generate articles"
python .github/skills/article-generation-skill/scripts/generate_article.py \
  --input data/summaries.json \
  --output articles

echo "==> Done"
echo "papers:    $(jq 'length' data/papers.json)"
echo "summaries: $(jq 'length' data/summaries.json)"
echo "articles:  $(find articles -maxdepth 1 -type f -name '*.md' | wc -l | xargs)"
