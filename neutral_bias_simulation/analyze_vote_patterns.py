import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
import matplotlib.ticker as mtick

# ディレクトリ設定
VOTES_FILE = '../votes.csv'  
CANDIDATES_FILE = '../candidates.csv'
OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_transform_data():
    """Load and transform data from CSV files"""
    # Load data
    votes_df = pd.read_csv(VOTES_FILE)
    candidates_df = pd.read_csv(CANDIDATES_FILE)
    
    # Translate project titles to English - using exact project names from candidates.csv
    project_name_translations = {
        "政を祭に変える #vote_forプロジェクト": "Politics to Festival #vote_for Project",
        "淡路島クエストカレッジ": "Awaji Island Quest College",
        "イナトリアートセンター計画": "Inatori Art Center Plan",
        "JINEN TRAVEL": "JINEN TRAVEL",
        "ビオ田んぼプロジェクト": "Bio Rice Field Project",
        "パラ旅応援団": "Para Travel Support Team",
        "10代・20代の「いま、やりたい」を後押しする拠点　ちばユースセンターPRISM": "Chiba Youth Center PRISM - Support for Teens and 20s"
    }
    
    if 'title' in candidates_df.columns:
        candidates_df['title'] = candidates_df['title'].map(
            lambda x: project_name_translations.get(x, x)
        )
    
    # Transform votes from wide to long format
    # Each row has votes for multiple candidates
    votes_long = pd.melt(
        votes_df, 
        id_vars=['voter_id', 'vote_id'], 
        value_vars=[f'candidate_{i}' for i in range(7)],
        var_name='candidate_column', 
        value_name='vote_value'
    )
    
    # Extract candidate_id from column name
    votes_long['candidate_id'] = votes_long['candidate_column'].str.extract(r'candidate_(\d+)').astype(int)
    
    # Drop intermediate column
    votes_long = votes_long.drop('candidate_column', axis=1)
    
    return candidates_df, votes_long

def analyze_vote_distribution(votes_df, candidates_df):
    """Analyze the distribution of votes"""
    # Basic statistics
    vote_stats = votes_df.groupby('candidate_id')['vote_value'].agg([
        'count', 'mean', 'std', 'min', 'max', 
        lambda x: x.value_counts().get(1, 0)  # Count of 1-point votes
    ]).rename(columns={'<lambda_0>': 'one_vote_count'})
    
    # Add candidate names
    if 'title' in candidates_df.columns:
        candidate_names = candidates_df.set_index('candidate_id')['title']
    else:
        candidate_names = candidates_df.set_index('candidate_id')['name']
        
    vote_stats = vote_stats.join(candidate_names, how='left')
    vote_stats.rename(columns={'title': 'name'}, inplace=True)
    
    # Calculate percentage of 1-point votes
    vote_stats['one_vote_percentage'] = vote_stats['one_vote_count'] / vote_stats['count'] * 100
    
    # Calculate zero votes (all voters - voters who voted)
    total_voters = len(votes_df['voter_id'].unique())
    vote_stats['zero_vote_count'] = total_voters - vote_stats['count']
    
    # Compare with theoretical distribution
    # Hypothesis: If votes were evenly distributed, 1-point votes would be ~1/9 (11.1%)
    vote_stats['expected_one_vote_count'] = vote_stats['count'] / 9
    vote_stats['one_vote_deviation'] = vote_stats['one_vote_count'] - vote_stats['expected_one_vote_count']
    vote_stats['one_vote_deviation_percentage'] = (vote_stats['one_vote_deviation'] / vote_stats['expected_one_vote_count']) * 100
    
    return vote_stats

def analyze_voter_patterns(votes_df):
    """Analyze voting patterns per voter"""
    # Voter statistics
    voter_stats = votes_df.groupby('voter_id').agg(
        total_votes=('vote_value', 'count'),
        one_votes=('vote_value', lambda x: (x == 1).sum()),
        mean_vote=('vote_value', 'mean'),
        max_vote=('vote_value', 'max')
    )
    
    voter_stats['one_vote_percentage'] = voter_stats['one_votes'] / voter_stats['total_votes'] * 100
    
    # Categorize voting patterns
    voter_stats['vote_pattern'] = pd.cut(
        voter_stats['one_vote_percentage'],
        bins=[0, 20, 40, 60, 80, 100],
        labels=['Very Low 1s', 'Low 1s', 'Medium 1s', 'High 1s', 'Very High 1s']
    )
    
    return voter_stats

