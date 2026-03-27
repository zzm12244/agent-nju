---
name: orchestrator
description: Use when starting a new development task - reads user requirements, initializes task.json, then drives the dev→test→fix loop until approved
---

# Orchestrator (主调度 Agent)

## 职责
接收用户需求，初始化任务，驱动开发→测试→修复的完整闭环，直到验收通过。

## 执行流程

### 1. 读取当前状态
```bash
cat .agent-communication/task.json 2>/dev/null || echo "无任务"
```

- 有未完成任务（action 不是 `approved`）：继续驱动现有任务
- 无任务或已完成：根据用户需求初始化新任务

### 2. 初始化任务（新需求时）
```bash
mkdir -p .agent-communication/history
```

写入 `.agent-communication/task.json`：
```json
{
  "version": "1.0",
  "timestamp": "<ISO时间>",
  "action": "dev_requested",
  "from": "orchestrator",
  "to": "dev-agent",
  "iteration": 0,
  "branch": "<当前分支>",
  "commit": "<当前commit>",
  "requirement": "<用户需求描述>",
  "acceptance_criteria": ["验收标准1", "验收标准2"],
  "report_path": ".code-review-reports/latest-report.md"
}
```

### 3. 驱动循环

根据 task.json 中的 action 决定下一步角色：

| action | 下一步 |
|--------|--------|
| `dev_requested` | 调用开发模式（code-fix skill） |
| `test_requested` | 调用测试模式（code-diff-review skill） |
| `approved` | 闭环结束，汇报结果 |
| `blocked` | 暂停，向用户说明阻塞原因 |

### 4. 结束条件

action 变为 `approved` 时：
```bash
# 归档任务
timestamp=$(date +%Y%m%d-%H%M%S)
cp .agent-communication/task.json .agent-communication/history/task-$timestamp.json
```

向用户汇报：完成的功能、迭代次数、最终测试结论。

## 注意事项
- 每次驱动前必须重新读取 task.json，不依赖内存状态
- iteration 超过 5 次仍未 approved，主动向用户说明卡点
- 不自己写代码，不自己测试，只做调度
