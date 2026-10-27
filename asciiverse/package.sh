#!/bin/sh
# Packs each game built by build.sh into its own archive for av:
# dist/<id>-<target>.tar.gz, or .zip for Windows, with the binary at the
# top, the game's man page where it has one, and the collection's licenses
# (CC0 and Apache-2.0, either applies) and README.
#
#   asciiverse/package.sh x86_64-unknown-linux-musl
set -eu
cd "$(dirname "$0")/.."
target="$1"
case "$target" in *windows*) exe=.exe ;; *) exe= ;; esac
mkdir -p dist
grep -v '^#' asciiverse/games.txt | while read -r id bin name; do
  name="${name:-$bin}"
  [ -n "$id" ] || continue
  stage="stage/$id"
  rm -rf "$stage" && mkdir -p "$stage"
  cp "out/$name$exe" LICENSE APACHE README.md "$stage/"
  [ -f "src/man/$bin.6" ] && cp "src/man/$bin.6" "$stage/"
  if [ -n "$exe" ]; then
    (cd "$stage" && zip -qr "../../dist/$id-$target.zip" .)
  else
    tar -czf "dist/$id-$target.tar.gz" -C "$stage" .
  fi
done
ls dist
