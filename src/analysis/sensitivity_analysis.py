#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QVにおける中立バイアスの感度分析スクリプト
1-2票の一定割合がバイアスによるものと仮定した場合の資金配分変化を分析
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.ticker as mtick

# 定数定義
EPSILON = 1e-10  # ゼロ除算回避のための小さな値
MAX_ITERATIONS = 10  # 最大反復回数
DATA_DIR = 'data'  # データディレクトリ
VOTES_FILE = f'{DATA_DIR}/votes.csv'
CANDIDATES_FILE = f'{DATA_DIR}/vote_summary.csv'
OUTPUT_DIR = './results/figures/neutral_bias'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_translation_dict():
    """日英翻訳用辞書"""
    return {
        "中立バイアス感度分析": "Neutral Bias Sensitivity Analysis",
        "小票バイアス割合": "Small Vote Bias Ratio",
        "予算配分変化率 (%)": "Budget Allocation Change (%)",
        "プロジェクト": "Project",
        "一律削減": "Uniform Reduction",
        "クラスター別削減": "Cluster-based Reduction",
        "プロジェクト別削減": "Project-specific Reduction",
        "元の配分": "Original Allocation",
        "バイアス補正後": "After Bias Correction",
        "バイアス感度分析レポート": "Bias Sensitivity Analysis Report",
        "シナリオ設定": "Scenario Settings",
        "削減モード": "Reduction Mode",
        "バイアス割合": "Bias Ratio",
        "影響を受けた投票数": "Affected Votes",
        "全体への影響": "Overall Impact",
        "投票数変化": "Vote Count Change",
        "予算配分変化": "Budget Allocation Change",
        "プロジェクト別影響": "Impact by Project",
        "元の票数": "Original Vote Count",
        "元の予算配分": "Original Budget Allocation",
        "補正後票数": "Adjusted Vote Count",
        "補正後予算配分": "Adjusted Budget Allocation",
        "変化率": "Change Rate",
        "まとめ": "Summary",
        "バイアス補正の総合影響": "Overall Effect of Bias Correction",
        "バイアス補正の影響": "Impact of Bias Correction",
        "最も影響を受けるプロジェクト": "Most Affected Project",
        "予算が増加するプロジェクト数": "Number of Projects with Increased Budget",
        "予算が減少するプロジェクト数": "Number of Projects with Decreased Budget",
        "平均的な変化率（絶対値）": "Average Change Rate (Absolute Value)"
    }

def translate_text(text, translation_dict=None):
    """テキスト翻訳ヘルパー関数"""
    if translation_dict is None:
        translation_dict = get_translation_dict()
    
    return translation_dict.get(text, text)

def translate_project_name(name):
    """プロジェクト名を英語に変換"""
    project_translations = {
        "政を祭に変える #vote_forプロジェクト": "Politics to Festival Project",
        "淡路島クエストカレッジ": "Awaji Island Quest College",
        "イナトリアートセンター計画": "Inatori Art Center Plan",
        "JINEN TRAVEL": "JINEN TRAVEL",  # 既に英語
        "ビオ田んぼプロジェクト": "Bio Rice Field Project",
        "パラ旅応援団": "Para Travel Support Team",
        "10代・20代の「いま、やりたい」を後押しする拠点　ちばユースセンターPRISM": "Chiba Youth Center PRISM"
    }
    
    # 既に英語のプロジェクト名はそのまま返す
    if name in ["Chiba Youth Center PRISM", "Awaji Island Quest College", 
               "Inatori Art Center Plan", "JINEN TRAVEL", 
               "Bio Rice Field Project", "Para Travel Support Team", 
               "Politics to Festival Project", "#vote_for Project"]:
        return name
    
    return project_translations.get(name, name)

def load_data():
    """CSVからデータを読み込む"""
    votes_df = pd.read_csv(VOTES_FILE)
    candidates_df = pd.read_csv(CANDIDATES_FILE)
    
    # プロジェクト名を英語に変換
    if 'title' in candidates_df.columns:
        candidates_df['title'] = candidates_df['title'].apply(translate_project_name)
    
    # 投票データの長形式への変換
    vote_rows = []
    
    for _, row in votes_df.iterrows():
        voter_id = row['voter_id']
        
        # 各候補者への投票を抽出
        for i in range(7):  # 0から6までの候補者
            col_name = f'candidate_{i}'
            if col_name in row and not pd.isna(row[col_name]):
                vote_rows.append({
                    'voter_id': voter_id,
                    'candidate_id': i,
                    'vote_value': int(row[col_name])
                })
    
    # 新しいデータフレームを作成
    votes_long_df = pd.DataFrame(vote_rows)
    
    return votes_long_df, candidates_df

