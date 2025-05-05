import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

"""
埋もれた声（最大選好以外の投票が一人一票方式では反映されない）に特化した分析スクリプト
"""

# フォントエラーを回避するための設定
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']

# 警告を抑制
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# ルートディレクトリへのパスを取得
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def analyze_buried_voices(votes_file='votes.csv', candidates_file='candidates.csv', threshold=4):
    """
    埋もれた声（最大選好以外の投票が一人一票方式では反映されない票）を分析する
    
    Parameters:
    -----------
    votes_file : str
        投票データのファイルパス
    candidates_file : str
        候補者データのファイルパス
    threshold : int
        分析に含める最小投票値の閾値（デフォルト: 4 - 強い選好）
    
    Returns:
    --------
    dict
        分析結果を含む辞書
    """
    # データの読み込み
    votes = pd.read_csv(os.path.join(ROOT_DIR, 'data', votes_file))
    candidates = pd.read_csv(os.path.join(ROOT_DIR, 'data', candidates_file))
    
    # 候補者数を動的に取得
    num_candidates = len(candidates)
    
    # 結果格納用の辞書を初期化
    buried_voices = {i: 0 for i in range(num_candidates)}
    votes_count = {i: 0 for i in range(num_candidates)}
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
                
                # 閾値以上の票を集計
                if vote_value >= threshold:
                    votes_count[i] += 1
                
                # 最大投票の更新
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
        
        # この投票者の最大投票を記録
        if max_candidate is not None:
            max_votes_count[max_candidate] += 1
    
    # 各候補に対する有効票で、最大投票ではないものを計算
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
        'votes_count': votes_count,
        'max_votes': max_votes_count,
        'buried_voices': buried_voices
    }
    
    return results

def analyze_specific_candidate(votes_file='votes.csv', candidate_id=0, threshold=4):
    """
    特定の候補に関する詳細分析を行う
    
    Parameters:
    -----------
    votes_file : str
        投票データのファイルパス
    candidate_id : int
        分析対象の候補者ID
    threshold : int
        分析に含める最小投票値の閾値
    
    Returns:
    --------
    dict
        特定候補者に関する詳細分析結果
    """
    # データの読み込み
    votes = pd.read_csv(os.path.join(ROOT_DIR, 'data', votes_file))
    
    # 特定候補への投票分布を収集
    votes_for_candidate = []
    for _, voter_row in votes.iterrows():
        col_name = f'candidate_{candidate_id}'
        if col_name in voter_row and not pd.isna(voter_row[col_name]):
            votes_for_candidate.append(voter_row[col_name])
    
    # 特定候補に票を入れたが他の候補に最大票を入れた人数
    votes_but_other_max = 0
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
                    votes_but_other_max += 1
    
    # 投票分布の集計
    vote_distribution = {}
    for vote in votes_for_candidate:
        vote_distribution[vote] = vote_distribution.get(vote, 0) + 1
    
    # 結果をまとめる
    results = {
        'vote_distribution': vote_distribution,
        'total_votes': len(votes_for_candidate),
        'votes_above_threshold': sum(1 for v in votes_for_candidate if v >= threshold),
        'votes_but_other_max': votes_but_other_max
    }
    
    return results

