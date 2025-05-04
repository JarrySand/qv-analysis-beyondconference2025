import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

# 出力ディレクトリの作成
os.makedirs('results/data', exist_ok=True)
os.makedirs('results/figures/comparison', exist_ok=True)
os.makedirs('results/reports', exist_ok=True)

# ジニ係数を計算する関数
def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    # 配列の値を昇順に並べ替え
    array = np.sort(array)
    
    # 累積和を計算して正規化
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    
    # ジニ係数の計算（ローレンツ曲線と均等分布線の間の面積の2倍）
    return np.sum((2 * index - n - 1) * array) / (n * np.sum(array))

# ローレンツ曲線を計算する関数
def lorenz_curve(values):
    # 値を昇順にソート
    sorted_values = np.sort(values)
    # 累積分布
    cumsum = np.cumsum(sorted_values)
    # 正規化
    cumsum_norm = cumsum / cumsum[-1]
    # 人口
    population = np.arange(1, len(values) + 1) / len(values)
    
    # (0,0)の追加
    return np.insert(population, 0, 0), np.insert(cumsum_norm, 0, 0)

# CSVファイルを読み込む
votes_df = pd.read_csv('data/votes.csv')
candidates_df = pd.read_csv('data/candidates.csv')
vote_summary = pd.read_csv('data/vote_summary.csv')

# 元のJSONファイルからも読み込み
with open('data/election.json', 'r', encoding='utf-8') as file:
    election_data = json.load(file)

# 英語名を使用するためのDataFrame作成
candidates_df_en = candidates_df.copy()
if 'title_en' in candidates_df.columns:
    # 英語名カラムが存在する場合、それをタイトルとして使用
    candidates_df_en['title'] = candidates_df['title_en']
    # vote_summaryも更新
    if 'title_original' not in vote_summary.columns:
        vote_summary['title_original'] = vote_summary['title']
    vote_summary['title'] = vote_summary['title_en']

# ====== 1. 一人一票方式のシミュレーション ======
print("一人一票方式のシミュレーションを実行中...")

# 各投票者の投票データを抽出
one_person_one_vote = {}
for voter_id in votes_df['voter_id'].unique():
    # この投票者の行を取得
    voter_row = votes_df[votes_df['voter_id'] == voter_id].iloc[0]
    
    # 各候補への投票を取得
    votes_for_candidates = {}
    max_vote = 0
    
    for i in range(len(candidates_df)):
        col_name = f'candidate_{i}'
        if col_name in voter_row and not pd.isna(voter_row[col_name]):
            vote_value = voter_row[col_name]
            votes_for_candidates[i] = vote_value
            if vote_value > max_vote:
                max_vote = vote_value
    
    # 最大投票値を持つ候補を特定
    max_candidates = [cand for cand, vote in votes_for_candidates.items() if vote == max_vote and vote > 0]
    
    # 同率一位の場合は票を分割
    vote_weight = 1.0 / len(max_candidates) if max_candidates else 0
    
    # 一人一票方式の投票を記録
    for cand in max_candidates:
        if cand not in one_person_one_vote:
            one_person_one_vote[cand] = 0
        one_person_one_vote[cand] += vote_weight

# 一人一票方式の結果を整理
opov_results = []
for cand_id, votes in one_person_one_vote.items():
    cand_name = candidates_df_en[candidates_df_en.index == cand_id]['title'].iloc[0]
    opov_results.append({
        'candidate_id': cand_id,
        'title': cand_name,
        'votes': votes
    })

# 一人一票方式の結果をデータフレームに変換
opov_df = pd.DataFrame(opov_results)
opov_df = opov_df.sort_values('votes', ascending=False).reset_index(drop=True)

# 総投票数を計算
total_opov_votes = opov_df['votes'].sum()

# 予算配分を計算（250,000円を票数に応じて比例配分）
budget = 250000
opov_df['budget_allocation'] = (opov_df['votes'] / total_opov_votes) * budget
opov_df['percentage'] = (opov_df['votes'] / total_opov_votes) * 100

# ====== 2. QV方式の結果を取得 ======
print("QV方式の結果を取得中...")

# 現在のQV方式の結果を整理
qv_results = []
for _, row in vote_summary.iterrows():
    qv_results.append({
        'candidate_id': row['candidate_id'],
        'title': row['title'],
        'votes': row['total_votes'],
        'vote_count': row['vote_count'],
        'average_vote': row['average_vote']
    })