def calculate_qv_results(votes_df, total_budget=250000):
    """QV方式の予算配分を計算"""
    # 各投票のコスト（= vote_value^2）とsqrt(cost)
    votes_df['cost'] = votes_df['vote_value']**2
    votes_df['sqrt_cost'] = np.sqrt(votes_df['cost'])
    
    # プロジェクトごとのsqrt(cost)の合計
    project_scores = votes_df.groupby('candidate_id')['sqrt_cost'].sum()
    
    # 全体のsqrt(cost)の合計
    total_score = project_scores.sum()
    
    # 予算配分計算
    budget_allocation = (project_scores / total_score) * total_budget if total_score > 0 else pd.Series(0, index=project_scores.index)
    
    # プロジェクトごとの投票数（合計）も計算
    vote_counts = votes_df.groupby('candidate_id')['vote_value'].sum()
    
    # 結果をDataFrameにまとめる
    results = pd.DataFrame({
        'total_sqrt_cost': project_scores,
        'budget_allocation': budget_allocation,
        'total_votes': vote_counts
    })
    
    return results

def apply_bias_correction(votes_df, bias_ratio, reduction_mode='uniform', cluster_data=None, project_specific_ratios=None):
    """
    中立バイアスの補正を適用する
    
    Parameters:
    -----------
    votes_df : DataFrame
        投票データ（長形式）
    bias_ratio : float
        1-2票のうちバイアスによるものと仮定する割合（0-1の値）
    reduction_mode : str
        'uniform' - すべての1-2票に一律の補正率を適用
        'cluster' - クラスターごとに異なる補正率を適用
        'project' - プロジェクトごとに異なる補正率を適用
    cluster_data : DataFrame
        クラスターモードで使用する投票者クラスターデータ
    project_specific_ratios : dict
        プロジェクトモードで使用するプロジェクトごとの補正率
        
    Returns:
    --------
    corrected_votes_df : DataFrame
        バイアス補正後の投票データ
    correction_stats : dict
        補正の統計情報
    """
    # コピーを作成して元データを変更しないようにする
    corrected_votes_df = votes_df.copy()
    
    # 1-2票の特定
    small_votes_mask = (corrected_votes_df['vote_value'] >= 1) & (corrected_votes_df['vote_value'] <= 2)
    small_votes_df = corrected_votes_df[small_votes_mask]
    
    # 補正対象の統計
    total_small_votes = len(small_votes_df)
    
    # 補正対象の投票をランダムに選択
    if reduction_mode == 'uniform':
        # 一律削減モード - 単純にランダムに選択
        np.random.seed(42)  # 結果の再現性のため
        random_indices = np.random.choice(
            small_votes_df.index, 
            size=int(total_small_votes * bias_ratio), 
            replace=False
        )
        
        # 選択された投票を0に設定（投票なしとする）
        corrected_votes_df.loc[random_indices, 'vote_value'] = 0
        
        affected_votes = len(random_indices)
        
    elif reduction_mode == 'cluster':
        # クラスター別削減モード - クラスターごとに異なる割合で削減
        if cluster_data is None:
            raise ValueError("クラスターモードにはクラスターデータが必要です")
        
        affected_votes = 0
        # クラスターごとに異なる補正率を適用
        for cluster_id, cluster_bias_ratio in cluster_data.items():
            # クラスターに属する投票者の小票を特定
            cluster_voters = cluster_data[cluster_data['cluster'] == cluster_id]['voter_id'].unique()
            cluster_small_votes = small_votes_df[small_votes_df['voter_id'].isin(cluster_voters)]
            
            # ランダムに選択して補正
            np.random.seed(42 + int(cluster_id))  # クラスターごとに異なるシード値
            random_indices = np.random.choice(
                cluster_small_votes.index, 
                size=int(len(cluster_small_votes) * cluster_bias_ratio), 
                replace=False
            )
            
            corrected_votes_df.loc[random_indices, 'vote_value'] = 0
            affected_votes += len(random_indices)
            
    elif reduction_mode == 'project':
        # プロジェクト別削減モード - プロジェクトごとに異なる割合で削減
        if project_specific_ratios is None:
            raise ValueError("プロジェクトモードにはプロジェクトごとの補正率が必要です")
        
        affected_votes = 0
        # プロジェクトごとに異なる補正率を適用
        for project_id, proj_bias_ratio in project_specific_ratios.items():
            # プロジェクトの小票を特定
            project_small_votes = small_votes_df[small_votes_df['candidate_id'] == project_id]
            
            # ランダムに選択して補正
            np.random.seed(42 + int(project_id))  # プロジェクトごとに異なるシード値
            random_indices = np.random.choice(
                project_small_votes.index, 
                size=int(len(project_small_votes) * proj_bias_ratio), 
                replace=False
            )
            
            corrected_votes_df.loc[random_indices, 'vote_value'] = 0
            affected_votes += len(random_indices)
    
    else:
        raise ValueError(f"Unknown reduction mode: {reduction_mode}")
    
    # 補正の統計情報
    correction_stats = {
        'total_small_votes': total_small_votes,
        'affected_votes': affected_votes,
        'affected_percentage': (affected_votes / total_small_votes * 100) if total_small_votes > 0 else 0
    }
    
    return corrected_votes_df, correction_stats

