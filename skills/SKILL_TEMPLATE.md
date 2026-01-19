# Skill: [Skill Name]

## Description
[簡短描述此技能的用途與適用範圍]

## Routing Logic
在執行前先完成路由判斷。若為「無分流」技能，仍需保留此區塊並標示固定路徑。

### Hard Rules (Governance)
- IF [condition] THEN [action]
- IF [condition] THEN [action]

### Soft Rules (Scoring)
- Base score: 0
- +1 if [condition]
- +3 if [condition]

### Routing Decision
- Score < 3: [fast/cheap path]
- Score >= 3: [standard/deep path]
---
> 簡化規則：若此技能無需路由，請寫明「固定走 single_path」。

## Execution Steps
1. [Step 1]
2. [Step 2]

## Fallback (Resilience)
- IF primary tool fails THEN switch to backup tool
- IF still fails THEN generate manual steps for user
---
> 簡化規則：若無替代工具，請寫明「失敗即回報，提供手動步驟」。

## Inputs / Outputs
- Inputs: [list inputs]
- Outputs: [list outputs]

## Limitations
- [limitations or boundaries]
---
> 簡化規則：若無硬性限制，請寫明「無特殊限制，但需人工確認輸入」。
