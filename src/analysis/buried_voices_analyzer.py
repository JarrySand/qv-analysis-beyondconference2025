import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

"""
埋もれた声（強い選好が一人一票方式では反映されない）に特化した分析スクリプト
"""

# フォントエラーを回避するための設定
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']

# 警告を抑制
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

def analyze_buried_voices(votes_file='data/votes.csv', candidates_file='data/candidates.csv', threshold=4):
    """
    埋もれた声（強い選好だが最大ではないため一人一票方式では反映されない票）を分析する
    
    Parameters:
    -----------
    votes_file : str
        投票データのファイルパス
    candidates_file : str
        候補者データのファイルパス
    threshold : int
        「強い選好」とみなす投票値の閾値（デフォルト: 4）
    
    Returns:
    --------
    dict
        分析結果を含む辞書
    """
    # データの読み込み
    votes = pd.read_csv(votes_file)
    candidates = pd.read_csv(candidates_file)
    
    # 候補者数を動的に取得
    num_candidates = len(candidates)
    
    # 結果格納用の辞書を初期化
    buried_voices = {i: 0 for i in range(num_candidates)}
    strong_votes_count = {i: 0 for i in range(num_candidates)}
    max_votes_count = {i: 0 for i in range(num_candidates)}
    
    # 各投票者の最大投票ポイントを特定
    for _, voter_row in votes.iterrows():
        max_vote = 0
        max_candidate = None
        
        # 各候補への投票を確認
        for i in range(num_candidates):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                
                # 強い票を集計
                if vote_value >= threshold:
                    strong_votes_count[i] += 1
                
                # 最大投票の更新
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
        
        # この投票者の最大投票を記録
        if max_candidate is not None:
            max_votes_count[max_candidate] += 1
    
    # 各候補に対する強い投票で、最大投票ではないものを計算
    for _, voter_row in votes.iterrows():
        max_vote = 0
        max_candidate = None
        
        # まず最大投票を特定
        for i in range(num_candidates):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
        
        # 埋もれた声を計算
        for i in range(num_candidates):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value >= threshold and i != max_candidate:
                    buried_voices[i] += 1
    
    # 結果を辞書にまとめる
    results = {
        'strong_votes': strong_votes_count,
        'max_votes': max_votes_count,
        'buried_voices': buried_voices
    }
    
    return results

def analyze_specific_candidate(votes_file='data/votes.csv', candidate_id=0, threshold=4):
    """
    特定の候補に関する詳細分析を行う
    
    Parameters:
    -----------
    votes_file : str
        投票データのファイルパス
    candidate_id : int
        分析対象の候補者ID
    threshold : int
        「強い選好」とみなす投票値の閾値
    
    Returns:
    --------
    dict
        特定候補者に関する詳細分析結果
    """
    # データの読み込み
    votes = pd.read_csv(votes_file)
    
    # 特定候補への投票分布を収集
    votes_for_candidate = []
    for _, voter_row in votes.iterrows():
        col_name = f'candidate_{candidate_id}'
        if col_name in voter_row and not pd.isna(voter_row[col_name]):
            votes_for_candidate.append(voter_row[col_name])
    
    # 特定候補に強い票を入れたが他の候補に最大票を入れた人数
    strong_but_other_max = 0
    for _, voter_row in votes.iterrows():
        col_name = f'candidate_{candidate_id}'
        if col_name in voter_row and not pd.isna(voter_row[col_name]):
            vote_value = voter_row[col_name]
            if vote_value >= threshold:
                # 最大投票を特定
                max_vote = vote_value
                max_candidate = candidate_id
                for i in range(len(votes.columns) - 1):  # 投票者IDカラムを除く
                    if i == candidate_id:
                        continue
                    other_col = f'candidate_{i}'
                    if other_col in voter_row and not pd.isna(voter_row[other_col]):
                        if voter_row[other_col] > max_vote:
                            max_vote = voter_row[other_col]
                            max_candidate = i
                
                if max_candidate != candidate_id:
                    strong_but_other_max += 1
    
    # 投票分布の集計
    vote_distribution = {}
    for vote in votes_for_candidate:
        vote_distribution[vote] = vote_distribution.get(vote, 0) + 1
    
    # 結果をまとめる
    results = {
        'vote_distribution': vote_distribution,
        'total_votes': len(votes_for_candidate),
        'strong_votes': sum(1 for v in votes_for_candidate if v >= threshold),
        'strong_but_other_max': strong_but_other_max
    }
    
    return results

