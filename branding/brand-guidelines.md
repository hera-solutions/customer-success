# Hera Solutions Brand Guidelines

Source of truth for Hera Solutions brand colors and typography. Reference this file (rather than hard-coding values) when producing customer-facing reports, PDFs, slides, documents, or any other branded artifact.

## Logos

Logo files (horizontal and vertical lockups, dog mark, wordmark, "is here to help" graphic) live in [`branding/logos/`](logos/). See [`branding/logos/README.md`](logos/README.md) for per-file dimensions and which file to use for each deliverable (PDF cover, repeating header, email signature, KB banner, avatar, slide).

## Colors

### Primary palette

| Name | HEX | Notes |
| --- | --- | --- |
| Hera Blue | `#0067bc` | Primary brand blue. Matches the website. Use this value as the canonical Hera Blue, even if other materials (banners, exports) appear slightly off — those were one-off adjustments made under time pressure and should not be treated as the standard. |
| Hera Pink | `#f9d2d9` | Secondary brand color. |

### Working palette (PDF reports)

These additional values are used in generated reports and are documented in [`reporting/pdf-generation-process.md`](../reporting/pdf-generation-process.md). They are derivative shades or functional UI colors (status indicators, row backgrounds), not brand-defining colors. Hera Blue (`#0067bc`) and Hera Pink (`#f9d2d9`) above are the only colors that count as brand identity.

| Element | HEX |
| --- | --- |
| Hera Blue Dark (accent) | `#00509a` |
| Hera Blue Light (row highlight) | `#e8f2fb` |
| Flag Red (violations) | `#c0392b` |
| Flag Red Light | `#fdecea` |
| Amber (warning) | `#e67e22` |
| Amber Light | `#fef9f0` |
| Orange Light (Netradyne rows) | `#fff8f0` |
| Green (positive) | `#1a7a3c` |
| Green Light | `#edf7f1` |
| Grey Light (alt rows) | `#f7f8fa` |
| Grey Mid (grid lines) | `#e2e6ea` |
| Grey Dark (labels, footer) | `#6c757d` |
| Near Black (body text) | `#1c2b3a` |

## Typography

The Hera Solutions brand typeface is **Aglet Slab**. Font files are stored in [`branding/fonts/`](fonts/) and should be installed locally or embedded in generated artifacts (PDFs, slide decks) where licensing allows.

### Available weights and styles

| Weight | Upright file | Italic file |
| --- | --- | --- |
| Extra Light | `agletslab-extralight.otf` | `agletslab-extralightitalic.otf` |
| Light | `agletslab-light.otf` | `agletslab-lightitalic.otf` |
| Regular | `agletslab-regular.otf` | `agletslab-italic.otf` |
| Semibold | `agletslab-semibold.otf` | `agletslab-semibolditalic.otf` |
| Bold | `agletslab-bold.otf` | `agletslab-bolditalic.otf` |
| Black | `agletslab-black.otf` | `agletslab-blackitalic.otf` |
| Ultra | `agletslab-ultra.otf` | `agletslab-ultraitalic.otf` |

### Usage guidance

- **Headlines / display:** Aglet Slab Bold or Black.
- **Subheads:** Aglet Slab Semibold.
- **Body copy:** Aglet Slab Regular (with Italic for emphasis).
- **Small captions / footnotes:** Aglet Slab Light or Regular at reduced size.
- **Avoid Ultra and Extra Light at body sizes** — reserve them for display use where the weight contrast is intentional.

### Fallback

When Aglet Slab cannot be embedded or the rendering surface does not support custom fonts (e.g., plain-text email, certain web contexts), fall back to a system slab serif or, failing that, a clean sans-serif. Do not substitute a decorative or display font that would change the brand feel.
