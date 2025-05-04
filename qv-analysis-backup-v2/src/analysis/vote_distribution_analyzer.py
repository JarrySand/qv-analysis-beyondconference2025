#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
投票値の分布分析と中立バイアス（1票の過剰使用）の検出を行うスクリプト
国際化対応版
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.ticker as mtick

# 翻訳辞書
def get_translation_dict():
    """日英翻訳辞書を作成"""
    return {
        # プロジェクト名
        "ちばユースセンターPRISM": "Chiba Youth Center PRISM",
        "政を祭に変える #vote_forプロジェクト": "#vote_for Project",
        "#vote_forプロジェクト": "#vote_for Project",
        "淡路島クエストカレッジ": "Awaji Island Quest College",
        "イナトリアートセンター計画": "Inatori Art Center Plan",
        "JINEN TRAVEL": "JINEN TRAVEL",
        "ビオ田んぼプロジェクト": "Bio Rice Field Project",
        "パラ旅応援団": "Para Travel Support Team",
        
        # ラベルとタイトル
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
        
        # レポート翻訳
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
        "投票値は均等分布と有意に異なっています。中立バイアスの存在が示唆されます。": 
            "Vote values differ significantly from equal distribution. This suggests the existence of neutral bias.",
        "投票値の分布は均等分布と有意に異なるとは言えません。": 
            "The distribution of vote values is not significantly different from equal distribution.",
        
        # 投票者パターン
        "Very Low 1s": "Very Low 1s",
        "Low 1s": "Low 1s",
        "Medium 1s": "Medium 1s",
        "High 1s": "High 1s",
        "Very High 1s": "Very High 1s"
    }

def translate_text(text, translation_dict=None):
    """翻訳辞書を使用してテキストを翻訳"""
    if translation_dict is None:
        translation_dict = get_translation_dict()
    
    return translation_dict.get(text, text)  # 翻訳がない場合は元の文字列を返す

