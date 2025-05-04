#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中立バイアスを除去した投票結果をシミュレーションするスクリプト
"""

import os
import pandas as pd
import numpy as np
import random

# Define file paths
ANALYSIS_OUTPUT_DIR = 'results/data'
SIMULATION_OUTPUT_DIR = 'results/data/simulation'
os.makedirs(SIMULATION_OUTPUT_DIR, exist_ok=True)

# Input files
VOTE_STATS_FILE = os.path.join(ANALYSIS_OUTPUT_DIR, 'vote_statistics.csv')
VOTER_STATS_FILE = os.path.join(ANALYSIS_OUTPUT_DIR, 'voter_statistics.csv')

# ディレクトリ設定
VOTES_FILE = 'data/votes.csv'
CANDIDATES_FILE = 'data/candidates.csv'

# シミュレーションパラメータ
# シナリオA: 全ての1票のうち、この割合を0票に変換
SCENARIO_A_PERCENTAGES = [0.1, 0.3, 0.5]

# シナリオB: 投票者の1票使用率に応じて、変換確率を変動させる
# 例: 'High 1s' パターンの投票者は高い確率で1票を0票に変換
SCENARIO_B_PROBABILITIES = {
    'Very Low 1s': 0.05,
    'Low 1s': 0.15,
    'Medium 1s': 0.30,
    'High 1s': 0.50,
    'Very High 1s': 0.70
}

# シナリオC: 統計的異常値検出（より高度な実装が必要なため、今回は簡略化）
# プロジェクトごとの1票比率が平均より著しく高い場合、その1票を変換
SCENARIO_C_THRESHOLD = 1.5 # 平均1票比率の1.5倍を超えるプロジェクトの1票を対象とする
SCENARIO_C_CONVERSION_RATE = 0.5 # 閾値を超えたプロジェクトの1票のうち、この割合を0票に変換

def load_csv_data():
    """CSVからデータを読み込む"""
    votes_df = pd.read_csv(VOTES_FILE)
    candidates_df = pd.read_csv(CANDIDATES_FILE)
    
    # ワイド形式からロング形式に変換
    # 各行が投票者、各列が候補者への投票値 → 各行が1つの投票を表すロング形式に変換
    votes_long_df = pd.melt(
        votes_df, 
        id_vars=['voter_id', 'vote_id'], 
        value_vars=[f'candidate_{i}' for i in range(7)],  # 候補者が7人
        var_name='candidate_column', 
        value_name='vote_value'
    )
    
    # candidate_column から candidate_id を抽出 (例: 'candidate_0' → 0)
    votes_long_df['candidate_id'] = votes_long_df['candidate_column'].str.extract(r'candidate_(\d+)').astype(int)
    
    # 不要な列を削除
    votes_long_df = votes_long_df.drop('candidate_column', axis=1)
    
    # 投票値が0の行を除外（実質的に投票していない）
    votes_long_df = votes_long_df[votes_long_df['vote_value'] > 0]
    
    # 候補者データのカラム名を確認し、必要に応じて変更
    candidates_df = candidates_df.rename(columns={
        'candidate_id': 'candidate_id',
        'title': 'name'  # title列をname列として扱う
    })
    
    return candidates_df, votes_long_df

def simulate_scenario_a(votes_df, percentage):
    """シナリオA: 一定割合の1票を0票に変換"""
    simulated_votes_df = votes_df.copy()
    
    # 1票のインデックスを取得
    one_vote_indices = simulated_votes_df[simulated_votes_df['vote_value'] == 1].index
    
    # 変換する1票の数
    num_to_convert = int(len(one_vote_indices) * percentage)
    
    # ランダムに変換するインデックスを選択
    indices_to_convert = random.sample(list(one_vote_indices), num_to_convert)
    
    # 選択された1票を0票に変換（実質的に削除）
    simulated_votes_df = simulated_votes_df.drop(indices_to_convert)
    
    return simulated_votes_df

def simulate_scenario_b(votes_df, voter_stats, probabilities):
    """シナリオB: 投票者のパターンに応じて1票を0票に変換"""
    simulated_votes_df = votes_df.copy()
    indices_to_drop = []
    
    for voter_id, stats in voter_stats.iterrows():
        voter_pattern = stats['vote_pattern']
        conversion_prob = probabilities.get(voter_pattern, 0) # パターンが見つからない場合は0
        
        # この投票者の1票を取得
        voter_one_votes = simulated_votes_df[
            (simulated_votes_df['voter_id'] == voter_id) & 
            (simulated_votes_df['vote_value'] == 1)
        ]
        
        for index, vote in voter_one_votes.iterrows():
            if random.random() < conversion_prob:
                indices_to_drop.append(index)
    
    # 選択された1票を削除
    simulated_votes_df = simulated_votes_df.drop(indices_to_drop)
    
    return simulated_votes_df

def simulate_scenario_c(votes_df, vote_stats, threshold, conversion_rate):
    """シナリオC: プロジェクトの1票比率に応じて1票を0票に変換"""
    simulated_votes_df = votes_df.copy()
    indices_to_drop = []
    
    # 平均1票比率を計算
    mean_one_vote_percentage = vote_stats['one_vote_percentage'].mean()
    
    # 1票比率が高いプロジェクトを特定
    high_bias_projects = vote_stats[vote_stats['one_vote_percentage'] > mean_one_vote_percentage * threshold]
    
    for _, project in high_bias_projects.iterrows():
        project_id = project['candidate_id']
        
        # このプロジェクトへの1票を取得
        project_one_votes = simulated_votes_df[
            (simulated_votes_df['candidate_id'] == project_id) &
            (simulated_votes_df['vote_value'] == 1)
        ]
        
        # 変換する1票の数
        num_to_convert = int(len(project_one_votes) * conversion_rate)
        
        # ランダムに変換するインデックスを選択（十分な票数があれば）
        if len(project_one_votes) > 0:
            # 最大でも利用可能な数だけ選択
            num_to_convert = min(num_to_convert, len(project_one_votes))
            indices_to_convert = random.sample(list(project_one_votes.index), num_to_convert)
            indices_to_drop.extend(indices_to_convert)
        
    # 重複を除去して削除
    simulated_votes_df = simulated_votes_df.drop(list(set(indices_to_drop)))
    
    return simulated_votes_df

def calculate_qv_results(votes_df):
    """QV方式の予算配分を計算"""
    # 各投票のコスト（= vote_value）とsqrt(cost)
    votes_df['cost'] = votes_df['vote_value']
    votes_df['sqrt_cost'] = np.sqrt(votes_df['cost'])
    
    # プロジェクトごとのsqrt(cost)の合計
    project_scores = votes_df.groupby('candidate_id')['sqrt_cost'].sum()
    
    # 全体のsqrt(cost)の合計
    total_score = project_scores.sum()
    
    # 予算配分計算 (仮の総予算を1とする)
    budget_allocation = (project_scores / total_score) if total_score > 0 else pd.Series(0, index=project_scores.index)
    
    # DataFrameにまとめる
    qv_results = pd.DataFrame({
        'total_sqrt_cost': project_scores,
        'budget_allocation_ratio': budget_allocation
    })
    
    return qv_results

def save_simulation_results(df, scenario_name, output_dir):
    """シミュレーション結果を保存"""
    filename = f"simulation_{scenario_name}_votes.csv"
    df.to_csv(os.path.join(output_dir, filename), index=False)
    print(f"Saved: {filename}")

def main():
    # データ読み込み
    candidates_df, votes_df = load_csv_data()
    
    # 既存の分析結果を読み込み
    try:
        vote_stats = pd.read_csv(VOTE_STATS_FILE)
        voter_stats = pd.read_csv(VOTER_STATS_FILE, index_col='voter_id')
    except FileNotFoundError:
        print(f"Error: 分析結果ファイルが見つかりません。先に analyze_vote_distribution.py を実行してください。")
        return

    # 元の投票結果
    original_qv_results = calculate_qv_results(votes_df)
    original_qv_results = original_qv_results.merge(
        candidates_df[['candidate_id', 'name']],  # 候補者IDと名前の列を使用
        left_index=True,
        right_on='candidate_id'
    ).set_index('name')
    original_qv_results.to_csv(os.path.join(SIMULATION_OUTPUT_DIR, 'original_qv_results.csv'))
    print("Saved: original_qv_results.csv")
    
    # シナリオAのシミュレーション実行と保存
    print("\n--- シナリオA --- (一定割合の1票を0票に変換)")
    for percentage in SCENARIO_A_PERCENTAGES:
        scenario_name = f"A_pct{int(percentage*100)}"
        print(f"Running {scenario_name}...")
        simulated_df_a = simulate_scenario_a(votes_df, percentage)
        save_simulation_results(simulated_df_a, scenario_name, SIMULATION_OUTPUT_DIR)
        # 配分計算も行う場合
        qv_results_a = calculate_qv_results(simulated_df_a)
        qv_results_a = qv_results_a.merge(
            candidates_df[['candidate_id', 'name']],  # 候補者IDと名前の列を使用
            left_index=True,
            right_on='candidate_id'
        ).set_index('name')
        qv_results_a.to_csv(os.path.join(SIMULATION_OUTPUT_DIR, f"qv_results_{scenario_name}.csv"))
        print(f"Saved: qv_results_{scenario_name}.csv")

    # シナリオBのシミュレーション実行と保存
    print("\n--- シナリオB --- (投票者パターンに応じて1票を0票に変換)")
    scenario_name_b = "B_voter_pattern"
    print(f"Running {scenario_name_b}...")
    simulated_df_b = simulate_scenario_b(votes_df, voter_stats, SCENARIO_B_PROBABILITIES)
    save_simulation_results(simulated_df_b, scenario_name_b, SIMULATION_OUTPUT_DIR)
    qv_results_b = calculate_qv_results(simulated_df_b)
    qv_results_b = qv_results_b.merge(
        candidates_df[['candidate_id', 'name']],  # 候補者IDと名前の列を使用
        left_index=True,
        right_on='candidate_id'
    ).set_index('name')
    qv_results_b.to_csv(os.path.join(SIMULATION_OUTPUT_DIR, f"qv_results_{scenario_name_b}.csv"))
    print(f"Saved: qv_results_{scenario_name_b}.csv")
    
    # シナリオCのシミュレーション実行と保存
    print("\n--- シナリオC --- (1票比率が高いプロジェクトの1票を変換)")
    scenario_name_c = f"C_threshold{SCENARIO_C_THRESHOLD}_rate{int(SCENARIO_C_CONVERSION_RATE*100)}"
    print(f"Running {scenario_name_c}...")
    simulated_df_c = simulate_scenario_c(
        votes_df, vote_stats, SCENARIO_C_THRESHOLD, SCENARIO_C_CONVERSION_RATE
    )
    save_simulation_results(simulated_df_c, scenario_name_c, SIMULATION_OUTPUT_DIR)
    qv_results_c = calculate_qv_results(simulated_df_c)
    qv_results_c = qv_results_c.merge(
        candidates_df[['candidate_id', 'name']],  # 候補者IDと名前の列を使用
        left_index=True,
        right_on='candidate_id'
    ).set_index('name')
    qv_results_c.to_csv(os.path.join(SIMULATION_OUTPUT_DIR, f"qv_results_{scenario_name_c}.csv"))
    print(f"Saved: qv_results_{scenario_name_c}.csv")

    print("\nシミュレーション完了！ 結果は simulation_results ディレクトリに保存されました。")

if __name__ == "__main__":
    main() 