def run_sensitivity_analysis(votes_df, candidates_df, bias_ratios=None, mode='uniform'):
    """
    一連の感度分析を実行する
    
    Parameters:
    -----------
    votes_df : DataFrame
        投票データ（長形式）
    candidates_df : DataFrame
        候補プロジェクトデータ
    bias_ratios : list
        テストするバイアス率のリスト（0-1の値）
    mode : str
        削減モード
        
    Returns:
    --------
    sensitivity_results : DataFrame
        感度分析結果
    """
    if bias_ratios is None:
        bias_ratios = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    # オリジナルの投票結果の計算
    original_results = calculate_qv_results(votes_df)
    
    # 結果保存用のリスト
    results_list = []
    
    # 各バイアス率でのシミュレーション
    for bias_ratio in bias_ratios:
        # バイアス補正の適用
        corrected_votes_df, correction_stats = apply_bias_correction(votes_df, bias_ratio, mode)
        
        # 補正後の投票結果の計算
        corrected_results = calculate_qv_results(corrected_votes_df)
        
        # プロジェクトごとの変化を計算
        for project_id in original_results.index:
            # 候補プロジェクト名の取得
            if 'title' in candidates_df.columns:
                project_name = candidates_df.loc[candidates_df['candidate_id'] == project_id, 'title'].iloc[0]
            else:
                project_name = f"Project {project_id}"
            
            # 英語名に変換
            project_name = translate_project_name(project_name)
            
            # 投票数と予算配分の変化率
            vote_change = (corrected_results.loc[project_id, 'total_votes'] - original_results.loc[project_id, 'total_votes']) / original_results.loc[project_id, 'total_votes'] * 100
            budget_change = (corrected_results.loc[project_id, 'budget_allocation'] - original_results.loc[project_id, 'budget_allocation']) / original_results.loc[project_id, 'budget_allocation'] * 100
            
            # 結果の保存
            results_list.append({
                'bias_ratio': bias_ratio,
                'project_id': project_id,
                'project_name': project_name,
                'original_votes': original_results.loc[project_id, 'total_votes'],
                'corrected_votes': corrected_results.loc[project_id, 'total_votes'],
                'vote_change_pct': vote_change,
                'original_budget': original_results.loc[project_id, 'budget_allocation'],
                'corrected_budget': corrected_results.loc[project_id, 'budget_allocation'],
                'budget_change_pct': budget_change,
                'affected_votes': correction_stats['affected_votes'],
                'total_small_votes': correction_stats['total_small_votes']
            })
    
    # 結果をDataFrameに変換
    sensitivity_results = pd.DataFrame(results_list)
    
    return sensitivity_results

def plot_sensitivity_results(sensitivity_results, output_file):
    """感度分析結果のプロット"""
    trans_dict = get_translation_dict()
    
    # プロジェクトごとに異なる色を使用
    projects = sensitivity_results['project_name'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(projects)))
    
    plt.figure(figsize=(12, 8))
    
    for i, project in enumerate(projects):
        project_data = sensitivity_results[sensitivity_results['project_name'] == project]
        plt.plot(
            project_data['bias_ratio'] * 100,  # パーセント表示に変換
            project_data['budget_change_pct'],
            marker='o',
            label=project,
            color=colors[i],
            linewidth=2
        )
    
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    
    # 英語のタイトルと軸ラベルを使用
    plt.title("Neutral Bias Sensitivity Analysis", fontsize=16)
    plt.xlabel("Small Vote Bias Ratio (%)", fontsize=14)
    plt.ylabel("Budget Allocation Change (%)", fontsize=14)
    plt.legend(title="Project", loc='best')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    
    return

