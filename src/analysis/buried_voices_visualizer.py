import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import os

# データの読み込み
votes_df = pd.read_csv('data/votes.csv')
candidates_df = pd.read_csv('data/candidates.csv')

# 英語名を使用するためのDataFrame作成
candidates_df_en = candidates_df.copy()
if 'title_en' in candidates_df.columns:
    # 英語名カラムが存在する場合、それをタイトルとして使用
    candidates_df_en['title'] = candidates_df['title_en']

# 「埋もれた声」を可視化するグラフ作成
def create_buried_voices_graph():
    # 各投票者の最大投票ポイントを特定
    max_votes = {}
    buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        voter_id = voter_row['voter_id']
        max_vote = 0
        max_candidate = None
        
        # 最大投票を特定（ステップ1）
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
        
        # この投票者の最大投票を記録
        if max_candidate is not None:
            max_votes[voter_id] = (max_candidate, max_vote)
            
            # 埋もれた声の計算（修正版アルゴリズム）
            # 投票値が最大投票の70%以上かつ3以上、かつ最大投票ではないものを「埋もれた声」としてカウント
            for i in range(len(candidates_df)):
                col_name = f'candidate_{i}'
                if col_name in voter_row and not pd.isna(voter_row[col_name]):
                    vote_value = voter_row[col_name]
                    if vote_value > max_vote * 0.7 and vote_value >= 3 and i != max_candidate:
                        buried_voices[i] += 1
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs('results/figures/comparison', exist_ok=True)
    
    # グラフ作成
    plt.figure(figsize=(12, 8))
    x = np.arange(len(candidates_df))
    
    # 英語のプロジェクト名を取得
    projects = candidates_df_en['title'].tolist()
    
    # 埋もれた声の数をグラフ化
    plt.bar(x, [buried_voices[i] for i in range(len(candidates_df))], color='darkred')
    
    plt.xlabel('Projects')
    plt.ylabel('Number of Strong Preferences Not Reflected in One-Person-One-Vote')
    plt.title('Hidden Voices Captured by Quadratic Voting')
    plt.xticks(x, projects, rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('results/figures/comparison/buried_voices.png', dpi=300, bbox_inches='tight')
    
    # データも保存
    os.makedirs('results/data', exist_ok=True)
    buried_df = pd.DataFrame({
        'project': projects,
        'buried_voices': [buried_voices[i] for i in range(len(candidates_df))]
    })
    buried_df.to_csv('results/data/buried_voices.csv', index=False)
    
    return buried_voices

# 投票強度のヒートマップを作成
def create_preference_intensity_heatmap():
    # 投票強度の分布を集計 (0-9の10段階)
    intensity_matrix = np.zeros((len(candidates_df), 10))
    
    for _, voter_row in votes_df.iterrows():
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = int(voter_row[col_name])
                if 0 <= vote_value <= 9:  # 範囲チェック
                    intensity_matrix[i, vote_value] += 1
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs('results/figures/comparison', exist_ok=True)
    
    # ヒートマップ作成
    plt.figure(figsize=(12, 8))
    
    # カスタムカラーマップ（赤→オレンジ→黄色→白）
    colors = [(0.8, 0, 0), (1, 0.4, 0), (1, 0.8, 0), (1, 1, 1)]
    cmap = LinearSegmentedColormap.from_list('custom_heatmap', colors)
    
    # 英語のプロジェクト名を取得
    projects = candidates_df_en['title'].tolist()
    
    ax = sns.heatmap(intensity_matrix, 
                     annot=True, 
                     fmt='g', 
                     cmap=cmap,
                     linewidths=.5,
                     cbar_kws={'label': 'Number of Voters'})
    
    # 軸ラベル
    ax.set_xlabel('Vote Intensity (0-9)')
    ax.set_ylabel('Projects')
    plt.title('Vote Intensity Distribution in Quadratic Voting')
    
    # Y軸のラベル（英語名を使用）
    plt.yticks(np.arange(0.5, len(candidates_df)+0.5), projects, rotation=0)
    
    # X軸のラベル
    plt.xticks(np.arange(0.5, 10.5), ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
    
    # 一人一票では反映されない部分に枠線を追加
    for i in range(len(candidates_df)):
        # 最大投票部分のみが反映されるので、最後の列に注目
        ax.add_patch(plt.Rectangle((9, i), 1, 1, fill=False, edgecolor='blue', lw=2, clip_on=False))
        ax.text(9.5, i+0.5, "Reflected in\nOne-Person-One-Vote", ha='center', va='center', fontsize=8, color='blue')
    
    plt.tight_layout()
    plt.savefig('results/figures/comparison/preference_intensity_heatmap.png', dpi=300, bbox_inches='tight')

# 「埋もれていた選好強度」を可視化
def create_preference_intensity_comparison():
    # 各投票者のデータを分析
    opov_votes = np.zeros(len(candidates_df))
    qv_intensity_by_level = {
        'weak': np.zeros(len(candidates_df)),   # 1-3ポイント
        'medium': np.zeros(len(candidates_df)), # 4-6ポイント
        'strong': np.zeros(len(candidates_df))  # 7-9ポイント
    }
    
    for _, voter_row in votes_df.iterrows():
        max_vote = 0
        max_candidate = None
        
        # 各候補への投票を分析
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                
                # 最大投票の特定（一人一票方式用）
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
                
                # QV方式の選好強度に基づく分類
                if 1 <= vote_value <= 3:
                    qv_intensity_by_level['weak'][i] += 1
                elif 4 <= vote_value <= 6:
                    qv_intensity_by_level['medium'][i] += 1
                elif 7 <= vote_value <= 9:
                    qv_intensity_by_level['strong'][i] += 1
        
        # 一人一票シミュレーション
        if max_candidate is not None:
            opov_votes[max_candidate] += 1
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs('results/figures/comparison', exist_ok=True)
    
    # グラフ作成
    plt.figure(figsize=(14, 10))
    
    x = np.arange(len(candidates_df))
    bar_width = 0.35
    
    # 英語のプロジェクト名を取得
    projects = candidates_df_en['title'].tolist()
    
    # QV方式の積み上げ棒グラフ
    plt.bar(x - bar_width/2, qv_intensity_by_level['weak'], bar_width,
            label='Weak Preference (1-3 points)', color='#FFC107', alpha=0.7)
    plt.bar(x - bar_width/2, qv_intensity_by_level['medium'], bar_width,
            bottom=qv_intensity_by_level['weak'], 
            label='Medium Preference (4-6 points)', color='#FF9800', alpha=0.7)
    plt.bar(x - bar_width/2, qv_intensity_by_level['strong'], bar_width,
            bottom=qv_intensity_by_level['weak'] + qv_intensity_by_level['medium'],
            label='Strong Preference (7-9 points)', color='#F44336', alpha=0.7)
    
    # 一人一票方式の棒グラフ
    plt.bar(x + bar_width/2, opov_votes, bar_width, 
            label='One-Person-One-Vote', color='#2196F3', alpha=0.7)
    
    # グラフ装飾
    plt.xlabel('Projects')
    plt.ylabel('Number of Voters')
    plt.title('Preference Intensity in QV vs. One-Person-One-Vote')
    plt.xticks(x, projects, rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # 強い選好だけで一人一票方式の結果を上回る部分に注釈
    for i in range(len(candidates_df)):
        if qv_intensity_by_level['strong'][i] > opov_votes[i]:
            plt.annotate('Strong preferences alone\nexceed OPOV votes',
                         xy=(i - bar_width/2, qv_intensity_by_level['weak'][i] + 
                             qv_intensity_by_level['medium'][i] + 
                             qv_intensity_by_level['strong'][i]),
                         xytext=(i - bar_width/2, qv_intensity_by_level['weak'][i] + 
                                qv_intensity_by_level['medium'][i] + 
                                qv_intensity_by_level['strong'][i] + 5),
                         arrowprops=dict(facecolor='black', shrink=0.05),
                         ha='center')
    
    plt.savefig('results/figures/comparison/preference_intensity_comparison.png', dpi=300, bbox_inches='tight')

# 埋もれた声の計算結果の詳細出力
def print_buried_voices_details(buried_voices):
    print("\n=== 埋もれた声の計算結果 ===")
    for i in range(len(candidates_df)):
        print(f"{i}. {candidates_df_en.loc[i, 'title']}: {buried_voices[i]}票")
    
    # HTML/JSで報告されていた値との比較
    html_buried = [21, 15, 14, 10, 9, 8, 7]
    html_projects = [
        'Chiba Youth Center PRISM',
        'Bio Rice Field Project',
        'Para Travel Support Team',
        'Awaji Island Quest College',
        'Inatori Art Center Plan',
        'JINEN TRAVEL',
        '#vote_for Project'
    ]
    
    print("\n=== HTML/JSの値と計算結果の比較 ===")
    for i, project in enumerate(html_projects):
        for j in range(len(candidates_df)):
            if candidates_df_en.loc[j, 'title'] == project:
                print(f"{project}: HTML/JS:{html_buried[i]} vs 計算:{buried_voices[j]}")

if __name__ == "__main__":
    print("「埋もれた声」を可視化するグラフを作成中...")
    buried_voices = create_buried_voices_graph()
    print_buried_voices_details(buried_voices)
    
    print("\n選好強度ヒートマップを作成中...")
    create_preference_intensity_heatmap()
    
    print("\n選好強度比較グラフを作成中...")
    create_preference_intensity_comparison()
    
    print("\nグラフの作成が完了しました。結果は以下のディレクトリに保存されています：")
    print("- 画像: results/figures/comparison/")
    print("- データ: results/data/")
    print("\n注意: 埋もれた声のカウント条件は「vote_value > max_vote * 0.7 and vote_value >= 3 and i != max_candidate」です。") 