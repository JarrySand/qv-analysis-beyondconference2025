import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats

# グラフのフォントエンコーディングを設定
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# 分析結果フォルダを作成
os.makedirs('results/data', exist_ok=True)
os.makedirs('results/reports', exist_ok=True)
os.makedirs('results/figures/statistics', exist_ok=True)

# データ読み込み
votes = pd.read_csv('data/votes.csv')
vote_summary = pd.read_csv('data/vote_summary.csv')
candidates = pd.read_csv('data/candidates.csv')

# 英語名を使用するためのデータフレーム準備
use_english_titles = 'title_en' in candidates.columns
if use_english_titles:
    # 元のタイトルを保存
    if 'title_original' not in vote_summary.columns:
        vote_summary['title_original'] = vote_summary['title']
    # 英語タイトルを使用
    vote_summary['title'] = vote_summary['title_en']

# 候補者ごとの投票データを抽出
vote_data = {}
for i in range(len(candidates)):
    col_name = f'candidate_{i}'
    if col_name in votes.columns:
        # 候補者名を取得（英語名を使用）
        if use_english_titles:
            cand_name = candidates.iloc[i]['title_en']
        else:
            cand_name = candidates.iloc[i]['title']
        
        # 投票データを取得
        vote_data[cand_name] = votes[col_name].dropna().values

# 基礎統計量を計算
stats_data = []
for project, data in vote_data.items():
    # ゼロ票を除外したデータ（Quadratic Votingでは0票は投票していないと解釈）
    non_zero_data = data[data > 0]
    
    stats_dict = {
        'Project': project,
        'Total Votes': sum(data),  # 合計票
        'Mean': np.mean(non_zero_data) if len(non_zero_data) > 0 else 0,  # 平均（0票を除く）
        'Median': np.median(non_zero_data) if len(non_zero_data) > 0 else 0,  # 中央値（0票を除く）
        'Std Dev': np.std(non_zero_data) if len(non_zero_data) > 0 else 0,  # 標準偏差（0票を除く）
        'Min': np.min(non_zero_data) if len(non_zero_data) > 0 else 0,  # 最小値（0票を除く）
        'Max': np.max(data),  # 最大値
        'Voters': len(non_zero_data),  # 投票者数（0票を除く）
        'Mode': stats.mode(non_zero_data)[0] if len(non_zero_data) > 0 else 0,  # 最頻値（0票を除く）
        'Zero Votes': np.sum(data == 0),  # 0票の数
    }
    stats_data.append(stats_dict)

# DataFrameに変換
stats_df = pd.DataFrame(stats_data)

# 予算配分を計算（総投票数に比例）
total_budget = 250000  # 総予算（円）
total_votes = stats_df['Total Votes'].sum()

# 各プロジェクトの予算配分計算
for i, row in stats_df.iterrows():
    vote_share = row['Total Votes'] / total_votes if total_votes > 0 else 0
    stats_df.loc[i, 'Budget Allocation'] = vote_share * total_budget
    stats_df.loc[i, 'Budget Percentage'] = vote_share * 100

# 合計得票数で降順ソート
stats_df = stats_df.sort_values(by='Total Votes', ascending=False)

# CSVファイルとして保存
stats_df.to_csv('results/data/voting_statistics.csv', index=False, encoding='utf-8-sig')

# テキスト形式でも統計情報を出力
with open('results/reports/statistics_report.txt', 'w', encoding='utf-8') as f:
    f.write("# Quadratic Voting Statistical Report\n\n")
    
    f.write("## Basic Statistics by Project\n\n")
    for _, row in stats_df.iterrows():
        f.write(f"### {row['Project']}\n")
        f.write(f"- Total Votes: {row['Total Votes']:.0f}\n")
        f.write(f"- Number of Voters: {row['Voters']:.0f}\n")
        f.write(f"- Mean Vote Value: {row['Mean']:.2f}\n")
        f.write(f"- Median Vote Value: {row['Median']:.1f}\n")
        f.write(f"- Most Common Vote (Mode): {row['Mode']:.0f}\n")
        f.write(f"- Standard Deviation: {row['Std Dev']:.2f}\n")
        f.write(f"- Min Vote: {row['Min']:.0f}\n")
        f.write(f"- Max Vote: {row['Max']:.0f}\n")
        f.write(f"- Number of Zero Votes: {row['Zero Votes']:.0f}\n")
        f.write(f"- Budget Allocation: {row['Budget Allocation']:,.0f} JPY ({row['Budget Percentage']:.1f}%)\n")
        f.write("\n")
    
    # 全体の投票データに関する統計情報
    f.write("## Overall Voting Statistics\n\n")
    
    # 投票者数（ユニークな投票者ID）
    total_voters = len(votes['voter_id'].unique())
    f.write(f"- Total Number of Voters: {total_voters}\n")
    
    # 合計投票数
    total_votes = sum([np.sum(data > 0) for data in vote_data.values()])
    f.write(f"- Total Number of Votes Cast: {total_votes}\n")
    
    # 平均投票先数（1人あたり何プロジェクトに投票したか）
    avg_projects_per_voter = total_votes / total_voters
    f.write(f"- Average Number of Projects Voted Per Person: {avg_projects_per_voter:.2f}\n")
    
    # 投票者1人あたりの平均投票ポイント
    total_points = sum([np.sum(data) for data in vote_data.values()])
    avg_points_per_voter = total_points / total_voters
    f.write(f"- Average Points Used Per Voter: {avg_points_per_voter:.2f}\n")
    
    # 最も多くのポイントを獲得したプロジェクト
    max_points_project = stats_df.iloc[0]['Project']
    max_points = stats_df.iloc[0]['Total Votes']
    f.write(f"- Project with Most Points: {max_points_project} ({max_points:.0f} points)\n")
    
    # 最も多くの投票者を獲得したプロジェクト
    most_voters_project = stats_df.sort_values(by='Voters', ascending=False).iloc[0]['Project']
    most_voters_count = stats_df.sort_values(by='Voters', ascending=False).iloc[0]['Voters']
    f.write(f"- Project with Most Voters: {most_voters_project} ({most_voters_count:.0f} voters)\n")

