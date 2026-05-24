# Office Expert 产品需求文档

**版本:** v1.0  
**日期:** 2026-05-24  
**所属项目:** MiniMax Skills  
**目标环境:** OpenClaw.NET、Claude Code、Cursor、Codex、OpenCode 等支持本地 skills 的 AI 编程工具

## 1. 背景

MiniMax-skills 已经具备多种 Office 相关专业能力，包括 DOCX、XLSX、PPTX 和 PDF 的创建、编辑、排版、验证与视觉设计。OfficeCLI 也提供了一套 Office 命令行能力和细分 skills，覆盖 Word、Excel、PowerPoint、论文、表单、仪表盘、财务模型、融资路演、Morph 动效和 3D Morph 演示等场景。

用户在 OpenClaw.NET 等 AI 编程环境中处理 Office 文件时，不希望先判断应该调用哪个底层 skill 或命令，而是希望通过一个统一入口完成任务理解、能力路由、文件处理、质量验证和失败回退。

因此，本需求定义一个统一的 Office 专家体验：以 MiniMax-skills 的 `office-expert` 作为主入口，融合 MiniMax Office specialist skills、OfficeCLI 可执行程序和 OfficeCLI 原生 skills，形成面向用户的一站式 Office 工作流。

## 2. 产品目标

### 2.1 核心目标

- 为 Office 文档任务提供统一入口 `office-expert`。
- 在 OpenClaw.NET 中支持同时安装 MiniMax-skills 和 OfficeCLI skills。
- 自动识别 Word、Excel、PowerPoint、PDF 和跨格式 Office 任务。
- 根据任务类型选择 OfficeCLI command workflow、OfficeCLI 原生 scene skills、MiniMax specialist skills 或组合路线。
- 在 OfficeCLI 不可用、失败或输出不可验证时，回退到 MiniMax 专业流程。
- 默认保护用户原文件，输出到新路径，并要求验证生成结果。

### 2.2 用户价值

- 降低用户选择 skill 的成本：用户只需描述 Office 任务。
- 提高 Office 任务成功率：标准操作走 OfficeCLI，复杂设计和结构化生成走 MiniMax specialist skills。
- 保留 OfficeCLI 原生 skills 的场景经验：论文、表单、仪表盘、财务模型、融资路演、Morph 和 3D Morph。
- 提供可诊断安装体验：通过 doctor 脚本明确 OfficeCLI 是否可用。
- 支持 OpenClaw.NET 的多 skills 源安装模型。

## 3. 目标用户

| 用户类型 | 需求 |
|---|---|
| AI 编程工具用户 | 在自然语言中创建、修改、转换、分析 Office 文档 |
| OpenClaw.NET 用户 | 在 OpenClaw.NET 中统一安装并调用 MiniMax 和 OfficeCLI skills |
| 文档生产用户 | 生成报告、合同、论文、表单、PDF、演示文稿 |
| 数据分析用户 | 从 Excel/CSV 生成仪表盘、财务模型、PPT 汇报 |
| 演示设计用户 | 创建 pitch deck、Morph 动效 PPT、3D 模型演示 |
| skill 维护者 | 在不 vendor OfficeCLI 的前提下维护清晰的 Office 能力边界 |

## 4. 用户问题

当前用户在 Office 任务中面临的问题：

1. Office 相关能力分散在多个 skills 中，入口不统一。
2. 用户需要理解 DOCX、XLSX、PPTX、PDF 的底层实现差异。
3. OfficeCLI 和 MiniMax-skills 各自有优势，但缺少统一路由。
4. OpenClaw.NET 场景下需要同时发现多个 skills 来源，但安装说明不够明确。
5. OfficeCLI 是否已安装、路径是否正确、版本是否可用，需要标准诊断方式。
6. 场景化任务，如财务模型、论文、Morph PPT，需要比文件类型更高层的意图识别。

## 5. 产品方案

### 5.1 总体方案

新增 `office-expert` 作为 Office 任务统一入口。该入口负责理解用户意图，并在以下能力之间路由：

- MiniMax specialist skills：
  - `minimax-docx`
  - `minimax-xlsx`
  - `pptx-generator`
  - `minimax-pdf`
- OfficeCLI command workflow：
  - 通过外部安装的 `officecli` 可执行程序执行标准 Office 操作。
- OfficeCLI native skills：
  - `officecli`
  - `officecli-docx`
  - `officecli-pptx`
  - `officecli-xlsx`
  - `officecli-academic-paper`
  - `officecli-word-form`
  - `officecli-data-dashboard`
  - `officecli-financial-model`
  - `officecli-pitch-deck`
  - `morph-ppt`
  - `morph-ppt-3d`