# QV方式の結果をデータフレームに変換
qv_df = pd.DataFrame(qv_results)
qv_df = qv_df.sort_values('votes', ascending=False).reset_index(drop=True)

# 総投票数を計算
total_qv_votes = qv_df['votes'].sum()

# 予算配分を計算
qv_df['budget_allocation'] = (qv_df['votes'] / total_qv_votes) * budget
qv_df['percentage'] = (qv_df['votes'] / total_qv_votes) * 100

# ====== 3. 比較結果を出力 ======
print("比較結果を出力中...")

# 結果を保存
opov_df.to_csv('results/data/one_person_one_vote_results.csv', index=False)

# 比較結果をマージ
comparison = pd.merge(
    qv_df[['title', 'votes', 'budget_allocation', 'percentage']], 
    opov_df[['title', 'votes', 'budget_allocation', 'percentage']], 
    on='title', 
    suffixes=('_qv', '_opov')
)

# 差分を計算
comparison['votes_diff'] = comparison['votes_qv'] - comparison['votes_opov']
comparison['budget_diff'] = comparison['budget_allocation_qv'] - comparison['budget_allocation_opov']
comparison['percentage_diff'] = comparison['percentage_qv'] - comparison['percentage_opov']

# 降順でソート（QVの得票数順）
comparison = comparison.sort_values('votes_qv', ascending=False).reset_index(drop=True)

# 結果を保存
comparison.to_csv('results/data/voting_methods_comparison.csv', index=False)

# ====== 4. 不平等度の計算（ジニ係数） ======
print("不平等度（ジニ係数）を計算中...")

# ジニ係数の計算
qv_gini = gini(qv_df['budget_allocation'])
opov_gini = gini(opov_df['budget_allocation'])

# ====== 5. 可視化 ======
print("結果を可視化中...")

# 1. 投票数の比較（棒グラフ）
plt.figure(figsize=(12, 8))
bar_width = 0.35
x = np.arange(len(comparison))

# プロジェクト名を取得
projects = comparison['title'].tolist()

# QV方式の投票数
plt.bar(x - bar_width/2, comparison['votes_qv'], bar_width, label='Quadratic Voting', color='royalblue')

# 一人一票方式の投票数
plt.bar(x + bar_width/2, comparison['votes_opov'], bar_width, label='One Person One Vote', color='darkorange')