def visualize_buried_voices(analysis_results, candidates_file='data/candidates.csv', output_dir='results/figures/comparison'):
    """
    埋もれた声の分析結果を可視化する
    
    Parameters:
    -----------
    analysis_results : dict
        analyze_buried_voices() の結果
    candidates_file : str
        候補者データのファイルパス
    output_dir : str
        出力先ディレクトリ
    """
    # 候補者データを読み込む
    candidates = pd.read_csv(candidates_file)
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 埋もれた声のグラフ
    plt.figure(figsize=(12, 8))
    x = np.arange(len(candidates))
    buried_values = [analysis_results['buried_voices'][i] for i in range(len(candidates))]
    
    plt.bar(x, buried_values, color='darkred')
    plt.xlabel('Candidates')
    plt.ylabel('Number of Buried Voices')
    plt.title('Buried Voices by Candidate')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/buried_voices.png', dpi=300)
    plt.close()
    
    # 強い投票と最大投票の比較グラフ
    plt.figure(figsize=(14, 8))
    strong_values = [analysis_results['strong_votes'][i] for i in range(len(candidates))]
    max_values = [analysis_results['max_votes'][i] for i in range(len(candidates))]
    
    width = 0.35
    plt.bar(x - width/2, strong_values, width, label='Strong Votes')
    plt.bar(x + width/2, max_values, width, label='Max Votes')
    
    plt.xlabel('Candidates')
    plt.ylabel('Number of Votes')
    plt.title('Strong Votes vs. Max Votes by Candidate')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/strong_vs_max_votes.png', dpi=300)
    plt.close()
    
    # 埋もれた声の割合（強い投票中の割合）
    plt.figure(figsize=(12, 8))
    buried_ratio = []
    for i in range(len(candidates)):
        if analysis_results['strong_votes'][i] > 0:
            ratio = analysis_results['buried_voices'][i] / analysis_results['strong_votes'][i] * 100
        else:
            ratio = 0
        buried_ratio.append(ratio)
    
    plt.bar(x, buried_ratio, color='orange')
    plt.xlabel('Candidates')
    plt.ylabel('Percentage (%)')
    plt.title('Percentage of Strong Votes that are Buried')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/buried_voices_ratio.png', dpi=300)
    plt.close()

def visualize_candidate_analysis(candidate_analysis, candidate_name, output_dir='results/figures/comparison'):
    """
    特定候補の詳細分析を可視化する
    
    Parameters:
    -----------
    candidate_analysis : dict
        analyze_specific_candidate() の結果
    candidate_name : str
        候補者名
    output_dir : str
        出力先ディレクトリ
    """
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 投票分布のグラフ
    plt.figure(figsize=(10, 6))
    votes = list(candidate_analysis['vote_distribution'].keys())
    counts = list(candidate_analysis['vote_distribution'].values())
    
    plt.bar(votes, counts, color='skyblue')
    plt.xlabel('Vote Value')
    plt.ylabel('Number of Voters')
    plt.title(f'Vote Distribution for {candidate_name}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/vote_distribution_{candidate_name.replace(" ", "_")}.png', dpi=300)
    plt.close()
    
    # 強い票のグラフ
    plt.figure(figsize=(8, 8))
    labels = ['Strong votes that are max', 'Strong votes that are buried']
    sizes = [
        candidate_analysis['strong_votes'] - candidate_analysis['strong_but_other_max'],
        candidate_analysis['strong_but_other_max']
    ]
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'salmon'])
    plt.axis('equal')
    plt.title(f'Strong Votes Analysis for {candidate_name}')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/strong_votes_analysis_{candidate_name.replace(" ", "_")}.png', dpi=300)
    plt.close()

def main():
    """メイン関数"""
    # ディレクトリ設定
    data_dir = 'data'
    output_dir = 'results/figures/buried_voices'
    
    # 埋もれた声の分析を実行
    print("埋もれた声の詳細分析を実行しています...")
    analysis_results = analyze_buried_voices(
        votes_file=f'{data_dir}/votes.csv',
        candidates_file=f'{data_dir}/candidates.csv',
        threshold=4
    )
    
    # 結果を表示
    print("\n=== 埋もれた声の分析結果 ===")
    candidates = pd.read_csv(f'{data_dir}/candidates.csv')
    for i in range(len(candidates)):
        print(f"{i}. {candidates.loc[i, 'title_en']}: {analysis_results['buried_voices'][i]}票")
    
    # 結果をCSVに保存
    results_df = pd.DataFrame({
        'candidate_id': candidates['candidate_id'],
        'project_name': candidates['title_en'],
        'buried_voices': [analysis_results['buried_voices'][i] for i in range(len(candidates))],
        'strong_votes': [analysis_results['strong_votes'][i] for i in range(len(candidates))],
        'max_votes': [analysis_results['max_votes'][i] for i in range(len(candidates))]
    })
    
    # 出力ディレクトリを作成
    os.makedirs('results/data', exist_ok=True)
    results_df.to_csv('results/data/buried_voices_analysis.csv', index=False)
    
    # 結果を可視化
    visualize_buried_voices(
        analysis_results=analysis_results,
        candidates_file=f'{data_dir}/candidates.csv',
        output_dir=output_dir
    )
    
    # 特定の候補の詳細分析
    # 例として最初の候補と最後の候補を分析
    for candidate_id in [0, len(candidates)-1]:
        candidate_name = candidates.loc[candidate_id, 'title_en']
        candidate_analysis = analyze_specific_candidate(
            votes_file=f'{data_dir}/votes.csv',
            candidate_id=candidate_id,
            threshold=4
        )
        
        visualize_candidate_analysis(
            candidate_analysis=candidate_analysis,
            candidate_name=candidate_name,
            output_dir=output_dir
        )
    
    print(f"\n詳細分析が完了しました。結果は {output_dir} に保存されています。")

if __name__ == "__main__":
    main() 