OpenClaw.NET 安装时应同时注册两个 skills 路径：

```text
/path/to/OfficeCLI/skills
/path/to/MiniMax-skills/skills
```

### 5.2 产品定位

`office-expert` 不是替代所有 Office skills 的单体实现，而是一个路由、协调和质量控制入口。

它负责回答：

- 这是 Word、Excel、PPT、PDF 还是跨格式任务？
- 这是标准命令行操作，还是需要复杂排版、公式、视觉设计或结构化生成？
- 是否应该优先使用 OfficeCLI？
- OfficeCLI 是否可用？
- 是否存在更合适的 OfficeCLI 原生 scene skill？
- 是否需要回退到 MiniMax specialist skill？
- 输出文件如何验证？

## 6. 功能需求

### 6.1 统一 Office 入口

**需求:** 当用户提出 Office 文档相关任务时，系统应优先使用 `office-expert` 作为入口。

**覆盖任务:**

- 创建 Office 文件
- 编辑 Office 文件
- 读取和摘要 Office 文件
- 格式转换
- 表格分析
- PPT 生成
- PDF 重排
- 模板填写
- 文档修复
- 跨格式生成
- 场景化 Office 任务

**验收标准:**

- `office-expert` frontmatter 描述覆盖 Word、Excel、PowerPoint、PDF 和跨格式 Office workflows。
- README skills 表中包含 `office-expert`。
- plugin metadata 包含 office、officecli、word、excel、ppt、pdf、morph 等关键词。

### 6.2 文件类型路由

**需求:** 系统应根据输入/输出文件类型选择合适路线。

| 文件类型 | 默认路线 |
|---|---|
| `.docx`, `.doc`, Word | `minimax-docx` + OfficeCLI DOCX workflow |
| `.xlsx`, `.xlsm`, `.csv`, `.tsv`, Excel | `minimax-xlsx` + OfficeCLI XLSX workflow |
| `.pptx`, `.ppt`, PowerPoint | `pptx-generator` + OfficeCLI PPTX workflow |
| `.pdf`, PDF | `minimax-pdf` + OfficeCLI conversion/extraction |
| 多文件或跨格式 | `office-expert` 协调整体 pipeline |

**验收标准:**

- `office-expert` 中存在 file type route table。
- 每条路线都明确对应 MiniMax specialist skill 和 OfficeCLI workflow。

### 6.3 场景化路由

**需求:** 系统应识别高层业务场景，而不是只依赖文件扩展名。

| 场景 | 路由策略 |
|---|---|
| 学术论文、毕业论文、引用、公式 | `minimax-docx` + OfficeCLI academic-paper rules |
| Word 表单、内容控件、受保护表单 | `minimax-docx` + OfficeCLI word-form rules |
| KPI 仪表盘、数据看板 | `minimax-xlsx` + OfficeCLI data-dashboard rules |
| DCF、LBO、预测、假设区、财务模型 | `minimax-xlsx` + OfficeCLI financial-model rules |
| 融资路演、投资人 deck | `pptx-generator` + OfficeCLI pitch-deck rules |
| Morph 动效、跨页连续动画 | `pptx-generator` + morph-ppt rules |
| GLB、3D Morph、模型镜头叙事 | `pptx-generator` + morph-ppt-3d rules |

**验收标准:**

- `officecli-adapter.md` 中保留 OfficeCLI scene skill mapping。
- `office-expert` 中保留 scene route table。
- 相关场景词能在描述中触发 `office-expert`。

### 6.4 OfficeCLI doctor 检测

**需求:** 在选择 OfficeCLI command workflow 前，应检测 OfficeCLI 是否可用。

**能力要求:**

- 支持默认检测 PATH 上的 `officecli`。
- 支持通过 `OFFICECLI_COMMAND` 指定可执行程序路径。
- 支持 `--json` 输出。
- 返回 OfficeCLI 可用状态、命令路径、版本、原因和安装建议。
- 不自动安装、不下载、不修改系统状态。

**验收标准:**

- 存在 `skills/office-expert/scripts/officecli_doctor.py`。
- 存在 `skills/office-expert/scripts/test_officecli_doctor.py`。
- doctor tests 通过。
- `validate_skills.py` 通过。

### 6.5 OfficeCLI fast path

**需求:** 对标准 Office 操作优先使用 OfficeCLI。

**OfficeCLI 优先条件:**

1. doctor 返回 `available: true`。
2. 已安装 OfficeCLI 的 help 暴露目标操作。
3. 任务属于标准读取、检查、转换、批处理或简单修改。
4. 输出可以被读取、检查或验证。

**验收标准:**

