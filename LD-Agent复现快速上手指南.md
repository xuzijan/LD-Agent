# LD-Agent 复现快速上手指南

> 按 5 步递进：Fork → 环境隔离 → 跑通示例 → 整理 I/O 与配置 → 统一评估与 AmbiCoding

---

## 论文背景

**论文**：*Hello Again! LLM-powered Personalized Agent for Long-term Dialogue* (NAACL 2025)  
**机构**：NUS、USTC、SMU  
**核心思想**：基于 LLM 的个性化长期对话代理，通过事件记忆、人物画像提取与检索，实现跨会话的个性化回复生成。

**评估场景**：MSC（Multi-Session Chat）多轮长期对话  

**当前项目**：`xuzijan/LD-Agent` 是 `leolee99/LD-Agent` 的 fork。

---

## Step 1：Fork 到自己仓库

- [x] Fork `leolee99/LD-Agent` → `xuzijan/LD-Agent`（或你的 GitHub 用户名）
- [ ] 在 README 或 commit 中注明 fork 来源与对应 commit
- [ ] `.gitignore` 排除大文件（模型权重、数据、nlgeval 指标等），只同步代码和配置

**建议 .gitignore 新增：**

```gitignore
*.safetensors
*.bin
*.pt
*.pth
logs/
outputs/
dataset/
nlgeval/metric/
.cache/
wandb/
```

---

## Step 2：环境隔离

每个 baseline 单独环境，避免依赖冲突。

**目录结构：**

```
/root/autodl-tmp/
├── LD-Agent/                 # 论文 4
│   ├── dataset/MSC/          # 数据（需从 Google Drive 下载）
│   ├── nlgeval/metric/       # 指标文件（需下载）或 mock
│   ├── logs/                 # 输出、模型
│   └── scripts/              # 脚本
├── experiments/
│   └── configs/
│       └── ld_agent_baseline.yaml   # 统一 baseline 配置
└── ...
```

**LD-Agent 环境：**

```bash
cd /root/autodl-tmp/LD-Agent
conda create -n ld-agent python=3.10 -y
conda activate ld-agent
pip install torch openai nltk numpy peft transformers spacy
```

**精简依赖（Mock 验证用）**：`requirements_mock.txt` 已提供最小依赖列表。

**配置 API Key**：编辑 `scripts/msc_gpt_eval.sh` 中的 `API_KEY=your_openai_api_key`，或通过 `--api_key` 传入。

---

## Step 3：按原作者示例跑通一次

### 3.1 Mock 验证（无需密钥）

```bash
cd /root/autodl-tmp/LD-Agent
conda activate ld-agent
bash scripts/validate_mock.sh
```

或分步执行：

```bash
# 终端 1：启动 Mock OpenAI 服务（端口 19998）
python scripts/mock_openai_server.py

# 终端 2：运行 QuickEval
python scripts/run_mock_eval.py --dataset quickeval --data_path dataset/MSC \
  --data_name test.json --id_set id_set.json --client chatgpt \
  --api_key dummy --api_base_url "http://127.0.0.1:19998/v1" --test_num 1
```

**Mock 数据**：`dataset/MSC/test.json`、`id_set.json` 已提供 1 条示例，格式与 MSC 一致。

### 3.2 真实 API 验证（ChatGPT）

```bash
# 编辑 scripts/msc_gpt_eval.sh 填入 API_KEY，或：
python main.py --dataset quickeval --data_path dataset/MSC --data_name test.json \
  --id_set id_set.json --client chatgpt --model gpt-3.5-turbo-1106 \
  --api_key sk-xxx --test_num 1
```

### 3.3 真实 API 验证（ChatGLM）

需下载 ChatGLM3-6B 及 LoRA 权重：

```bash
# 下载 checkpoints：https://drive.google.com/drive/folders/1o59iS9Hr0uol_yentajBw1mJIllIDlGJ
# 放置到 logs/models/summarizer, extractor, generator
bash scripts/msc_glm_quick_eval.sh
```

### 3.4 论文官方 MSC 评估

