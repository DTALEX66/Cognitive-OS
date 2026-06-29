# RoutePackage 数据规范

## 1. 核心对象

```text
RoutePackage
RouteNode
KnowledgeItem
MemoryEncoding
VisualAsset
QualityScore
ChangeSummary
TrainingRecord
```

## 2. 必填字段

RoutePackage：
- routeId
- title
- version
- status
- nodes
- createdAt
- updatedAt

RouteNode：
- nodeId
- order
- locationName
- knowledge
- memory

KnowledgeItem：
- coreFact
- question
- answer
- riskLevel

MemoryEncoding：
- memoryImageText
- visualElementMap

## 3. 版本规则

- routeId 不因换图改变。
- imageVersion 因候选图改变。
- 事实层改动必须增加 changeSummary.factChanges。
- 分享时必须携带 sourceRouteId 和 forkedFromVersion。

## 4. 导入导出规则

默认导出：知识结构、路线节点、记忆图文、版本、质量评分。
默认不导出：个人训练记录、私人笔记、错题历史。
