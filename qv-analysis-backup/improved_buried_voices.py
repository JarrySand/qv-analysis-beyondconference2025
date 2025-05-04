import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

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

# 「埋もれた声」を確率的に計算するグラフ作成
def calculate_buried_voices_probabilistic():
    # 各投票者の最大投票ポイントを特定
    max_votes = {}
    buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        voter_id = voter_row['voter_id']
        
        # 各候補への投票を確認
        vote_values = {}
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                vote_values[i] = vote_value
        
        if not vote_values:
            continue
            
        # 最大投票値を見つける
        max_vote_value = max(vote_values.values())
        
        # 最大投票値を持つ候補をリストアップ
        max_candidates = [cand for cand, value in vote_values.items() if value == max_vote_value]
        
        # 最大投票を確率的に分配（同点最高位がある場合）
        probability_per_candidate = 1.0 / len(max_candidates)  # 確率を均等に分配
        
        # 「埋もれた声」を計算 - 4以上の投票でかつ最大投票候補ではない場合
        for candidate, vote_value in vote_values.items():
            if vote_value >= 4:
                if candidate in max_candidates:
                    # 最大投票候補の場合、(1-選ばれる確率)を埋もれた声としてカウント
                    # 選ばれる確率 = probability_per_candidate
                    # 選ばれない確率 = 1 - probability_per_candidate
                    buried_voices[candidate] += (1 - probability_per_candidate)
                else:
                    # 最大投票候補ではない場合、100%埋もれた声としてカウント
                    buried_voices[candidate] += 1
    
    return buried_voices

# 改善前後の「埋もれた声」計算方法を比較するグラフ作成
def compare_algorithms():
    # 単純な最大投票方式（最初に見つかった最大値のみを最大投票とする）
    simple_buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        max_vote = 0
        max_candidate = None
        
        # 最大投票を特定
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
        
        # 埋もれた声を計算
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value >= 4 and i != max_candidate:
                    simple_buried_voices[i] += 1
    
    # 確率的方式
    probabilistic_buried_voices = calculate_buried_voices_probabilistic()
    
    # 元の実装方式（vote_value < max_vote）
    original_buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        max_vote = 0
        
        # 最大投票値を特定
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value > max_vote:
                    max_vote = vote_value
        
        # 埋もれた声を計算（元の方法: vote_value >= 4 and vote_value < max_vote）
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value >= 4 and vote_value < max_vote:
                    original_buried_voices[i] += 1
    
    # HTMLのJS値
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
    
    # HTML/JSの値と対応する候補IDのマッピングを作成
    html_mapping = {}
    for i, project in enumerate(html_projects):
        for j in range(len(candidates_df)):
            title = candidates_df.loc[j, 'title']
            en_title = project_names.get(title, title)
            if en_title == project:
                html_mapping[j] = i
    
    # 結果の表示
    print("\n=== 「埋もれた声」計算方法の比較 ===")
    print("candidate_id: 元の実装 / 単純最大投票 / 確率的方式 / HTML/JS値")
    
    for i in range(len(candidates_df)):
        title = candidates_df.loc[i, 'title']
        en_title = project_names.get(title, title)
        html_val = html_buried[html_mapping[i]] if i in html_mapping else "N/A"
        
        print(f"{i}. {title} ({en_title}): " +
              f"{original_buried_voices[i]:.2f} / {simple_buried_voices[i]:.2f} / " +
              f"{probabilistic_buried_voices[i]:.2f} / {html_val}")
    
    # グラフ作成用のデータ準備
    projects = [project_names.get(title, title) for title in candidates_df['title'].tolist()]
    
    # フォルダが存在しない場合は作成
    os.makedirs('comparison_simulation', exist_ok=True)
    
    # グラフ作成
    plt.figure(figsize=(14, 10))
    x = np.arange(len(candidates_df))
    bar_width = 0.2
    opacity = 0.8
    
    plt.bar(x - bar_width*1.5, [original_buried_voices[i] for i in range(len(candidates_df))], 
            bar_width, alpha=opacity, color='blue', label='元の実装方式')
    
    plt.bar(x - bar_width*0.5, [simple_buried_voices[i] for i in range(len(candidates_df))], 
            bar_width, alpha=opacity, color='red', label='単純最大投票方式')
    
    plt.bar(x + bar_width*0.5, [probabilistic_buried_voices[i] for i in range(len(candidates_df))], 
            bar_width, alpha=opacity, color='green', label='確率的方式')
    
    # HTML/JSの値をプロット
    html_values = [0] * len(candidates_df)
    for i in range(len(candidates_df)):
        if i in html_mapping:
            html_values[i] = html_buried[html_mapping[i]]
    
    plt.bar(x + bar_width*1.5, html_values, 
            bar_width, alpha=opacity, color='purple', label='HTML/JS値')
    
    plt.xlabel('プロジェクト')
    plt.ylabel('埋もれた声の数')
    plt.title('「埋もれた声」計算方法の比較')
    plt.xticks(x, projects, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.savefig('comparison_simulation/buried_voices_comparison.png', dpi=300, bbox_inches='tight')
    
    return {
        'original': original_buried_voices,
        'simple': simple_buried_voices,
        'probabilistic': probabilistic_buried_voices,
        'html': html_values
    }

if __name__ == "__main__":
    print("「埋もれた声」計算方法の比較分析を実行中...")
    results = compare_algorithms()
    
    print("\n分析が完了しました。結果はcomparison_simulationディレクトリに保存されています。")
    print("3つの計算方法と元のHTML/JS値の差異を比較しました。")
    print("特に同点最高位がある場合、確率的手法では各候補が選ばれる確率に基づいて埋もれた声をカウントしています。") 