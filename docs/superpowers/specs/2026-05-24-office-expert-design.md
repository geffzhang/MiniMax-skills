# Office 专家融合设计

## 目标

在 MiniMax-skills 中打造一个统一的 Office 专家体验，融合两套能力：

- MiniMax 现有 Office skills：`minimax-docx`、`minimax-xlsx`、`pptx-generator`、`minimax-pdf`。
- OfficeCLI 现有 skills：`officecli`、`officecli-docx`、`officecli-pptx`、`officecli-xlsx` 以及若干场景化 Office skills。

交付目标仍以 MiniMax-skills 为主。OpenClaw.NET 不需要改 runtime，只需要能通过现有 skill/plugin 兼容机制安装、发现、检查和调用融合后的 MiniMax skills。

本阶段不把 OfficeCLI 源码、二进制或 `E:\GitHub\OfficeCLI\skills` 目录整体搬进 MiniMax-skills。OfficeCLI 作为外部安装的命令工具存在，OfficeCLI skills 作为设计、路由、命令纪律和 QA gate 的参考体系被内联吸收。

## 已确认决策

- 新增 `office-expert` 作为统一 Office 聚合入口。
- `office-expert` 同时吸收 MiniMax Office skills 和 OfficeCLI skills 的路由规则。
- 不新增 `officecli-docx`、`officecli-pptx` 等独立 MiniMax skill，避免重复入口。
- 不 vendor OfficeCLI，不打包 OfficeCLI 二进制。
- 采用“外部安装 + doctor 检测”的方式发现 OfficeCLI。
- 保留 MiniMax 现有四个 Office skills 的专业能力，并给它们增加 OfficeCLI fast path 引用。
- OfficeCLI skills 采用“内联融合”：提炼触发词、场景层、命令工作流、验证门禁和设计规则，不复制整份 skill 目录。

## OfficeCLI skill 体系映射

`E:\GitHub\OfficeCLI\skills` 是参考输入，按三层吸收到 MiniMax-skills。

### 核心层

- `officecli`
- `officecli-docx`
- `officecli-pptx`
- `officecli-xlsx`

核心层用于补强 `office-expert` 和共享适配文档中的命令路线、help-first 习惯、schema-first 约束、增量修改流程和输出验证要求。

### 场景层

- `officecli-academic-paper`
- `officecli-word-form`
- `officecli-data-dashboard`
- `officecli-financial-model`
- `officecli-pitch-deck`

场景层不作为独立 MiniMax skill 暴露，而是进入 `office-expert` 的高层意图路由：

- academic paper → `minimax-docx` + OfficeCLI academic-paper 规则。
- word form → `minimax-docx` + OfficeCLI word-form 规则。
- data dashboard → `minimax-xlsx` + OfficeCLI dashboard 规则。
- financial model → `minimax-xlsx` + OfficeCLI financial-model 规则。
- pitch deck → `pptx-generator` + OfficeCLI pitch-deck 规则。

### 高级 PPT 动效层

- `morph-ppt`
- `morph-ppt-3d`

这两类能力进入 `office-expert` 和 `pptx-generator` 的 PPT 高级路线：

- morph animation deck → `pptx-generator` + morph-ppt 命名、ghosting、verify 和 style library 规则。
- 3D morph deck → `pptx-generator` + morph-ppt-3d 的 GLB 模型、镜头、模型内容布局和兼容性检查规则。

## 整体架构

### 聚合 skill：`office-expert`

新增 `skills/office-expert/SKILL.md`，作为用户面对的统一入口。触发词覆盖 Office、Word、Excel、PowerPoint、PPT、PDF、DOCX、XLSX、spreadsheet、presentation，以及相关中文表达。

`office-expert` 负责：