**数据来源**：[Google Drive](https://drive.google.com/drive/folders/1ZyYYofzFWW2CxtW0XQZxMQtJ2EtroULX)（event summary、persona extraction、response generation、MSC）

**指标文件**：[nlgeval metric](https://drive.google.com/file/d/122sh6_nsu9ZHuefQeAPEpnX0X6jJdPXA/view) 解压到 `nlgeval/metric/`

**运行 MSC 评估**：

```bash
# ChatGPT（需 API Key）
bash scripts/msc_gpt_eval.sh

# ChatGLM（需模型与 LoRA）
bash scripts/msc_glm_eval.sh
```

---

## Step 4：整理输入输出、重要参数、配置

### 4.1 输入格式（完整）

**QuickEval（带标注 persona）**

| 输入 | 类型 | 说明 | 来源 |
|------|------|------|------|
| test.json | JSON | 每样本含 conversations | `--data_name` |
| id_set.json | JSON | 每样本 session_number | `--id_set` |
| conversations[0] | str | 系统提示 | 数据字段 |
| conversations[1] | str | 用户输入 | 数据字段 |
| conversations[2] | str | 参考回复（ground truth） | 数据字段 |

**test.json 单条样本格式：**
```json
{
  "conversations": [
    {"content": "系统提示"},
    {"content": "用户输入"},
    {"content": "参考回复"}
  ]
}
```

**MSC 完整评估**

| 输入 | 类型 | 说明 | 来源 |
|------|------|------|------|
| sequential_test.json | JSON | 多会话对话序列 | `--data_name` |
| 各 session 含 dialog、time_pass | - | 对话与时间间隔 | 数据字段 |

### 4.2 输出格式（完整）

**QuickEval**

| 输出 | 类型 | 说明 |
|------|------|------|
| Mean Score | array | [B-1, B-2, B-3, B-4, R-L, Dist-1, Dist-2, Dist-3] |
| Mean Session N Score | array | 各 session 的 8 维指标 |
| logs/*.log | 文件 | 详细日志 |

**MSC**

| 输出 | 类型 | 说明 |
|------|------|------|
| 各 sample 平均分 | array | 同上 8 维 |
| 各 session 平均分 | array | 同上 |
| sampling 时 | JSON | `logs/sampling/train.json` |

### 4.3 重要参数（完整）

| 参数 | 位置 | 默认 | 说明 |
|------|------|------|------|
| --dataset | 命令行 | msc | msc / quickeval |
| --client | 命令行 | chatglm | chatgpt / chatglm |
| --model | 命令行 | gpt-3.5-turbo-1106 | ChatGPT 模型名 |
| --api_key | 命令行 | - | OpenAI API Key |
| --api_base_url | 命令行 | None | Mock 时填 http://127.0.0.1:19998/v1 |
| --test_num | 命令行 | 0 | 0=全部，>0 为样本数 |
| --relevance_memory_number | 命令行 | 1 | 相关记忆检索数 |
| --context_memory_number | 命令行 | 30 | 上下文记忆数 |
| --max_input_length | 命令行 | 2048 | ChatGLM 输入最大长度 |
| --max_output_length | 命令行 | 64 | ChatGLM 输出最大长度 |
| --gpus | 命令行 | 0 | GPU 编号 |

### 4.4 YAML 配置文件（完整）

**训练配置路径**：`Trainer/configs/`（summarizer.yaml、extractor.yaml、generator.yaml）

| 文件 | 说明 |
|------|------|
| summarizer.yaml | 事件摘要 LoRA 训练 |
| extractor.yaml | 人物画像提取 LoRA 训练 |
| generator.yaml | 回复生成 LoRA 训练 |

**generator.yaml 关键字段：**
```yaml
max_input_length: 2048
max_output_length: 64
peft_config:
  peft_type: LORA
  r: 8
  lora_alpha: 32
```

**评估 baseline 配置**：`experiments/configs/ld_agent_baseline.yaml` 已提供，包含 data、memory、model、openai、chatglm、sampling、evaluation 等分组，供统一入口 `run_baseline("ld_agent", config_path)` 使用。当前 main.py 仍通过命令行传参，后续可增加 YAML 加载逻辑。

### 4.5 脚本命令行参数

**validate_mock.sh**

| 说明 |
|------|
| 启动 Mock 服务 → 运行 QuickEval → 停止 Mock |

**run_mock_eval.py**

| 参数 | 说明 |
|------|------|
| --dataset quickeval | 使用 QuickEval 模式 |
| --api_base_url | Mock API 地址 |
| --test_num 1 | 仅跑 1 条验证流程 |

**main.py（通用）**

| 参数 | 说明 |
|------|------|
| --dataset | msc / quickeval |
| --client | chatgpt / chatglm |
| --api_key | OpenAI Key |
| --api_base_url | Mock 时必填 |
| --test_num | 样本数限制 |

---

## Step 5：统一评估与 AmbiCoding 适配

### 5.1 统一输入输出接口

- **统一输入**：`{id, query, context?, personas?, options?, ...}` 的 dict
- **统一输出**：`{id, pred, ground_truth?, scores?, metadata?}` 的 dict
- **统一入口**：`run_baseline("ld_agent", config_path)` 分发到 LD-Agent 实现

### 5.2 AmbiCoding 数据集转换

- 明确 AmbiCoding 原始格式
- 为 LD-Agent 写转换脚本：`AmbiCoding → MSC/QuickEval 输入格式`
- 转换脚本需可复现（固定 seed、版本）

### 5.3 统一评估脚本

- 输入：各 baseline 的预测结果（统一格式）
- 输出：同一套指标（Bleu、ROUGE、Distinct 等）
- 评估逻辑与 baseline 解耦

### 5.4 Prompt Template

**论文/代码中的 Prompt**

- QuickEval：系统提示与用户输入来自 `conversations[0]`、`conversations[1]`
- MSC：EventMemory、Personas、Generator 内部构造 prompt，见 `Module/` 下各模块

**建议**：在 YAML 或单独文件中保存完整 prompt 模板，便于复现与对比。

---

## 数据流简图

```
用户输入 → 记忆检索(context + relevance) → 人物画像更新 → Generator(LLM) → 回复
                ↑
                └── EventMemory (ChromaDB) + Personas
```

---

## 常见问题

| 问题 | 排查 |
|------|------|
| 找不到 API Key | 检查 `--api_key` 或 msc_gpt_eval.sh 中的 API_KEY |
| nlgeval 报错 No module named 'metric' | 使用 Mock 时已有 nlgeval/metric 占位；正式评估需下载 [metric 文件](https://drive.google.com/file/d/122sh6_nsu9ZHuefQeAPEpnX0X6jJdPXA/view) |
| Mock 验证端口占用 | 修改 scripts/mock_openai_server.py 中 PORT，或 `pkill -f mock_openai_server` |
| ChatGLM 显存不足 | 推荐 32GB+ GPU；可减小 batch_size、max_input_length |

---

## 参考链接

- [LD-Agent 论文 (NAACL 2025)](https://aclanthology.org/2025.naacl-long.272/)
- [LD-Agent arXiv](https://arxiv.org/pdf/2406.05925)
- [上游仓库 leolee99/LD-Agent](https://github.com/leolee99/LD-Agent)
- [数据集与指标 Google Drive](https://drive.google.com/drive/folders/1ZyYYofzFWW2CxtW0XQZxMQtJ2EtroULX)
