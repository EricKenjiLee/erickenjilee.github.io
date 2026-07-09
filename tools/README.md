# tools/

Build scripts for the site. Currently just the publications-page generator.

## `build_pubs.py` → `publications.html`

Regenerates the whole Publications page (the interactive swim-lane plot,
the publications table, the invited-talks & conference-talks tables, the
per-year colour gradient, dark-mode CSS, and the hover/detail JS).

**Run it from the repo root:**

```bash
python3 tools/build_pubs.py
```

It overwrites `publications.html` in place. Python 3, standard library only
(no dependencies).

### Inputs
- `tools/kenji_lee_trajectory_figure.html` — the source swim-lane figure
  (the `<svg>` timeline plot + the original talks table). The desktop plot is
  lifted from here; a transposed vertical version is generated for mobile.
- `publications.html` (the existing page) — only its `<header>` nav and
  `<footer>` are lifted, so the page keeps the same chrome as the rest of the
  site. Regeneration is therefore idempotent.

### Where the content lives (edit these in `build_pubs.py`)
- `PUBS_DATA` — the publications table rows (year, title, venue, role, stream).
- `INVITED` — the "Invited talks & seminars" rows (year, host, institution, format).
- `STREAMS` / `_stream()` — stream tags, incl. the split `Cell types × …` chips.
- `YEAR_COLORS` / `_year_ramp()` — the constant-luminance per-year colour ramp.
- Conference talks come from the figure file and are filtered inline.

After editing, re-run the command above and commit the regenerated
`publications.html` together with your change.
