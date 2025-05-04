#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中立バイアス（1票の過剰使用）のシミュレーション基本クラス
"""

import os
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns

class BiasSimulatorBase:
    """中立バイアスシミュレーションの基本クラス"""
    
    def __init__(self, votes_file='data/votes.csv', candidates_file='data/candidates.csv', 
                 output_dir='results/bias_simulation'):
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
        self.votes_long_df = self.convert_to_long_format(self.votes_df)
        
        print(f"データ読み込み完了: {len(self.votes_long_df)}行の投票データ")
    
    @staticmethod
    def convert_to_long_format(votes_df):
        """
        投票データを長形式に変換
        
        Parameters:
        -----------
        votes_df : pandas.DataFrame
            投票データ（横形式）
            
        Returns:
        --------
        pandas.DataFrame
            投票データ（長形式）
        """
        vote_rows = []
        
        for _, row in votes_df.iterrows():
            voter_id = row['voter_id']
            
            # 各候補者への投票を抽出
            for i in range(10):  # 最大10人の候補者を想定
                col_name = f'candidate_{i}'
                if col_name in row and not pd.isna(row[col_name]):
                    vote_rows.append({
                        'voter_id': voter_id,
                        'candidate_id': i,
                        'vote_value': int(row[col_name])
                    })
        
        # 新しいデータフレームを作成
        return pd.DataFrame(vote_rows)
    
    @staticmethod
    def convert_to_wide_format(votes_long_df):
        """
        長形式の投票データを横形式に変換
        
        Parameters:
        -----------
        votes_long_df : pandas.DataFrame
            投票データ（長形式）
            
        Returns:
        --------
        pandas.DataFrame
            投票データ（横形式）
        """
        unique_voters = votes_long_df['voter_id'].unique()
        vote_data = {
            'voter_id': unique_voters
        }
        
        # 各候補者への投票を追加
        for voter_id in unique_voters:
            voter_votes = votes_long_df[votes_long_df['voter_id'] == voter_id]
            for _, vote in voter_votes.iterrows():
                candidate_id = vote['candidate_id']
                col_name = f'candidate_{candidate_id}'
                vote_data.setdefault(col_name, [])
                
                if len(vote_data[col_name]) < len(unique_voters):
                    vote_data[col_name].extend([None] * (len(unique_voters) - len(vote_data[col_name])))
                
                voter_index = list(unique_voters).index(voter_id)
                vote_data[col_name][voter_index] = vote['vote_value']
        
        # データフレームに変換
        return pd.DataFrame(vote_data)
    
    def calculate_qv_results(self, votes_long_df=None):
        """
        QV方式の予算配分を計算
        
        Parameters:
        -----------
        votes_long_df : pandas.DataFrame, optional
            投票データ（長形式）。指定しない場合は元のデータを使用
            
        Returns:
        --------
        pandas.DataFrame
            QV方式の予算配分結果
        """
        if votes_long_df is None:
            votes_long_df = self.votes_long_df
        
        # 各投票のコスト（= vote_value）とsqrt(cost)
        votes_long_df = votes_long_df.copy()
        votes_long_df['cost'] = votes_long_df['vote_value']
        votes_long_df['sqrt_cost'] = np.sqrt(votes_long_df['cost'])
        
        # プロジェクトごとのsqrt(cost)の合計
        project_scores = votes_long_df.groupby('candidate_id')['sqrt_cost'].sum()
        
        # 全体のsqrt(cost)の合計
        total_score = project_scores.sum()
        
        # 予算配分計算 (総予算を1とする)
        budget_allocation = (project_scores / total_score) if total_score > 0 else pd.Series(0, index=project_scores.index)
        
        # DataFrameにまとめる
        qv_results = pd.DataFrame({
            'candidate_id': project_scores.index,
            'total_sqrt_cost': project_scores.values,
            'budget_allocation_ratio': budget_allocation.values
        })
        
        # 候補者名を追加
        qv_results = qv_results.merge(self.candidates_df[['id', 'title']], left_on='candidate_id', right_on='id')
        
        return qv_results
    
    def simulate(self):
        """
        シミュレーション実行（子クラスでオーバーライド）
        
        Returns:
        --------
        pandas.DataFrame
            シミュレーション結果の投票データ（長形式）
        """
        raise NotImplementedError("子クラスで実装する必要があります")
    
    def compare_results(self, original_results, simulated_results):
        """
        元の結果とシミュレーション結果を比較
        
        Parameters:
        -----------
        original_results : pandas.DataFrame
            元の予算配分結果
        simulated_results : pandas.DataFrame
            シミュレーション後の予算配分結果
            
        Returns:
        --------
        pandas.DataFrame
            比較結果
        """
        # 候補者IDで結合
        comparison = original_results.merge(
            simulated_results,
            on=['candidate_id', 'id', 'title'],
            suffixes=('_original', '_simulated')
        )
        
        # 変化量を計算
        comparison['budget_change'] = comparison['budget_allocation_ratio_simulated'] - comparison['budget_allocation_ratio_original']
        comparison['budget_change_percentage'] = (comparison['budget_change'] / comparison['budget_allocation_ratio_original']) * 100
        
        return comparison
    
    def plot_comparison(self, comparison, output_file=None):
        """
        予算配分の比較結果をプロット
        
        Parameters:
        -----------
        comparison : pandas.DataFrame
            比較結果
        output_file : str, optional
            出力ファイルパス。指定しない場合はself.output_dirに保存
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, 'budget_comparison.png')
        
        plt.figure(figsize=(14, 8))
        
        # 候補者名の短縮
        comparison['short_title'] = comparison['title'].str.slice(0, 20)
        
        # データを変化量の絶対値でソート
        sorted_data = comparison.sort_values(by='budget_change_percentage', ascending=False)
        
        # バープロット作成
        ax = sns.barplot(
            x='short_title',
            y='budget_change_percentage',
            data=sorted_data,
            palette='coolwarm'
        )
        
        # ゼロラインを表示
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # プロット装飾
        plt.title('Budget Allocation Change After Bias Correction')
        plt.xlabel('Project')
        plt.ylabel('Change in Budget Allocation (%)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 値のラベルを追加
        for i, v in enumerate(sorted_data['budget_change_percentage']):
            ax.text(i, v + (1 if v >= 0 else -1), f"{v:.1f}%", ha='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        print(f"比較グラフを保存しました: {output_file}")
    
    def run_simulation(self):
        """
        シミュレーションの実行と結果比較
        """
        print("シミュレーションを実行しています...")
        
        # 元の予算配分を計算
        original_results = self.calculate_qv_results()
        
        # シミュレーション実行
        simulated_votes = self.simulate()
        
        # シミュレーション後の予算配分を計算
        simulated_results = self.calculate_qv_results(simulated_votes)
        
        # 結果比較
        comparison = self.compare_results(original_results, simulated_results)
        
        # 比較結果をプロット
        self.plot_comparison(comparison)
        
        # 結果をCSVに保存
        original_results.to_csv(os.path.join(self.output_dir, 'original_results.csv'), index=False)
        simulated_results.to_csv(os.path.join(self.output_dir, 'simulated_results.csv'), index=False)
        comparison.to_csv(os.path.join(self.output_dir, 'comparison_results.csv'), index=False)
        
        print(f"シミュレーション完了。結果は {self.output_dir} に保存されました。")
        
        return comparison 