def visualize_buried_voices(analysis_results, candidates_file='candidates.csv', output_dir='buried_voices', threshold=4):
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
    threshold : int
        使用した閾値
    """
    # 候補者データを読み込む
    candidates = pd.read_csv(os.path.join(ROOT_DIR, 'data', candidates_file))
    
    # 出力ディレクトリの作成
    output_path = os.path.join(ROOT_DIR, 'results', 'figures', output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    # サブディレクトリの作成
    threshold_dir = os.path.join(output_path, f'threshold_{threshold}')
    os.makedirs(threshold_dir, exist_ok=True)
    
    # 埋もれた声のグラフ
    plt.figure(figsize=(12, 8))
    x = np.arange(len(candidates))
    buried_values = [analysis_results['buried_voices'][i] for i in range(len(candidates))]
    
    plt.bar(x, buried_values, color='darkred')
    plt.xlabel('Candidates')
    plt.ylabel('Number of Buried Voices')
    plt.title(f'Buried Voices by Candidate (Threshold = {threshold})')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(threshold_dir, 'buried_voices.png'), dpi=300)
    plt.close()
    
    # すべての投票と最大投票の比較グラフ
    plt.figure(figsize=(14, 8))
    all_values = [analysis_results['votes_count'][i] for i in range(len(candidates))]
    max_values = [analysis_results['max_votes'][i] for i in range(len(candidates))]
    
    width = 0.35
    plt.bar(x - width/2, all_values, width, label=f'Votes ≥ {threshold}')
    plt.bar(x + width/2, max_values, width, label='Max Votes')
    
    plt.xlabel('Candidates')
    plt.ylabel('Number of Votes')
    plt.title(f'Votes (≥ {threshold}) vs. Max Votes by Candidate')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(threshold_dir, 'votes_vs_max_votes.png'), dpi=300)
    plt.close()
    
    # 埋もれた声の割合（全投票中の割合）
    plt.figure(figsize=(12, 8))
    buried_ratio = []
    for i in range(len(candidates)):
        if analysis_results['votes_count'][i] > 0:
            ratio = analysis_results['buried_voices'][i] / analysis_results['votes_count'][i] * 100
        else:
            ratio = 0
        buried_ratio.append(ratio)
    
    plt.bar(x, buried_ratio, color='orange')
    plt.xlabel('Candidates')
    plt.ylabel('Percentage (%)')
    plt.title(f'Percentage of Votes (≥ {threshold}) that are Buried')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(threshold_dir, 'buried_voices_ratio.png'), dpi=300)
    plt.close()

def visualize_candidate_analysis(candidate_analysis, candidate_name, output_dir='buried_voices', threshold=4):
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
    threshold : int
        使用した閾値
    """
    # 出力ディレクトリの作成
    output_path = os.path.join(ROOT_DIR, 'results', 'figures', output_dir)
    threshold_dir = os.path.join(output_path, f'threshold_{threshold}')
    os.makedirs(threshold_dir, exist_ok=True)
    
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
    plt.savefig(os.path.join(threshold_dir, f'vote_distribution_{candidate_name.replace(" ", "_")}.png'), dpi=300)
    plt.close()
    
    # 全票のグラフ
    plt.figure(figsize=(8, 8))
    labels = ['Votes that are max', 'Votes that are buried']
    sizes = [
        candidate_analysis['votes_above_threshold'] - candidate_analysis['votes_but_other_max'],
        candidate_analysis['votes_but_other_max']
    ]
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'salmon'])
    plt.axis('equal')
    plt.title(f'Votes Analysis for {candidate_name} (Threshold = {threshold})')
    plt.tight_layout()
    plt.savefig(os.path.join(threshold_dir, f'votes_analysis_{candidate_name.replace(" ", "_")}.png'), dpi=300)
    plt.close()

def compare_thresholds(votes_file='votes.csv', candidates_file='candidates.csv', output_dir='buried_voices'):
    """
    異なる閾値（1と4）での埋もれた声の分析結果を比較する
    
    Parameters:
    -----------
    votes_file : str
        投票データのファイルパス
    candidates_file : str
        候補者データのファイルパス
    output_dir : str
        出力先ディレクトリ
    """
    # 出力ディレクトリの作成
    output_path = os.path.join(ROOT_DIR, 'results', 'figures', output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    # 候補者データを読み込む
    candidates = pd.read_csv(os.path.join(ROOT_DIR, 'data', candidates_file))
    
    # 異なる閾値で分析を実行
    thresholds = [1, 4]
    results = {}
    
    for threshold in thresholds:
        results[threshold] = analyze_buried_voices(
            votes_file=votes_file,
            candidates_file=candidates_file,
            threshold=threshold
        )
    
    # 閾値による埋もれた声の比較グラフ
    plt.figure(figsize=(14, 8))
    x = np.arange(len(candidates))
    width = 0.35
    
    buried_values_1 = [results[1]['buried_voices'][i] for i in range(len(candidates))]
    buried_values_4 = [results[4]['buried_voices'][i] for i in range(len(candidates))]
    
    plt.bar(x - width/2, buried_values_1, width, label='Threshold = 1')
    plt.bar(x + width/2, buried_values_4, width, label='Threshold = 4')
    
    plt.xlabel('Candidates')
    plt.ylabel('Number of Buried Voices')
    plt.title('Comparison of Buried Voices by Threshold')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'buried_voices_comparison.png'), dpi=300)
    plt.close()
    
    # 埋もれた声の割合の比較グラフ
    plt.figure(figsize=(14, 8))
    buried_ratio_1 = []
    buried_ratio_4 = []
    
    for i in range(len(candidates)):
        if results[1]['votes_count'][i] > 0:
            ratio_1 = results[1]['buried_voices'][i] / results[1]['votes_count'][i] * 100
        else:
            ratio_1 = 0
        
        if results[4]['votes_count'][i] > 0:
            ratio_4 = results[4]['buried_voices'][i] / results[4]['votes_count'][i] * 100
        else:
            ratio_4 = 0
        
        buried_ratio_1.append(ratio_1)
        buried_ratio_4.append(ratio_4)
    
    plt.bar(x - width/2, buried_ratio_1, width, label='Threshold = 1', color='lightblue')
    plt.bar(x + width/2, buried_ratio_4, width, label='Threshold = 4', color='salmon')
    
    plt.xlabel('Candidates')
    plt.ylabel('Percentage (%)')
    plt.title('Comparison of Buried Voices Ratio by Threshold')
    plt.xticks(x, candidates['title_en'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'buried_voices_ratio_comparison.png'), dpi=300)
    plt.close()
    
    # 結果をCSVに保存
    results_df = pd.DataFrame({
        'candidate_id': candidates['candidate_id'],
        'project_name': candidates['title_en'],
        'buried_voices_t1': [results[1]['buried_voices'][i] for i in range(len(candidates))],
        'buried_voices_t4': [results[4]['buried_voices'][i] for i in range(len(candidates))],
        'votes_count_t1': [results[1]['votes_count'][i] for i in range(len(candidates))],
        'votes_count_t4': [results[4]['votes_count'][i] for i in range(len(candidates))],
        'max_votes': [results[1]['max_votes'][i] for i in range(len(candidates))]
    })
    
    data_dir = os.path.join(ROOT_DIR, 'results', 'data')
    os.makedirs(data_dir, exist_ok=True)
    results_df.to_csv(os.path.join(data_dir, 'buried_voices_comparison.csv'), index=False)

