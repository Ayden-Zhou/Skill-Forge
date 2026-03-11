# Outline

## Motivation

开源 skills 库已经积累了大量人类+AI 共写的程序性知识，但目前主要被当作外部模块调用，还没有被系统地当成训练数据来研究。核心问题是：能不能把这些 skills 转化为高质量的 procedural supervision，让模型学到可迁移的程序知识，而不只是做 skill retrieval。

## Research Scope（研究范围）

研究范围是本研究可能涉及的问题空间，覆盖 1-3 篇论文的工作量。最终的研究成果是 scope 的一个子集。

递进结构：**什么值得学 → 怎么处理 → 怎么学 → 学到了什么 → 学了之后怎样 → 能否闭环**

1. **刻画与筛选**：开源 skill 仓库中，哪些 skill 包含可迁移的 procedural knowledge？如何定义和度量 skill 的"训练价值"？
2. **表示与重组**：原始 skill 需要怎样的预处理（统一 schema、抽象、合并）才能成为有效的训练信号？处理前后的差距有多大？
3. **训练样本选择**：训练的时候具体到每一个样本，应该如何选择 skill。
4. **训练范式**：用 skill 作为 supervision 的最佳训练方式是什么（SFT / distillation / RL with skill）？不同范式下模型的学习行为有何不同？
5. **学习深度**：模型学到的是表面格式模仿，还是真正的 procedural prior？如何区分和度量这两者？
6. **训练影响**：skill 训练对模型的其他能力有什么影响？不同类型的 skill 带来的影响是否一致？训练后模型是否仍然需要 skill？
7. **泛化边界**：以上结论在不同模型尺寸、不同问题领域下是否稳定？
8. **Co-evolution**：模型能否反过来改进 skill 库？模型产生 skill 的能力和 learn from skill 的能力能否 co-train？skill 是否需要随模型参数迭代？

## Research Challenges

研究过程中可能会需要解决的问题

1. **Skill 质量不齐**：开源 skill 仓库噪声大，缺乏统一的质量评价标准，筛选策略本身需要验证。
2. **Skill 质量定义**：用什么来定义skill质量。能造成最大性能提升的skill也最适合用来训练吗 ？
3. **训练稳定性**
4. **skill和benchmark的mismatch**

## Research Context（研究现状）

我们可以把大的研究领域定义为如何从文本信息中改善模型，进而分为三个部分：

- 如何生成文本信息（文本信息从哪里来？）
- 如何管理文本信息（文本信息后续如何管理、如何改进、如何读取）
- 如何构建训练闭环（是否进行训练，如何进行训练）

对于文本信息，我们也可以进一步按照性质

### 学术名词

现有的研究如何从文本信息中获得训练信号的方法已有许多，对于不同的文本类信息的名称有主要包括：

- prompt: 定义最宽泛。
- trajectory：强调来源是LLM生成的response。
- reflection: 强调来源是对于错误trajectory的再处理。
- feedback：强调来源是外部环境（例如编译器报错）。
- procedure memory：强调信息是流程描述。
- skill: 强调是程序化记忆+外部能力包

### 相关研究

