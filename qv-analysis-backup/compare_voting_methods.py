import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# Define our own gini function since it's not in scipy.stats
def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    # Convert pandas Series to numpy array if needed
    if isinstance(array, pd.Series):
        array = array.values
    
    # All values need to be positive for Gini calculation
    array = np.array(array, dtype=float)
    
    # If array is empty or contains only zeros, return 0
    if len(array) == 0 or np.all(array == 0):
        return 0.0
    
    # Sort array
    array = np.sort(array)
    # Get indices
    index = np.arange(1, array.shape[0] + 1)
    # Compute Gini coefficient
    n = array.shape[0]
    return ((2 * np.sum(index * array)) / (n * np.sum(array))) - ((n + 1) / n)

# 分析結果フォルダを作成
os.makedirs('analysis_results', exist_ok=True)

# データ読み込み
print("データを読み込み中...")
votes_df = pd.read_csv('votes.csv')
candidates_df = pd.read_csv('candidates.csv')
vote_summary = pd.read_csv('vote_summary.csv')

# 元のJSONファイルからも読み込み
with open('election.json', 'r', encoding='utf-8') as file:
    election_data = json.load(file)

# 英語名マッピング
project_names = {
    '10代・20代の「いま、やりたい」を後押しする拠点　ちばユースセンターPRISM': 'Chiba Youth Center PRISM',
    'ちばユースセンターPRISM': 'Chiba Youth Center PRISM',
    '政を祭に変える #vote_forプロジェクト': '#vote_for Project',
    '#vote_forプロジェクト': '#vote_for Project',
    '淡路島クエストカレッジ': 'Awaji Island Quest College',
    'イナトリアートセンター計画': 'Inatori Art Center Plan',
    'JINEN TRAVEL': 'JINEN TRAVEL',
    'ビオ田んぼプロジェクト': 'Bio Rice Field Project',
    'パラ旅応援団': 'Para Travel Support Team'
}

# マッピングを反転（日本語名→英語名）
reverse_project_names = {jp: en for en, jp in project_names.items()}

# 候補者名を英語名に変換
for i, row in candidates_df.iterrows():
    title = row['title']
    if title in project_names:
        candidates_df.at[i, 'title_en'] = project_names[title]
    else:
        candidates_df.at[i, 'title_en'] = title

