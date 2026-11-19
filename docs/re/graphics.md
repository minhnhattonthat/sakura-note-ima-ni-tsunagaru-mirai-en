# Graphics-text survey

Status: **incomplete** (phase 1 item still open).

## Seen on screen so far (original ROM, cold boot; shots in work/qa/explore1-2)
| screen | text | source guess |
|---|---|---|
| title | logo サクラノート + subtitle, two menu buttons (white on blue) | RGCN/RCSN graphics (not font) |
| file select | three slot banners (pink header label on each slot), はじめから / つづきからはじめる popup | slot label graphic; popup labels may be font text (arm9 0x0927A4 はじめから) |
| name entry | "NAME ENTRY" bar, tab bar `L <あいう アイウ abc> R`, BackSpace / Enter keys | graphics (Latin already); keyboard keys are font cells from table 2838 |

## To do (static sweep)
Render every RGCN (576 raw + 496 LZ10) with its following RLCN palette into numbered contact sheets with the
FILEDATA id, plus the 177 LZ10 "QQ" blocks (format unknown, first find out what they are), and list every cell with
Japanese here: id, screen, what it says. Then warp to chapter cards, game over, ending and credits in phase 2 and
add what the sweep missed.