def generate_detailed_analysis(sensitivity_results, bias_ratio=0.5, output_file=None):
    """
    特定のバイアス率での詳細分析レポートを生成
    
    Parameters:
    -----------
    sensitivity_results : DataFrame
        感度分析結果
    bias_ratio : float
        詳細分析するバイアス率
    output_file : str
        出力ファイル名（Noneの場合は出力せず）
        
    Returns:
    --------
    detailed_results : DataFrame
        詳細分析結果
    """
    trans_dict = get_translation_dict()
    
    # 指定されたバイアス率のデータを抽出
    detailed_results = sensitivity_results[sensitivity_results['bias_ratio'] == bias_ratio].copy()
    
    # 予算配分変化の絶対値でソート
    detailed_results = detailed_results.sort_values(by='budget_change_pct', key=abs, ascending=False)
    
    # プロット作成（棒グラフ）
    plt.figure(figsize=(12, 8))
    
    bars = plt.bar(
        detailed_results['project_name'],
        detailed_results['budget_change_pct'],
        color=plt.cm.RdBu(np.interp(detailed_results['budget_change_pct'], 
                                  [detailed_results['budget_change_pct'].min(), 
                                   detailed_results['budget_change_pct'].max()], 
                                  [0, 1]))
    )
    
    # バーの上に値を表示
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2.,
            height + (0.5 if height >= 0 else -1.5),
            f"{height:.1f}%",
            ha='center', 
            va='bottom' if height >= 0 else 'top'
        )
    
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    
    # 英語のタイトルと軸ラベルを使用
    plt.title(f"Impact of Bias Correction ({bias_ratio*100:.0f}%)", fontsize=16)
    plt.ylabel("Budget Allocation Change (%)", fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # 詳細分析結果のグラフを保存
    if output_file:
        detail_graph_file = output_file.replace('.png', f'_detail_{int(bias_ratio*100)}.png')
        plt.savefig(detail_graph_file)
        plt.close()
    else:
        plt.close()
    
    # テキストレポートも生成
    if output_file:
        report_file = output_file.replace('.png', f'_report_{int(bias_ratio*100)}.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Bias Sensitivity Analysis Report\n\n")
            
            f.write("## Scenario Settings\n\n")
            f.write(f"- Bias Ratio: {bias_ratio*100:.0f}%\n")
            f.write(f"- Affected Votes: {detailed_results['affected_votes'].iloc[0]} / {detailed_results['total_small_votes'].iloc[0]} ({detailed_results['affected_votes'].iloc[0]/detailed_results['total_small_votes'].iloc[0]*100:.1f}%)\n\n")
            
            f.write("## Impact by Project\n\n")
            f.write("| Project | Original Vote Count | Adjusted Vote Count | Change Rate | Original Budget Allocation | Adjusted Budget Allocation | Change Rate |\n")
            f.write("|------------|------------|------------|------------|------------|------------|------------|\n")
            
            for _, row in detailed_results.iterrows():
                f.write(f"| {row['project_name']} | {row['original_votes']:.0f} | {row['corrected_votes']:.0f} | {row['vote_change_pct']:.1f}% | {row['original_budget']:.0f} | {row['corrected_budget']:.0f} | {row['budget_change_pct']:.1f}% |\n")
            
            f.write("\n## Summary\n\n")
            
            # 最も影響を受けるプロジェクトとその変化率
            most_affected = detailed_results.iloc[0]
            f.write(f"- Most Affected Project: {most_affected['project_name']} ({most_affected['budget_change_pct']:.1f}%)\n")
            
            # 予算増加/減少するプロジェクト数
            increased = len(detailed_results[detailed_results['budget_change_pct'] > 0])
            decreased = len(detailed_results[detailed_results['budget_change_pct'] < 0])
            f.write(f"- Number of Projects with Increased Budget: {increased}\n")
            f.write(f"- Number of Projects with Decreased Budget: {decreased}\n")
            
            # 平均的な変化率の絶対値
            avg_abs_change = detailed_results['budget_change_pct'].abs().mean()
            f.write(f"- Average Change Rate (Absolute Value): {avg_abs_change:.1f}%\n")
    
    return detailed_results

def main():
    """メイン処理"""
    print("中立バイアス感度分析を開始します...")
    
    # データ読み込み
    votes_df, candidates_df = load_data()
    
    # 感度分析の実行（一律削減モード）
    sensitivity_results = run_sensitivity_analysis(
        votes_df, 
        candidates_df, 
        bias_ratios=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        mode='uniform'
    )
    
    # 結果をCSVとして保存
    sensitivity_results.to_csv(os.path.join(OUTPUT_DIR, 'sensitivity_analysis_results.csv'), index=False)
    
    # 感度分析結果のプロット
    plot_sensitivity_results(
        sensitivity_results, 
        os.path.join(OUTPUT_DIR, 'sensitivity_analysis.png')
    )
    
    # 特定のバイアス率での詳細分析
    # 実際の適用では、最も現実的と思われるバイアス率（例：50%）での詳細分析を行う
    for bias_ratio in [0.3, 0.5, 0.7]:
        detailed_results = generate_detailed_analysis(
            sensitivity_results, 
            bias_ratio=bias_ratio,
            output_file=os.path.join(OUTPUT_DIR, 'sensitivity_analysis.png')
        )
    
    print("感度分析が完了しました。結果は output ディレクトリに保存されています。")

if __name__ == "__main__":
    main() 