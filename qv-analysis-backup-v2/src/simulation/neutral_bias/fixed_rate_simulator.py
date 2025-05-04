#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
一定割合の1票を0票に変換する中立バイアスシミュレーター
"""

import os
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from .bias_simulator_base import BiasSimulatorBase

class FixedRateSimulator(BiasSimulatorBase):
    """一定割合の1票を0票に変換するシミュレーター"""
    
    def __init__(self, conversion_rate=0.3, votes_file='data/votes.csv', 
                 candidates_file='data/candidates.csv', 
                 output_dir='results/bias_simulation/fixed_rate'):
        """
        初期化
        
        Parameters:
        -----------
        conversion_rate : float
            1票を0票に変換する割合 (0.0～1.0)
        votes_file : str
            投票データのファイルパス
        candidates_file : str
            候補者データのファイルパス
        output_dir : str
            出力ディレクトリ
        """
        # 変換率を保存
        self.conversion_rate = conversion_rate
        
        # 親クラスの初期化
        super().__init__(votes_file, candidates_file, output_dir)
    
    def simulate(self):
        """
        一定割合の1票を0票に変換するシミュレーション
        
        Returns:
        --------
        pandas.DataFrame
            シミュレーション結果の投票データ（長形式）
        """
        print(f"1票の {self.conversion_rate*100:.1f}% を0票に変換するシミュレーションを実行しています...")
        
        # 元のデータをコピー
        simulated_df = self.votes_long_df.copy()
        
        # 1票のインデックスを取得
        one_vote_indices = simulated_df[simulated_df['vote_value'] == 1].index
        
        # 変換する1票の数
        num_to_convert = int(len(one_vote_indices) * self.conversion_rate)
        
        # ランダムに変換するインデックスを選択
        indices_to_convert = random.sample(list(one_vote_indices), num_to_convert)
        
        # 選択された1票を0票に変換（実質的に削除）
        simulated_df = simulated_df.drop(indices_to_convert)
        
        print(f"{num_to_convert}票（全体の{num_to_convert/len(self.votes_long_df)*100:.1f}%）を1票から0票に変換しました")
        
        return simulated_df
    
    def run_simulations(self, rates=None):
        """
        複数の変換率でシミュレーションを実行
        
        Parameters:
        -----------
        rates : list of float, optional
            変換率のリスト。指定しない場合は[0.1, 0.3, 0.5]を使用
            
        Returns:
        --------
        dict
            変換率ごとの比較結果
        """
        if rates is None:
            rates = [0.1, 0.3, 0.5]
        
        print(f"複数の変換率 {rates} でシミュレーションを実行しています...")
        
        # 元の予算配分を計算
        original_results = self.calculate_qv_results()
        
        # 各変換率でシミュレーション
        results = {}
        for rate in rates:
            # 変換率を設定
            self.conversion_rate = rate
            
            # シミュレーション実行
            simulated_votes = self.simulate()
            
            # シミュレーション後の予算配分を計算
            simulated_results = self.calculate_qv_results(simulated_votes)
            
            # 結果比較
            comparison = self.compare_results(original_results, simulated_results)
            
            # 結果を保存
            results[rate] = {
                'simulated_votes': simulated_votes,
                'budget_results': simulated_results,
                'comparison': comparison
            }
            
            # 比較結果をプロット
            output_file = os.path.join(self.output_dir, f'budget_comparison_rate{int(rate*100)}.png')
            self.plot_comparison(comparison, output_file)
            
            # 結果をCSVに保存
            simulated_results.to_csv(
                os.path.join(self.output_dir, f'simulated_results_rate{int(rate*100)}.csv'), 
                index=False
            )
            comparison.to_csv(
                os.path.join(self.output_dir, f'comparison_rate{int(rate*100)}.csv'), 
                index=False
            )
        
        # 変換率間の比較グラフ
        self.plot_rate_comparison(results, rates)
        
        # 元の結果を保存
        original_results.to_csv(os.path.join(self.output_dir, 'original_results.csv'), index=False)
        
        print(f"複数のシミュレーション完了。結果は {self.output_dir} に保存されました。")
        
        return results
    
    def plot_rate_comparison(self, results, rates):
        """
        異なる変換率間の比較プロット
        
        Parameters:
        -----------
        results : dict
            変換率ごとの結果
        rates : list of float
            変換率のリスト
        """
        plt.figure(figsize=(15, 10))
        
        # 各候補者の予算配分変化を計算
        candidates = results[rates[0]]['budget_results']['title'].unique()
        
        # データフレームの準備
        plot_data = []
        for rate in rates:
            comparison = results[rate]['comparison']
            for _, row in comparison.iterrows():
                plot_data.append({
                    'rate': f"{int(rate*100)}%",
                    'title': row['title'],
                    'budget_change_percentage': row['budget_change_percentage']
                })
        
        plot_df = pd.DataFrame(plot_data)
        
        # プロット作成
        ax = sns.barplot(
            x='title',
            y='budget_change_percentage',
            hue='rate',
            data=plot_df,
            palette='viridis'
        )
        
        # ゼロラインを表示
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # プロット装飾
        plt.title('Budget Allocation Change Comparison Across Different Conversion Rates')
        plt.xlabel('Project')
        plt.ylabel('Change in Budget Allocation (%)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend(title='Conversion Rate')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'rate_comparison.png'), dpi=300)
        plt.close()
        
        print(f"変換率比較グラフを保存しました: {os.path.join(self.output_dir, 'rate_comparison.png')}")

def main():
    """メイン実行関数"""
    # 変換率
    rates = [0.1, 0.3, 0.5]
    
    # シミュレーター作成
    simulator = FixedRateSimulator(
        votes_file='data/votes.csv',
        candidates_file='data/candidates.csv',
        output_dir='results/bias_simulation/fixed_rate'
    )
    
    # 複数の変換率でシミュレーション実行
    simulator.run_simulations(rates)

if __name__ == "__main__":
    main() 