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
