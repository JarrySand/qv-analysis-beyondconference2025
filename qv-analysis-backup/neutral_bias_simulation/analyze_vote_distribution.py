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

# Add dictionary for Japanese to English translation
def get_translation_dict():
    """Create a dictionary for Japanese to English translation"""
    return {
        # Project names (if needed)
        # Labels and titles
        "投票値の分布": "Vote Value Distribution",
        "投票値": "Vote Value",
        "投票数": "Number of Votes", 
        "均等分布の期待値": "Expected (uniform distribution)",
        "コスト調整分布の期待値": "Expected (cost-adjusted distribution)",
        "プロジェクトごとの1票比率": "1-Vote Ratio by Project",
        "プロジェクト名": "Project Name",
        "1票の割合 (%)": "1-Vote Ratio (%)",
        "均等分布での期待値 (11.1%)": "Expected Value for Equal Distribution (11.1%)",
        "投票者の1票使用パターン分布": "Distribution of 1-Vote Usage Patterns",
        "1票使用パターン": "1-Vote Usage Pattern",
        "投票者数": "Number of Voters",
        "プロジェクト別 投票値分布ヒートマップ": "Vote Value Distribution Heatmap by Project",
        
        # Report translations
        "中立バイアス分析レポート": "Neutral Bias Analysis Report",
        "基本統計情報": "Basic Statistical Information",
        "総投票数": "Total Votes",
        "総投票者数": "Total Voters",
        "総1票数": "Total 1-Vote Count",
        "総0票数": "Total 0-Vote Count",
        "中立バイアス検定結果": "Neutral Bias Test Results",
        "カイ二乗値": "Chi-Square Value",
        "p値": "p-Value",
        "1票過剰数": "1-Vote Excess",
        "1票過剰率": "1-Vote Excess Rate",
        "結果": "Result",
        "投票値は均等分布と有意に異なっています。中立バイアスの存在が示唆されます。": "Vote values differ significantly from equal distribution. This suggests the existence of neutral bias.",
        "投票値の分布は均等分布と有意に異なるとは言えません。": "The distribution of vote values is not significantly different from equal distribution.",
        "プロジェクト別1票比率": "1-Vote Ratio by Project",
        "プロジェクト名": "Project Name",
        "総投票数": "Total Votes",
        "1票数": "1-Vote Count",
        "1票比率": "1-Vote Ratio",
        "期待1票数": "Expected 1-Vote Count",
        "1票過剰率": "1-Vote Excess Rate",
        "投票者パターン分析": "Voter Pattern Analysis",
        "1票使用パターン": "1-Vote Usage Pattern",
        "投票者数": "Number of Voters",
        "割合": "Percentage",
        "まとめと次のステップ": "Summary and Next Steps",
        "Very Low 1s": "Very Low 1s",
        "Low 1s": "Low 1s",
        "Medium 1s": "Medium 1s",
        "High 1s": "High 1s",
        "Very High 1s": "Very High 1s",
        "強い": "strong",
        "中程度の": "moderate",
        "弱い": "weak",
        "分析の結果、投票データには": "As a result of the analysis, the voting data suggests the existence of ",
        "中立バイアスの存在が示唆されています。": " neutral bias.",
        "具体的には、1票（最小投票値）が理論的な期待値よりも": "Specifically, 1-votes (minimum vote value) were used ",
        "多く使用されています。": "% more than the theoretical expected value.",
        "この結果に基づき、以下の追加分析が推奨されます：": "Based on these results, the following additional analyses are recommended:",
        "シナリオシミュレーション: 一定割合の1票を0票に変換した場合の予算配分変化": "Scenario simulation: Changes in budget allocation when converting a certain percentage of 1-votes to 0-votes",
        "投票者別分析: 投票パターンによる中立バイアスの影響度の違い": "Voter-specific analysis: Differences in the impact of neutral bias by voting pattern",
        "UIデザイン提案: バイアスを軽減するための投票インターフェース改善案": "UI design proposal: Interface improvements to reduce bias",
        "分析完了！ 結果は analysis_output ディレクトリに保存されました。": "Analysis complete! Results have been saved to the analysis_output directory.",
        "Expected (uniform distribution)": "Expected (uniform distribution)",
        "Expected (cost-adjusted distribution)": "Expected (cost-adjusted distribution)"
    }