class VoteDistributionAnalyzer:
    """投票分布分析クラス"""
    
    def __init__(self, votes_file='data/votes.csv', candidates_file='data/candidates.csv', 
                 output_dir='results/figures/basic_analysis'):
        """
        初期化
        
        Parameters:
        -----------
        votes_file : str
            投票データのファイルパス
        candidates_file : str
            候補者データのファイルパス
        output_dir : str
            出力ディレクトリ
        """
        self.votes_file = votes_file
        self.candidates_file = candidates_file
        self.output_dir = output_dir
        self.translation_dict = get_translation_dict()
        
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        # データ読み込み
        self.load_data()
    
    def load_data(self):
        """データの読み込みと前処理"""
        print("データを読み込んでいます...")
        
        # CSVファイル読み込み
        self.votes_df = pd.read_csv(self.votes_file)
        self.candidates_df = pd.read_csv(self.candidates_file)
        
        # 投票データを長形式に変換
        self.convert_to_long_format()
        
        print(f"データ読み込み完了: {len(self.votes_long_df)}行の投票データ")
    
    def convert_to_long_format(self):
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
            self.candidates_df[['id', 'title']], 
            left_index=True, 
            right_on='id'
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
            labels=[translate_text('Very Low 1s'), translate_text('Low 1s'), 
                    translate_text('Medium 1s'), translate_text('High 1s'), 
                    translate_text('Very High 1s')]
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
                   label=translate_text('均等分布の期待値'))
        
        plt.title(translate_text('投票値の分布'))
        plt.xlabel(translate_text('投票値'))
        plt.ylabel(translate_text('投票数'))
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
        
        plt.figure(figsize=(12, 8))
        
        data = self.vote_stats.sort_values('one_vote_percentage', ascending=False)
        
        # タイトルを英語に変換
        data['title_en'] = data['title'].apply(lambda x: translate_text(x))
        
        ax = sns.barplot(x='title_en', y='one_vote_percentage', data=data)
        
        # 期待値のライン（均等分布では11.1%程度）
        plt.axhline(y=100/9, color='r', linestyle='--', 
                   label=translate_text('均等分布での期待値 (11.1%)'))
        
        plt.title(translate_text('プロジェクトごとの1票比率'))
        plt.xlabel(translate_text('プロジェクト名'))
        plt.ylabel(translate_text('1票の割合 (%)'))
        plt.legend()
        
        # パーセント表示の設定
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        
        # X軸ラベルの回転
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'one_vote_by_project.png'), dpi=300)
        plt.close()
        
        print(f"グラフを保存しました: {os.path.join(self.output_dir, 'one_vote_by_project.png')}")
    
    def plot_voter_patterns(self):
        """投票者の投票パターン分布をプロット"""
        print("投票者パターン分布グラフを作成しています...")
        
        plt.figure(figsize=(10, 6))
        
        pattern_counts = self.voter_stats['vote_pattern'].value_counts().sort_index()
        
        ax = sns.barplot(x=pattern_counts.index, y=pattern_counts.values)
        
        # 各棒の上に値を表示
        for i, v in enumerate(pattern_counts.values):
            ax.text(i, v + 0.5, str(v), ha='center')
        
        plt.title(translate_text('投票者の1票使用パターン分布'))
        plt.xlabel(translate_text('1票使用パターン'))
        plt.ylabel(translate_text('投票者数'))
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
        
        # 候補者名を取得
        candidate_names = []
        for idx in cross_tab.index:
            title = self.candidates_df[self.candidates_df['id'] == idx]['title'].values[0]
            candidate_names.append(translate_text(title))
        
        cross_tab.index = candidate_names
        
        # ヒートマップ描画
        ax = sns.heatmap(cross_tab, annot=True, cmap="YlGnBu", fmt='d')
        
        plt.title(translate_text('プロジェクト別 投票値分布ヒートマップ'))
        plt.xlabel(translate_text('投票値'))
        plt.ylabel(translate_text('プロジェクト名'))
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'vote_heatmap.png'), dpi=300)
        plt.close()
        
        print(f"グラフを保存しました: {os.path.join(self.output_dir, 'vote_heatmap.png')}")
    
    def generate_report(self):
        """分析結果のレポート生成"""
        print("分析レポートを生成しています...")
        
        report_file = os.path.join(self.output_dir, 'neutral_bias_report.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# {translate_text('中立バイアス分析レポート')}\n\n")
            
            # 基本統計情報
            f.write(f"## {translate_text('基本統計情報')}\n\n")
            f.write(f"- {translate_text('総投票数')}: {len(self.votes_long_df)}\n")
            f.write(f"- {translate_text('総投票者数')}: {len(self.votes_df)}\n")
            f.write(f"- {translate_text('総1票数')}: {self.bias_results['vote_distribution'].get(1, 0)} "
                   f"({self.bias_results['vote_distribution'].get(1, 0) / len(self.votes_long_df) * 100:.2f}%)\n\n")
            
            # カイ二乗検定結果
            f.write(f"## {translate_text('中立バイアス検定結果')}\n\n")
            f.write(f"- {translate_text('カイ二乗値')}: {self.bias_results['chi2_statistic']:.4f}\n")
            f.write(f"- {translate_text('p値')}: {self.bias_results['p_value']:.8f}\n")
            f.write(f"- {translate_text('1票過剰数')}: {self.bias_results['one_vote_excess']:.2f}\n")
            f.write(f"- {translate_text('1票過剰率')}: {self.bias_results['one_vote_excess_percentage']:.2f}%\n\n")
            
            # 検定結果の解釈
            f.write(f"### {translate_text('結果')}\n\n")
            if self.bias_results['is_biased']:
                f.write(f"{translate_text('投票値は均等分布と有意に異なっています。中立バイアスの存在が示唆されます。')}\n\n")
            else:
                f.write(f"{translate_text('投票値の分布は均等分布と有意に異なるとは言えません。')}\n\n")
            
            # プロジェクト別1票比率
            f.write(f"## {translate_text('プロジェクト別1票比率')}\n\n")
            f.write("| Project | Total Votes | 1-Vote Count | 1-Vote Ratio | Expected 1-Votes | Excess (%) |\n")
            f.write("|---------|-------------|--------------|--------------|-----------------|------------|\n")
            
            for _, row in self.vote_stats.sort_values('one_vote_percentage', ascending=False).iterrows():
                project_name = translate_text(row['title'])
                f.write(f"| {project_name} | {row['count']} | {row['one_vote_count']} | "
                       f"{row['one_vote_percentage']:.1f}% | {row['expected_one_vote_count']:.1f} | "
                       f"{row['one_vote_deviation_percentage']:.1f}% |\n")
            
            f.write("\n")
            
            # 投票者パターン分析
            f.write(f"## {translate_text('投票者パターン分析')}\n\n")
            pattern_counts = self.voter_stats['vote_pattern'].value_counts().sort_index()
            total_voters = len(self.voter_stats)
            
            f.write("| Pattern | Voters | Percentage |\n")
            f.write("|---------|--------|------------|\n")
            
            for pattern, count in pattern_counts.items():
                percentage = count / total_voters * 100
                f.write(f"| {pattern} | {count} | {percentage:.1f}% |\n")
            
            f.write("\n")
            
            # まとめと次のステップ
            f.write("## Summary and Next Steps\n\n")
            
            # バイアスの強さを評価
            bias_strength = ""
            if self.bias_results['one_vote_excess_percentage'] > 50:
                bias_strength = translate_text("強い")
            elif self.bias_results['one_vote_excess_percentage'] > 20:
                bias_strength = translate_text("中程度の")
            else:
                bias_strength = translate_text("弱い")
            
            f.write(f"{translate_text('分析の結果、投票データには')}{bias_strength}"
                   f"{translate_text('中立バイアスの存在が示唆されています。')}\n")
            f.write(f"{translate_text('具体的には、1票（最小投票値）が理論的な期待値よりも')}"
                   f"{self.bias_results['one_vote_excess_percentage']:.1f}"
                   f"{translate_text('多く使用されています。')}\n\n")
            
            f.write(f"{translate_text('この結果に基づき、以下の追加分析が推奨されます：')}\n\n")
            f.write(f"1. {translate_text('シナリオシミュレーション: 一定割合の1票を0票に変換した場合の予算配分変化')}\n")
            f.write(f"2. {translate_text('投票者別分析: 投票パターンによる中立バイアスの影響度の違い')}\n")
            f.write(f"3. {translate_text('UIデザイン提案: バイアスを軽減するための投票インターフェース改善案')}\n")
        
        print(f"レポートを保存しました: {report_file}")
        return report_file
    
    def run_all_analyses(self):
        """すべての分析と可視化を実行"""
        print("すべての分析を実行しています...\n")
        
        # 分析実行
        self.analyze_vote_distribution()
        self.calculate_voter_patterns()
        self.detect_neutral_bias()
        
        # 可視化
        self.plot_vote_distribution()
        self.plot_one_vote_percentage_by_project()
        self.plot_voter_patterns()
        self.plot_heatmap_vote_distribution()
        
        # レポート生成
        report_file = self.generate_report()
        
        print(f"\n分析完了！ 結果は {self.output_dir} ディレクトリに保存されました。")
        print(f"レポート: {report_file}")

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