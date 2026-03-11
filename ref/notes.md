# Ref Notes

`ref/` 用来放参考资料，不是当前项目的主实现目录。

## 当前一级子目录

- `project_info/`
  - 存放本项目自身的研究背景和问题定义。
  - 目前只有 `project.md`，内容是 research scope、challenge 和 context，属于项目内部研究草稿，不是代码依赖。

- `open_source/`
  - 存放外部开源项目的参考实现或源码快照。
  - 目前只有 `SDPO/`，且目录完整，包含 `README.md`、`setup.py`、`verl/`、`examples/`、`experiments/`、`tests/` 等，说明这里不是摘录，而是一个可独立运行/阅读的上游项目副本。
  - 从 `README.md` 可验证该项目是 “Self-Distilled Policy Optimization (SDPO)” 的实现，主要用于 RLVR / rich feedback 训练流程参考。

- `related_works/`
  - 预留给相关论文、方法笔记或外部工作的整理。
  - 当前为空目录，还没有实际内容，因此不要假设这里已经形成固定结构。

## 使用约定

- 往 `ref/` 增加内容时，优先按“项目内部资料 / 外部开源代码 / 相关工作整理”三类分别放入上述目录。
- 如果 `related_works/` 后续开始使用，需要再补充它的目录约定，避免和 `project_info/` 的研究草稿混在一起。
