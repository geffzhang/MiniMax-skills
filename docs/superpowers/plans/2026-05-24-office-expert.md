# Office Expert Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 MiniMax-skills 中新增 `office-expert` 聚合 skill，并把 OfficeCLI skills 的核心层、场景层、动效层规则内联融合到 MiniMax Office 工作流。

**Architecture:** 新增一个聚合 skill 负责 Office 任务路由，一个共享 adapter 文档集中维护 OfficeCLI 命令与 OfficeCLI skill 规则，一个 doctor 脚本检测外部 `officecli` 是否可用。现有 `minimax-docx`、`minimax-xlsx`、`pptx-generator`、`minimax-pdf` 只增加短的 fast path 引用，保留原专业流程。

**Tech Stack:** Markdown `SKILL.md`、Python 3 标准库、MiniMax skill validation script、现有 README/plugin metadata JSON。

---

## File Structure

Create:

- `skills/office-expert/SKILL.md` — Office 聚合入口，负责文件类型路由、场景路由、OfficeCLI fast path、MiniMax fallback。
- `skills/office-expert/references/officecli-adapter.md` — OfficeCLI 命令、OfficeCLI skills、MiniMax specialist skills 的共享融合规则。
- `skills/office-expert/scripts/officecli_doctor.py` — 检测 `OFFICECLI_COMMAND` 或 PATH 上的 `officecli`，支持人类可读输出和 `--json`。
- `skills/office-expert/scripts/test_officecli_doctor.py` — doctor 脚本的 stdlib unittest。
- `skills/office-expert/scripts/requirements.txt` — 空文件，满足仓库脚本目录约定。

Modify:

- `README.md` — 在技能表中新增 `office-expert`。
- `README_zh.md` — 在中文技能表中新增 `office-expert`。
- `.claude-plugin/plugin.json` — 增加 Office expert 搜索关键词。
- `.cursor-plugin/plugin.json` — 增加 Office expert 搜索关键词。
- `skills/minimax-docx/SKILL.md` — 增加 OfficeCLI fast path 引用。
- `skills/minimax-xlsx/SKILL.md` — 增加 OfficeCLI fast path 引用。
- `skills/pptx-generator/SKILL.md` — 增加 OfficeCLI fast path 引用。
- `skills/minimax-pdf/SKILL.md` — 增加 OfficeCLI fast path 引用。

Do not copy files from `E:\GitHub\OfficeCLI\skills` into MiniMax-skills.

---

### Task 1: Add doctor tests first

**Files:**
- Create: `skills/office-expert/scripts/test_officecli_doctor.py`
- Create: `skills/office-expert/scripts/requirements.txt`

- [ ] **Step 1: Create the script directory**

Run:

```bash
mkdir -p "skills/office-expert/scripts"
```

Expected: command exits `0`.

- [ ] **Step 2: Create empty requirements file**

Create `skills/office-expert/scripts/requirements.txt` with empty content.

- [ ] **Step 3: Write the failing doctor tests**

Create `skills/office-expert/scripts/test_officecli_doctor.py` with this exact content:

```python
#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("officecli_doctor.py")


class OfficeCliDoctorTests(unittest.TestCase):
    def run_doctor(self, env):
        merged_env = os.environ.copy()
        merged_env.update(env)
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=Path(__file__).parents[2],
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.stderr, "")
        return completed.returncode, json.loads(completed.stdout)

    def test_reports_unavailable_when_command_is_missing(self):
        code, payload = self.run_doctor({"OFFICECLI_COMMAND": "definitely-missing-officecli-command"})
        self.assertEqual(code, 1)
        self.assertFalse(payload["available"])
        self.assertEqual(payload["command"], "definitely-missing-officecli-command")
        self.assertIn("not found", payload["reason"])
        self.assertIn("Install OfficeCLI", payload["guidance"])

    def test_reports_available_for_configured_python_command(self):
        code, payload = self.run_doctor({"OFFICECLI_COMMAND": sys.executable})
        self.assertEqual(code, 0)
        self.assertTrue(payload["available"])
        self.assertEqual(payload["command"], sys.executable)
        self.assertTrue(payload["version"])
        self.assertEqual(payload["source"], "OFFICECLI_COMMAND")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run tests and verify they fail because implementation is missing**

Run:

```bash
python skills/office-expert/scripts/test_officecli_doctor.py
```

Expected: FAIL with a message that `officecli_doctor.py` cannot be opened or does not exist.

- [ ] **Step 5: Commit tests**

```bash
git add skills/office-expert/scripts/test_officecli_doctor.py skills/office-expert/scripts/requirements.txt
git commit -m "test: add officecli doctor tests"
```

Expected: new commit containing only the test file and empty requirements file.

---

### Task 2: Implement `officecli_doctor.py`

**Files:**
- Create: `skills/office-expert/scripts/officecli_doctor.py`
- Test: `skills/office-expert/scripts/test_officecli_doctor.py`

- [ ] **Step 1: Write the doctor script**

Create `skills/office-expert/scripts/officecli_doctor.py` with this exact content:

```python
#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

