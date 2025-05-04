import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
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
            
            # 埋もれた声の計算（ステップ2、修正版）- 4以上の投票かつ最大投票ではないものを「埋もれた声」としてカウント
            for i in range(len(candidates_df)):
                col_name = f'candidate_{i}'
                if col_name in voter_row and not pd.isna(voter_row[col_name]):
                    vote_value = voter_row[col_name]
                    if vote_value >= 4 and i != max_candidate:
                        buried_voices[i] += 1
    
    # フォルダが存在しない場合は作成
    os.makedirs('comparison_simulation', exist_ok=True)
    
    # グラフ作成
    plt.figure(figsize=(12, 8))
    x = np.arange(len(candidates_df))
    
    # 英語のプロジェクト名を取得
    projects = [project_names.get(title, title) for title in candidates_df['title'].tolist()]
    
    # 埋もれた声の数をグラフ化
    plt.bar(x, [buried_voices[i] for i in range(len(candidates_df))], color='darkred')
    
    plt.xlabel('Projects')
    plt.ylabel('Number of Strong Preferences Not Reflected in One-Person-One-Vote')
    plt.title('Hidden Voices Captured by Quadratic Voting (Fixed Algorithm)')
    plt.xticks(x, projects, rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('comparison_simulation/buried_voices_fixed.png', dpi=300, bbox_inches='tight')
    
    # データも保存
    buried_df = pd.DataFrame({
        'project': projects,
        'buried_voices': [buried_voices[i] for i in range(len(candidates_df))]
    })
    buried_df.to_csv('comparison_simulation/buried_voices_fixed.csv', index=False)
    
    # HTMLのJSと計算結果の比較
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
    
    print("\n=== HTML/JSの値と修正されたアルゴリズムでの計算結果の比較 ===")
    for i, project in enumerate(html_projects):
        for j in range(len(candidates_df)):
            title = candidates_df.loc[j, 'title']
            en_title = project_names.get(title, title)
            if en_title == project:
                print(f"{project}: HTML/JS:{html_buried[i]} vs 修正計算:{buried_voices[j]}")
    
    return buried_voices

if __name__ == "__main__":
    print("「埋もれた声」を可視化するグラフを作成中（修正版アルゴリズム）...")
    buried_voices = create_buried_voices_graph()
    
    print("\n=== 修正されたアルゴリズムでの埋もれた声の計算結果 ===")
    for i in range(len(candidates_df)):
        title = candidates_df.loc[i, 'title']
        en_title = project_names.get(title, title)
        print(f"{i}. {title} ({en_title}): {buried_voices[i]}票")
    
    print("\nグラフの作成が完了しました。結果は comparison_simulation ディレクトリに保存されています。")
    print("注意: オリジナルのアルゴリズムでは「vote_value >= 4 and vote_value < max_vote」という条件で埋もれた声をカウントしていましたが、")
    print("修正版では「vote_value >= 4 and i != max_candidate」という条件に変更しました。") 