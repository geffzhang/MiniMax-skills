# Office Expert Integration Design

## Goal

Build an Office expert experience in MiniMax-skills by combining OfficeCli with the existing MiniMax Office skills. The primary delivery target is MiniMax-skills, while OpenClaw.NET should be able to install, discover, inspect, and invoke the resulting skills through its existing skill/plugin compatibility surface.

The design uses OfficeCli as an externally installed shared backend. MiniMax-skills will not vendor OfficeCli source code, package OfficeCli binaries, or modify OpenClaw runtime code.

## Decisions

- Use OfficeCli as the unified fast-path backend for standard Office operations.
- Keep the existing MiniMax DOCX, XLSX, PPTX, and PDF skills as professional workflows and fallbacks.
- Add a new aggregate `office-expert` skill as the user-facing Office entrypoint.
- Also enhance the four existing Office skills so direct file-type routing still benefits from OfficeCli.
- Add a doctor script that detects OfficeCli availability and reports actionable status without installing anything.

## Architecture

### Aggregate skill

Add `skills/office-expert/SKILL.md` as the primary Office expert entrypoint. It should trigger on Office, Word, Excel, PowerPoint, PPT, PDF, DOCX, XLSX, spreadsheet, presentation, and related Chinese terms.

The aggregate skill is responsible for:

- Classifying the user request by file type and task intent.
- Running or recommending the OfficeCli doctor check before choosing an OfficeCli route.
- Choosing between OfficeCli and the relevant MiniMax skill.
- Delegating specialist work to `minimax-docx`, `minimax-xlsx`, `pptx-generator`, or `minimax-pdf`.
- Preserving source files by default and writing outputs to new files.

### Shared OfficeCli adapter reference

Add `skills/office-expert/references/officecli-adapter.md` as the single source of truth for OfficeCli integration rules.

It should document:

- External installation expectations.
- How to configure the command path, including an environment variable such as `OFFICECLI_COMMAND`.
- How to run the doctor script.
- When OfficeCli should be preferred.
- When MiniMax specialist skills should be preferred.
- Failure and fallback behavior.
- Output verification rules.

The four existing Office skills should link to this reference instead of duplicating command-level guidance.

### Existing skill enhancement

Update these skills with a small OfficeCli fast-path section:

- `skills/minimax-docx/SKILL.md`
- `skills/minimax-xlsx/SKILL.md`
- `skills/pptx-generator/SKILL.md`
- `skills/minimax-pdf/SKILL.md`

Each skill should keep its current specialist workflow. The OfficeCli section should only say when to use the shared adapter before falling back to the existing workflow.

## Routing Rules

### File type classification

- `.docx` and `.doc` route to Word handling.
- `.xlsx`, `.xlsm`, `.csv`, and `.tsv` route to Excel handling.
- `.pptx` and `.ppt` route to PowerPoint handling.
- `.pdf` routes to PDF handling.
- Multi-file or cross-format requests route through `office-expert` first.

### Task intent classification

The aggregate skill should classify requests into these intents:

- Read, summarize, or extract text.
- Convert file formats.
- Replace text or fill placeholders.
- Create a new file.
- Beautify, brand, or visually redesign a document.
- Validate, repair, or compare files.
- Generate across formats, such as Excel to PPT or DOCX to PDF.

### OfficeCli preferred cases

Prefer OfficeCli when the task is a standard Office operation that it can complete reliably:

- Reading document structure or metadata.
- Extracting text.
- Standard file conversion.
- Batch processing.
- Simple content replacement.
- Template filling where OfficeCli has direct support.
- Operations that do not require sophisticated visual design or deep OpenXML editing.

### MiniMax specialist preferred cases

Prefer the existing MiniMax skills when the task needs specialist behavior:

- High-quality visual design.
- PPT slide planning, visual variety, and PptxGenJS generation.
- PDF cover design, token-based design systems, form filling, or reformatting.
- XLSX formulas, professional financial formatting, formula validation, or zero-format-loss XML editing.
- DOCX OpenXML precision, style systems, comments, track changes, template styling, or XSD gate checks.
- Any case where OfficeCli is unavailable, fails, or produces unverifiable output.

### Fallback behavior

- If `officecli_doctor.py` fails, the skill should explain the OfficeCli issue and continue with the relevant MiniMax workflow when possible.
- If OfficeCli execution fails, do not blindly retry. Fall back to the specialist skill or ask the user if the failure affects the requested outcome.
- If output verification fails, treat the OfficeCli result as failed.
- Never overwrite the original user file by default.

