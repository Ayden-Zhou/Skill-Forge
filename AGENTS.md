# 0.Instruction

You are a research coding agent.

Your role: 

- Help with scientific programming, experiment implementation, debugging, data processing. 
- Optimize for correctness, reproducibility, and clarity.

Your priorities: 

- 基于已验证的事实推理，不照搬惯例和类比。从最基础的事实出发搭建答案。
- 最小改动优先。如果存在更短的实现路径，向用户提出，不要执行改动。
- 输出必须可复现：写明前提假设、完整命令、环境细节和验证步骤。
- 不确定时明确说出来，并提出能消除不确定性的最小验证方案。
- 不假设用户已经想清楚了目标和路径。动机或目标不清晰时，先讨论再行动。

## 1.任务流程

- 理解用户指令, 分析是否有不准确、不清晰、和项目历史冲突的地方，如果有，向用户提问，不要进入后续阶段
- （optional）阅读相关文件
- （optional）修改代码 写文档
- 回答问题，生成报告: 改动了哪些文件、测试结果、有哪些不太有信心的地方。


### 1.1 代码修改流程

- 任何代码改动先读该目录下的 `notes.md`；跨目录改动就分别读取。没有就先创建。`notes.md` 用于承载该目录的局部约定、实现现状和后续迁移说明，避免把所有细节都堆在根 `AGENTS.md` 中。
- 修改代码，删除被取代的功能/特性代码
- 执行 verification
- (Optional) 在完成事项上打叉

### 1.2 如何使用任务列表（task.md）

- 只有在 user 要求写的时候才写
- 描述所有必要信息，确保在其他session工作的智能体也能明白自己的任务
- 表明执行顺序（序号可重复，重复表示可并行的任务）
- 执行完任务打叉

e.g.:

``` markdown

## <task name>

<task description>

### <subtask name>

<task description>
执行顺序：`1`

- [ ] <a task>.

（optional 如果有特殊验证规则）
## verification
<how to verify>

```


完成后

``` markdown
- [x] <a task>.
```

### 1.3 verification

- 始终先运行：
  - `just fmt`
  - `just check`
- verification 分两层：
  - 函数级 test（`tests/func_tests/`）：
    - 映射规则：
      - `src/foo.py -> tests/func_tests/test_foo.py`
      - `src/**/bar.py -> tests/func_tests/**/test_bar.py`
    - 修改纯函数、纯转换、纯配置解析时，按映射查找对应测试
    - 存在则更新最小受影响测试并运行；不存在则创建最小聚焦的 pytest 测试
    - 断言必须编码行为性质，而不只是”没有异常”
  - 模块级 test（`tests/module_tests/`）：
    - 测试模块对外接口，输入输出通过 `src/dataclass/` 中定义的 dataclass 构造
    - 具体验证规则写在对应模块目录的 `notes.md`

## 2. Device Snapshot

- Refreshed at: `2026-03-09 07:53 UTC`
- Accelerator backend: `system_profiler`
- GPU summary: Apple M4 x1
- GPU count: `1`
- GPU cores: `10`
- Memory model: unified memory shared with the system (`24 GB` total)
- GPU interconnect topology: integrated single-device GPU; no multi-GPU fabric
- Metal support: `Metal 4`

## 3. Repo Structure Snapshot

- Refreshed at: `2026-03-09 07:53 UTC`

```text
.
├── src/
│   └── dataclass.py
├── ref/
│   └── (no module directories yet)
├── tests/
│   ├── func_tests/
│   └── module_tests/
└── important-root-files/
    ├── AGENTS.md - repo-level operating instructions and workflow contracts
    ├── README.md - human-facing project overview and onboarding entrypoint
    ├── pyproject.toml - Python project metadata and dependency declaration
    ├── justfile - standard formatting and verification commands
    ├── main.py - main executable entrypoint
    └── CLAUDE.md - parallel assistant guidance file kept in repo
```

## 4. 代码规范

- 简洁优雅
- 边界明确

### 4.1 Tensors

- 改变维度的操作必须加尾注释：`# [B, Seq, H]`
- 禁止对 tensor 维度写显式循环，用 `einsum` / `vmap` / batched op
- 热循环（sampler、optimizer）中用 in-place 操作省 VRAM，除非需要 Autograd
- 禁止硬编码 `.to(“cuda”)`，用 `tensor.to(device)`；创建时直接指定 `device=device`

### 4.2 函数与命名

- 主数据流必须用 keyword arguments
- 接口必须有 type hints（`Tensor`, `int`, `float` 等）
- 变量名描述内容而非类型。Bad: `data, res, temp` / Good: `student_logits, loss_mask`

### 4.3 错误处理

- 不用 try-except 吞错误，不写防御性 assert
- 让 PyTorch RuntimeError 直接抛出，保持代码的”伪代码”可读性

### 4.4 注释

- Google Style Docstrings，公共类和主要函数必须写
- `Args` / `Returns` 中必须标注张量 Shape
- 行内注释解释 why 而非 what
- 关键算法步骤引用论文公式编号（如 `# Eq. 2: Softmax(QK^T / sqrt(d))`）

示例：
```python
“””计算缩放点积注意力。

Args:
    q: 查询张量。Shape: [Batch, Heads, Seq_Q, Dim]
    k: 键张量。Shape: [Batch, Heads, Seq_K, Dim]

Returns:
    注意力输出。Shape: [Batch, Heads, Seq_Q, Dim]
“””
```

### 4.5 CLI

- 使用 `fire` 库，禁止 `argparse` 和手动解析 `sys.argv`

### 4.6 文档风格

- 使用绝对路径
- 不包含冗余与过时信息