def main():
    """メイン関数"""
    # ディレクトリ設定
    output_dir = 'buried_voices'
    
    # 異なる閾値で埋もれた声を分析・比較
    print("異なる閾値での埋もれた声の比較分析を実行しています...")
    
    # 閾値の比較分析を実行
    compare_thresholds(
        output_dir=output_dir
    )
    
    # 閾値1での埋もれた声分析
    print("\n閾値1での埋もれた声の分析を実行中...")
    analysis_results_t1 = analyze_buried_voices(
        threshold=1
    )
    
    # 閾値4での埋もれた声分析
    print("\n閾値4での埋もれた声の分析を実行中...")
    analysis_results_t4 = analyze_buried_voices(
        threshold=4
    )
    
    # 結果を表示
    print("\n=== 埋もれた声の分析結果 ===")
    candidates = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'candidates.csv'))
    
    print("\n閾値1での埋もれた声:")
    for i in range(len(candidates)):
        print(f"{i}. {candidates.loc[i, 'title_en']}: {analysis_results_t1['buried_voices'][i]}票")
    
    print("\n閾値4での埋もれた声:")
    for i in range(len(candidates)):
        print(f"{i}. {candidates.loc[i, 'title_en']}: {analysis_results_t4['buried_voices'][i]}票")
    
    # 結果を可視化
    visualize_buried_voices(
        analysis_results=analysis_results_t1,
        output_dir=output_dir,
        threshold=1
    )
    
    visualize_buried_voices(
        analysis_results=analysis_results_t4,
        output_dir=output_dir,
        threshold=4
    )
    
    # 特定の候補の詳細分析
    # 例として最初の候補と最後の候補を分析
    for candidate_id in [0, len(candidates)-1]:
        candidate_name = candidates.loc[candidate_id, 'title_en']
        
        # 閾値1での分析
        candidate_analysis_t1 = analyze_specific_candidate(
            candidate_id=candidate_id,
            threshold=1
        )
        
        visualize_candidate_analysis(
            candidate_analysis=candidate_analysis_t1,
            candidate_name=candidate_name,
            output_dir=output_dir,
            threshold=1
        )
        
        # 閾値4での分析
        candidate_analysis_t4 = analyze_specific_candidate(
            candidate_id=candidate_id,
            threshold=4
        )
        
        visualize_candidate_analysis(
            candidate_analysis=candidate_analysis_t4,
            candidate_name=candidate_name,
            output_dir=output_dir,
            threshold=4
        )
    
    print(f"\n詳細分析が完了しました。結果は {os.path.join(ROOT_DIR, 'results', 'figures', output_dir)} に保存されています。")

if __name__ == "__main__":
    main() 