def detect_neutral_bias(votes_df, vote_stats):
    """Detect neutral bias patterns"""
    # Overall vote distribution
    vote_dist = votes_df['vote_value'].value_counts().sort_index()
    vote_dist_pct = vote_dist / vote_dist.sum() * 100
    
    # 投票値ごとのコスト（1票=1クレジット、9票=81クレジット）
    vote_costs = {i: i**2 for i in range(1, 10)}
    
    # 総クレジット（99）と投票者数から理論的な投票分布を計算
    # 各票数のコストを考慮した期待分布をモデル化
    total_votes = len(votes_df)
    total_voters = len(votes_df['voter_id'].unique())
    avg_credits_per_voter = 99  # 各投票者に割り当てられた総クレジット
    
    # コストに反比例する理論分布モデル（仮定）
    # より精緻なモデルは複雑なシミュレーションが必要だが、ここでは簡易的に反比例モデルを使用
    inverse_costs = {i: 1/vote_costs[i] for i in range(1, 10)}
    total_inverse = sum(inverse_costs.values())
    
    # 期待される各投票値の比率
    expected_ratios = {i: inverse_costs[i]/total_inverse for i in range(1, 10)}
    
    # 理論的期待値（コスト構造を考慮した場合）
    expected_per_vote_cost_adjusted = {i: total_votes * expected_ratios[i] for i in range(1, 10)}
    
    # 従来の均等分布での期待値（参考用）
    expected_per_vote_uniform = total_votes / 9
    
    # 観測値と均等分布期待値（従来の計算法）
    observed_counts = np.array([vote_dist.get(i, 0) for i in range(1, 10)])
    expected_counts_uniform = np.ones(9) * expected_per_vote_uniform
    
    # 観測値とコスト調整済み期待値
    expected_counts_adjusted = np.array([expected_per_vote_cost_adjusted[i] for i in range(1, 10)])
    
    # カイ二乗統計量の計算（均等分布との比較）
    chi2_stat_uniform = np.sum(((observed_counts - expected_counts_uniform) ** 2) / expected_counts_uniform)
    
    # カイ二乗統計量の計算（コスト調整済み分布との比較）
    chi2_stat_adjusted = np.sum(((observed_counts - expected_counts_adjusted) ** 2) / expected_counts_adjusted)
    
    # p値の計算（自由度8のカイ二乗分布）
    p_value_uniform = stats.chi2.sf(chi2_stat_uniform, 8)
    p_value_adjusted = stats.chi2.sf(chi2_stat_adjusted, 8)
    
    # 1票の過剰使用に関する統計（両方の期待値モデルと比較）
    one_vote_excess_uniform = vote_dist.get(1, 0) - expected_per_vote_uniform
    one_vote_excess_pct_uniform = (one_vote_excess_uniform / expected_per_vote_uniform) * 100 if expected_per_vote_uniform > 0 else 0
    
    one_vote_excess_adjusted = vote_dist.get(1, 0) - expected_per_vote_cost_adjusted[1]
    one_vote_excess_pct_adjusted = (one_vote_excess_adjusted / expected_per_vote_cost_adjusted[1]) * 100 if expected_per_vote_cost_adjusted[1] > 0 else 0
    
    # 1票比率のプロジェクト間格差
    one_vote_percentages = vote_stats['one_vote_percentage']
    one_vote_std = one_vote_percentages.std()
    one_vote_range = one_vote_percentages.max() - one_vote_percentages.min()
    
    return {
        'vote_distribution': vote_dist,
        'vote_distribution_percentage': vote_dist_pct,
        'expected_distribution_uniform': {i: expected_per_vote_uniform for i in range(1, 10)},
        'expected_distribution_cost_adjusted': expected_per_vote_cost_adjusted,
        'chi2_statistic_uniform': chi2_stat_uniform,
        'p_value_uniform': p_value_uniform,
        'chi2_statistic_adjusted': chi2_stat_adjusted,
        'p_value_adjusted': p_value_adjusted,
        'one_vote_excess_uniform': one_vote_excess_uniform,
        'one_vote_excess_percentage_uniform': one_vote_excess_pct_uniform,
        'one_vote_excess_adjusted': one_vote_excess_adjusted,
        'one_vote_excess_percentage_adjusted': one_vote_excess_pct_adjusted,
        'one_vote_percentage_std': one_vote_std,
        'one_vote_percentage_range': one_vote_range,
        'expected_ratios': expected_ratios  # コスト調整後の理論的な分布比率
    }

