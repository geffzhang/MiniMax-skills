---
name: office-expert
description: >
  Unified Office expert for Word, Excel, PowerPoint, PDF, and cross-format Office workflows.
  Use when the user asks to create, edit, analyze, convert, repair, beautify, or route any
  Office document task, including DOCX, XLSX, PPTX, PDF, academic papers, Word forms,
  dashboards, financial models, pitch decks, Morph animation decks, and 3D Morph decks.
  Combines OfficeCLI command workflows and OfficeCLI skill rules with MiniMax specialist
  skills: minimax-docx, minimax-xlsx, pptx-generator, and minimax-pdf.
license: MIT
metadata:
  version: "1.0"
  category: productivity
  sources:
    - OfficeCLI skills taxonomy
    - MiniMax DOCX/XLSX/PPTX/PDF skills
---

# Office Expert

Use this skill as the first stop for Office work. It routes tasks across OfficeCLI command workflows and MiniMax specialist skills.

## Required reference

Read `references/officecli-adapter.md` before choosing an OfficeCLI route.

Run this check when OfficeCLI might be useful:

```bash
python skills/office-expert/scripts/officecli_doctor.py --json
```

If OfficeCLI is unavailable, explain the reason and continue with the MiniMax specialist route when possible.

## Route by file type

| Input or output | Route |
|---|---|
| `.docx`, `.doc`, Word, report, contract, formal document | `minimax-docx` plus OfficeCLI DOCX workflow when available |
| `.xlsx`, `.xlsm`, `.csv`, `.tsv`, Excel, spreadsheet | `minimax-xlsx` plus OfficeCLI XLSX workflow when available |
| `.pptx`, `.ppt`, PowerPoint, deck, slides | `pptx-generator` plus OfficeCLI PPTX workflow when available |
| `.pdf`, PDF form, polished PDF, print-ready document | `minimax-pdf` plus OfficeCLI conversion or extraction when available |
| Multi-file or cross-format task | Use this skill to coordinate the pipeline, then delegate to specialists |

## Route by scene

| User asks for | Route |
|---|---|
| Academic paper, thesis, citations, equations, cross references | `minimax-docx` with OfficeCLI academic-paper rules |
| Fillable Word form, content controls, protected form | `minimax-docx` with OfficeCLI word-form rules |
| KPI dashboard, dashboard workbook, metric view | `minimax-xlsx` with OfficeCLI data-dashboard rules |
| DCF, LBO, forecast, assumptions, financial model | `minimax-xlsx` with OfficeCLI financial-model rules |
| Pitch deck, investor deck, fundraising deck | `pptx-generator` with OfficeCLI pitch-deck rules |
| Morph, smooth transition, cross-slide motion | `pptx-generator` with morph-ppt rules |
| GLB model, 3D Morph deck, cinematic model presentation | `pptx-generator` with morph-ppt-3d rules |

## OfficeCLI fast path

Use OfficeCLI first when all are true:

1. `officecli_doctor.py --json` reports `available: true`.
2. The installed OfficeCLI help exposes the needed operation.
3. The task is a standard Office read, inspect, convert, batch, or simple mutation workflow.
4. The output can be verified by reading, inspecting, or validating the generated file.

Always ask command help before guessing flags:

```bash
officecli help
officecli help docx --json
officecli help pptx --json
officecli help xlsx --json
```

## MiniMax specialist route

Use MiniMax specialist skills when the user needs:

- DOCX OpenXML precision, template formatting, comments, revisions, style systems, or XSD checks.
- XLSX formulas, zero-format-loss XML edits, financial formatting, formula validation, or workbook repair.
- PPTX visual design, slide variety, PptxGenJS generation, or custom deck composition.
- PDF cover design, token-based visual identity, form filling, or reformatting.
- Any output that OfficeCLI cannot produce or verify.

## Cross-format pipeline examples

- Excel to PPT: use OfficeCLI or `minimax-xlsx` to inspect data, then `pptx-generator` for slide design.
- DOCX to PDF: use OfficeCLI for standard conversion, then `minimax-pdf` if visual redesign is required.
- PDF to DOCX: use OfficeCLI extraction if available, then `minimax-docx` for structured reconstruction.
- Dashboard to pitch deck: use OfficeCLI dashboard rules to identify KPIs, then `pptx-generator` for investor-facing slides.

## Safety rules

- Never overwrite the original file by default.
- Write outputs to a new path.
- Verify every generated file before reporting completion.
- If OfficeCLI fails, do not blindly retry. Switch to the relevant MiniMax specialist route or ask the user when the requested result changes.