- 根据文件类型、任务意图和场景词识别任务。
- 读取 OfficeCLI skill 体系提炼出的路由规则。
- 判断是否需要 OfficeCLI doctor 检测。
- 选择 OfficeCLI command workflow、MiniMax specialist skill，或两者组合。
- 将专业任务委托到 `minimax-docx`、`minimax-xlsx`、`pptx-generator`、`minimax-pdf`。
- 对场景任务套用 OfficeCLI 的场景规则，例如 academic paper、dashboard、financial model、pitch deck、morph deck。
- 默认保护原文件，输出到新文件。

### 共享适配文档：`officecli-adapter.md`

新增 `skills/office-expert/references/officecli-adapter.md`，作为 OfficeCLI 融合规则的唯一来源。

它不只是安装说明，还要定义：

- OfficeCLI 外部安装要求。
- 命令路径配置方式，例如 `OFFICECLI_COMMAND`。
- `officecli_doctor.py` 的使用方式。
- OfficeCLI core skill 到 MiniMax skill 的映射。
- OfficeCLI scene skill 到 `office-expert` 场景路由的映射。
- OfficeCLI 的 help-first、schema-first、shell quoting、incremental mutation 和 QA gate 原则。
- morph-ppt 的命名、ghosting、verify、style library 引用规则。
- OfficeCLI 失败、不可用或输出不可验证时的回退规则。

四个现有 Office skills 引用这份文档，不在各自文件里重复维护完整 OfficeCLI 命令规则。

### 现有 MiniMax Office skills 增强

修改以下文件，增加简短的 OfficeCLI fast path 与共享适配文档引用：

- `skills/minimax-docx/SKILL.md`
- `skills/minimax-xlsx/SKILL.md`
- `skills/pptx-generator/SKILL.md`
- `skills/minimax-pdf/SKILL.md`

这些修改不能重写原有专业流程。MiniMax 的 OpenXML、XLSX XML、PptxGenJS、PDF 设计系统仍是专业能力主体。

## 路由规则

### 文件类型识别

- `.docx`、`.doc` → Word 路线。
- `.xlsx`、`.xlsm`、`.csv`、`.tsv` → Excel 路线。
- `.pptx`、`.ppt` → PowerPoint 路线。
- `.pdf` → PDF 路线。
- 多文件或跨格式任务 → 先进入 `office-expert` 聚合路线。

### 任务意图识别

`office-expert` 识别这些意图：

- 读取、摘要、提取文本。
- 格式转换。
- 批量替换、模板填写。
- 创建新文件。
- 美化、排版、品牌化。
- 校验、修复、对比。
- 跨格式生成，例如 Excel → PPT、DOCX → PDF、PDF → Word。
- 场景化生成，例如论文、表单、仪表盘、财务模型、融资路演、Morph 动效演示。

### OfficeCLI 优先场景

优先走 OfficeCLI command workflow 的情况：

- 标准 Office 文件读取。
- 结构、元数据、文本提取。
- 标准格式转换。
- 批量处理。
- 简单文本替换。
- OfficeCLI 已有直接支持的模板填写。
- 需要严格命令参数、schema、增量修改和验证门禁的 Office 操作。
- 不需要复杂视觉设计、深度 OpenXML 手工控制或 MiniMax 专属设计系统的任务。

### MiniMax specialist 优先场景

优先走 MiniMax 现有 skills 的情况：

- 高质量视觉设计。
- PPT 页面设计、多 slide 编排、视觉多样性和 PptxGenJS 生成。
- PDF 封面、排版、品牌系统、表单填写或重排。
- XLSX 公式、专业财务格式、公式校验、零格式损失 XML 编辑。
- DOCX OpenXML 精细结构、样式系统、批注、修订、模板格式和 XSD gate check。
- OfficeCLI 不可用、命令失败或输出无法验证。

### 场景路由

