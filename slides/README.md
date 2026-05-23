# Marp Slides Template

> **This is a shared template repository — do not commit your presentation content here.**
> Create your own copy (see step 1) and work there. Changes pushed back to this repo affect everyone who uses it as a starting point.

A ready-to-use slide template built with [Marp](https://marp.app/) — write your presentation in plain Markdown or ask Claude to generate it and export to HTML, PDF, or PowerPoint.

---

## 1. Create your own copy

Click **"Use this template"** at the top of the GitLab page (or clone it):

```bash
git clone https://gitlab.com/graphaware/sandbox/marp-slides-template.git my-talk
cd my-talk
```

---

## 2. Install dependencies

Run the setup target — it checks whether Node.js is installed and installs it via [Homebrew](https://brew.sh/) if needed, then installs the project dependencies:

```bash
make setup
```

That's it — Marp CLI is installed locally, nothing global needed.

---

## 3. Authoring with Claude Code

If you use [Claude Code](https://claude.ai/code), run `/slides` at any time to load the full authoring rules and template reference.

### Generate slides from a braindump

Drop a Markdown file with rough notes into the `scratch/` folder, then ask Claude to generate slides from it:

```
/slides generate slides from my braindump
```

Claude will read your notes, structure them into slides, and write the result into `slides.md`. If `scratch/` contains multiple files it will ask which one to use.

Exclusion markers are respected — any content below a line like `!!!NOT USE BELOW CONTENT!!!` is ignored.

## 4. Edit your slides

Open `slides.md` in any text editor and start writing. Each slide is separated by `---`.

```markdown
---

# My slide title

- Bullet one
- Bullet two

---
```

Put images in the `assets/` folder and reference them as `![](assets/my-image.png)`.

---

## 5. Preview while you write

```bash
make watch    # opens in your browser, auto-refreshes on save
make preview  # presenter view (notes + timer)
```

---

## 6. Export your slides

```bash
make build    # HTML  → dist/slides.html
make pdf      # PDF   → dist/slides.pdf
make pptx     # PPTX  → dist/slides.pptx
```

Open the file in `dist/` to share or present.

---

## Slide layouts

Apply a layout to any slide by adding a comment right after the `---` separator:

```markdown
---

<!-- _class: cover -->

# Title slide

---

<!-- _class: img-left -->

![](assets/diagram.png)

- Point one
- Point two
```

| Class | Best for |
|---|---|
| `cover` | Title, section breaks, closing slide |
| `module` | Chapter / section header |
| `img-left` | Image on the left, bullets on the right |
| `img-right` | Bullets on the left, image on the right |
| `img-bottom` | Full-width image with a caption below |
| `exercise` | Exercise or lab slide |
| `quiz` | Quiz slide |
| `conc` | Conclusion slide |

Prebuilt snippets for each layout live in `templates/` — copy and paste freely.

---

## Customise the branding

All colours, fonts, and logos are in `theme/graphaware.css`. To use your own brand:

1. Open `theme/graphaware.css` and update the CSS variables at the top of the file (colours, font names).
2. Replace the logo files in `theme/` with your own (`logo.svg` and the PNG variant).
3. Update the `header:` line in `slides.md` to point to your new logo file.

---

## Project structure

```
slides.md          ← your presentation (edit this)
assets/            ← images used in slides
scratch/           ← braindump notes for Claude-assisted authoring
theme/             ← CSS theme and logo files
templates/         ← copy-paste layout snippets
dist/              ← build output (gitignored)
```

---

## Built with

- [Marp CLI](https://github.com/marp-team/marp-cli) — Markdown → HTML / PDF / PPTX