# HTML形式のレポートも作成（視覚的に整った統計情報）
with open('results/reports/statistics_report.html', 'w', encoding='utf-8') as f:
    # 全体の投票データに関する統計情報を変数に格納
    total_voters = len(votes['voter_id'].unique())
    total_votes_cast = sum([np.sum(data > 0) for data in vote_data.values()])
    avg_projects_per_voter = total_votes_cast / total_voters
    total_points = sum([np.sum(data) for data in vote_data.values()])
    avg_points_per_voter = total_points / total_voters
    max_points_project = stats_df.iloc[0]['Project']
    max_points = stats_df.iloc[0]['Total Votes']
    most_voters_project = stats_df.sort_values(by='Voters', ascending=False).iloc[0]['Project']
    most_voters_count = stats_df.sort_values(by='Voters', ascending=False).iloc[0]['Voters']
    
    # HTML開始
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Quadratic Voting Analysis - Statistical Report</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { text-align: left; padding: 12px; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .project-section { margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .stat-label { font-weight: bold; color: #555; }
        .summary-box { background-color: #edf6ff; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Quadratic Voting Statistical Report</h1>
    
    <div class="summary-box">
        <h2>Overall Summary</h2>"""
    
    # 要約情報を追加
    html += f"""
        <p><span class="stat-label">Total Number of Voters:</span> {total_voters}</p>
        <p><span class="stat-label">Total Number of Votes Cast:</span> {total_votes_cast}</p>
        <p><span class="stat-label">Average Number of Projects Voted Per Person:</span> {avg_projects_per_voter:.2f}</p>
        <p><span class="stat-label">Average Points Used Per Voter:</span> {avg_points_per_voter:.2f}</p>
        <p><span class="stat-label">Project with Most Points:</span> {max_points_project} ({max_points:.0f} points)</p>
        <p><span class="stat-label">Project with Most Voters:</span> {most_voters_project} ({most_voters_count:.0f} voters)</p>
    </div>
    
    <h2>Statistical Data by Project</h2>
    <table>
        <tr>
            <th>Project</th>
            <th>Total Votes</th>
            <th>Voters</th>
            <th>Mean</th>
            <th>Median</th>
            <th>Mode</th>
            <th>Std Dev</th>
            <th>Budget (JPY)</th>
            <th>Budget %</th>
        </tr>"""
    
    # テーブルのデータ行を追加
    for _, row in stats_df.iterrows():
        html += f"""
        <tr>
            <td>{row['Project']}</td>
            <td>{row['Total Votes']:.0f}</td>
            <td>{row['Voters']:.0f}</td>
            <td>{row['Mean']:.2f}</td>
            <td>{row['Median']:.1f}</td>
            <td>{row['Mode']:.0f}</td>
            <td>{row['Std Dev']:.2f}</td>
            <td>{row['Budget Allocation']:,.0f}</td>
            <td>{row['Budget Percentage']:.1f}%</td>
        </tr>"""
    
    # HTML終了
    html += """
    </table>
    
    <div class="summary-box">
        <h2>Interpretation</h2>
        <p>This report shows the statistical analysis of the Quadratic Voting results. The budget allocation is proportional to the total votes received by each project.</p>
        <p>Quadratic Voting allows voters to express the intensity of their preferences by allocating points across different projects. The statistics above reflect both the breadth (number of voters) and depth (intensity of preference) for each project.</p>
    </div>
</body>
</html>"""
    
    # HTMLファイルに書き込み
    f.write(html)

# プロジェクト別の投票分布グラフも作成
try:
    for project, data in vote_data.items():
        # 非ゼロデータのみ使用
        non_zero_data = data[data > 0]
        if len(non_zero_data) > 0:
            plt.figure(figsize=(10, 6))
            # ヒストグラム作成（1-9の範囲で）
            plt.hist(non_zero_data, bins=range(1, 11), alpha=0.7, color='skyblue', edgecolor='black')
            plt.title(f'Vote Distribution for {project}')
            plt.xlabel('Vote Value')
            plt.ylabel('Number of Voters')
            plt.xticks(range(1, 10))
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # ファイル名に使える形式にプロジェクト名を変換
            safe_name = project.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
            plt.savefig(f'results/figures/statistics/vote_dist_{safe_name}.png', dpi=300)
            plt.close()
    
    print("プロジェクト別投票分布グラフを生成しました")
except Exception as e:
    print(f"グラフ生成中にエラーが発生しました: {e}")

print("\n統計分析が完了しました。結果は results フォルダに保存されています。")
print("- voting_statistics.csv: 統計データのCSVファイル")
print("- statistics_report.txt: テキスト形式の統計レポート")
print("- statistics_report.html: HTML形式の視覚的な統計レポート") 