import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# データの読み込み
votes_df = pd.read_csv('votes.csv')
candidates_df = pd.read_csv('candidates.csv')

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

# 候補者名を英語名に変換
candidates_df_en = candidates_df.copy()
for i, row in candidates_df.iterrows():
    title = row['title']
    if title in project_names:
        candidates_df_en.at[i, 'title'] = project_names[title]
    else:
        candidates_df_en.at[i, 'title'] = title

# 「埋もれた声」を可視化するグラフ作成
def create_buried_voices_graph():
    # 各投票者の最大投票ポイントを特定
    max_votes = {}
    buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        voter_id = voter_row['voter_id']
        max_vote = 0
        max_candidate = None
        
        # 各候補への投票を確認
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                
                # 最大投票の更新
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
                
                # 強い選好（4以上のポイント）だが最大でない場合、埋もれた声としてカウント
                if vote_value >= 4 and vote_value < max_vote:
                    buried_voices[i] += 1
        
        # この投票者の最大投票を記録
        max_votes[voter_id] = (max_candidate, max_vote)
    
    # グラフ作成
    plt.figure(figsize=(12, 8))
    x = np.arange(len(candidates_df))
    
    # 英語のプロジェクト名を取得
    projects = [project_names.get(title, title) for title in candidates_df['title'].tolist()]
    
    # 埋もれた声の数をグラフ化
    plt.bar(x, [buried_voices[i] for i in range(len(candidates_df))], color='darkred')
    
    plt.xlabel('Projects')
    plt.ylabel('Number of Strong Preferences Not Reflected in One-Person-One-Vote')
    plt.title('Hidden Voices Captured by Quadratic Voting')
    plt.xticks(x, projects, rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('comparison_simulation/buried_voices.png', dpi=300, bbox_inches='tight')
    
    # データも保存
    buried_df = pd.DataFrame({
        'project': projects,
        'buried_voices': [buried_voices[i] for i in range(len(candidates_df))]
    })
    buried_df.to_csv('comparison_simulation/buried_voices.csv', index=False)
    
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
    
    # ヒートマップ作成
    plt.figure(figsize=(12, 8))
    
    # カスタムカラーマップ（赤→オレンジ→黄色→白）
    colors = [(0.8, 0, 0), (1, 0.4, 0), (1, 0.8, 0), (1, 1, 1)]
    cmap = LinearSegmentedColormap.from_list('custom_heatmap', colors)
    
    # 英語のプロジェクト名を取得
    projects = [project_names.get(title, title) for title in candidates_df['title'].tolist()]
    
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
    plt.savefig('comparison_simulation/preference_intensity_heatmap.png', dpi=300, bbox_inches='tight')

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
    
    # グラフ作成
    plt.figure(figsize=(14, 10))
    
    x = np.arange(len(candidates_df))
    bar_width = 0.35
    
    # 英語のプロジェクト名を取得
    projects = [project_names.get(title, title) for title in candidates_df['title'].tolist()]
    
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
    
    plt.savefig('comparison_simulation/preference_intensity_comparison.png', dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    print("「埋もれた声」を可視化するグラフを作成中...")
    create_buried_voices_graph()
    
    print("選好強度ヒートマップを作成中...")
    create_preference_intensity_heatmap()
    
    print("選好強度比較グラフを作成中...")
    create_preference_intensity_comparison()
    
    print("グラフの作成が完了しました。結果は comparison_simulation ディレクトリに保存されています。") 