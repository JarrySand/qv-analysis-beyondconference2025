#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
投票値の分布分析と中立バイアス（1票の過剰使用）の検出を行うスクリプト
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.ticker as mtick

# ディレクトリ設定
VOTES_FILE = '../votes.csv'  
CANDIDATES_FILE = '../candidates.csv'
OUTPUT_DIR = './analysis_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_csv_data():
    """CSVからデータを読み込む"""
    votes_df = pd.read_csv(VOTES_FILE)
    candidates_df = pd.read_csv(CANDIDATES_FILE)
    
    # 投票データのカラム名を確認し、必要に応じて変更
    votes_df = votes_df.rename(columns={
        'voter': 'voter_id',
        'candidate': 'candidate_id', 
        'vote': 'vote_value'
    })
    
    # 候補者データのカラム名を確認し、必要に応じて変更
    candidates_df = candidates_df.rename(columns={
        'id': 'id',
        'name': 'name'
    })
    
    return candidates_df, votes_df

def analyze_vote_distribution(votes_df, candidates_df):
    """投票値の分布分析"""
    # 基本統計量の計算
    vote_stats = votes_df.groupby('candidate_id')['vote_value'].agg([
        'count', 'mean', 'std', 'min', 'max', 
        lambda x: x.value_counts().get(1, 0)  # 1票の数
    ]).rename(columns={'<lambda_0>': 'one_vote_count'})
    
    # 候補者名を追加
    vote_stats = vote_stats.merge(
        candidates_df[['id', 'name']], 
        left_index=True, 
        right_on='id'
    )
    
    # 1票の割合を計算
    vote_stats['one_vote_percentage'] = vote_stats['one_vote_count'] / vote_stats['count'] * 100
    
    # 0票の数を計算（全投票者数 - 投票者数）
    total_voters = len(votes_df['voter_id'].unique())
    vote_stats['zero_vote_count'] = total_voters - vote_stats['count']
    
    # 理論的な分布との比較のための指標
    # 仮説: 投票値が均等に分布する場合、1票の割合は約1/9 (11.1%)になるはず
    vote_stats['expected_one_vote_count'] = vote_stats['count'] / 9
    vote_stats['one_vote_deviation'] = vote_stats['one_vote_count'] - vote_stats['expected_one_vote_count']
    vote_stats['one_vote_deviation_percentage'] = (vote_stats['one_vote_deviation'] / vote_stats['expected_one_vote_count']) * 100
    
    return vote_stats

def calculate_voter_patterns(votes_df):
    """投票者ごとの投票パターン分析"""
    # 投票者ごとの統計
    voter_stats = votes_df.groupby('voter_id').agg(
        total_votes=('vote_value', 'count'),
        one_votes=('vote_value', lambda x: (x == 1).sum()),
        mean_vote=('vote_value', 'mean'),
        max_vote=('vote_value', 'max')
    )
    
    voter_stats['one_vote_percentage'] = voter_stats['one_votes'] / voter_stats['total_votes'] * 100
    
    # 投票パターンによるグループ分け
    voter_stats['vote_pattern'] = pd.cut(
        voter_stats['one_vote_percentage'],
        bins=[0, 20, 40, 60, 80, 100],
        labels=['Very Low 1s', 'Low 1s', 'Medium 1s', 'High 1s', 'Very High 1s']
    )
    
    return voter_stats

def detect_neutral_bias(votes_df, vote_stats):
    """中立バイアスの検出"""
    # 全体の投票値分布
    vote_dist = votes_df['vote_value'].value_counts().sort_index()
    vote_dist_pct = vote_dist / vote_dist.sum() * 100
    
    # 均等分布を仮定した場合の期待値
    total_votes = len(votes_df) 
    expected_per_vote = total_votes / 9  # 均等分布なら各票数(1-9)は同じ頻度
    
    # 分布の不均等性を計算
    observed_counts = np.array([vote_dist.get(i, 0) for i in range(1, 10)])
    expected_counts = np.ones(9) * expected_per_vote
    
    # カイ二乗統計量を手動で計算
    chi2_stat = np.sum(((observed_counts - expected_counts) ** 2) / expected_counts)
    
    # 自由度 = 9-1 = 8のカイ二乗分布のp値を計算
    # SciPy の stats.chi2.sf関数を使用 (生のカイ二乗検定ではなく)
    p_value = stats.chi2.sf(chi2_stat, 8)  # 8 degrees of freedom (9 categories - 1)
    
    # 1票過剰使用の検出
    one_vote_excess = vote_dist.get(1, 0) - expected_per_vote
    one_vote_excess_pct = (one_vote_excess / expected_per_vote) * 100 if expected_per_vote > 0 else 0
    
    # プロジェクトごとの1票比率の不均等性
    one_vote_percentages = vote_stats['one_vote_percentage']
    one_vote_std = one_vote_percentages.std()
    one_vote_range = one_vote_percentages.max() - one_vote_percentages.min()
    
    return {
        'vote_distribution': vote_dist,
        'vote_distribution_percentage': vote_dist_pct,
        'chi2_statistic': chi2_stat,
        'p_value': p_value,
        'one_vote_excess': one_vote_excess,
        'one_vote_excess_percentage': one_vote_excess_pct,
        'one_vote_percentage_std': one_vote_std,
        'one_vote_percentage_range': one_vote_range
    }

