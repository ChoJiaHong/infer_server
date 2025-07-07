import pandas as pd

# 讀取 CSV 檔案
file_path = "merged_stats.csv"  # 或改成你的實際路徑
df = pd.read_csv(file_path)

# 確保 zero_ratio 是 float，如果是百分比形式像 65.07 則除以 100
df['max_rps'] = df['rps'] / (1 - df['zero_ratio'] / 100)

# 儲存結果到新的 CSV（可選）
df.to_csv("with_max_rps.csv", index=False)

# 顯示前幾筆結果（可選）
print(df[['timestamp', 'rps', 'zero_ratio', 'max_rps']])
