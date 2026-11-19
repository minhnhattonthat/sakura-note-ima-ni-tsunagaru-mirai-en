#!/bin/sh
# usage: review.sh FIRST LAST  (page numbers) -> work/sweep/review/rFIRST.tsv
cd /c/Users/nathan/Documents/translation/sakura-note-ima-ni-tsunagaru-mirai-en
mkdir -p work/sweep/review
args=""
names=""
i=$1
while [ $i -le $2 ]; do
  f=$(printf "work/sweep/p%03d.png" $i)
  [ -f "$f" ] && { args="$args -i $f"; names="$names $(basename $f)"; }
  i=$((i+1))
done
prompt="You are a read-only visual reviewer for a Japanese-to-English Nintendo DS fan translation. The attached images are, in order, the contact-sheet pages:$names. Each page holds many cells of game graphics; every cell has a small yellow label above it (a FILEDATA id such as '1139 tiles', '1139 scr1140', '2845#3' or '2842 raw'). Look closely at every cell, zooming mentally, and list EVERY cell that contains any readable text drawn as graphics: Japanese (kana, kanji, Japanese punctuation) and also Latin/English text (titles, buttons, labels). Ignore the yellow labels themselves. Output ONLY tab-separated lines, no prose, no markdown: page<TAB>cell label<TAB>language (JA or EN or MIXED)<TAB>the text as you read it<TAB>what it looks like (logo, menu button, header, sign, number, icon label, etc.). For a page with no text cell output one line: page<TAB>-<TAB>-<TAB>none<TAB>-. Do not run any commands or edit files."
codex exec --skip-git-repo-check -s read-only $args -o "work/sweep/review/r$(printf %03d $1).tsv" "$prompt" > "work/sweep/review/log$(printf %03d $1).txt" 2>&1
echo "done $1-$2 exit $?"
