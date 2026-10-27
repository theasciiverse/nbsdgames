#!/bin/sh
# Builds every game in asciiverse/games.txt into out/. The compiler and
# curses library come from the environment, so one script serves every
# target (see .github/workflows/release.yml):
#
#   CC=cc LIBS="-lncurses -lm" asciiverse/build.sh                    # macOS
#   LDFLAGS="-static -s" asciiverse/build.sh                          # Alpine
#   CC=x86_64-w64-mingw32-gcc CFLAGS="-O2 -I$PDC" \
#     LIBS="$PDC/wincon/pdcurses.a -lm" LDFLAGS="-static -s" EXE=.exe asciiverse/build.sh
set -eu
cd "$(dirname "$0")/.."
CC="${CC:-cc}"
CFLAGS="${CFLAGS:--O2}"
LDFLAGS="${LDFLAGS:-}"
LIBS="${LIBS:--lncurses -lm}"
EXE="${EXE:-}"
mkdir -p out
grep -v '^#' asciiverse/games.txt | while read -r id bin name; do
  name="${name:-$bin}"
  [ -n "$id" ] || continue
  # scores go to /var/games when it is writable, else to ~/.<game>_scores
  $CC $CFLAGS -Wno-unused-result -DSCORES_DIR='"/var/games"' "src/$bin.c" $LDFLAGS $LIBS -o "out/$name$EXE"
  echo "built $name$EXE"
done