- `office-expert` 定义 OfficeCLI fast path 条件。
- `minimax-docx`、`minimax-xlsx`、`pptx-generator`、`minimax-pdf` 都引用 OfficeCLI fast path。
- `officecli-adapter.md` 要求 help-first，不猜命令参数。

### 6.6 MiniMax specialist fallback

**需求:** 对复杂生成、视觉设计、结构化修复和 OfficeCLI 失败场景，应使用 MiniMax specialist skills。

**MiniMax 优先条件:**

- DOCX 需要 OpenXML 精细结构、样式、批注、修订、模板应用或 XSD 检查。
- XLSX 需要公式、零格式损失编辑、财务格式、公式校验或 workbook repair。
- PPTX 需要原创视觉设计、多 slide 编排、PptxGenJS 生成或 Morph/3D 叙事。
- PDF 需要封面设计、视觉系统、表单填写或重排。
- OfficeCLI 不可用、失败或输出无法验证。

**验收标准:**

- `office-expert` 明确 MiniMax specialist route。
- 四个现有 Office specialist skills 保留原专业流程，不被 OfficeCLI fast path 覆盖。

### 6.7 OpenClaw.NET 安装体验

**需求:** 文档应明确 OpenClaw.NET 需要同时安装两个 skills 来源。

**安装模型:**

```bash
git clone https://github.com/iOfficeAI/OfficeCLI.git
git clone https://github.com/MiniMax-AI/skills.git
```

OpenClaw.NET 配置：

```text
/path/to/OfficeCLI/skills
/path/to/MiniMax-skills/skills
```

OfficeCLI command 检测：

```bash
cd /path/to/MiniMax-skills
python skills/office-expert/scripts/officecli_doctor.py --json
```

**验收标准:**

- README 和 README_zh 均包含 OpenClaw.NET 安装说明。
- `officecli-adapter.md` 中包含双 skills 路径安装模型。
- `office-expert` 中说明 OpenClaw.NET 注册双路径时应保留 OfficeCLI native skills 作为直接执行路径。

### 6.8 输出安全和验证

**需求:** Office 文件处理必须保护用户原文件，并验证输出结果。

**规则:**

- 默认不覆盖原文件。
- 输出到新路径。
- 每次写入后验证生成文件。
- OfficeCLI 失败时不盲目重试。
- 输出无法读取、文本抽取为空或校验失败时，视为失败。

**验收标准:**

- `office-expert` 和 `officecli-adapter.md` 均包含安全输出规则。
- 实际工作流在报告完成前要求验证生成文件。

## 7. 非功能需求

### 7.1 兼容性

- 不要求 OpenClaw.NET 修改 runtime。
- 不 vendor OfficeCLI 源码。
- 不打包 OfficeCLI 二进制。
- OfficeCLI skills 可通过独立 skills path 安装。
- MiniMax-skills 保持现有 skill 目录结构。

### 7.2 可维护性

- OfficeCLI 融合规则集中维护在 `officecli-adapter.md`。
- 四个 MiniMax Office specialist skills 只保留短 fast path 引用，避免重复维护命令规则。
- `office-expert` 负责高层路由，不复制所有 specialist skill 的实现细节。

### 7.3 可验证性

- 使用 `validate_skills.py` 进行结构校验。
- 使用 doctor unit tests 检查 OfficeCLI detection。
- 使用 README 和 adapter consistency checks 验证文档同步。

## 8. 用户旅程

### 8.1 安装旅程

1. 用户安装或 clone OfficeCLI。
2. 用户 clone MiniMax-skills。
3. 用户在 OpenClaw.NET 中注册 `OfficeCLI/skills`。
4. 用户在 OpenClaw.NET 中注册 `MiniMax-skills/skills`。
5. 用户运行 `officecli_doctor.py --json` 检查 OfficeCLI command 是否可用。
6. 用户开始通过自然语言提交 Office 任务。

### 8.2 使用旅程：Excel 到 PPT

1. 用户输入：“分析这个 Excel 文件，并生成一个汇报 PPT。”
2. `office-expert` 判断为跨格式任务。
3. 系统优先用 OfficeCLI 或 `minimax-xlsx` 读取和分析表格。
4. 系统将数据洞察交给 `pptx-generator` 生成演示稿。
5. 系统验证 PPT 文件可读并报告输出路径。

### 8.3 使用旅程：财务模型

1. 用户输入：“创建一个三年收入预测和 DCF 财务模型。”
2. `office-expert` 识别 financial model 场景。
3. 系统应用 OfficeCLI financial-model rules。
4. 执行层使用 `minimax-xlsx` 和 OfficeCLI XLSX workflow。
5. 系统验证公式、格式和 workbook 输出。

