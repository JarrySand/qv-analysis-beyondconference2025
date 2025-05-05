import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib
# 標準フォントを使用
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# CSVファイルを読み込む
vote_summary = pd.read_csv('data/vote_summary.csv')
candidates = pd.read_csv('data/candidates.csv')
votes = pd.read_csv('data/votes.csv')

# 既に英語名がCSVに含まれている場合はtitle_enカラムを使用
use_english_titles = 'title_en' in vote_summary.columns
if use_english_titles:
    # 英語タイトルをメインのタイトルとして使用
    if 'title_original' not in vote_summary.columns:
        vote_summary['title_original'] = vote_summary['title']
    vote_summary['title'] = vote_summary['title_en']

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

# 出力ディレクトリの作成
os.makedirs('results/data', exist_ok=True)
os.makedirs('results/reports', exist_ok=True)
os.makedirs('results/figures/basic_analysis', exist_ok=True)

# 予算配分を含む結果を保存
vote_summary.to_csv('results/data/vote_summary_with_budget.csv', index=False, encoding='utf-8-sig')

try:
    # 1. 総投票数の棒グラフ
    plt.figure(figsize=(12, 8))
    # 英語のタイトルを使用
    sns.barplot(x='title', y='total_votes', data=vote_summary.sort_values(by='total_votes', ascending=False))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.title('Total Votes by Project')
    plt.savefig('results/figures/basic_analysis/total_votes.png', dpi=300)
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
    plt.savefig('results/figures/basic_analysis/budget_allocation.png', dpi=300)
    plt.close()
    print("予算配分グラフを生成しました")
except Exception as e:
    print(f"予算配分グラフの生成中にエラーが発生しました: {e}")

try:
    # 3. 投票者が投票した候補数の分布グラフ
    # 各投票者が何人の候補に投票したかカウント
    candidates_voted_counts = []
    
    # 投票者IDごとにユニークな行を取得
    for voter_id in votes['voter_id'].unique():
        # この投票者の行を取得
        voter_row = votes[votes['voter_id'] == voter_id].iloc[0]
        
        # 投票した候補数をカウント
        vote_count = 0
        for i in range(len(candidates)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]) and voter_row[col_name] > 0:
                vote_count += 1
        
        candidates_voted_counts.append(vote_count)
    
    # 分布カウント
    vote_count_distribution = pd.Series(candidates_voted_counts).value_counts().sort_index()
    
    # グラフ作成
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x=vote_count_distribution.index, y=vote_count_distribution.values)
    
    # 各棒の上に値を表示
    for i, v in enumerate(vote_count_distribution.values):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    plt.title('Distribution of Number of Candidates Voted by Voters')
    plt.xlabel('Number of Candidates Voted')
    plt.ylabel('Number of Voters')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('results/figures/basic_analysis/voters_voting_pattern.png', dpi=300)
    plt.close()
    print("投票した候補数分布グラフを生成しました")
except Exception as e:
    print(f"投票した候補数分布グラフの生成中にエラーが発生しました: {e}")

# テキスト形式でも結果を出力（英語で）
with open('results/reports/results_summary.txt', 'w', encoding='utf-8') as f:
    f.write("# Quadratic Voting Analysis Results\n\n")
    
    f.write("## Voting Results Summary\n")
    sorted_results = vote_summary.sort_values(by='total_votes', ascending=False)
    for _, row in sorted_results.iterrows():
        f.write(f"- {row['title']}: {row['total_votes']} votes (average: {row['average_vote']})\n")
    
    f.write("\n## Budget Allocation Results (250,000 JPY)\n")
    sorted_budget = vote_summary.sort_values(by='budget_allocation', ascending=False)
    for _, row in sorted_budget.iterrows():
        f.write(f"- {row['title']}: {row['budget_allocation']} JPY ({row['budget_allocation']/total_budget*100:.1f}%)\n")
    
    f.write("\n## Voter Participation Statistics\n")
    if 'vote_count_distribution' in locals():
        f.write("### Number of Candidates Voted Per Voter\n")
        for count, num_voters in vote_count_distribution.items():
            f.write(f"- {count} candidates: {num_voters} voters\n")
        f.write(f"\nAverage candidates voted per voter: {np.mean(candidates_voted_counts):.2f}\n")

# 予算配分テーブル
with open('results/reports/budget_allocation_table.txt', 'w', encoding='utf-8-sig') as f:
    f.write("# Budget Allocation Table\n\n")
    f.write("| Project Name | Votes | Budget (JPY) | Percentage |\n")
    f.write("|-------------|-------|---------|------|\n")
    
    sorted_budget = vote_summary.sort_values(by='budget_allocation', ascending=False)
    for _, row in sorted_budget.iterrows():
        f.write(f"| {row['title']} | {row['total_votes']} | {row['budget_allocation']:,} | {row['budget_allocation']/total_budget*100:.1f}% |\n")

# 日本語と英語の対応表を作成（title_originalがある場合のみ）
if use_english_titles and 'title_original' in vote_summary.columns:
    with open('results/reports/project_name_mapping.txt', 'w', encoding='utf-8-sig') as f:
        f.write("# プロジェクト名対応表 / Project Name Mapping\n\n")
        f.write("| Original Japanese Name | English Name |\n")
        f.write("|------------------------|-------------|\n")
        for _, row in vote_summary.iterrows():
            if row['title_original'] != row['title_en'] and row['title_en'] != 'JINEN TRAVEL':  # 既に英語なので除外
                f.write(f"| {row['title_original']} | {row['title_en']} |\n")

print("\n分析が完了しました。結果は results フォルダに保存されています。") 