def plot_vote_distribution(vote_dist, bias_results, output_file):
    """Plot vote value distribution"""
    plt.figure(figsize=(12, 8))
    
    # 実際の投票分布
    ax = sns.barplot(x=vote_dist.index, y=vote_dist.values, color='steelblue', alpha=0.7, label='Actual votes')
    
    # 期待値（均等分布）
    expected_uniform = np.array([bias_results['expected_distribution_uniform'][i] for i in range(1, 10)])
    plt.plot(range(len(expected_uniform)), expected_uniform, 'r--', label='Expected (uniform distribution)', linewidth=2)
    
    # 期待値（コスト調整済み）
    expected_adjusted = np.array([bias_results['expected_distribution_cost_adjusted'][i] for i in range(1, 10)])
    plt.plot(range(len(expected_adjusted)), expected_adjusted, 'g--', label='Expected (cost-adjusted distribution)', linewidth=2)
    
    plt.title('Vote Value Distribution')
    plt.xlabel('Vote Value')
    plt.ylabel('Number of Votes')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 1票を強調表示
    bars = ax.patches
    if len(bars) > 0:
        bars[0].set_facecolor('orange')
        bars[0].set_alpha(0.9)
    
    # 各票数の割合とコスト情報をテキストで追加
    for i, (votes, exp_uniform, exp_adjusted) in enumerate(zip(vote_dist.values, expected_uniform, expected_adjusted)):
        vote_value = i + 1
        cost = vote_value ** 2
        plt.text(i, votes + 5, f"Cost: {cost}", ha='center', fontsize=9)
        diff_pct = ((votes - exp_adjusted) / exp_adjusted * 100) if exp_adjusted > 0 else 0
        plt.text(i, votes - 20, f"{diff_pct:.1f}%", ha='center', fontsize=9, color='darkgreen' if diff_pct < 0 else 'darkred')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def plot_one_vote_percentage_by_project(vote_stats, bias_results, output_file):
    """Plot 1-point vote percentage by project"""
    plt.figure(figsize=(12, 8))
    
    data = vote_stats.sort_values('one_vote_percentage', ascending=False)
    
    ax = sns.barplot(x='name', y='one_vote_percentage', data=data, color='steelblue')
    
    # 1票の期待割合（コスト調整済みモデル）
    expected_one_vote_ratio = bias_results['expected_ratios'][1] * 100
    plt.axhline(y=expected_one_vote_ratio, color='g', linestyle='--', 
               label=f'Expected 1-point ratio (cost-adjusted): {expected_one_vote_ratio:.1f}%')
    
    # 1票の期待割合（均等分布）
    plt.axhline(y=100/9, color='r', linestyle='--', 
               label=f'Expected 1-point ratio (uniform): {100/9:.1f}%')
    
    # 1票の実際の平均割合
    avg_one_vote_pct = vote_stats['one_vote_percentage'].mean()
    plt.axhline(y=avg_one_vote_pct, color='black', linestyle='-', 
               label=f'Average 1-point ratio: {avg_one_vote_pct:.1f}%')
    
    plt.title('1-Point Vote Percentage by Project')
    plt.xlabel('Project Name')
    plt.ylabel('1-Point Vote Percentage (%)')
    plt.legend()
    
    # Format as percentage
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    
    # 各プロジェクトの期待値からの偏差を表示
    for i, row in enumerate(data.itertuples()):
        diff_pct = row.one_vote_percentage - expected_one_vote_ratio
        plt.text(i, row.one_vote_percentage + 1, f"{diff_pct:+.1f}%", 
                ha='center', color='darkred' if diff_pct > 0 else 'darkgreen')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

