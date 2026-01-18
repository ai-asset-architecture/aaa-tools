---
name: data-inspect-logs
description: Analyze Body Log CSV files to provide health insights and summary statistics.
metadata:
  domain: data-analysis
  owner: Advisor
  short-description: 日誌數據探勘
---

# Data Inspect Logs

## When to use
- Use when the user asks for a summary of their health data (e.g., "How is my sleep this week?").
- Use to debug data quality issues (e.g., "Why is the graph empty?").

## Execution Steps

1.  **Locate Data**
    Confirm the path to the CSV file (usually in `pbos-backend/data/` or a user-provided path).

2.  **Run Analysis**
    Execute the python script to parse and summarize the CSV.
    
    ```bash
    python3 scripts/analyze_csv.py <path_to_csv_file>
    ```

3.  **Interpret Results**
    - The script outputs basic stats (Mean, Max, Min) and missing value counts.
    - **Advisor Task**: Translate these numbers into a natural language health insight.
    - **Alert**: If "Missing Values" > 0, warn the user about potential data quality issues (PHAD risk).