def translate_project_name(name):
    """Translate project names to English"""
    project_translations = {
        # Add specific project name translations here as they appear in your data
        "政を祭に変える #vote_forプロジェクト": "Politics to Festival Project",
        "淡路島クエストカレッジ": "Awaji Island Quest College",
        "イナトリアートセンター計画": "Inatori Art Center Plan",
        "JINEN TRAVEL": "JINEN TRAVEL",  # Keep as is if already in English
        "ビオ田んぼプロジェクト": "Bio Rice Field Project",
        "パラ旅応援団": "Para Travel Support Team",
        "10代・20代の「いま、やりたい」を後押しする拠点　ちばユースセンターPRISM": "Chiba Youth Center PRISM"
    }
    
    return project_translations.get(name, name)  # Return original if no translation

def translate_text(text, translation_dict=None):
    """Translate text using the translation dictionary"""
    if translation_dict is None:
        translation_dict = get_translation_dict()
    
    return translation_dict.get(text, text)  # Return original if no translation

# ディレクトリ設定
VOTES_FILE = '../votes.csv'  
CANDIDATES_FILE = '../vote_summary.csv'
OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_csv_data():
    """CSVからデータを読み込む"""
    votes_df = pd.read_csv(VOTES_FILE)
    candidates_df = pd.read_csv(CANDIDATES_FILE)
    
    # 候補者データのカラム名を確認し、必要に応じて変更
    if 'title' in candidates_df.columns:
        candidates_df['name'] = candidates_df['title'].apply(translate_project_name)
    
    # 投票データの変換 - 各候補者カラムを1行に変換する
    # 現在: 各行が投票者、列が候補者
    # 目標: 各行が1つの投票を表す (投票者と候補者のペア)
    
    # 長形式データに変換
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
    
    return candidates_df, votes_long_df

