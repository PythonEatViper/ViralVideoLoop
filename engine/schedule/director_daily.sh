#!/bin/sh
# The director's unattended daily run. Started by launchd (see `./vvl schedule install`),
# or by hand / by the secretary: sh engine/schedule/director_daily.sh
# It may read and write files in this repo and run ./vvl. It cannot spend credits or publish.
export PATH="/usr/local/bin:/opt/homebrew/bin:/opt/miniconda3/bin:/usr/bin:/bin"
cd "$(dirname "$0")/../.." || exit 1
echo "=== director run $(date '+%Y-%m-%d %H:%M') ==="
./vvl ingest
./vvl prompt director | claude -p "Do your daily run now, following the role description on stdin. Today is $(date '+%A %Y-%m-%d')." \
  --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Bash(./vvl:*)" "Bash(ls:*)" "Bash(cat:*)" "Bash(date:*)" \
  --max-turns 60
./vvl build