- academic paper：使用 OfficeCLI academic-paper 的论文结构、引用、公式、交叉引用规则，执行层落到 `minimax-docx` 和 OfficeCLI DOCX workflow。
- word form：使用 OfficeCLI word-form 的内容控件、表单字段、保护和填写规则，执行层落到 `minimax-docx` 和 OfficeCLI DOCX workflow。
- data dashboard：使用 OfficeCLI data-dashboard 的 KPI、图表、布局和数据验证规则，执行层落到 `minimax-xlsx` 和 OfficeCLI XLSX workflow。
- financial model：使用 OfficeCLI financial-model 的模型结构、公式、假设区、DCF/LBO 等规则，执行层落到 `minimax-xlsx` 和 OfficeCLI XLSX workflow。
- pitch deck：使用 OfficeCLI pitch-deck 的叙事结构和投资人视角规则，执行层落到 `pptx-generator` 和 OfficeCLI PPTX workflow。
- morph animation deck：使用 morph-ppt 的 Morph 命名、ghosting、verify 和样式库规则，执行层落到 `pptx-generator`。
- 3D morph deck：使用 morph-ppt-3d 的 GLB 模型、相机、模型内容布局和兼容性规则，执行层落到 `pptx-generator`。

### 回退规则

- `officecli_doctor.py` 失败时，说明 OfficeCLI 不可用原因，并尽量继续走 MiniMax 专业流程。
- OfficeCLI 命令失败时，不盲目重试，改走对应 MiniMax specialist skill，或在结果受影响时询问用户。
- 输出文件无法读取、文本抽取为空、校验失败时，视为 OfficeCLI 输出失败。
- 默认不覆盖用户原文件。

### 跨格式任务

跨格式任务采用“OfficeCLI 结构处理 + MiniMax 内容重组/设计”的组合模式。

例子：

- Excel → PPT：先提取或分析表格数据，再用 `pptx-generator` 做幻灯片设计。
- DOCX → PDF：OfficeCLI 做标准转换；如果需要美化或重排，再用 `minimax-pdf`。
- PDF → Word：OfficeCLI 做提取/转换；如果需要结构化重建，再用 `minimax-docx`。
- Excel dashboard → PPT：`officecli-data-dashboard` 规则帮助识别 KPI 和图表，`pptx-generator` 负责演示稿表达。

## 新增文件

### `skills/office-expert/SKILL.md`

聚合入口，包含 frontmatter、触发描述、文件类型路由、场景路由、OfficeCLI skills 内联融合规则、OfficeCLI fast path、MiniMax fallback、安全输出规则。

### `skills/office-expert/references/officecli-adapter.md`

共享适配与融合规则文档。它连接三件事：OfficeCLI 命令、OfficeCLI skills 规则、MiniMax specialist skills。

### `skills/office-expert/scripts/officecli_doctor.py`

环境检测脚本，只检测不安装。

预期行为：

- 先检查 `OFFICECLI_COMMAND`，再检查 PATH 上的 `officecli`。
- 尝试运行版本命令。
- 默认输出人类可读结果。
- 支持 `--json` 输出机器可读结果。
- OfficeCLI 可用时返回 `0`。
- OfficeCLI 不可用或版本检测失败时返回 `1`。
- 不下载、不安装、不修改系统状态。

## 修改文件

### `README.md`

在 skills 表中新增 `office-expert`。描述为：统一 Office 专家，融合 OfficeCLI skills 与 MiniMax DOCX/XLSX/PPTX/PDF skills。

### `README_zh.md`

同步新增中文说明。

### `.claude-plugin/plugin.json`

如果插件 metadata 使用关键词发现，加入 `office-expert` 和 Office 相关关键词。

### `.cursor-plugin/plugin.json`

如果插件 metadata 使用关键词发现，加入 `office-expert` 和 Office 相关关键词。

### 现有 Office skills

增加简短 OfficeCLI fast path 和共享适配文档引用：

- `skills/minimax-docx/SKILL.md`
- `skills/minimax-xlsx/SKILL.md`
- `skills/pptx-generator/SKILL.md`
- `skills/minimax-pdf/SKILL.md`

### 不直接修改或复制的 OfficeCLI 文件

以下目录只作为参考，不复制到 MiniMax-skills：

- `E:\GitHub\OfficeCLI\skills\officecli*`
- `E:\GitHub\OfficeCLI\skills\morph-ppt*`