def analyze_vote_distribution(votes_df, candidates_df):
    """投票値の分布分析"""
    # 基本統計量の計算
    vote_stats = votes_df.groupby('candidate_id')['vote_value'].agg([
        'count', 'mean', 'std', 'min', 'max', 
        lambda x: (x == 1).sum()  # 1票の数
    ]).rename(columns={'<lambda_0>': 'one_vote_count'})
    
    # 候補者名を追加
    vote_stats = vote_stats.merge(
        candidates_df[['candidate_id', 'name']], 
        on='candidate_id',
        how='left'
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
        labels=[translate_text('Very Low 1s'), translate_text('Low 1s'), 
                translate_text('Medium 1s'), translate_text('High 1s'), 
                translate_text('Very High 1s')]
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
    
    # Fix for chi-square test: scale expected values to match observed total
    observed_total = observed_counts.sum()
    expected_counts = expected_counts * (observed_total / expected_counts.sum())
    
    # カイ二乗統計量を手動で計算
    chi2_stat = np.sum(((observed_counts - expected_counts) ** 2) / expected_counts)
    
    # 自由度 = 9-1 = 8のカイ二乗分布のp値を計算
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
    trans_dict = get_translation_dict()
    
    plt.figure(figsize=(14, 8))
    
    # 0-9の範囲のデータのみを抽出
    filtered_vote_dist = vote_dist[vote_dist.index.isin(range(0, 10))]
    
    # 合計票数の計算（0-9の範囲のみ）
    total_votes = filtered_vote_dist.sum()
    
    # 各投票値のコスト計算
    costs = {i: i**2 for i in range(0, 10)}
    
    # 棒グラフの作成
    bars = plt.bar(filtered_vote_dist.index, filtered_vote_dist.values, 
             alpha=0.7, color='steelblue', width=0.7)
    
    # 均等分布の期待値（各投票値で等確率）
    expected_value_uniform = total_votes / 10  # 0-9の10種類
    plt.axhline(y=expected_value_uniform, color='r', linestyle='--', 
                label=translate_text('Expected (uniform distribution)', trans_dict))
    
    # コスト調整分布の理論値（コストが高いほど低確率）
    # 各投票値の理論的確率はコストに反比例する
    max_vote_val = 9
    prob_dist = []
    for i in range(0, max_vote_val+1):
        if i == 0:  # 0票の場合は特別に処理
            prob_dist.append(0.1)  # 仮の確率（データに合わせて調整）
        else:
            # コストに反比例する確率（高コスト＝低確率）
            prob_dist.append(1/costs[i])
    
    # 確率を正規化して合計が1になるようにする
    prob_dist = np.array(prob_dist) / sum(prob_dist)
    
    # 理論的分布に基づく期待票数
    expected_counts_cost_adjusted = total_votes * prob_dist
    
    # コスト調整分布の理論値をプロット
    plt.plot(range(0, max_vote_val+1), expected_counts_cost_adjusted, 'g--', 
             linewidth=2, label=translate_text('Expected (cost-adjusted distribution)', trans_dict))
    
    # 棒グラフに各投票値の割合と対応するコストを表示
    for i, v in enumerate(filtered_vote_dist.values):
        vote_value = filtered_vote_dist.index[i]
        percentage = v / total_votes * 100
        cost = costs.get(vote_value, 0)
        
        if v > 0:  # 値が0より大きい場合のみラベルを表示
            plt.text(i, v + 5, f"Cost: {cost}", 
                     ha='center', va='bottom', fontweight='bold')
            plt.text(i, v/2, f"{percentage:.1f}%", 
                     ha='center', va='center', color='white', fontweight='bold')
    
    plt.title(translate_text('Vote Value Distribution', trans_dict), fontsize=14)
    plt.xlabel(translate_text('Vote Value', trans_dict), fontsize=12)
    plt.ylabel(translate_text('Number of Votes', trans_dict), fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(range(0, max_vote_val+1))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def plot_one_vote_percentage_by_project(vote_stats, output_file):
    """プロジェクトごとの1票比率をプロット"""
    trans_dict = get_translation_dict()
    
    plt.figure(figsize=(12, 8))
    
    data = vote_stats.sort_values('one_vote_percentage', ascending=False)
    
    ax = sns.barplot(x='name', y='one_vote_percentage', data=data)
    
    # 期待値のライン（均等分布では11.1%程度）
    plt.axhline(y=100/9, color='r', linestyle='--', label=translate_text('均等分布での期待値 (11.1%)', trans_dict))
    
    plt.title(translate_text('プロジェクトごとの1票比率', trans_dict))
    plt.xlabel(translate_text('プロジェクト名', trans_dict))
    plt.ylabel(translate_text('1票の割合 (%)', trans_dict))
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
    trans_dict = get_translation_dict()
    
    plt.figure(figsize=(10, 6))
    
    pattern_counts = voter_stats['vote_pattern'].value_counts().sort_index()
    
    ax = sns.barplot(x=pattern_counts.index, y=pattern_counts.values)
    
    # 各棒の上に値を表示
    for i, v in enumerate(pattern_counts.values):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    plt.title(translate_text('投票者の1票使用パターン分布', trans_dict))
    plt.xlabel(translate_text('1票使用パターン', trans_dict))
    plt.ylabel(translate_text('投票者数', trans_dict))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_heatmap_vote_distribution(votes_df, candidates_df, output_file):
    """投票値の分布ヒートマップをプロット"""
    trans_dict = get_translation_dict()
    
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
        name = candidates_df[candidates_df['candidate_id'] == idx]['name'].values[0]
        candidate_names.append(name)
    
    cross_tab.index = candidate_names
    
    # ヒートマップ描画
    ax = sns.heatmap(cross_tab, annot=True, cmap="YlGnBu", fmt='d')
    
    plt.title(translate_text('プロジェクト別 投票値分布ヒートマップ', trans_dict))
    plt.xlabel(translate_text('投票値', trans_dict))
    plt.ylabel(translate_text('プロジェクト名', trans_dict))
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def generate_report(vote_stats, voter_stats, bias_results, output_file):
    """分析結果のレポート生成"""
    trans_dict = get_translation_dict()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {translate_text('中立バイアス分析レポート', trans_dict)}\n\n")
        
        # 基本統計情報
        f.write(f"## 1. {translate_text('基本統計情報', trans_dict)}\n\n")
        f.write(f"- {translate_text('総投票数', trans_dict)}: {vote_stats['count'].sum()}\n")
        f.write(f"- {translate_text('総投票者数', trans_dict)}: {len(voter_stats)}\n")
        f.write(f"- {translate_text('総1票数', trans_dict)}: {vote_stats['one_vote_count'].sum()} ({vote_stats['one_vote_count'].sum() / vote_stats['count'].sum() * 100:.2f}%)\n")
        f.write(f"- {translate_text('総0票数', trans_dict)}: {vote_stats['zero_vote_count'].sum()}\n\n")
        
        # カイ二乗検定結果
        f.write(f"## 2. {translate_text('中立バイアス検定結果', trans_dict)}\n\n")
        f.write(f"- {translate_text('カイ二乗値', trans_dict)}: {bias_results['chi2_statistic']:.4f}\n")
        f.write(f"- {translate_text('p値', trans_dict)}: {bias_results['p_value']:.8f}\n")
        f.write(f"- {translate_text('1票過剰数', trans_dict)}: {bias_results['one_vote_excess']:.2f} {translate_text('票', trans_dict)}\n")
        f.write(f"- {translate_text('1票過剰率', trans_dict)}: {bias_results['one_vote_excess_percentage']:.2f}%\n\n")
        
        if bias_results['p_value'] < 0.05:
            f.write(f"**{translate_text('結果', trans_dict)}**: {translate_text('投票値は均等分布と有意に異なっています。中立バイアスの存在が示唆されます。', trans_dict)}\n\n")
        else:
            f.write(f"**{translate_text('結果', trans_dict)}**: {translate_text('投票値の分布は均等分布と有意に異なるとは言えません。', trans_dict)}\n\n")
        
        # プロジェクト別1票比率
        f.write(f"## 3. {translate_text('プロジェクト別1票比率', trans_dict)}\n\n")
        f.write(f"| {translate_text('プロジェクト名', trans_dict)} | {translate_text('総投票数', trans_dict)} | {translate_text('1票数', trans_dict)} | {translate_text('1票比率', trans_dict)} | {translate_text('期待1票数', trans_dict)} | {translate_text('1票過剰率', trans_dict)} |\n")
        f.write("|--------------|---------|-------|---------|----------|----------|\n")
        
        for _, row in vote_stats.sort_values('one_vote_percentage', ascending=False).iterrows():
            f.write(f"| {row['name']} | {row['count']} | {row['one_vote_count']} | {row['one_vote_percentage']:.2f}% | {row['expected_one_vote_count']:.2f} | {row['one_vote_deviation_percentage']:.2f}% |\n")
        
        f.write("\n")
        
        # 投票者パターン分析
        f.write(f"## 4. {translate_text('投票者パターン分析', trans_dict)}\n\n")
        pattern_counts = voter_stats['vote_pattern'].value_counts().sort_index()
        
        f.write(f"| {translate_text('1票使用パターン', trans_dict)} | {translate_text('投票者数', trans_dict)} | {translate_text('割合', trans_dict)} |\n")
        f.write("|---------------|---------|------|\n")
        
        for pattern, count in pattern_counts.items():
            f.write(f"| {pattern} | {count} | {count/len(voter_stats)*100:.2f}% |\n")
        
        f.write("\n")
        
        # まとめと次のステップ
        f.write(f"## 5. {translate_text('まとめと次のステップ', trans_dict)}\n\n")
        
        if bias_results['one_vote_excess_percentage'] > 50:
            bias_level = translate_text("強い", trans_dict)
        elif bias_results['one_vote_excess_percentage'] > 20:
            bias_level = translate_text("中程度の", trans_dict)
        else:
            bias_level = translate_text("弱い", trans_dict)
        
        f.write(f"{translate_text('分析の結果、投票データには', trans_dict)}{bias_level}{translate_text('中立バイアスの存在が示唆されています。', trans_dict)}")
        f.write(f"{translate_text('具体的には、1票（最小投票値）が理論的な期待値よりも', trans_dict)}")
        f.write(f"{bias_results['one_vote_excess_percentage']:.2f}{translate_text('多く使用されています。', trans_dict)}\n\n")
        
        f.write(f"{translate_text('この結果に基づき、以下の追加分析が推奨されます：', trans_dict)}\n\n")
        f.write(f"1. {translate_text('シナリオシミュレーション: 一定割合の1票を0票に変換した場合の予算配分変化', trans_dict)}\n")
        f.write(f"2. {translate_text('投票者別分析: 投票パターンによる中立バイアスの影響度の違い', trans_dict)}\n")
        f.write(f"3. {translate_text('UIデザイン提案: バイアスを軽減するための投票インターフェース改善案', trans_dict)}\n")

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
    
    print(translate_text("分析完了！ 結果は analysis_output ディレクトリに保存されました。"))

if __name__ == "__main__":
    main() 