### 8.4 使用旅程：Morph 演示

1. 用户输入：“做一个有平滑 Morph 转场的产品演示 PPT。”
2. `office-expert` 识别 Morph 场景。
3. 系统应用 morph-ppt 的 shape naming、ghosting 和 transition rules。
4. 执行层使用 `pptx-generator` 生成 deck。
5. 系统提示用户使用支持 Morph 的 viewer 验证视觉效果。

## 9. 成功指标

| 指标 | 目标 |
|---|---|
| Office 任务入口清晰度 | 用户可通过 `office-expert` 发起主流 Office 任务 |
| 安装可诊断性 | doctor 能明确 OfficeCLI 可用/不可用及原因 |
| skill 结构合规 | `validate_skills.py` 全量通过 |
| 场景覆盖 | 覆盖论文、表单、仪表盘、财务模型、pitch deck、Morph、3D Morph |
| 回退能力 | OfficeCLI 不可用时仍可继续使用 MiniMax specialist route |
| 文档一致性 | README、README_zh、adapter、office-expert 安装模型一致 |

## 10. 范围边界

### 10.1 本期范围

- 新增 `office-expert` 聚合 skill。
- 新增 OfficeCLI adapter reference。
- 新增 OfficeCLI doctor detection script 和 tests。
- 增强四个 MiniMax Office specialist skills 的 OfficeCLI fast path。
- 更新 README、README_zh 和 plugin metadata。
- 明确 OpenClaw.NET 双 skills 路径安装模型。

### 10.2 非本期范围

- 不修改 OpenClaw.NET runtime。
- 不复制 OfficeCLI skills 到 MiniMax-skills。
- 不将 OfficeCLI 打包进 MiniMax-skills。
- 不自动安装 OfficeCLI。
- 不新增 `officecli-docx`、`officecli-pptx`、`officecli-xlsx` 等 MiniMax 独立 skill。
- 不保证 OfficeCLI 所有命令参数稳定，实际命令以已安装版本 help 为准。

## 11. 风险与应对

| 风险 | 影响 | 应对 |
|---|---|---|
| OfficeCLI 未安装或不在 PATH | fast path 不可用 | doctor 输出原因，回退 MiniMax specialist route |
| OfficeCLI skills 未在 OpenClaw.NET 注册 | 原生 scene skills 不能直接调用 | adapter 保留 inline rules，README 明确双路径安装 |
| OfficeCLI help 与本地规则不一致 | 命令失败或参数错误 | help-first，已安装命令 help 优先 |
| MiniMax 和 OfficeCLI 能力边界模糊 | 用户体验不稳定 | `office-expert` 统一路由，adapter 集中维护规则 |
| Morph/3D viewer 兼容性差 | 输出视觉效果不符合预期 | 要求在支持目标特性的 viewer 中验证 |
| 文档更新不同步 | 安装或使用路径混乱 | README、README_zh、adapter、skill 共同维护安装模型 |

## 12. 发布与验证计划

### 12.1 发布内容

- `skills/office-expert/SKILL.md`
- `skills/office-expert/references/officecli-adapter.md`
- `skills/office-expert/scripts/officecli_doctor.py`
- `skills/office-expert/scripts/test_officecli_doctor.py`
- `skills/office-expert/scripts/requirements.txt`
- `skills/minimax-docx/SKILL.md`
- `skills/minimax-xlsx/SKILL.md`
- `skills/pptx-generator/SKILL.md`
- `skills/minimax-pdf/SKILL.md`
- `README.md`
- `README_zh.md`
- `.claude-plugin/plugin.json`
- `.cursor-plugin/plugin.json`

### 12.2 验证命令

```bash
python skills/office-expert/scripts/test_officecli_doctor.py
python .claude/skills/pr-review/scripts/validate_skills.py
python skills/office-expert/scripts/officecli_doctor.py --json
```

### 12.3 验收结果

当前实现过程中已验证：

- doctor unit tests 通过。
- MiniMax skills 全量结构校验通过。
- OfficeCLI doctor 能检测到 PATH 上的 OfficeCLI。
- README、README_zh、office-expert、officecli-adapter 已补充 OpenClaw.NET 双 skills 路径安装模型。

## 13. 后续迭代建议

1. 在 OpenClaw.NET 文档中补充多 skills path 的 UI 配置截图或示例配置。
2. 为 `office-expert` 增加更多真实用户任务样例。
3. 建立 OfficeCLI help snapshot 测试，减少命令参数漂移风险。
4. 增加端到端样例：Excel → PPT、DOCX → PDF、financial model、Morph deck。
5. 根据实际用户反馈，优化 `office-expert` 的触发描述和路由优先级。