def plot_vote_distribution(vote_dist, output_file):
    """投票値の分布をプロット"""
    plt.figure(figsize=(10, 6))
    
    ax = sns.barplot(x=vote_dist.index, y=vote_dist.values)
    
    expected_value = sum(vote_dist.values) / 9
    plt.axhline(y=expected_value, color='r', linestyle='--', label='均等分布の期待値')
    
    plt.title('投票値の分布')
    plt.xlabel('投票値')
    plt.ylabel('投票数')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 1票の部分を強調
    bars = ax.patches
    bars[0].set_facecolor('orange')
    
    # 保存
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_one_vote_percentage_by_project(vote_stats, output_file):
    """プロジェクトごとの1票比率をプロット"""
    plt.figure(figsize=(12, 8))
    
    data = vote_stats.sort_values('one_vote_percentage', ascending=False)
    
    ax = sns.barplot(x='name', y='one_vote_percentage', data=data)
    
    # 期待値のライン（均等分布では11.1%程度）
    plt.axhline(y=100/9, color='r', linestyle='--', label='均等分布での期待値 (11.1%)')
    
    plt.title('プロジェクトごとの1票比率')
    plt.xlabel('プロジェクト名')
    plt.ylabel('1票の割合 (%)')
    plt.legend()
    
    # パーセント表示の設定
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    
    # X軸ラベルの回転
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_voter_patterns(voter_stats, output_file):
    """投票者の投票パターン分布をプロット"""
    plt.figure(figsize=(10, 6))
    
    pattern_counts = voter_stats['vote_pattern'].value_counts().sort_index()
    
    ax = sns.barplot(x=pattern_counts.index, y=pattern_counts.values)
    
    # 各棒の上に値を表示
    for i, v in enumerate(pattern_counts.values):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    plt.title('投票者の1票使用パターン分布')
    plt.xlabel('1票使用パターン')
    plt.ylabel('投票者数')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_heatmap_vote_distribution(votes_df, candidates_df, output_file):
    """投票値の分布ヒートマップをプロット"""
    plt.figure(figsize=(14, 10))
    
    # クロステーブルの作成（候補者×投票値）
    cross_tab = pd.crosstab(
        votes_df['candidate_id'], 
        votes_df['vote_value'],
        margins=False
    )
    
    # 候補者名を取得
    candidate_names = []
    for idx in cross_tab.index:
        name = candidates_df[candidates_df['id'] == idx]['name'].values[0]
        candidate_names.append(name)
    
    cross_tab.index = candidate_names
    
    # ヒートマップ描画
    ax = sns.heatmap(cross_tab, annot=True, cmap="YlGnBu", fmt='d')
    
    plt.title('プロジェクト別 投票値分布ヒートマップ')
    plt.xlabel('投票値')
    plt.ylabel('プロジェクト名')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def generate_report(vote_stats, voter_stats, bias_results, output_file):
    """分析結果のレポート生成"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 中立バイアス分析レポート\n\n")
        
        # 基本統計情報
        f.write("## 1. 基本統計情報\n\n")
        f.write(f"- 総投票数: {vote_stats['count'].sum()}\n")
        f.write(f"- 総投票者数: {len(voter_stats)}\n")
        f.write(f"- 総1票数: {vote_stats['one_vote_count'].sum()} ({vote_stats['one_vote_count'].sum() / vote_stats['count'].sum() * 100:.2f}%)\n")
        f.write(f"- 総0票数: {vote_stats['zero_vote_count'].sum()}\n\n")
        
        # カイ二乗検定結果
        f.write("## 2. 中立バイアス検定結果\n\n")
        f.write(f"- カイ二乗値: {bias_results['chi2_statistic']:.4f}\n")
        f.write(f"- p値: {bias_results['p_value']:.8f}\n")
        f.write(f"- 1票過剰数: {bias_results['one_vote_excess']:.2f} 票\n")
        f.write(f"- 1票過剰率: {bias_results['one_vote_excess_percentage']:.2f}%\n\n")
        
        if bias_results['p_value'] < 0.05:
            f.write("**結果**: 投票値は均等分布と有意に異なっています。中立バイアスの存在が示唆されます。\n\n")
        else:
            f.write("**結果**: 投票値の分布は均等分布と有意に異なるとは言えません。\n\n")
        
        # プロジェクト別1票比率
        f.write("## 3. プロジェクト別1票比率\n\n")
        f.write("| プロジェクト名 | 総投票数 | 1票数 | 1票比率 | 期待1票数 | 1票過剰率 |\n")
        f.write("|--------------|---------|-------|---------|----------|----------|\n")
        
        for _, row in vote_stats.sort_values('one_vote_percentage', ascending=False).iterrows():
            f.write(f"| {row['name']} | {row['count']} | {row['one_vote_count']} | {row['one_vote_percentage']:.2f}% | {row['expected_one_vote_count']:.2f} | {row['one_vote_deviation_percentage']:.2f}% |\n")
        
        f.write("\n")
        
        # 投票者パターン分析
        f.write("## 4. 投票者パターン分析\n\n")
        pattern_counts = voter_stats['vote_pattern'].value_counts().sort_index()
        
        f.write("| 1票使用パターン | 投票者数 | 割合 |\n")
        f.write("|---------------|---------|------|\n")
        
        for pattern, count in pattern_counts.items():
            f.write(f"| {pattern} | {count} | {count/len(voter_stats)*100:.2f}% |\n")
        
        f.write("\n")
        
        # まとめと次のステップ
        f.write("## 5. まとめと次のステップ\n\n")
        
        if bias_results['one_vote_excess_percentage'] > 50:
            bias_level = "強い"
        elif bias_results['one_vote_excess_percentage'] > 20:
            bias_level = "中程度の"
        else:
            bias_level = "弱い"
        
        f.write(f"分析の結果、投票データには{bias_level}中立バイアスの存在が示唆されています。")
        f.write("具体的には、1票（最小投票値）が理論的な期待値よりも")
        f.write(f"{bias_results['one_vote_excess_percentage']:.2f}%多く使用されています。\n\n")
        
        f.write("この結果に基づき、以下の追加分析が推奨されます：\n\n")
        f.write("1. シナリオシミュレーション: 一定割合の1票を0票に変換した場合の予算配分変化\n")
        f.write("2. 投票者別分析: 投票パターンによる中立バイアスの影響度の違い\n")
        f.write("3. UIデザイン提案: バイアスを軽減するための投票インターフェース改善案\n")

def main():
    # データ読み込み
    candidates_df, votes_df = load_csv_data()
    
    # 分析実行
    vote_stats = analyze_vote_distribution(votes_df, candidates_df)
    voter_stats = calculate_voter_patterns(votes_df)
    bias_results = detect_neutral_bias(votes_df, vote_stats)
    
    # 可視化
    plot_vote_distribution(
        bias_results['vote_distribution'], 
        os.path.join(OUTPUT_DIR, 'vote_distribution.png')
    )
    
    plot_one_vote_percentage_by_project(
        vote_stats, 
        os.path.join(OUTPUT_DIR, 'one_vote_percentage_by_project.png')
    )
    
    plot_voter_patterns(
        voter_stats, 
        os.path.join(OUTPUT_DIR, 'voter_patterns.png')
    )
    
    plot_heatmap_vote_distribution(
        votes_df, 
        candidates_df, 
        os.path.join(OUTPUT_DIR, 'vote_heatmap.png')
    )
    
    # レポート生成
    generate_report(
        vote_stats, 
        voter_stats, 
        bias_results, 
        os.path.join(OUTPUT_DIR, 'neutral_bias_report.md')
    )
    
    # CSVファイル保存
    vote_stats.to_csv(os.path.join(OUTPUT_DIR, 'vote_statistics.csv'), index=False)
    voter_stats.to_csv(os.path.join(OUTPUT_DIR, 'voter_statistics.csv'), index=True)
    
    print("分析完了！ 結果は analysis_output ディレクトリに保存されました。")

if __name__ == "__main__":
    main() 