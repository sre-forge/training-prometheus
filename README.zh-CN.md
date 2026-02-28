# training-prometheus

一个用于 SRE 查询工作流的**确定性 Prometheus 环境画像与静态技能编译器**。

## 项目概述

`training-prometheus` 是一个**只读训练框架**，用于分析目标 Prometheus/Thanos 环境，并编译出**稳定、可用于生产的静态查询技能**。

它**不是**运行时查询助手，而是一个**构建系统（builder system）**。

该项目的核心思想是：不要在生产阶段依赖运行时探索、动态指标猜测或临场排障，而应先在训练阶段完成学习与验证，再输出静态能力。

## 为什么需要它

真实生产中的 Prometheus 生态差异很大：

- Exporter 组合不同
- 标签拓扑结构不同
- 保留策略与采集间隔不同
- 命名规范不一致
- 基数规模与查询成本差异巨大

因此，通用查询模板在生产中常常失败，常见原因包括：

- 目标指标不存在
- 标签结构不匹配
- 聚合假设不成立
- 高基数导致查询不稳定
- rate 窗口不合理
- 命名空间范围假设错误

`training-prometheus` 通过“先学习、后编译”的流程，将这些不确定性前置到隔离的训练阶段。

## 核心模型

框架将流程抽象为一个确定性的编译管道：

```text
Environment E
      ↓
Training Pipeline
      ↓
Semantic Model M
      ↓
Validated Query Set Q
      ↓
Static Skill S

S = Compile(E, Contract)
```

输出的技能是静态的、可版本化、可审计的。

## 设计原则

1. **只读优先（Read-only by Design）**
   - 不修改 Prometheus
   - 不写 recording rules
   - 不变更集群状态
   - 仅进行读取与分析

2. **确定性输出（Deterministic Output）**
   - 相同环境描述符必须生成相同结果
   - 可复现性是硬性要求

3. **关注点分离（Separation of Concerns）**
   - 训练技能：探索、学习、验证、评估
   - 生产技能：只执行，不学习、不发现、不兜底猜测

4. **语义优先（Semantic First）**
   - 先定义 SRE 语义契约，再映射具体指标
   - 避免仅靠字符串关键词匹配

## SRE 语义契约（v1）

典型语义域包括：

- `cpu_usage`
- `memory_usage`
- `cpu_limit`
- `network_rx`
- `connection_count`
- `file_descriptors`
- `thread_count`
- `saturation`
- `error_rate`

训练流程会把这些语义域映射到环境中的真实指标表达式，并完成验证。

## 输入：环境描述符

系统接收结构化环境描述符，例如：

```json
{
  "environment_name": "qa",
  "prometheus_endpoint": "https://qa-thanos.example.com",
  "namespace_scope": ["sre"],
  "cluster_type": "kubernetes",
  "retention_days": 7,
  "scrape_interval": "30s",
  "sre_contract_version": "v1"
}
```

该描述符定义了训练边界与约束。

## 训练阶段

### Phase 0 — 契约定义

定义抽象的 SRE 语义目标。

### Phase 1 — 环境快照

采集：

- 全量指标名
- 指标类型
- 标签结构
- Exporter/目标信息
- 抓取配置特征

输出：环境画像快照。

### Phase 2 — 拓扑分析

分析标签层级与资源拓扑（如 namespace、pod、container、node、workload）。

输出：环境拓扑模型。

### Phase 3 — 语义映射

将契约中的语义域映射到具体指标与变换方式。

示例：

- `cpu_usage` → `container_cpu_usage_seconds_total` + `rate()`

输出：语义映射模型。

### Phase 4 — 查询验证

对每个语义域：

- 构建 PromQL 模板
- 执行 instant query
- 执行 range query
- 验证聚合逻辑
- 检查基数规模
- 检测 NaN/全零等异常

输出：验证报告。

### Phase 5 — 稳定性评估

评估：

- 查询延迟
- 时间序列数量
- 跨命名空间影响
- 保留窗口安全性
- 高基数风险

输出：稳定性报告。

### Phase 6 — 技能编译

仅当验证与稳定性都达标时，生成静态生产技能：

```text
sre-<env>-prometheus-query/
    skill.md
    query_templates.json
    query_engine.py
    metadata.json
```

## 非目标（Non-Goals）

本项目不负责：

- 替代 Prometheus
- 作为可视化仪表盘
- 运行时动态猜测指标
- 自动修复/自愈逻辑
- 修改告警规则

它是严格的“训练 + 编译”框架。

## 生产价值

通过将不确定性前移，产出的技能可以做到：

- 可预测
- 稳定
- 可版本管理
- 可审计
- 可复现

## 未来方向

后续可扩展方向：

- Kubernetes 环境建模
- 多云可观测性画像
- 告警策略编译
- 故障模式建模
- 基线学习
- 事故知识集成

长期目标是成为一个“环境建模 + SRE 能力编译”平台。

## 项目状态

**早期设计阶段。**

实现路线图即将发布。

## 项目理念

> 我们不构建靠猜测运行的工具。
>
> 我们构建先学习、后确定性执行的系统。
>
> **训练先于生产。**