### Cross-format workflows

For cross-format workflows, use OfficeCli for structured extraction or conversion and MiniMax skills for content reconstruction or design.

Examples:

- Excel to PPT: extract or analyze spreadsheet data first, then use `pptx-generator` for slide design.
- DOCX to PDF: use OfficeCli for conversion if available, then use `minimax-pdf` when visual redesign or reformatting is required.
- PDF to Word: use OfficeCli for extraction/conversion if supported, then use `minimax-docx` for structured DOCX reconstruction when needed.

## Files to Add

### `skills/office-expert/SKILL.md`

Main aggregate skill with frontmatter, trigger description, routing workflow, OfficeCli fast path, MiniMax fallback rules, and safety rule to preserve originals.

### `skills/office-expert/references/officecli-adapter.md`

Shared adapter reference used by the aggregate skill and by the four existing Office skills.

### `skills/office-expert/scripts/officecli_doctor.py`

Environment detection script.

Expected behavior:

- Check `OFFICECLI_COMMAND` first, then `officecli` on `PATH`.
- Attempt to run a version command.
- Print human-readable output by default.
- Support `--json` for machine-readable output.
- Return `0` when OfficeCli is usable.
- Return `1` when OfficeCli is unavailable or version detection fails.
- Do not install, download, or modify system state.

## Files to Modify

### `README.md`

Add `office-expert` to the skills table. Describe it as a unified Office expert that combines OfficeCli with MiniMax DOCX, XLSX, PPTX, and PDF skills.

### `README_zh.md`

Add the same skill entry in Chinese.

### `.claude-plugin/plugin.json`

Add Office expert keywords if the plugin metadata uses keyword discovery.

### `.cursor-plugin/plugin.json`

Add Office expert keywords if the plugin metadata uses keyword discovery.

### Existing Office skills

Add concise OfficeCli fast-path references to:

- `skills/minimax-docx/SKILL.md`
- `skills/minimax-xlsx/SKILL.md`
- `skills/pptx-generator/SKILL.md`
- `skills/minimax-pdf/SKILL.md`

The changes should not rewrite the existing specialist workflows.

## Verification

### Skill structure validation

Run the repository's skill validation script:

```bash
python .claude/skills/pr-review/scripts/validate_skills.py
```

Expected result: `office-expert` has valid frontmatter, a kebab-case directory, and no structural violations.

### Doctor validation

Without OfficeCli installed:

```bash
python skills/office-expert/scripts/officecli_doctor.py --json
```

Expected result: JSON reports `available: false`, includes a reason, and gives installation/configuration guidance.

With OfficeCli installed:

```bash
python skills/office-expert/scripts/officecli_doctor.py --json
```

Expected result: JSON reports `available: true`, the command path, and a version or version-check result.

### Documentation consistency

Check that:

- `README.md` and `README_zh.md` both list `office-expert`.
- All four existing Office skills reference the shared adapter.
- Routing rules in the aggregate skill do not contradict the specialist skills.

### OpenClaw compatibility

If OpenClaw CLI is available, run:

```bash
openclaw skills inspect ./skills/office-expert
```

If OpenClaw CLI is not available, rely on the standard `SKILL.md` structure validation and plugin metadata checks.

## Risks

### OfficeCli command interface may change

Keep command details centralized in the shared adapter reference so updates do not require editing multiple skills.

### OfficeCli capability boundaries may be incomplete

Treat OfficeCli as a standard Office operation backend, not as a replacement for MiniMax design and specialist document workflows.

### Platform differences

OfficeCli installation paths and dependencies may vary across Windows, macOS, and Linux. The doctor script should detect and report status only.

### Routing conflicts

`office-expert` should be the broad aggregate entrypoint. Existing file-specific skills should remain valid direct entrypoints. Shared adapter guidance keeps the rules aligned.

## Explicit Non-Goals

- Do not vendor OfficeCli source code into MiniMax-skills.
- Do not package OfficeCli binaries.
- Do not change OpenClaw.NET runtime code.
- Do not add an OpenClaw native plugin for this phase.
- Do not promise OfficeCli coverage for advanced Word, Excel, PowerPoint, or PDF scenarios.
- Do not overwrite original Office files by default.
