import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib
# 標準フォントを使用
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# CSVファイルを読み込む
vote_summary = pd.read_csv('vote_summary.csv')
candidates = pd.read_csv('candidates.csv')
votes = pd.read_csv('votes.csv')

# プロジェクト名を英語表記に変更
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

# タイトルを変更
for orig, eng in project_names.items():
    vote_summary.loc[vote_summary['title'] == orig, 'title'] = eng

# コンソールに集計結果を表示
print("===== 投票結果の概要 =====")
print(vote_summary.sort_values(by='total_votes', ascending=False))

# 予算配分の計算
total_budget = 250000  # 25万円
total_votes = vote_summary['total_votes'].sum()
vote_summary['budget_allocation'] = (vote_summary['total_votes'] / total_votes) * total_budget
vote_summary['budget_allocation'] = vote_summary['budget_allocation'].round().astype(int)

print("\n===== 予算配分結果 =====")
print(vote_summary[['candidate_id', 'title', 'total_votes', 'budget_allocation']].sort_values(by='budget_allocation', ascending=False))

# フォルダ作成
os.makedirs('analysis_results', exist_ok=True)

# CSVファイルに結果を保存
vote_summary.to_csv('analysis_results/vote_summary_with_budget.csv', index=False, encoding='utf-8-sig')

try:
    # 1. 総投票数の棒グラフ
    plt.figure(figsize=(12, 8))
    # 英語のタイトルを使用
    sns.barplot(x='title', y='total_votes', data=vote_summary.sort_values(by='total_votes', ascending=False))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.title('Total Votes by Project')
    plt.savefig('analysis_results/total_votes.png', dpi=300)
    plt.close()
    print("総投票数グラフを生成しました")
except Exception as e:
    print(f"総投票数グラフの生成中にエラーが発生しました: {e}")

try:
    # 2. 予算配分の円グラフ
    plt.figure(figsize=(12, 10))
    vote_summary_sorted = vote_summary.sort_values(by='budget_allocation', ascending=False)
    # 英語のラベルに予算額を追加
    labels = [f'{title} ({budget:,} JPY)' for title, budget in zip(vote_summary_sorted['title'], vote_summary_sorted['budget_allocation'])]
    plt.pie(vote_summary_sorted['budget_allocation'], 
            labels=labels,
            autopct='%1.1f%%',
            startangle=90)
    plt.axis('equal')
    plt.title('Budget Allocation (250,000 JPY)')
    plt.tight_layout()
    plt.savefig('analysis_results/budget_allocation.png', dpi=300)
    plt.close()
    print("予算配分グラフを生成しました")
except Exception as e:
    print(f"予算配分グラフの生成中にエラーが発生しました: {e}")

# テキスト形式でも結果を出力（英語で）
with open('analysis_results/results_summary.txt', 'w', encoding='utf-8') as f:
    f.write("# Quadratic Voting Analysis Results\n\n")
    
    f.write("## Voting Results Summary\n")
    sorted_results = vote_summary.sort_values(by='total_votes', ascending=False)
    for _, row in sorted_results.iterrows():
        f.write(f"- {row['title']}: {row['total_votes']} votes (average: {row['average_vote']})\n")
    
    f.write("\n## Budget Allocation Results (250,000 JPY)\n")
    sorted_budget = vote_summary.sort_values(by='budget_allocation', ascending=False)
    for _, row in sorted_budget.iterrows():
        f.write(f"- {row['title']}: {row['budget_allocation']} JPY ({row['budget_allocation']/total_budget*100:.1f}%)\n")

# 予算配分テーブル
with open('analysis_results/budget_allocation_table.txt', 'w', encoding='utf-8-sig') as f:
    f.write("# Budget Allocation Table\n\n")
    f.write("| Project Name | Votes | Budget (JPY) | Percentage |\n")
    f.write("|-------------|-------|---------|------|\n")
    
    sorted_budget = vote_summary.sort_values(by='budget_allocation', ascending=False)
    for _, row in sorted_budget.iterrows():
        f.write(f"| {row['title']} | {row['total_votes']} | {row['budget_allocation']:,} | {row['budget_allocation']/total_budget*100:.1f}% |\n")

# 日本語と英語の対応表を作成
with open('analysis_results/project_name_mapping.txt', 'w', encoding='utf-8-sig') as f:
    f.write("# プロジェクト名対応表 / Project Name Mapping\n\n")
    f.write("| Original Japanese Name | English Name |\n")
    f.write("|------------------------|-------------|\n")
    for jp, en in project_names.items():
        if jp != 'JINEN TRAVEL':  # 既に英語なので除外
            f.write(f"| {jp} | {en} |\n")

print("\n分析が完了しました。結果は analysis_results フォルダに保存されています。") 