# タイトルを変更
for orig, eng in project_names.items():
    vote_summary.loc[vote_summary['title'] == orig, 'title'] = eng

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
    cand_name = candidates_df[candidates_df['candidate_id'] == cand_id]['title_en'].iloc[0]
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
opov_df.to_csv('analysis_results/one_person_one_vote_results.csv', index=False)

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
comparison.to_csv('analysis_results/voting_methods_comparison.csv', index=False)

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
plt.savefig('analysis_results/voting_methods_vote_comparison.png', dpi=300, bbox_inches='tight')
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
plt.savefig('analysis_results/voting_methods_budget_comparison.png', dpi=300, bbox_inches='tight')
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
plt.savefig('analysis_results/voting_methods_percentage_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. ジニ係数の比較（棒グラフ）
plt.figure(figsize=(8, 6))
plt.bar(['Quadratic Voting', 'One Person One Vote'], [qv_gini, opov_gini], color=['royalblue', 'darkorange'])
plt.ylabel('Gini Coefficient')
plt.title('Inequality of Budget Allocation (Gini Coefficient)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('analysis_results/voting_methods_gini_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. ローレンツ曲線の作成
def lorenz_curve(values):
    # 値を昇順にソート
    values_sorted = np.sort(values)
    # 累積和を計算
    values_cumsum = np.cumsum(values_sorted)
    # 正規化
    values_cumsum_normalized = values_cumsum / values_cumsum[-1]
    # x軸の値（累積人口割合）
    x = np.linspace(0, 1, len(values))
    return x, values_cumsum_normalized

plt.figure(figsize=(8, 8))

# 完全平等線
plt.plot([0, 1], [0, 1], 'k--', label='Perfect Equality')

# QV方式のローレンツ曲線
x_qv, y_qv = lorenz_curve(qv_df['budget_allocation'])
plt.plot(x_qv, y_qv, 'royalblue', label=f'Quadratic Voting (Gini={qv_gini:.3f})')

# 一人一票方式のローレンツ曲線
x_opov, y_opov = lorenz_curve(opov_df['budget_allocation'])
plt.plot(x_opov, y_opov, 'darkorange', label=f'One Person One Vote (Gini={opov_gini:.3f})')

plt.xlabel('Cumulative Share of Projects')
plt.ylabel('Cumulative Share of Budget')
plt.title('Lorenz Curve of Budget Allocation')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.savefig('analysis_results/voting_methods_lorenz_curve.png', dpi=300, bbox_inches='tight')
plt.close()

# ====== 6. テキストレポートの生成 ======
print("テキストレポートを生成中...")

with open('analysis_results/voting_methods_comparison_report.txt', 'w', encoding='utf-8') as f:
    f.write("# 投票方式の比較分析レポート\n\n")
    
    f.write("## 概要\n\n")
    f.write(f"- 投票者数: {len(votes_df['voter_id'].unique())}\n")
    f.write(f"- 候補プロジェクト数: {len(candidates_df)}\n")
    f.write(f"- 総予算: {budget:,} 円\n\n")
    
    f.write("## 二次投票方式 (Quadratic Voting) と一人一票方式の比較\n\n")
    f.write("### 投票結果\n\n")
    
    for i, row in comparison.iterrows():
        f.write(f"{i+1}. {row['title']}\n")
        f.write(f"   - QV方式得票: {row['votes_qv']:.1f} 票 ({row['percentage_qv']:.1f}%)\n")
        f.write(f"   - 一人一票方式得票: {row['votes_opov']:.1f} 票 ({row['percentage_opov']:.1f}%)\n")
        f.write(f"   - 差分: {row['votes_diff']:.1f} 票 ({row['percentage_diff']:.1f}%)\n\n")
    
    f.write("### 予算配分\n\n")
    
    for i, row in comparison.iterrows():
        f.write(f"{i+1}. {row['title']}\n")
        f.write(f"   - QV方式配分: {row['budget_allocation_qv']:,.0f} 円 ({row['percentage_qv']:.1f}%)\n")
        f.write(f"   - 一人一票方式配分: {row['budget_allocation_opov']:,.0f} 円 ({row['percentage_opov']:.1f}%)\n")
        f.write(f"   - 差分: {row['budget_diff']:,.0f} 円 ({row['percentage_diff']:.1f}%)\n\n")
    
    f.write("### 不平等度分析\n\n")
    f.write(f"- QV方式のジニ係数: {qv_gini:.4f}\n")
    f.write(f"- 一人一票方式のジニ係数: {opov_gini:.4f}\n")
    f.write(f"- 差分: {qv_gini - opov_gini:.4f}\n\n")
    
    if qv_gini < opov_gini:
        f.write("※ QV方式の方が予算配分の不平等度が低いです（より公平な配分）\n\n")
    else:
        f.write("※ 一人一票方式の方が予算配分の不平等度が低いです（より公平な配分）\n\n")
    
    f.write("## 分析結果の考察\n\n")
    f.write("- QV方式と一人一票方式の主な違いは、投票の強度を表現できるかどうかにあります。\n")
    f.write("- QV方式では、強い選好を持つ投票者が自分のポイントを特定のプロジェクトに集中投資できます。\n")
    f.write("- 一人一票方式では、全ての投票者の意見が同じ重みを持ちますが、選好の強さを表現できません。\n")
    f.write("- ジニ係数の比較から、どちらの方式がより公平な予算配分を実現するかを客観的に評価できます。\n")

print("分析が完了しました。結果は analysis_results ディレクトリに保存されています。") 