DEFAULT_GUIDANCE = (
    "Install OfficeCLI and ensure it is on PATH, or set OFFICECLI_COMMAND "
    "to the absolute path of the officecli executable."
)


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def configured_command():
    configured = os.getenv("OFFICECLI_COMMAND", "").strip()
    if configured:
        return configured, "OFFICECLI_COMMAND"
    return "officecli", "PATH"


def resolve_command(command, source):
    if os.path.isabs(command) or os.sep in command or (os.altsep and os.altsep in command):
        return command if os.path.exists(command) else None
    resolved = shutil.which(command)
    if resolved:
        return resolved
    if source == "OFFICECLI_COMMAND":
        return None
    return None


def read_version(executable):
    attempts = ([executable, "--version"], [executable, "version"])
    last_error = ""
    for args in attempts:
        completed = subprocess.run(
            args,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        combined = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
        if completed.returncode == 0 and combined:
            return combined.splitlines()[0]
        last_error = combined or f"exit code {completed.returncode}"
    raise RuntimeError(last_error or "version command produced no output")


def build_status():
    command, source = configured_command()
    resolved = resolve_command(command, source)
    base = {
        "checkedAt": utc_now(),
        "command": command,
        "resolvedCommand": resolved,
        "source": source,
        "guidance": DEFAULT_GUIDANCE,
    }

    if not resolved:
        base.update(
            {
                "available": False,
                "version": None,
                "reason": f"command not found: {command}",
            }
        )
        return base

    try:
        version = read_version(resolved)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        base.update(
            {
                "available": False,
                "version": None,
                "reason": f"version check failed: {exc}",
            }
        )
        return base

    base.update(
        {
            "available": True,
            "version": version,
            "reason": "ok",
        }
    )
    return base


def print_text(status):
    if status["available"]:
        print("OfficeCLI: available")
        print(f"Command: {status['command']}")
        print(f"Resolved: {status['resolvedCommand']}")
        print(f"Version: {status['version']}")
    else:
        print("OfficeCLI: unavailable")
        print(f"Command: {status['command']}")
        print(f"Reason: {status['reason']}")
        print(status["guidance"])


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check whether OfficeCLI is available for office-expert.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    status = build_status()
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_text(status)
    return 0 if status["available"] else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run doctor tests and verify they pass**

Run:

```bash
python skills/office-expert/scripts/test_officecli_doctor.py
```

Expected: `OK`.

- [ ] **Step 3: Run unavailable JSON check**

Run:

```bash
OFFICECLI_COMMAND=definitely-missing-officecli-command python skills/office-expert/scripts/officecli_doctor.py --json
```

Expected: exit code `1`; JSON contains `"available": false` and `"reason": "command not found: definitely-missing-officecli-command"`.

- [ ] **Step 4: Run available JSON check using Python as stand-in command**

Run:

```bash
OFFICECLI_COMMAND="$(command -v python)" python skills/office-expert/scripts/officecli_doctor.py --json
```

Expected: exit code `0`; JSON contains `"available": true`, `"source": "OFFICECLI_COMMAND"`, and a non-empty `version`.

- [ ] **Step 5: Commit doctor implementation**

```bash
git add skills/office-expert/scripts/officecli_doctor.py
git commit -m "feat: add officecli doctor"
```

Expected: new commit containing only `officecli_doctor.py`.

---

### Task 3: Add shared OfficeCLI adapter reference

**Files:**
- Create: `skills/office-expert/references/officecli-adapter.md`

- [ ] **Step 1: Create references directory**

Run:

```bash
mkdir -p "skills/office-expert/references"
```

Expected: command exits `0`.

- [ ] **Step 2: Write adapter reference**

Create `skills/office-expert/references/officecli-adapter.md` with this exact content:

```markdown
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
```

- [ ] **Step 3: Commit adapter reference**

```bash
git add skills/office-expert/references/officecli-adapter.md
git commit -m "docs: add officecli adapter reference"
```

Expected: new commit containing only the adapter reference.

---

### Task 4: Add `office-expert` aggregate skill

**Files:**
- Create: `skills/office-expert/SKILL.md`
- Reference: `skills/office-expert/references/officecli-adapter.md`

- [ ] **Step 1: Write `office-expert` skill**

Create `skills/office-expert/SKILL.md` with this exact content:

```markdown
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
```

- [ ] **Step 2: Validate the new skill directory only**

Run:

```bash
python .claude/skills/pr-review/scripts/validate_skills.py --path skills/office-expert
```

Expected: `Validation PASSED.` with zero errors.

- [ ] **Step 3: Commit aggregate skill**

```bash
git add skills/office-expert/SKILL.md
git commit -m "feat: add office expert skill"
```

Expected: new commit containing only `SKILL.md`.

---

### Task 5: Add OfficeCLI fast path to existing Office skills

**Files:**
- Modify: `skills/minimax-docx/SKILL.md`
- Modify: `skills/minimax-xlsx/SKILL.md`
- Modify: `skills/pptx-generator/SKILL.md`
- Modify: `skills/minimax-pdf/SKILL.md`

- [ ] **Step 1: Update `minimax-docx` after the overview line**

In `skills/minimax-docx/SKILL.md`, after line containing:

```markdown
Create, edit, and format DOCX documents via CLI tools or direct C# scripts built on OpenXML SDK (.NET).
```

Insert:

```markdown

## OfficeCLI fast path

If the task is a standard Word read, inspect, convert, or simple mutation workflow, first read `../office-expert/references/officecli-adapter.md` and run:

```bash
python ../office-expert/scripts/officecli_doctor.py --json
```

Use OfficeCLI only when the doctor reports it is available and installed command help exposes the needed operation. Keep this skill's OpenXML SDK workflow for academic papers, Word forms, custom styles, comments, revisions, template application, XSD validation, and any case that needs precise DOCX structure control.
```

- [ ] **Step 2: Update `minimax-xlsx` after the direct handling line**

In `skills/minimax-xlsx/SKILL.md`, after line containing:

```markdown
Handle the request directly. Do NOT spawn sub-agents. Always write the output file the user requests.
```

Insert:

```markdown

## OfficeCLI fast path

If the task is a standard Excel read, inspect, convert, or simple workbook mutation workflow, first read `../office-expert/references/officecli-adapter.md` and run:

```bash
python ../office-expert/scripts/officecli_doctor.py --json
```

Use OfficeCLI only when the doctor reports it is available and installed command help exposes the needed operation. Keep this skill's XML workflow for formulas, zero-format-loss edits, financial models, dashboards, formula validation, workbook repair, and professional formatting.
```

- [ ] **Step 3: Update `pptx-generator` after the overview paragraph**

In `skills/pptx-generator/SKILL.md`, after line containing:

```markdown
This skill handles all PowerPoint tasks: reading/analyzing existing presentations, editing template-based decks via XML manipulation, and creating presentations from scratch using PptxGenJS. It includes a complete design system (color palettes, fonts, style recipes) and detailed guidance for every slide type.
```

Insert:

```markdown

## OfficeCLI fast path

If the task is a standard PowerPoint read, inspect, convert, or simple deck mutation workflow, first read `../office-expert/references/officecli-adapter.md` and run:

```bash
python ../office-expert/scripts/officecli_doctor.py --json
```

Use OfficeCLI only when the doctor reports it is available and installed command help exposes the needed operation. Keep this skill's PptxGenJS workflow for original deck design, pitch decks, Morph animation decks, 3D Morph decks, visual variety, slide composition, and text-based QA.
```

- [ ] **Step 4: Update `minimax-pdf` after the title block**

In `skills/minimax-pdf/SKILL.md`, after line containing:

```markdown
Three tasks. One skill.
```

Insert:

```markdown

## OfficeCLI fast path

If the task is a standard PDF extraction or Office-to-PDF conversion workflow, first read `../office-expert/references/officecli-adapter.md` and run:

```bash
python ../office-expert/scripts/officecli_doctor.py --json
```

Use OfficeCLI only when the doctor reports it is available and installed command help exposes the needed operation. Keep this skill's visual PDF workflow for cover design, print-ready layout, PDF form filling, document reformatting, typography, and color identity.
```

- [ ] **Step 5: Verify references are present**

Run:

```bash
python - <<'PY'
from pathlib import Path
files = [
    Path('skills/minimax-docx/SKILL.md'),
    Path('skills/minimax-xlsx/SKILL.md'),
    Path('skills/pptx-generator/SKILL.md'),
    Path('skills/minimax-pdf/SKILL.md'),
]
for path in files:
    text = path.read_text(encoding='utf-8')
    assert '../office-expert/references/officecli-adapter.md' in text, path
    assert '../office-expert/scripts/officecli_doctor.py' in text, path
print('officecli fast path references ok')
PY
```

Expected: `officecli fast path references ok`.

- [ ] **Step 6: Commit existing skill updates**

```bash
git add skills/minimax-docx/SKILL.md skills/minimax-xlsx/SKILL.md skills/pptx-generator/SKILL.md skills/minimax-pdf/SKILL.md
git commit -m "feat: connect office skills to officecli adapter"
```

Expected: new commit containing only the four existing skill files.

---

### Task 6: Update README entries and plugin keywords

**Files:**
- Modify: `README.md`
- Modify: `README_zh.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.cursor-plugin/plugin.json`

- [ ] **Step 1: Add English README row**

In `README.md`, insert this row immediately before the `minimax-pdf` row:

```markdown
| `office-expert` | Unified Office expert combining OfficeCLI skill workflows with MiniMax DOCX, XLSX, PPTX, and PDF specialist skills. Routes Word, Excel, PowerPoint, PDF, academic papers, Word forms, dashboards, financial models, pitch decks, Morph decks, and 3D Morph decks. | Official |
```

- [ ] **Step 2: Add Chinese README row**

In `README_zh.md`, insert this row immediately before the `minimax-pdf` row:

```markdown
| `office-expert` | 统一 Office 专家，融合 OfficeCLI skills 工作流与 MiniMax DOCX、XLSX、PPTX、PDF 专业技能。路由 Word、Excel、PowerPoint、PDF、学术论文、Word 表单、仪表盘、财务模型、融资路演、Morph 动效和 3D Morph 演示。 | Official |
```

- [ ] **Step 3: Update `.claude-plugin/plugin.json` keywords**

Replace the existing `keywords` array with:

```json
["skills", "frontend", "fullstack", "android", "ios", "shader", "gif", "sticker", "office", "officecli", "word", "docx", "document", "excel", "xlsx", "spreadsheet", "financial-model", "dashboard", "powerpoint", "ppt", "pptx", "presentation", "pitch-deck", "morph", "pdf", "multimodal", "video", "image", "audio", "music", "minimax"]
```

- [ ] **Step 4: Update `.cursor-plugin/plugin.json` keywords**

Replace the existing `keywords` array with the same array:

```json
["skills", "frontend", "fullstack", "android", "ios", "shader", "gif", "sticker", "office", "officecli", "word", "docx", "document", "excel", "xlsx", "spreadsheet", "financial-model", "dashboard", "powerpoint", "ppt", "pptx", "presentation", "pitch-deck", "morph", "pdf", "multimodal", "video", "image", "audio", "music", "minimax"]
```

- [ ] **Step 5: Verify JSON files parse**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
for path in [Path('.claude-plugin/plugin.json'), Path('.cursor-plugin/plugin.json')]:
    data = json.loads(path.read_text(encoding='utf-8'))
    assert 'office' in data['keywords'], path
    assert 'officecli' in data['keywords'], path
    assert 'morph' in data['keywords'], path
print('plugin metadata ok')
PY
```

Expected: `plugin metadata ok`.

- [ ] **Step 6: Commit README and metadata updates**

```bash
git add README.md README_zh.md .claude-plugin/plugin.json .cursor-plugin/plugin.json
git commit -m "docs: list office expert skill"
```

Expected: new commit containing only README and metadata files.

---

### Task 7: Run repository validation

**Files:**
- Validate: all skill files under `skills/`
- Validate: doctor tests
- Validate: plugin JSON

- [ ] **Step 1: Run doctor tests**

Run:

```bash
python skills/office-expert/scripts/test_officecli_doctor.py
```

Expected: `OK`.

- [ ] **Step 2: Run full skill validation**

Run:

```bash
python .claude/skills/pr-review/scripts/validate_skills.py
```

Expected: `Validation PASSED.` with zero errors. Warnings only pass if they are existing warnings unrelated to `office-expert`; record them in the final report.

- [ ] **Step 3: Run README/metadata consistency check**

Run:

```bash
python - <<'PY'
from pathlib import Path
readme = Path('README.md').read_text(encoding='utf-8')
readme_zh = Path('README_zh.md').read_text(encoding='utf-8')
skill = Path('skills/office-expert/SKILL.md').read_text(encoding='utf-8')
adapter = Path('skills/office-expert/references/officecli-adapter.md').read_text(encoding='utf-8')
assert '| `office-expert` |' in readme
assert '| `office-expert` |' in readme_zh
for token in ['officecli-academic-paper', 'officecli-word-form', 'officecli-data-dashboard', 'officecli-financial-model', 'officecli-pitch-deck', 'morph-ppt', 'morph-ppt-3d']:
    assert token in adapter, token
for token in ['minimax-docx', 'minimax-xlsx', 'pptx-generator', 'minimax-pdf']:
    assert token in skill, token
print('office expert consistency ok')
PY
```

Expected: `office expert consistency ok`.

- [ ] **Step 4: Verify validation did not leave unstaged edits**

Run:

```bash
git diff --exit-code -- skills/office-expert README.md README_zh.md .claude-plugin/plugin.json .cursor-plugin/plugin.json skills/minimax-docx/SKILL.md skills/minimax-xlsx/SKILL.md skills/pptx-generator/SKILL.md skills/minimax-pdf/SKILL.md
```

Expected: exit code `0` and no diff output. If this command prints a diff, return to the task that owns the changed file, make the exact correction there, rerun its verification, and commit that task before continuing.

---

### Task 8: Final review and handoff

**Files:**
- Review: `docs/superpowers/specs/2026-05-24-office-expert-design.md`
- Review: all files changed by Tasks 1–7

- [ ] **Step 1: Review changed files**

Run:

```bash
git status --short && git log --oneline -8
```

Expected: working tree contains no unexpected modified files from implementation tasks.

- [ ] **Step 2: Confirm spec coverage**

Run:

```bash
python - <<'PY'
from pathlib import Path
required = {
    'skills/office-expert/SKILL.md': ['academic paper', 'word form', 'data dashboard', 'financial model', 'pitch deck', 'Morph', '3D Morph'],
    'skills/office-expert/references/officecli-adapter.md': ['officecli-docx', 'officecli-pptx', 'officecli-xlsx', 'morph-ppt', 'morph-ppt-3d'],
    'skills/office-expert/scripts/officecli_doctor.py': ['OFFICECLI_COMMAND', '--json', 'available'],
}
for file_name, tokens in required.items():
    text = Path(file_name).read_text(encoding='utf-8')
    for token in tokens:
        assert token in text, f'{file_name} missing {token}'
print('spec coverage check ok')
PY
```

Expected: `spec coverage check ok`.

- [ ] **Step 3: Final report**

Report these items to the user:

- New `office-expert` skill path.
- New adapter reference path.
- New doctor script path.
- Validation commands run and their results.
- Whether OfficeCLI itself was installed on this machine and detected by doctor.
- Any pre-existing untracked files left untouched.
