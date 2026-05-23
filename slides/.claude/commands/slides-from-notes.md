# Generate slides from braindump notes

First load slide authoring rules: run `/slides`.

## Workflow

1. **Identify the source file**: check `$ARGUMENTS` for a filename hint.
   - If a specific file is clearly named, read `scratch/<file>`.
   - If the argument is vague or absent, list all `.md` files in `scratch/` (excluding `.gitkeep`) and ask the user which one to use. Do not guess if there are multiple files.
   - If `scratch/` contains exactly one `.md` file, use it without asking.

2. **Read the source file** and generate slides into `slides.md`, following all authoring rules from `/slides`.

3. **Braindump-specific rules**:
   - Respect explicit exclusion markers such as `!!!NOT USE BELOW CONTENT!!!` — do not generate slides from content below them.
   - Only include technical facts you are confident about. If unsure whether a behaviour is enabled by default, omit the clarification rather than guessing.
   - Derive a logical slide structure from the notes — group related ideas, add section breaks, and create a cover slide if one is missing.
   - Do not copy braindump prose verbatim; rewrite into concise slide bullets.