plt.xlabel('Projects')
plt.ylabel('Votes')
plt.title('Comparison of Voting Methods: Vote Distribution')
plt.xticks(x, projects, rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('results/figures/comparison/voting_methods_vote_comparison.png', dpi=300, bbox_inches='tight')
print("Saved voting methods comparison graph!")
plt.close()

# 2. 予算配分の比較（棒グラフ）
plt.figure(figsize=(12, 8))

# QV方式の予算配分
plt.bar(x - bar_width/2, comparison['budget_allocation_qv'], bar_width, label='Quadratic Voting', color='royalblue')

# 一人一票方式の予算配分
plt.bar(x + bar_width/2, comparison['budget_allocation_opov'], bar_width, label='One Person One Vote', color='darkorange')

plt.xlabel('Projects')
plt.ylabel('Budget Allocation (JPY)')
plt.title('Comparison of Voting Methods: Budget Allocation')
plt.xticks(x, projects, rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('results/figures/comparison/voting_methods_budget_comparison.png', dpi=300, bbox_inches='tight')
print("Saved budget comparison graph!")
plt.close()

# 3. パーセンテージの比較（棒グラフ）
plt.figure(figsize=(12, 8))

# QV方式のパーセンテージ
plt.bar(x - bar_width/2, comparison['percentage_qv'], bar_width, label='Quadratic Voting', color='royalblue')

# 一人一票方式のパーセンテージ
plt.bar(x + bar_width/2, comparison['percentage_opov'], bar_width, label='One Person One Vote', color='darkorange')

plt.xlabel('Projects')
plt.ylabel('Percentage (%)')
plt.title('Comparison of Voting Methods: Budget Percentage')
plt.xticks(x, projects, rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('results/figures/comparison/voting_methods_percentage_comparison.png', dpi=300, bbox_inches='tight')
print("Saved percentage comparison graph!")
plt.close()

# 4. 差分の比較（横棒グラフ）
plt.figure(figsize=(12, 8))

# 予算配分の差分
plt.barh(projects, comparison['budget_diff'], color=['royalblue' if x > 0 else 'darkorange' for x in comparison['budget_diff']])

plt.xlabel('Budget Difference (QV - OPOV) in JPY')
plt.ylabel('Projects')
plt.title('Budget Allocation Difference: QV vs. One-Person-One-Vote')
plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('results/figures/comparison/budget_difference.png', dpi=300, bbox_inches='tight')
print("Saved budget difference graph!")
plt.close()

# 5. ローレンツ曲線とジニ係数の可視化
plt.figure(figsize=(10, 8))

# 均等分布（理想的な平等）
plt.plot([0, 1], [0, 1], 'k--', label='Perfect Equality')

# QV方式のローレンツ曲線
x_qv, y_qv = lorenz_curve(qv_df['budget_allocation'].values)
plt.plot(x_qv, y_qv, 'b-', label=f'QV (Gini={qv_gini:.3f})')

# 一人一票方式のローレンツ曲線
x_opov, y_opov = lorenz_curve(opov_df['budget_allocation'].values)
plt.plot(x_opov, y_opov, 'r-', label=f'OPOV (Gini={opov_gini:.3f})')

plt.xlabel('Cumulative Share of Projects')
plt.ylabel('Cumulative Share of Budget')
plt.title('Lorenz Curves: Budget Inequality Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/figures/comparison/lorenz_curves.png', dpi=300, bbox_inches='tight')
print("Saved Lorenz curves graph!")
plt.close()

# 6. ジニ係数比較の可視化
plt.figure(figsize=(8, 6))
gini_values = [qv_gini, opov_gini]
labels = ['Quadratic Voting', 'One Person One Vote']
colors = ['royalblue', 'darkorange']

plt.bar(labels, gini_values, color=colors)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
plt.ylabel('Gini Coefficient')
plt.title('Inequality Comparison: Gini Coefficient')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('results/figures/comparison/voting_methods_gini_comparison.png', dpi=300, bbox_inches='tight')
print("Saved Gini coefficient comparison graph!")
plt.close()

# 結果をテキストファイルに保存
with open('results/reports/voting_methods_comparison.txt', 'w', encoding='utf-8') as f:
    f.write("# Voting Methods Comparison: QV vs One-Person-One-Vote\n\n")
    
    f.write("## Budget Allocation Comparison\n\n")
    f.write("| Project | QV Votes | OPOV Votes | QV Budget | OPOV Budget | QV % | OPOV % | Difference |\n")
    f.write("|---------|----------|------------|-----------|-------------|------|-------|------------|\n")
    
    for _, row in comparison.iterrows():
        f.write(f"| {row['title']} | {row['votes_qv']:.1f} | {row['votes_opov']:.1f} | "
                f"{row['budget_allocation_qv']:,.0f} | {row['budget_allocation_opov']:,.0f} | "
                f"{row['percentage_qv']:.1f}% | {row['percentage_opov']:.1f}% | "
                f"{row['budget_diff']:+,.0f} |\n")
    
    f.write("\n## Inequality Measures\n\n")
    f.write(f"- Quadratic Voting Gini Coefficient: {qv_gini:.3f}\n")
    f.write(f"- One-Person-One-Vote Gini Coefficient: {opov_gini:.3f}\n")
    
    if qv_gini < opov_gini:
        f.write(f"- Quadratic Voting results in a more equal budget distribution (lower Gini coefficient).\n")
    else:
        f.write(f"- One-Person-One-Vote results in a more equal budget distribution (lower Gini coefficient).\n")
    
    f.write("\n## Interpretation\n\n")
    f.write("Quadratic Voting allows voters to express the intensity of their preferences, ")
    f.write("which can result in a different budget allocation compared to traditional One-Person-One-Vote systems. ")
    f.write("The Gini coefficient measures the inequality of the distribution, with 0 being perfect equality ")
    f.write("and 1 being maximum inequality.\n\n")
    
    f.write("The differences observed in the allocation highlight how QV captures preference intensity, ")
    f.write("potentially leading to a more nuanced representation of collective preferences.")

print("\n比較分析が完了しました。結果は results/data, results/figures/comparison, results/reports ディレクトリに保存されています。") 