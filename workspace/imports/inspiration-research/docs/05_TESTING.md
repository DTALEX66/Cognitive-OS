# 05 TESTING — v0.2

## 测试框架
- pytest (Python)
- 测试目录: backend/tests/

## 测试统计
| 层级 | 通过数 |
|------|--------|
| MVP核心 (API/Store/MCP/FSRS) | 74 |
| A线实验 (认知/编码/技能/教学) | 57 |
| 总计 | 131 |

## 运行测试
`powershell
set PYTHONPATH=backend
python -m pytest backend/tests/ -q
`

## 健康检查
提交前必须通过: python scripts/health_check.py
