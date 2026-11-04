#!/usr/bin/env bash
# Re-render every deck whose qmd changed since its PDF was last committed,
# regenerate the PDF with decktape, then commit and push.
#
# Usage: ./update-pdfs.sh ["commit message"]
set -euo pipefail

root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$root"

last_commit() { git log -1 --format=%ct -- "$1" 2>/dev/null || true; }

# The live-revealjs runtime is an ES module, which Chrome refuses to load over file://.
port=8765
python3 -m http.server "$port" -d docs >/dev/null 2>&1 &
server=$!
trap 'kill $server' EXIT
sleep 1

changed=()
for qmd in present/soft-matter_*.qmd; do
  deck=$(basename "$qmd" .qmd)
  name=${deck#soft-matter_}
  html=docs/$deck.html
  pdf=docs/pdfs/slides-$name.pdf

  # Only the qmd decides: full-site renders touch every html without changing content.
  # Git timestamps rather than mtimes, since checkouts/pulls touch mtimes.
  dirty=$(git status --porcelain -- "$qmd")
  src_t=$(last_commit "$qmd"); pdf_t=$(last_commit "$pdf")
  if [[ -z $dirty && -f $pdf && ${pdf_t:-0} -ge ${src_t:-0} ]]; then
    continue
  fi

  # Already rebuilt by an earlier, interrupted run: just carry it into the commit.
  if [[ -n $(git status --porcelain -- "$pdf") && $pdf -nt $qmd ]]; then
    echo ">> $name (PDF already up to date)"
    git add -- "$qmd" "$html" "$pdf"
    [[ -d docs/${deck}_files ]] && git add -- "docs/${deck}_files"
    changed+=("$name")
    continue
  fi

  echo ">> $name"
  (cd present && quarto render "$deck.qmd")
  # Pyodide and plotly come from CDNs; the default 20 s page load isn't always enough.
  decktape reveal --size 1600x900 --page-load-timeout 120000 "http://localhost:$port/$deck.html" "$pdf"
  git add -- "$qmd" "$html" "$pdf"
  [[ -d docs/${deck}_files ]] && git add -- "docs/${deck}_files"
  changed+=("$name")
done

if [[ ${#changed[@]} -eq 0 ]]; then
  echo "All PDFs up to date."
  exit 0
fi

git add -- docs/search.json docs/sitemap.xml present/styles.css docs/styles.css
git commit -m "${1:-Update slides and PDFs for ${changed[*]}}"
git push

# The site is served from the gh-pages branch, not from docs/ on main.
(cd present && quarto publish gh-pages --no-render --no-prompt)
