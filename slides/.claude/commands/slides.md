# Slide authoring rules

Audience is developers — use precise technical language, avoid over-explaining basics, include concrete examples and commands where relevant.

- Keep slides concise — max ~5 bullets per slide, short punchy lines. Slides are read live, not as a document.
- Add slides freely when the topic warrants it — don't cram content onto a single slide.
- Never touch branding (theme CSS, logos, colors, header/footer) unless explicitly asked.
- Do not add video plan slides (`<!-- _class: video -->`) unless explicitly asked.

## Templates

Templates live in `templates/` — copy their structure into `slides.md`, never edit the template files themselves.

| File | Class | Use when |
|---|---|---|
| `cover.md` | `cover` | Title, section break, closing slides |
| `image-left-list-right.md` | `img-left` | Image illustrates the concept; bullets explain it |
| `image-right-list-left.md` | `img-right` | Bullets lead; image reinforces on the right |
| `full-slide-image-description-below.md` | `img-bottom` | A single visual deserves full-slide prominence |

**Proactively recommend images**: when adding or editing a slide that would benefit from a visual, suggest where to place it and what it should show. Use a `picsum.photos` placeholder until a real asset is provided:

```markdown
![Description](https://picsum.photos/seed/your-seed/600/800)
```

**Track missing images**: every placeholder image added must be recorded in `images-index.md`. Each entry must include the slide number and a clear description of what the real image should show:

```markdown
| Slide | Description |
|---|---|
| 5 | Architecture diagram showing the data pipeline |
```

## File structure

```
slides.md         # The presentation
assets/           # Images referenced from slides
scratch/          # Braindump notes — input for slide generation
theme/            # CSS theme + logos — do not edit unless asked
templates/        # Slide layout templates — copy structure, never modify
dist/             # Build output (gitignored)
```

For generating slides from braindump notes, run `/slides-from-notes`.
