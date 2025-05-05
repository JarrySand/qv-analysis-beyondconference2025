#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
投票値の分布分析と中立バイアス（1票の過剰使用）の検出を行うスクリプト
国際化対応版（英語表示のみ）
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.ticker as mtick
import time  # 処理時間計測用
import gc  # ガベージコレクション用

# パフォーマンス向上のための設定
plt.rcParams['figure.dpi'] = 100
plt.switch_backend('agg')  # 描画エンジンを高速なものに

# フォントエラーを回避するための設定
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']

# 警告を抑制
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

class VoteDistributionAnalyzer:
    """投票分布分析クラス"""
    
    def __init__(self, votes_file='data/votes.csv', candidates_file='data/candidates.csv', output_dir='output/analysis'):
        """初期化"""
        self.votes_file = votes_file
        self.candidates_file = candidates_file
        self.output_dir = output_dir
        
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        # データの読み込み
        print(f"投票データを読み込んでいます: {votes_file}")
        self.votes_df = pd.read_csv(votes_file)
        
        print(f"候補者データを読み込んでいます: {candidates_file}")
        self.candidates_df = pd.read_csv(candidates_file)
        
        # 分析結果格納用
        self.votes_long_df = None
        self.vote_distribution = None
        self.vote_stats = None
        self.voter_stats = None
        self.bias_results = None
        
        # 長形式データへの変換
        self._convert_to_long_format()
    
    def _convert_to_long_format(self):
        """投票データを長形式に変換"""
        vote_rows = []
        
        for _, row in self.votes_df.iterrows():
            voter_id = row['voter_id']
            
            # 各候補者への投票を抽出
            for i in range(len(self.candidates_df)):
                col_name = f'candidate_{i}'
                if col_name in row and not pd.isna(row[col_name]):
                    vote_rows.append({
                        'voter_id': voter_id,
                        'candidate_id': i,
                        'vote_value': int(row[col_name])
                    })
        
        # 新しいデータフレームを作成
        self.votes_long_df = pd.DataFrame(vote_rows)

    def analyze_vote_distribution(self):
        """投票値の分布分析"""
        print("投票分布を分析しています...")
        
        # 候補者ごとの投票統計
        self.vote_stats = self.votes_long_df.groupby('candidate_id')['vote_value'].agg([
            'count', 'mean', 'std', 'min', 'max', 
            lambda x: (x == 1).sum()  # 1票の数
        ]).rename(columns={'<lambda_0>': 'one_vote_count'})
        
        # 候補者名を追加
        self.vote_stats = self.vote_stats.merge(
            self.candidates_df[['candidate_id', 'title']], 
            left_index=True, 
            right_on='candidate_id'
        )
        
        # 1票の割合を計算
        self.vote_stats['one_vote_percentage'] = self.vote_stats['one_vote_count'] / self.vote_stats['count'] * 100
        
        # 理論的な分布との比較
        # 仮説: 投票値が均等に分布する場合、1票の割合は約1/9 (11.1%)になるはず
        self.vote_stats['expected_one_vote_count'] = self.vote_stats['count'] / 9
        self.vote_stats['one_vote_deviation'] = self.vote_stats['one_vote_count'] - self.vote_stats['expected_one_vote_count']
        self.vote_stats['one_vote_deviation_percentage'] = (self.vote_stats['one_vote_deviation'] / self.vote_stats['expected_one_vote_count']) * 100
        
        return self.vote_stats
    
    def calculate_voter_patterns(self):
        """投票者ごとの投票パターン分析"""
        print("投票者パターンを分析しています...")
        
        # 投票者ごとの統計
        self.voter_stats = self.votes_long_df.groupby('voter_id').agg(
            total_votes=('vote_value', 'count'),
            one_votes=('vote_value', lambda x: (x == 1).sum()),
            mean_vote=('vote_value', 'mean'),
            max_vote=('vote_value', 'max')
        )
        
        self.voter_stats['one_vote_percentage'] = self.voter_stats['one_votes'] / self.voter_stats['total_votes'] * 100
        
        # 投票パターンによるグループ分け
        self.voter_stats['vote_pattern'] = pd.cut(
            self.voter_stats['one_vote_percentage'],
            bins=[0, 20, 40, 60, 80, 100],
            labels=["Very Low 1s", "Low 1s", "Medium 1s", "High 1s", "Very High 1s"]
        )
        
        return self.voter_stats
    
    def detect_neutral_bias(self):
        """中立バイアスの検出"""
        print("中立バイアスを検出しています...")
        
        # 全体の投票値分布
        vote_dist = self.votes_long_df['vote_value'].value_counts().sort_index()
        vote_dist_pct = vote_dist / vote_dist.sum() * 100
        
        # 均等分布を仮定した場合の期待値
        total_votes = len(self.votes_long_df) 
        expected_per_vote = total_votes / 9  # 均等分布なら各票数(1-9)は同じ頻度
        
        # 分布の不均等性を計算
        observed_counts = np.array([vote_dist.get(i, 0) for i in range(1, 10)])
        expected_counts = np.ones(9) * expected_per_vote
        
        # カイ二乗統計量を計算
        chi2_stat = np.sum(((observed_counts - expected_counts) ** 2) / expected_counts)
        
        # 自由度 = 9-1 = 8のカイ二乗分布のp値を計算
        p_value = stats.chi2.sf(chi2_stat, 8)
        
        # 1票過剰使用の検出
        one_vote_excess = vote_dist.get(1, 0) - expected_per_vote
        one_vote_excess_pct = (one_vote_excess / expected_per_vote) * 100 if expected_per_vote > 0 else 0
        
        # プロジェクトごとの1票比率の不均等性
        one_vote_percentages = self.vote_stats['one_vote_percentage']
        one_vote_std = one_vote_percentages.std()
        one_vote_range = one_vote_percentages.max() - one_vote_percentages.min()
        
        self.bias_results = {
            'vote_distribution': vote_dist,
            'vote_distribution_percentage': vote_dist_pct,
            'chi2_statistic': chi2_stat,
            'p_value': p_value,
            'one_vote_excess': one_vote_excess,
            'one_vote_excess_percentage': one_vote_excess_pct,
            'one_vote_percentage_std': one_vote_std,
            'one_vote_percentage_range': one_vote_range,
            'is_biased': p_value < 0.05
        }
        
        return self.bias_results
    
    def plot_vote_distribution(self):
        """投票値の分布をプロット"""
        print("投票値の分布グラフを作成しています...")
        
        plt.figure(figsize=(10, 6))
        
        vote_dist = self.bias_results['vote_distribution']
        
        ax = sns.barplot(x=vote_dist.index, y=vote_dist.values)
        
        expected_value = sum(vote_dist.values) / 9
        plt.axhline(y=expected_value, color='r', linestyle='--', 
                   label="Expected Value for Equal Distribution (11.1%)")
        
        plt.title("Vote Value Distribution")
        plt.xlabel("Vote Value")
        plt.ylabel("Number of Votes")
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 1票の部分を強調
        bars = ax.patches
        if len(bars) > 0:
            bars[0].set_facecolor('orange')
        
        # 保存
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'vote_distribution.png'), dpi=300)
        plt.close()
        
        print(f"グラフを保存しました: {os.path.join(self.output_dir, 'vote_distribution.png')}")
    
    def plot_one_vote_percentage_by_project(self):
        """プロジェクトごとの1票比率をプロット"""
        print("プロジェクトごとの1票比率グラフを作成しています...")
        start_time = time.time()
        
        plt.figure(figsize=(12, 8))
        
        # データの準備
        data = self.vote_stats.sort_values('one_vote_percentage', ascending=False)
        
        # votes_statsにtitle_enがなければ、candidates_dfから取得して追加
        if 'title_en' not in data.columns:
            title_en_map = dict(zip(self.candidates_df['candidate_id'], self.candidates_df['title_en']))
            data['title_en'] = data['candidate_id'].map(title_en_map)
        
        # 英語のプロジェクト名でプロット
        ax = sns.barplot(x='title_en', y='one_vote_percentage', data=data)
        
        # 期待値のライン（均等分布では11.1%程度）
        plt.axhline(y=100/9, color='r', linestyle='--', 
                   label="Expected Value for Equal Distribution (11.1%)")
        
        plt.title("1-Vote Ratio by Project")
        plt.xlabel("Project Name")
        plt.ylabel("1-Vote Ratio (%)")
        plt.legend()
        
        # パーセント表示の設定
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        
        # X軸ラベルの回転
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'one_vote_by_project.png'), dpi=300)
        plt.close()
        
        print(f"グラフを保存しました: {os.path.join(self.output_dir, 'one_vote_by_project.png')}")
        print(f"  処理時間: {time.time() - start_time:.2f}秒")
    
    def plot_voter_patterns(self):
        """投票者の投票パターン分布をプロット"""
        print("投票者パターン分布グラフを作成しています...")
        
        plt.figure(figsize=(10, 6))
        
        pattern_counts = self.voter_stats['vote_pattern'].value_counts().sort_index()
        
        ax = sns.barplot(x=pattern_counts.index, y=pattern_counts.values)
        
        # 各棒の上に値を表示
        for i, v in enumerate(pattern_counts.values):
            ax.text(i, v + 0.5, str(v), ha='center')
        
        plt.title("Distribution of 1-Vote Usage Patterns")
        plt.xlabel("1-Vote Usage Pattern")
        plt.ylabel("Number of Voters")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'voter_patterns.png'), dpi=300)
        plt.close()
        
        print(f"グラフを保存しました: {os.path.join(self.output_dir, 'voter_patterns.png')}")
    
    def plot_heatmap_vote_distribution(self):
        """投票値の分布ヒートマップをプロット"""
        print("投票値の分布ヒートマップを作成しています...")
        
        plt.figure(figsize=(14, 10))
        
        # クロステーブルの作成（候補者×投票値）
        cross_tab = pd.crosstab(
            self.votes_long_df['candidate_id'], 
            self.votes_long_df['vote_value'],
            margins=False
        )
        
        # 候補者名をCSVから直接取得
        candidate_names = []
        for idx in cross_tab.index:
            # candidates.csvから英語のタイトルを取得
            title_en = self.candidates_df[self.candidates_df['candidate_id'] == idx]['title_en'].values[0]
            candidate_names.append(title_en)
        
        cross_tab.index = candidate_names
        
        # ヒートマップ描画
        ax = sns.heatmap(cross_tab, annot=True, cmap="YlGnBu", fmt='d')
        
        plt.title("Vote Value Distribution Heatmap by Project")
        plt.xlabel("Vote Value")
        plt.ylabel("Project Name")
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'vote_heatmap.png'), dpi=300)
        plt.close()
        
        print(f"グラフを保存しました: {os.path.join(self.output_dir, 'vote_heatmap.png')}")
    
    def generate_report(self):
        """分析結果のテキストレポートを生成"""
        print("分析レポートを生成しています...")
        
        # レポートファイルパス
        report_file = os.path.join(self.output_dir, 'bias_analysis_report.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Neutral Bias Analysis Report\n\n")
            
            # 基本統計情報
            f.write(f"## Basic Statistical Information\n\n")
            f.write(f"- Total Votes: {len(self.votes_long_df)}\n")
            f.write(f"- Total Voters: {len(self.votes_df)}\n")
            f.write(f"- Total 1-Vote Count: {self.bias_results['vote_distribution'].get(1, 0)} "
                  f"({self.bias_results['vote_distribution'].get(1, 0) / len(self.votes_long_df) * 100:.2f}%)\n\n")
            
            # カイ二乗検定結果
            f.write(f"## Chi-Square Test Results\n\n")
            f.write(f"- Chi-Square Value: x^2={self.bias_results['chi2_statistic']:.4f}\n")
            f.write(f"- p-Value: {self.bias_results['p_value']:.8f}\n")
            f.write(f"- 1-Vote Excess: {self.bias_results['one_vote_excess']:.2f}\n")
            f.write(f"- 1-Vote Excess Rate: {self.bias_results['one_vote_excess_percentage']:.2f}%\n\n")
            
            # 検定結果の解釈
            f.write(f"### Result\n\n")
            if self.bias_results['is_biased']:
                f.write(f"Vote values differ significantly from equal distribution. This suggests the existence of neutral bias.\n\n")
            else:
                f.write(f"The distribution of vote values is not significantly different from equal distribution.\n\n")
            
            # プロジェクト別1票比率
            f.write(f"## 1-Vote Ratio by Project\n\n")
            f.write("| Project | Total Votes | 1-Vote Count | 1-Vote Ratio | Expected 1-Votes | Excess (%) |\n")
            f.write("|---------|------------|-------------|-------------|----------------|----------|\n")
            
            for _, row in self.vote_stats.sort_values('one_vote_percentage', ascending=False).iterrows():
                project_name = row['title']
                f.write(f"| {project_name} | {row['count']} | {row['one_vote_count']} | "
                       f"{row['one_vote_percentage']:.1f}% | {row['expected_one_vote_count']:.1f} | "
                       f"{row['one_vote_deviation_percentage']:.1f}% |\n")
            
            f.write("\n")
            
            # 投票者パターン分析
            f.write(f"## Voter Pattern Analysis\n\n")
            f.write("| Pattern Category | Voters | Percentage |\n")
            f.write("|-----------------|--------|------------|\n")
            
            # 投票者パターンの結果
            voter_pattern_stats = self.voter_stats['vote_pattern'].value_counts(normalize=True) * 100
            for category, percentage in voter_pattern_stats.items():
                f.write(f"| {category} | {self.voter_stats['vote_pattern'].value_counts()[category]} | {percentage:.1f}% |\n")
            
            f.write("\n")
            
            # 結論
            bias_strength = ""
            if self.bias_results['one_vote_excess_percentage'] > 50:
                bias_strength = "Strong"
            elif self.bias_results['one_vote_excess_percentage'] > 20:
                bias_strength = "Moderate"
            else:
                bias_strength = "Weak"
            
            f.write(f"This analysis suggests the existence of {bias_strength} neutral bias in the voting data.\n")
            f.write(f"Specifically, 1-vote (minimum vote value) is being used {self.bias_results['one_vote_excess_percentage']:.1f}% more than the expected value.\n\n")
            
            f.write("Recommendations for further analysis:\n\n")
            f.write("1. Scenario Simulation: How budget allocation changes when a certain percentage of 1-votes are converted to 0-votes\n")
            f.write("2. Voter-Specific Analysis: Differences in the impact of voting patterns on neutral bias\n")
            f.write("3. UI Design Proposal: Improvements to the voting interface to reduce bias\n")
        
        print(f"レポートを保存しました: {report_file}")
        return report_file
    
    def run_all_analyses(self):
        """すべての分析と可視化を実行"""
        print("すべての分析を実行しています...\n")
        start_time = time.time()
        
        # 必須の初期分析
        self.analyze_vote_distribution()
        self.calculate_voter_patterns()
        
        # 分析実行
        self.detect_neutral_bias()
        
        # ガベージコレクションを実行
        gc.collect()
        
        # 可視化（個別に実行してメモリを解放）
        self.plot_vote_distribution()
        gc.collect()
        
        self.plot_one_vote_percentage_by_project()
        gc.collect()
        
        self.plot_voter_patterns()
        gc.collect()
        
        self.plot_heatmap_vote_distribution()
        gc.collect()
        
        # レポート生成
        report_file = self.generate_report()
        gc.collect()
        
        print(f"\n分析完了！ 結果は {self.output_dir} ディレクトリに保存されました。")
        print(f"レポート: {report_file}")
        print(f"総処理時間: {time.time() - start_time:.2f}秒")

def main():
    """メイン関数"""
    # ディレクトリ設定
    data_dir = 'data'
    output_dir = 'results/figures/basic_analysis'
    
    # 分析インスタンス作成
    analyzer = VoteDistributionAnalyzer(
        votes_file=f'{data_dir}/votes.csv',
        candidates_file=f'{data_dir}/candidates.csv',
        output_dir=output_dir
    )
    
    # 分析実行
    analyzer.run_all_analyses()
    
    print(f"\n分析が完了しました。結果は {output_dir} ディレクトリに保存されています。")

if __name__ == "__main__":
    main() 