实现时可以读取这些 skill 的触发词、路由规则、命令纪律和 QA gates，但最终维护入口在 MiniMax-skills。

## 验证策略

### skill 结构验证

运行 MiniMax-skills 现有校验脚本：

```bash
python .claude/skills/pr-review/scripts/validate_skills.py
```

预期结果：`office-expert` frontmatter 合规，目录名是 kebab-case，没有结构错误。

### doctor 验证

无 OfficeCLI 环境：

```bash
python skills/office-expert/scripts/officecli_doctor.py --json
```

预期结果：JSON 报告 `available: false`，包含原因和修复建议。

有 OfficeCLI 环境：

```bash
python skills/office-expert/scripts/officecli_doctor.py --json
```

预期结果：JSON 报告 `available: true`，包含命令路径和版本检测结果。

### 文档一致性验证

检查：

- `README.md` 和 `README_zh.md` 都列出 `office-expert`。
- 四个 MiniMax Office skills 都引用共享 adapter。
- `office-expert` 的核心层、场景层、动效层路由与共享 adapter 一致。
- 没有把 OfficeCLI 场景 skills 暴露成重复 MiniMax skill 入口。

### OpenClaw 兼容验证

如果本机有 OpenClaw CLI，运行：

```bash
openclaw skills inspect ./skills/office-expert
```

如果没有 OpenClaw CLI，则以标准 `SKILL.md` 结构验证和插件 metadata 检查为准。

### OfficeCLI skills 融合验证

实现后抽查这些场景是否能路由到正确路线：

- “写一篇带引用和公式的学术论文” → academic paper → `minimax-docx` + OfficeCLI DOCX 规则。
- “做一个可填写的 Word 表单” → word form → `minimax-docx` + OfficeCLI form 规则。
- “用 Excel 做 KPI dashboard” → data dashboard → `minimax-xlsx` + dashboard 规则。
- “做一个 DCF 财务模型” → financial model → `minimax-xlsx` + financial model 规则。
- “做融资路演 PPT” → pitch deck → `pptx-generator` + pitch deck 规则。
- “做 Morph 动画 PPT” → morph deck → `pptx-generator` + morph-ppt 规则。
- “做带 GLB 模型的 3D Morph PPT” → 3D morph deck → `pptx-generator` + morph-ppt-3d 规则。

## 风险

### OfficeCLI command interface 变化

命令细节集中在共享 adapter 中，避免四个 MiniMax Office skills 分散硬编码。

### OfficeCLI skills 与 MiniMax skills 重叠

不复制 OfficeCLI skills，不新增重复入口。`office-expert` 负责统一路由，现有 MiniMax specialist skills 负责专业执行。

### OfficeCLI 能力边界不完整

OfficeCLI 只作为标准 Office 操作和场景规则来源，不替代 MiniMax 的设计系统、OpenXML 深度资料、PptxGenJS 生成和 PDF 美化流程。

### 平台差异

Windows、macOS、Linux 上 OfficeCLI 安装路径和依赖可能不同。doctor 只检测和报告，不安装。

### Morph/3D PPT 依赖复杂

morph-ppt 和 morph-ppt-3d 涉及动画命名、ghosting、GLB 模型兼容性和样式资产。实现时只提炼规则，避免直接复制大量模板资产，除非后续单独确认许可和维护策略。

## 明确不做

- 不把 OfficeCLI 源码 vendor 到 MiniMax-skills。
- 不打包 OfficeCLI 二进制。
- 不整体复制 `E:\GitHub\OfficeCLI\skills`。
- 不新增 `officecli-docx`、`officecli-pptx`、`officecli-xlsx` 等独立 MiniMax skill。
- 不让 OfficeCLI 场景 skills 与 MiniMax skills 形成重复入口。
- 不修改 OpenClaw.NET runtime 代码。
- 不新增 OpenClaw 原生插件。
- 不承诺 OfficeCLI 覆盖所有 Word、Excel、PowerPoint、PDF 高级场景。
- 不默认覆盖用户原始 Office 文件。