def plot_voter_patterns(voter_stats, output_file):
    """Plot voter pattern distribution"""
    plt.figure(figsize=(10, 6))
    
    pattern_counts = voter_stats['vote_pattern'].value_counts().sort_index()
    
    ax = sns.barplot(x=pattern_counts.index, y=pattern_counts.values)
    
    # Display values above bars
    for i, v in enumerate(pattern_counts.values):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    plt.title('Voter Pattern Distribution of 1-Point Votes')
    plt.xlabel('1-Point Vote Usage Pattern')
    plt.ylabel('Number of Voters')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def generate_report(vote_stats, voter_stats, bias_results, output_file):
    """Generate analysis report"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Neutral Bias Analysis Report\n\n")
        
        # Basic statistics
        f.write("## 1. Basic Statistics\n\n")
        f.write(f"- Total votes: {vote_stats['count'].sum()}\n")
        f.write(f"- Total voters: {len(voter_stats)}\n")
        f.write(f"- Total 1-point votes: {vote_stats['one_vote_count'].sum()} ({vote_stats['one_vote_count'].sum() / vote_stats['count'].sum() * 100:.2f}%)\n")
        f.write(f"- Total 0-point votes: {vote_stats['zero_vote_count'].sum()}\n\n")
        
        # Theoretical distribution information
        f.write("## 2. Theoretical Vote Distribution Analysis\n\n")
        f.write("### Quadratic Voting Cost Structure\n\n")
        f.write("| Vote Value | Cost (Credits) | Expected Ratio (Cost-Adjusted) | Expected Ratio (Uniform) |\n")
        f.write("|------------|----------------|--------------------------------|-------------------------|\n")
        
        for i in range(1, 10):
            f.write(f"| {i} | {i**2} | {bias_results['expected_ratios'][i]*100:.2f}% | {100/9:.2f}% |\n")
        
        f.write("\n")
        
        # Chi-square test results
        f.write("### Distribution Test Results\n\n")
        f.write(f"#### Compared to Uniform Distribution\n")
        f.write(f"- Chi-square value: {bias_results['chi2_statistic_uniform']:.4f}\n")
        f.write(f"- p-value: {bias_results['p_value_uniform']:.8f}\n")
        f.write(f"- Excess 1-point votes: {bias_results['one_vote_excess_uniform']:.2f} votes\n")
        f.write(f"- Excess 1-point percentage: {bias_results['one_vote_excess_percentage_uniform']:.2f}%\n\n")
        
        f.write(f"#### Compared to Cost-Adjusted Distribution\n")
        f.write(f"- Chi-square value: {bias_results['chi2_statistic_adjusted']:.4f}\n")
        f.write(f"- p-value: {bias_results['p_value_adjusted']:.8f}\n")
        f.write(f"- Excess 1-point votes: {bias_results['one_vote_excess_adjusted']:.2f} votes\n")
        f.write(f"- Excess 1-point percentage: {bias_results['one_vote_excess_percentage_adjusted']:.2f}%\n\n")
        
        if bias_results['p_value_adjusted'] < 0.05:
            f.write(f"**Result**: Vote values differ significantly even from the cost-adjusted distribution. Neutral bias likely exists beyond what can be explained by QV's cost structure.\n\n")
        else:
            f.write(f"**Result**: Vote value distribution does not differ significantly from the cost-adjusted theoretical distribution.\n\n")
        
        # Project-specific 1-point vote ratios
        f.write("## 3. 1-Point Vote Ratio by Project\n\n")
        f.write("| Project Name | Total Votes | 1-Point Votes | 1-Point % | Average 1-Point % | Deviation |\n")
        f.write("|--------------|---------|-------|---------|----------|----------|\n")
        
        avg_one_vote_pct = vote_stats['one_vote_percentage'].mean()
        
        for _, row in vote_stats.sort_values('one_vote_percentage', ascending=False).iterrows():
            deviation = row['one_vote_percentage'] - avg_one_vote_pct
            f.write(f"| {row['name']} | {row['count']} | {row['one_vote_count']} | {row['one_vote_percentage']:.2f}% | {avg_one_vote_pct:.2f}% | {deviation:+.2f}% |\n")
        
        f.write("\n")
        
        # Voter pattern analysis
        f.write("## 4. Voter Pattern Analysis\n\n")
        pattern_counts = voter_stats['vote_pattern'].value_counts().sort_index()
        
        f.write("| 1-Point Use Pattern | Voter Count | Percentage |\n")
        f.write("|---------------|---------|------|\n")
        
        for pattern, count in pattern_counts.items():
            f.write(f"| {pattern} | {count} | {count/len(voter_stats)*100:.2f}% |\n")
        
        f.write("\n")
        
        # Summary and next steps
        f.write("## 5. Summary and Next Steps\n\n")
        
        if bias_results['one_vote_excess_percentage_adjusted'] > 50:
            bias_level = "strong"
        elif bias_results['one_vote_excess_percentage_adjusted'] > 20:
            bias_level = "moderate"
        elif bias_results['one_vote_excess_percentage_adjusted'] > 0:
            bias_level = "weak"
        else:
            bias_level = "no"
            
        f.write(f"The analysis suggests {bias_level} evidence of neutral bias in the voting data. ")
        f.write(f"Specifically, 1-point votes (minimum vote value) are used ")
        f.write(f"{bias_results['one_vote_excess_percentage_adjusted']:.2f}% more than theoretically expected, even after accounting for QV's quadratic cost structure.\n\n")
        
        f.write("Based on these results, the following additional analyses are recommended:\n\n")
        f.write("1. Scenario simulation: Analyze budget allocation changes if a certain percentage of 1-point votes were converted to 0-point votes\n")
        f.write("2. Voter-specific analysis: Examine how different voting patterns impact neutral bias\n")
        f.write("3. UI design proposals: Develop voting interface improvements to mitigate bias\n")

def main():
    # Load and transform data
    candidates_df, votes_df = load_and_transform_data()
    
    # Run analysis
    vote_stats = analyze_vote_distribution(votes_df, candidates_df)
    voter_stats = analyze_voter_patterns(votes_df)
    bias_results = detect_neutral_bias(votes_df, vote_stats)
    
    # Visualizations
    plot_vote_distribution(
        bias_results['vote_distribution'], 
        bias_results,
        os.path.join(OUTPUT_DIR, 'vote_distribution.png')
    )
    
    plot_one_vote_percentage_by_project(
        vote_stats, 
        bias_results,
        os.path.join(OUTPUT_DIR, 'one_vote_percentage_by_project.png')
    )
    
    plot_voter_patterns(
        voter_stats, 
        os.path.join(OUTPUT_DIR, 'voter_patterns.png')
    )
    
    # Generate report
    generate_report(
        vote_stats, 
        voter_stats, 
        bias_results, 
        os.path.join(OUTPUT_DIR, 'neutral_bias_report.md')
    )
    
    # Save CSV files
    vote_stats.to_csv(os.path.join(OUTPUT_DIR, 'vote_statistics.csv'), index=False)
    voter_stats.to_csv(os.path.join(OUTPUT_DIR, 'voter_statistics.csv'), index=True)
    
    # Save theoretical distributions for further analysis
    theoretical_dists = pd.DataFrame({
        'vote_value': list(range(1, 10)),
        'observed_count': [bias_results['vote_distribution'].get(i, 0) for i in range(1, 10)],
        'uniform_expected': [bias_results['expected_distribution_uniform'][i] for i in range(1, 10)],
        'cost_adjusted_expected': [bias_results['expected_distribution_cost_adjusted'][i] for i in range(1, 10)],
        'cost': [i**2 for i in range(1, 10)],
        'expected_ratio': [bias_results['expected_ratios'][i] for i in range(1, 10)]
    })
    theoretical_dists.to_csv(os.path.join(OUTPUT_DIR, 'theoretical_distributions.csv'), index=False)
    
    print("Analysis complete! Results saved in the output directory.")

if __name__ == "__main__":
    main() 