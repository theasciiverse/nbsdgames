# Changes from upstream

This is the Asciiverse packaging of New BSD Games by abakh and contributors
(CC0, public domain), from [abakh/nbsdgames](https://github.com/abakh/nbsdgames),
the `upstream` remote. The `asciiverse` branch starts from upstream's tag
v6.0.3 (2026-10-05), its newest commit at the time.

In the Asciiverse catalog each game is its own title, credited as part of
New BSD Games. The `nbsdgames` menu is not built: av is the menu.

## Code

- **Scores on Windows.** When the system score folder (`/var/games`) cannot
  be written, the games keep scores in `~/.<game>_scores`. Windows has no
  `HOME`, so that path was built from a null pointer; it now falls back to
  `USERPROFILE`.

- **Centred in the terminal.** The games draw from the top left corner, so
  on a big terminal the board sat in a corner. `src/centre.h`, included from
  `common.h`, swaps `stdscr` for a pad when curses starts, so the games draw
  exactly as before; `refresh()` and `getch()` then show the drawn area of the
  current screen centred, a resized terminal re-centres it (the games never
  see `KEY_RESIZE`), and mouse positions are translated back. The area grows
  while the game keeps drawing over it, so the board does not jump about, and
  starts over when the game moves to another screen (from a question to the
  board, or to a help page). A terminal smaller than the game shows its top
  left part, as before. Two games needed a line or two: `jewels` laid itself
  out from the terminal size (board centred by `COLS`, keys on the bottom
  line) and now has a fixed layout; `sjump` draws its next squares past its
  80x24 field, so it caps the measured area at the field.

## Packaging (new files)

- `asciiverse/games.txt`: the catalog id and binary of each of the 22
  games. `sos` is published as `nbsd-sos`, because `sos` is also Red Hat's
  system report tool and av links each title into `~/.local/bin` by id.
- `asciiverse/build.sh`: builds every game into `out/` with the compiler and
  curses library given in the environment.
- `asciiverse/package.sh`: one archive per game and target in `dist/`, the
  binary at the top beside its man page, LICENSE and README.md.
- `.github/workflows/release.yml`: static Linux builds in Alpine (x86_64,
  aarch64), macOS (x86_64, arm64) and Windows x86_64 cross-built with MinGW
  against PDCurses 3.9, plus SHA256SUMS, on a tag.

## Not built

- System packages: New BSD Games is already packaged by Debian, Fedora,
  openSUSE, Alpine, Arch (AUR), the BSDs and Homebrew
  (https://repology.org/project/nbsdgames/versions).
