#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simulation and comparison analysis of the utility maximization hypothesis model with actual voting distribution
"""

import os
import gc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import matplotlib.ticker as mtick
import time

# Font settings to avoid font errors
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# Directory setup
INPUT_DIR = 'data/'
OUTPUT_DIR = 'results/figures/neutral_bias'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Add dictionary for Japanese to English translation
def get_translation_dict():
    """Create a dictionary for Japanese to English translation"""
    return {
        "効用最大化モデルと実際の投票値分布の比較": "Comparison of Utility Maximization Model and Actual Vote Distribution",
        "投票値": "Vote Value",
        "割合 (%)": "Percentage (%)",
        "実際の分布": "Actual Distribution",
        "効用最大化モデル": "Utility Maximization Model",
        "効用最大化モデルからの偏差": "Deviation from Utility Maximization Model",
        "偏差 (%)": "Deviation (%)",
        "投票値": "Vote Value",
        "異なる選好強度分布での効用最大化モデル": "Utility Maximization Model with Different Preference Distributions",
        "一様分布": "Uniform Distribution",
        "正規分布": "Normal Distribution",
        "べき乗分布": "Power-law Distribution",
        "実データ": "Actual Data",
        "投票値別の理論値と実測値の比較": "Comparison of Theoretical and Actual Values by Vote Value",
        "効用最大化モデル（理論値）": "Utility Maximization Model (Theoretical)",
        "実際の投票分布（実測値）": "Actual Vote Distribution",
        "投票者クラスター別の理論分布との乖離": "Deviation from Theoretical Distribution by Voter Cluster",
        "クラスター": "Cluster",
        "平均偏差 (%)": "Average Deviation (%)",
        "効用最大化シミュレーション結果": "Utility Maximization Simulation Results",
        
        # Report translations
        "効用最大化仮説検証レポート": "Utility Maximization Hypothesis Verification Report",
        "シミュレーション設定": "Simulation Settings",
        "シミュレーション回数": "Number of Simulations",
        "プロジェクト数": "Number of Projects",
        "最大クレジット": "Maximum Credits",
        "選好強度分布": "Preference Intensity Distribution",
        "基本統計比較": "Basic Statistical Comparison",
        "指標": "Metric",
        "理論値": "Theoretical Value",
        "実測値": "Actual Value",
        "差異": "Difference",
        "1票の割合": "1-Vote Percentage",
        "2票の割合": "2-Vote Percentage",
        "3-5票の割合": "3-5 Vote Percentage",
        "6-9票の割合": "6-9 Vote Percentage",
        "中央値": "Median",
        "最頻値": "Mode",
        "エントロピー": "Entropy",
        "統計的検定結果": "Statistical Test Results",
        "カイ二乗値": "Chi-Square Value",
        "自由度": "Degrees of Freedom",
        "p値": "p-Value",
        "結論": "Conclusion",
        "効用最大化仮説の検証結果": "Utility Maximization Hypothesis Verification Results",
        "選好強度分布の修正モデル": "Modified Preference Intensity Distribution Model",
        "分布名": "Distribution Name",
        "パラメータ": "Parameters",
        "AIC": "AIC",
        "BIC": "BIC",
        "適合度": "Goodness of Fit",
        "まとめと解釈": "Summary and Interpretation"
    }

def translate_text(text, translation_dict=None):
    """Translate text using the translation dictionary"""
    if translation_dict is None:
        translation_dict = get_translation_dict()
    
    return translation_dict.get(text, text)  # Return original if no translation

def translate_project_name(name):
    """Translate project names to English"""
    project_translations = {
        "ちばユースセンターPRISM": "Chiba Youth Center PRISM",
        "JINEN TRAVEL": "JINEN TRAVEL",  # Keep as is if already in English
        "ユースマンスプロジェクト": "Youth Month Project",
        "若者の参加を広げる会議": "Conference for Expanding Youth Participation",
        "学生と行政の協働プロジェクト": "Student-Administration Collaboration Project",
        "市民メディアラボ": "Citizen Media Lab",
        "青少年育成交流事業": "Youth Development Exchange Program"
    }
    
    return project_translations.get(name, name)  # Return original if no translation

def load_data():
    """Load voting data and project data"""
    votes_df = pd.read_csv(INPUT_DIR + 'votes.csv')
    candidates_df = pd.read_csv(INPUT_DIR + 'candidates.csv')
    
    # Translate project names if needed
    if 'title' in candidates_df.columns and 'title_en' in candidates_df.columns:
        candidates_df['title'] = candidates_df['title_en']
    elif 'title' in candidates_df.columns:
        candidates_df['title'] = candidates_df['title'].apply(translate_project_name)
    
    return votes_df, candidates_df

def get_vote_distribution(votes_df):
    """Get the actual distribution of vote values"""
    # Extract vote values
    vote_values = []
    for col in votes_df.columns:
        if col.startswith('candidate_'):
            votes = votes_df[col].dropna().values
            # Filter out negative values
            votes = [v for v in votes if v >= 0]
            vote_values.extend(votes)
    
    # Calculate vote distribution
    vote_counts = pd.Series(vote_values).value_counts().sort_index()
    vote_percentages = vote_counts / vote_counts.sum() * 100
    
    return vote_counts, vote_percentages

def get_filtered_vote_distribution(votes_df, min_value=1):
    """
    Get the distribution of vote values, filtering out votes below min_value
    
    Parameters:
    -----------
    votes_df : pd.DataFrame
        Dataframe containing voting data
    min_value : int
        Minimum vote value to include (default: 1)
        
    Returns:
    --------
    vote_counts : pd.Series
        Count of votes for each vote value (filtered)
    vote_percentages : pd.Series
        Percentage of votes for each vote value (filtered)
    """
    # Extract voting values
    vote_values = []
    for col in votes_df.columns:
        if col.startswith('candidate_'):
            votes = votes_df[col].dropna().values
            # Filter values
            filtered_votes = [v for v in votes if v >= min_value]
            vote_values.extend(filtered_votes)
    
    # Calculate distribution
    if not vote_values:  # Check for empty list
        return pd.Series(), pd.Series()
    
    vote_counts = pd.Series(vote_values).value_counts().sort_index()
    vote_percentages = vote_counts / vote_counts.sum() * 100
    
    return vote_counts, vote_percentages

def simulate_optimal_votes(n_simulations=1000, n_projects=7, max_credits=99, 
                          preference_distribution='uniform', params=None):
    """
    Simulate optimal votes based on the utility maximization hypothesis
    
    Parameters:
    -----------
    n_simulations : int
        Number of simulations to run
    n_projects : int
        Number of projects to vote for
    max_credits : int
        Maximum credits available per voter
    preference_distribution : str
        Type of preference distribution ('uniform', 'normal', 'power_law')
    params : dict
        Parameters for the preference distribution
        
    Returns:
    --------
    vote_counts : pd.Series
        Count of votes for each vote value
    vote_percentages : pd.Series
        Percentage of votes for each vote value
    """
    simulated_votes = []
    
    # Default parameters
    if params is None:
        params = {}
    
    for _ in range(n_simulations):
        # Generate random preference intensities based on the specified distribution
        if preference_distribution == 'uniform':
            # Uniform distribution between min and max
            min_val = params.get('min', 0)
            max_val = params.get('max', 10)
            preferences = np.random.uniform(min_val, max_val, n_projects)
        
        elif preference_distribution == 'normal':
            # Normal distribution with mean and std
            mean = params.get('mean', 5)
            std = params.get('std', 2)
            preferences = np.random.normal(mean, std, n_projects)
            preferences = np.clip(preferences, 0, None)  # No negative preferences
        
        elif preference_distribution == 'power_law':
            # Power law distribution (simplification)
            alpha = params.get('alpha', 1.5)
            preferences = np.random.pareto(alpha, n_projects) + 1  # +1 to avoid zero
            preferences = np.clip(preferences, 0, 10)  # Cap at 10 for consistency
        
        else:
            raise ValueError(f"Unknown preference distribution: {preference_distribution}")
        
        # Optimal voting calculation
        # v_i = u_i / sqrt(sum(u_i^2) / C)
        denominator = np.sqrt(np.sum(preferences**2) / max_credits)
        if denominator == 0:  # Avoid division by zero
            optimal_votes = np.zeros(n_projects)
        else:
            optimal_votes = preferences / denominator
        
        # Discretize votes (round to 1-9)
        discretized_votes = np.clip(np.round(optimal_votes), 0, 9)
        
        # Only include positive votes
        positive_votes = discretized_votes[discretized_votes > 0]
        
        simulated_votes.extend(positive_votes)
    
    # Count votes by value
    vote_counts = pd.Series(simulated_votes).value_counts().sort_index()
    vote_percentages = vote_counts / vote_counts.sum() * 100
    
    return vote_counts, vote_percentages

def simulate_optimal_votes_with_zero(n_simulations=1000, n_projects=7, max_credits=99, 
                                    preference_distribution='uniform', params=None, 
                                    indifference_threshold=0.5, decision_cost=0.2):
    """
    Simulate optimal votes with the possibility of 0 votes when preference is below threshold
    """
    simulated_votes = []
    
    # Default parameters
    if params is None:
        params = {}
    
    print(f"  Debug: Starting simulation (threshold={indifference_threshold}, cost={decision_cost})")
    
    for sim in range(n_simulations // n_projects):
        # Generate random preference intensities
        if preference_distribution == 'uniform':
            preferences = np.random.uniform(0, 10, n_projects)
        elif preference_distribution == 'normal':
            mu = params.get('mu', 5)
            sigma = params.get('sigma', 2)
            preferences = np.random.normal(mu, sigma, n_projects)
            preferences = np.clip(preferences, 0, 10)  # Clip to valid range
        elif preference_distribution == 'power_law':
            alpha = params.get('alpha', 2)
            # Generate power-law distributed values
            preferences = np.random.pareto(alpha, n_projects) * 3
            preferences = np.clip(preferences, 0, 10)  # Clip to valid range
        else:
            raise ValueError(f"Unknown distribution: {preference_distribution}")
        
        # Apply indifference threshold and decision cost
        adjusted_preferences = np.copy(preferences)
        for i in range(n_projects):
            if preferences[i] < indifference_threshold:
                adjusted_preferences[i] = 0
            else:
                adjusted_preferences[i] -= decision_cost
                if adjusted_preferences[i] < 0:
                    adjusted_preferences[i] = 0
        
        # Calculate optimal vote allocation
        credits_used = 0
        final_votes = np.zeros(n_projects)
        
        # Sort indices by adjusted preference in descending order
        sorted_indices = np.argsort(-adjusted_preferences)
        
        for idx in sorted_indices:
            if adjusted_preferences[idx] <= 0:
                continue
                
            # Calculate votes based on square root formula
            optimal_votes = np.sqrt(adjusted_preferences[idx])
            
            # Round to nearest integer
            votes = np.round(optimal_votes)
            
            # Check if we have enough credits left
            cost = votes ** 2
            if credits_used + cost > max_credits:
                # If not enough credits, allocate maximum possible
                max_possible = int(np.sqrt(max_credits - credits_used))
                votes = max_possible
                cost = votes ** 2
            
            # Update votes and credits
            final_votes[idx] = votes
            credits_used += cost
            
            # If no more credits, break
            if credits_used >= max_credits:
                break
        
        # Print simulation details
        print(f"    Simulation {sim+1}: Preference values = {preferences.round(2)}")
        print(f"    Simulation {sim+1}: Adjusted preferences = {adjusted_preferences.round(2)}")
        print(f"    Simulation {sim+1}: Final votes = {final_votes.astype(int)}")
        
        # Add to simulated votes
        for i in range(n_projects):
            simulated_votes.append(final_votes[i])
    
    # Calculate distribution
    vote_counts = pd.Series(simulated_votes).value_counts().sort_index()
    vote_percentages = vote_counts / vote_counts.sum() * 100
    
    print(f"  Debug: Total votes generated: {len(simulated_votes)}")
    print(f"  Debug: Vote value types: {sorted(vote_counts.index.tolist())}")
    print(f"  Debug: 0-vote percentage: {vote_percentages.get(0, 0):.2f}%")
    
    return vote_counts, vote_percentages

def compare_distributions(actual_percentages, simulated_percentages):
    """Compare actual and simulated distributions"""
    # Align indices
    all_indices = sorted(set(actual_percentages.index) | set(simulated_percentages.index))
    
    # Create a DataFrame for comparison
    comparison_df = pd.DataFrame(index=all_indices)
    comparison_df['actual'] = actual_percentages.reindex(all_indices, fill_value=0)
    comparison_df['simulated'] = simulated_percentages.reindex(all_indices, fill_value=0)
    comparison_df['deviation'] = comparison_df['actual'] - comparison_df['simulated']
    comparison_df['deviation_pct'] = comparison_df['deviation'] / comparison_df['simulated'] * 100
    
    return comparison_df

def chi_square_test(actual_counts, simulated_counts):
    """Perform chi-square test to compare distributions"""
    # Align indices
    all_indices = sorted(set(actual_counts.index) | set(simulated_counts.index))
    
    # データ型をfloatに変換（整数でない可能性があるため）
    actual_array = np.array([float(actual_counts.get(i, 0)) for i in all_indices])
    expected_array = np.array([float(simulated_counts.get(i, 0)) for i in all_indices])
    
    # 要素が0またはNaNのインデックスを特定
    valid_indices = (expected_array > 0) & (np.isfinite(expected_array)) & (np.isfinite(actual_array))
    
    if not np.any(valid_indices):
        print("  警告: 有効な比較要素がありません")
        return float('inf'), 0.0, 0
    
    # 有効な要素のみを抽出
    actual_valid = actual_array[valid_indices]
    expected_valid = expected_array[valid_indices]
    
    # 合計を一致させるようにスケーリング
    expected_valid_scaled = expected_valid * (actual_valid.sum() / expected_valid.sum())
    
    # カイ二乗統計量を手動で計算（より制御可能）
    chi2_stat = np.sum((actual_valid - expected_valid_scaled) ** 2 / expected_valid_scaled)
    
    # 自由度
    df = sum(valid_indices) - 1
    
    # p値の計算
    p_value = 1.0
    try:
        p_value = stats.chi2.sf(chi2_stat, df)
    except:
        p_value = 0.0
    
    return chi2_stat, p_value, df

def plot_distribution_comparison(comparison_df, output_file):
    """Plot comparison of actual and simulated distributions"""
    trans_dict = get_translation_dict()
    
    # 負の票（インデックス < 0）を除外
    filtered_df = comparison_df[comparison_df.index >= 0].copy()
    
    plt.figure(figsize=(12, 8))
    
    # Bar plot of percentages
    ax1 = plt.subplot(2, 1, 1)
    bar_width = 0.35
    x = np.arange(len(filtered_df.index))
    
    ax1.bar(x - bar_width/2, filtered_df['actual'], bar_width, 
            label=translate_text('実際の分布', trans_dict), color='#1f77b4', alpha=0.8)
    ax1.bar(x + bar_width/2, filtered_df['simulated'], bar_width, 
            label=translate_text('効用最大化モデル', trans_dict), color='#ff7f0e', alpha=0.8)
    
    ax1.set_xlabel(translate_text('投票値', trans_dict))
    ax1.set_ylabel(translate_text('割合 (%)', trans_dict))
    ax1.set_title(translate_text('効用最大化モデルと実際の投票値分布の比較', trans_dict))
    ax1.set_xticks(x)
    ax1.set_xticklabels(filtered_df.index)
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Bar plot of deviations
    ax2 = plt.subplot(2, 1, 2)
    ax2.bar(x, filtered_df['deviation'], color='#2ca02c', alpha=0.8)
    ax2.axhline(y=0, color='r', linestyle='-')
    
    ax2.set_xlabel(translate_text('投票値', trans_dict))
    ax2.set_ylabel(translate_text('偏差 (%)', trans_dict))
    ax2.set_title(translate_text('効用最大化モデルからの偏差', trans_dict))
    ax2.set_xticks(x)
    ax2.set_xticklabels(filtered_df.index)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def plot_multiple_distributions(actual_percentages, distributions_dict, output_file):
    """Plot comparison of actual data with multiple theoretical distributions"""
    trans_dict = get_translation_dict()
    
    plt.figure(figsize=(12, 8))
    
    # Get all possible vote values
    all_indices = set(actual_percentages.index)
    for dist_data in distributions_dict.values():
        all_indices.update(dist_data.index)
    # 負の投票値を除外
    all_indices = sorted([idx for idx in all_indices if idx >= 0])
    
    # Create x-axis positions
    x = np.arange(len(all_indices))
    
    # Plot actual data
    plt.plot(x, [actual_percentages.get(i, 0) for i in all_indices], 'o-', 
             label=translate_text('実データ', trans_dict), linewidth=2, color='black')
    
    # Plot each distribution
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for i, (name, dist_data) in enumerate(distributions_dict.items()):
        plt.plot(x, [dist_data.get(i, 0) for i in all_indices], 'o-', 
                 label=translate_text(name, trans_dict), linewidth=2, color=colors[i % len(colors)])
    
    plt.xlabel(translate_text('投票値', trans_dict))
    plt.ylabel(translate_text('割合 (%)', trans_dict))
    plt.title(translate_text('異なる選好強度分布での効用最大化モデル', trans_dict))
    plt.xticks(x, all_indices)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def generate_report(votes_df, actual_counts, actual_percentages, 
                   simulated_counts, simulated_percentages, comparison_df,
                   chi2_stat, p_value, df, output_file):
    """Generate a report of the analysis"""
    trans_dict = get_translation_dict()
    
    # Calculate additional statistics
    actual_grouped = {
        '1': actual_percentages.get(1, 0),
        '2': actual_percentages.get(2, 0),
        '3-5': sum(actual_percentages.get(i, 0) for i in range(3, 6)),
        '6-9': sum(actual_percentages.get(i, 0) for i in range(6, 10))
    }
    
    simulated_grouped = {
        '1': simulated_percentages.get(1, 0),
        '2': simulated_percentages.get(2, 0),
        '3-5': sum(simulated_percentages.get(i, 0) for i in range(3, 6)),
        '6-9': sum(simulated_percentages.get(i, 0) for i in range(6, 10))
    }
    
    # Calculate entropies
    actual_values = [v for v in actual_percentages.values]
    actual_entropy = stats.entropy(actual_values / sum(actual_values))
    
    simulated_values = [v for v in simulated_percentages.values]
    simulated_entropy = stats.entropy(simulated_values / sum(simulated_values))
    
    # Generate report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {translate_text('効用最大化仮説検証レポート', trans_dict)}\n\n")
        
        f.write(f"## {translate_text('シミュレーション設定', trans_dict)}\n\n")
        f.write(f"- {translate_text('シミュレーション回数', trans_dict)}: 1000\n")
        f.write(f"- {translate_text('プロジェクト数', trans_dict)}: 7\n")
        f.write(f"- {translate_text('最大クレジット', trans_dict)}: 99\n")
        f.write(f"- {translate_text('選好強度分布', trans_dict)}: {translate_text('一様分布', trans_dict)} [0, 10]\n\n")
        
        f.write(f"## {translate_text('基本統計比較', trans_dict)}\n\n")
        f.write("| {} | {} | {} | {} |\n".format(
            translate_text('指標', trans_dict),
            translate_text('理論値', trans_dict),
            translate_text('実測値', trans_dict),
            translate_text('差異', trans_dict)
        ))
        f.write("|---|---|---|---|\n")
        
        # Vote percentages by group
        for group, name in [('1', '1票の割合'), ('2', '2票の割合'), 
                           ('3-5', '3-5票の割合'), ('6-9', '6-9票の割合')]:
            f.write("| {} | {:.2f}% | {:.2f}% | {:.2f}% |\n".format(
                translate_text(name, trans_dict),
                simulated_grouped[group],
                actual_grouped[group],
                actual_grouped[group] - simulated_grouped[group]
            ))
        
        # Entropy
        f.write("| {} | {:.4f} | {:.4f} | {:.4f} |\n".format(
            translate_text('エントロピー', trans_dict),
            simulated_entropy,
            actual_entropy,
            actual_entropy - simulated_entropy
        ))
        
        f.write("\n## {}\n\n".format(translate_text('統計的検定結果', trans_dict)))
        f.write("- {}: {:.4f}\n".format(translate_text('カイ二乗値', trans_dict), chi2_stat))
        f.write("- {}: {}\n".format(translate_text('自由度', trans_dict), df))
        f.write("- {}: {:.8f}\n".format(translate_text('p値', trans_dict), p_value))
        
        if p_value < 0.05:
            f.write("\n{}: ".format(translate_text('結論', trans_dict)))
            f.write("{} (p < 0.05)\n".format(
                "実際の投票分布は効用最大化モデルの理論分布と有意に異なります"
            ))
        else:
            f.write("\n{}: ".format(translate_text('結論', trans_dict)))
            f.write("{} (p >= 0.05)\n".format(
                "実際の投票分布は効用最大化モデルの理論分布と統計的に一致します"
            ))
        
        f.write("\n## {}\n\n".format(translate_text('まとめと解釈', trans_dict)))
        
        # Write detailed interpretation based on results
        if actual_grouped['1'] < simulated_grouped['1']:
            f.write("- 実際の投票では、理論モデルが予測するよりも**1票の使用が{:.2f}%少ない**です。\n".format(
                simulated_grouped['1'] - actual_grouped['1']
            ))
            f.write("  - これは投票者が単純なコスト最適化行動をとっていないことを示唆しています。\n")
        else:
            f.write("- 実際の投票では、理論モデルが予測するよりも**1票の使用が{:.2f}%多い**です。\n".format(
                actual_grouped['1'] - simulated_grouped['1']
            ))
            f.write("  - これは「関心の低いプロジェクトにも形式的に投票する」という中立バイアス仮説を支持する可能性があります。\n")
        
        if actual_grouped['3-5'] > simulated_grouped['3-5']:
            f.write("- 中間票（3-5票）の使用が理論値より{:.2f}%多く、投票者は選好の差別化を重視している可能性があります。\n".format(
                actual_grouped['3-5'] - simulated_grouped['3-5']
            ))
        
        # Overall conclusion
        f.write("\n### {}\n\n".format(translate_text('効用最大化仮説の検証結果', trans_dict)))
        
        if p_value < 0.05 and actual_grouped['1'] < simulated_grouped['1']:
            f.write("効用最大化仮説は部分的に支持されますが、投票者は**単純なコスト最適化よりも選好表現を優先**している可能性が高いです。\n")
            f.write("特に「選好強度の小さいプロジェクトには小票（1票）を投じる」という理論予測とは異なり、\n")
            f.write("実際には投票者は中票（3-5票）を多用し、プロジェクト間の選好差を明確に表現しています。\n")
        elif p_value < 0.05 and actual_grouped['1'] > simulated_grouped['1']:
            f.write("効用最大化仮説よりも**中立バイアス仮説**がより説明力を持つ可能性があります。\n")
            f.write("投票者は理論的に予測されるよりも多くの1票を投じており、「関心の低いプロジェクトにも形式的に投票する」\n")
            f.write("という行動パターンが観察されています。\n")
        else:
            f.write("効用最大化仮説は統計的に支持され、投票者は自身の選好強度に比例した投票行動をとっていると考えられます。\n")
        
        f.write("\n今後の研究としては、より複雑な選好強度分布モデルを検討し、実際の投票行動をより正確に説明できる\n")
        f.write("理論モデルの構築が期待されます。\n")

def main():
    """Main function to execute the analysis"""
    print("Starting utility maximization hypothesis simulation analysis...")
    
    # Load data
    votes_df, candidates_df = load_data()
    print(f"Data loading complete: {len(votes_df)} voting records, {len(candidates_df)} projects")
    
    # Get actual vote distribution
    actual_counts, actual_percentages = get_vote_distribution(votes_df)
    
    # Print actual distribution
    print("Actual vote value distribution:")
    for i in range(10):
        if i in actual_percentages.index:
            pct = actual_percentages[i]
            print(f"  {i} votes: {pct:.2f}%")
    
    print("\nApproach 1: Analysis excluding 0 votes from actual data")
    # Filter out 0 votes for comparison with traditional model
    filtered_counts, filtered_percentages = get_filtered_vote_distribution(votes_df, min_value=1)
    
    # Print filtered distribution
    print("Actual vote value distribution (excluding 0 votes):")
    for i in range(1, 10):
        if i in filtered_percentages.index:
            pct = filtered_percentages[i]
            print(f"  {i} votes: {pct:.2f}%")
    
    # Simulate using traditional utility maximization model (no zero votes)
    print("\nTraditional utility maximization model simulation:")
    traditional_sim_counts, traditional_sim_percentages = simulate_optimal_votes(
        n_simulations=1000,  # 1000 simulations for efficiency
        n_projects=7,
        max_credits=99,
        preference_distribution='uniform'
    )
    
    # Print simulated distribution
    print("Traditional utility maximization model theoretical distribution:")
    for i in sorted(traditional_sim_percentages.index):
        pct = traditional_sim_percentages[i]
        print(f"  {i:.1f} votes: {pct:.2f}%")
    
    # Compare distributions
    traditional_comparison = compare_distributions(actual_percentages, traditional_sim_percentages)
    print("\nTraditional model vs. all data comparison:")
    print(traditional_comparison)
    
    # Perform chi-square test
    chi2_stat, p_value, df = chi_square_test(actual_counts, traditional_sim_counts)
    print(f"Chi-square test for traditional model vs. all data: x^2={chi2_stat:.4f}, df={df}, p={p_value:.8f}")
    
    # Compare with filtered data
    filtered_comparison = compare_distributions(filtered_percentages, traditional_sim_percentages)
    print("\nTraditional model vs. filtered data comparison:")
    print(filtered_comparison)
    
    # Perform chi-square test with filtered data
    filtered_chi2_stat, filtered_p_value, filtered_df = chi_square_test(filtered_counts, traditional_sim_counts)
    print(f"Chi-square test for traditional model vs. filtered data: x^2={filtered_chi2_stat:.4f}, df={filtered_df}, p={filtered_p_value:.8f}")
    
    # Plot distribution comparison
    traditional_output_file = os.path.join(OUTPUT_DIR, 'utility_max_comparison.png')
    plot_distribution_comparison(traditional_comparison, traditional_output_file)
    
    # Plot filtered comparison (NEW)
    filtered_output_file = os.path.join(OUTPUT_DIR, 'filtered_utility_max_comparison.png')
    plot_distribution_comparison(filtered_comparison, filtered_output_file)
    print(f"Filtered comparison plot saved to: {filtered_output_file}")
    
    # Approach 2: Enhanced model with 0 votes
    print("\nApproach 2: Utility maximization model including 0 votes")
    
    # Parameter grid search
    thresholds = [0.5, 1.0, 1.5, 2.0]
    costs = [0.1, 0.2, 0.3, 0.4]
    
    best_threshold = None
    best_cost = None
    best_zero_percent_diff = float('inf')
    best_chi2 = float('inf')
    best_sim_counts = None
    best_sim_percentages = None
    
    # Get actual zero vote percentage
    actual_zero_percent = actual_percentages.get(0, 0)
    
    print("Parameter optimization in progress...")
    for i, threshold in enumerate(thresholds):
        for j, cost in enumerate(costs):
            try:
                print(f"  Debug: Starting simulation {i*len(costs)+j+1}/{len(thresholds)*len(costs)} (threshold={threshold}, cost={cost})")
                zero_sim_counts, zero_sim_percentages = simulate_optimal_votes_with_zero(
                    n_simulations=1000,
                    n_projects=7,
                    max_credits=99,
                    preference_distribution='uniform',
                    indifference_threshold=threshold,
                    decision_cost=cost
                )
                
                # Force garbage collection after each simulation
                gc.collect()
                
                # Calculate zero vote percentage difference
                model_zero_percent = zero_sim_percentages.get(0, 0)
                zero_percent_diff = abs(model_zero_percent - actual_zero_percent)
                
                print(f"  Threshold={threshold}, Cost={cost}: 0-vote percentage={model_zero_percent:.2f}% (Actual: {actual_zero_percent:.2f}%, Difference: {zero_percent_diff:.2f}%)")
                
                # Chi-square test for full distribution
                try:
                    zero_chi2_stat, zero_p_value, zero_df = chi_square_test(actual_counts, zero_sim_counts)
                    print(f"    x^2={zero_chi2_stat:.4f}, p={zero_p_value:.4f}, df={zero_df}")
                except Exception as e:
                    print(f"    Statistical test error: {str(e)}")
                    zero_chi2_stat = float('inf')
                
                # Update best parameters based on zero percentage difference and chi-square
                if zero_percent_diff < best_zero_percent_diff or (zero_percent_diff == best_zero_percent_diff and zero_chi2_stat < best_chi2):
                    best_threshold = threshold
                    best_cost = cost
                    best_zero_percent_diff = zero_percent_diff
                    best_chi2 = zero_chi2_stat
                    best_sim_counts = zero_sim_counts
                    best_sim_percentages = zero_sim_percentages
                    print(f"    Found new optimal parameters!")
                
            except Exception as e:
                print(f"  Simulation error (threshold={threshold}, cost={cost}): {str(e)}")
                
    print(f"\nOptimal parameters: Threshold={best_threshold}, Cost={best_cost}, 0-vote difference={best_zero_percent_diff:.2f}%, x^2={best_chi2:.4f}")
    
    if best_sim_percentages is not None:
        # Compare best model with actual data
        zero_comparison = compare_distributions(actual_percentages, best_sim_percentages)
        
        # Plot enhanced model comparison
        zero_output_file = os.path.join(OUTPUT_DIR, 'zero_model_comparison.png')
        plot_distribution_comparison(zero_comparison, zero_output_file)
        print(f"Zero model comparison plot saved to: {zero_output_file}")
        
        # Plot comprehensive model comparison (NEW)
        distributions_dict = {
            '従来モデル': traditional_sim_percentages,
            'ゼロ投票モデル': best_sim_percentages
        }
        model_comparison_file = os.path.join(OUTPUT_DIR, 'model_comparison.png')
        plot_multiple_distributions(actual_percentages, distributions_dict, model_comparison_file)
        print(f"Model comparison plot saved to: {model_comparison_file}")
        
        # Chi-square test for the best model
        try:
            zero_chi2_stat, zero_p_value, zero_df = chi_square_test(actual_counts, best_sim_counts)
            print(f"Chi-square test for 0-vote model vs. all data: x^2={zero_chi2_stat:.4f}, df={zero_df}, p={zero_p_value:.8f}")
        except Exception as e:
            print(f"Statistical test error for 0-vote model vs. all data: {str(e)}")
        
        # Generate report
        try:
            report_file = os.path.join(OUTPUT_DIR, 'utility_max_analysis_report.md')
            generate_report(
                votes_df=votes_df,
                actual_counts=actual_counts,
                actual_percentages=actual_percentages,
                simulated_counts=best_sim_counts,
                simulated_percentages=best_sim_percentages,
                comparison_df=zero_comparison,
                chi2_stat=zero_chi2_stat,
                p_value=zero_p_value,
                df=zero_df,
                output_file=report_file
            )
        except Exception as e:
            print(f"Report generation error: {str(e)}")
    
    print("\nUtility maximization analysis complete. Results saved to the 'results/figures/neutral_bias' directory.")

if __name__ == "__main__":
    main() 