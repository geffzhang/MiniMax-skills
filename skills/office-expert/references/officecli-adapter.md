# OfficeCLI Adapter

This reference defines how `office-expert` and the MiniMax Office skills use OfficeCLI and the OfficeCLI skill system.

## Installation model

OfficeCLI is external. This repository does not vendor OfficeCLI source code and does not package OfficeCLI binaries.

Before choosing an OfficeCLI route, run:

```bash
python skills/office-expert/scripts/officecli_doctor.py --json
```

The command path is resolved in this order:

1. `OFFICECLI_COMMAND`
2. `officecli` on `PATH`

If the doctor reports `available: false`, explain the reason and continue with the MiniMax specialist workflow when the requested task can still be completed.

## Help-first rule

OfficeCLI command help is authoritative for the installed version.

Use these commands before guessing command names, enum values, or property names:

```bash
officecli --version
officecli help
officecli help docx --json
officecli help pptx --json
officecli help xlsx --json
```

When a local OfficeCLI skill note and installed command help disagree, command help wins.

## Core skill mapping

| OfficeCLI skill | MiniMax route | Use for |
|---|---|---|
| `officecli` | `office-expert` | Shared command discipline, help-first, schema-first, quoting, incremental execution |
| `officecli-docx` | `minimax-docx` | Standard DOCX read, convert, inspect, simple write workflows |
| `officecli-pptx` | `pptx-generator` | Standard PPTX creation, inspection, mutation, delivery gates |
| `officecli-xlsx` | `minimax-xlsx` | Standard XLSX read, inspect, formula-aware workbook workflows |

## Scene skill mapping

| OfficeCLI scene skill | MiniMax route | Routing signal |
|---|---|---|
| `officecli-academic-paper` | `minimax-docx` | academic paper, citations, equations, cross references, thesis, journal paper |
| `officecli-word-form` | `minimax-docx` | fillable Word form, content controls, protected form, form fields |
| `officecli-data-dashboard` | `minimax-xlsx` | KPI dashboard, dashboard workbook, charts, metrics view |
| `officecli-financial-model` | `minimax-xlsx` | DCF, LBO, assumptions, financial model, forecast model |
| `officecli-pitch-deck` | `pptx-generator` | pitch deck, investor deck, fundraising deck, startup deck |
| `morph-ppt` | `pptx-generator` | morph, smooth cross-slide motion, shape continuity, Keynote-style transition |
| `morph-ppt-3d` | `pptx-generator` | 3D morph deck, GLB model, cinematic camera, model-content layout |

## OfficeCLI preferred cases

Prefer OfficeCLI when all of these are true:

1. The doctor reports OfficeCLI is available.
2. The task is a standard Office operation that the installed command help exposes.
3. The user does not require MiniMax visual design, OpenXML deep repair, PptxGenJS custom generation, or PDF design identity.
4. Output can be verified by reading, inspecting, or validating the generated file.

## MiniMax preferred cases

Prefer MiniMax specialist workflows for:

- DOCX OpenXML structure, custom styles, template application, comments, revisions, XSD validation.
- XLSX zero-format-loss XML edits, formulas, financial formatting, workbook repair.
- PPTX original deck creation, visual variety, slide-level design, PptxGenJS code generation.
- PDF visual identity, cover design, form filling, document reformatting.
- Any case where OfficeCLI is unavailable, fails, or produces output that cannot be verified.

## Workflow discipline to inherit from OfficeCLI skills

- Ask OfficeCLI help before guessing command flags.
- Prefer machine-readable help when available.
- Use single-quoted shell values for `$`, `!!`, `#`, and JSON bodies.
- Use heredocs for multi-operation batches.
- Mutate incrementally and verify after every write.
- Attribute failures as agent error, renderer limitation, command limitation, or skill gap.
- Never overwrite the original user file by default.

## Morph PPT rules to inherit

Use these only when the user asks for smooth cross-slide motion.

- Match shapes across adjacent slides with identical names.
- Use `!!scene-*` for persistent scene actors.
- Use `!!actor-*` for foreground actors that evolve across slides.
- Use `#sN-*` for per-slide content.
- Move exiting actors off-canvas instead of deleting them.
- Apply `transition=morph` to slides that should animate from the previous slide.
- Verify visible motion by checking shape names and reviewing generated slides in a Morph-capable viewer.
- Warn that LibreOffice and many web viewers may render Morph as a fade.

## 3D Morph rules to inherit

Use these only when the user asks for GLB or 3D model content.

- Check that the user supplied a `.glb` model or explicitly wants help finding one.
- Keep the 3D model and text layout from fighting for the same focal area.
- Use camera and model positioning as part of the narrative plan.
- Verify the deck in PowerPoint 365, Keynote, WPS, or another viewer that supports the target 3D features.
