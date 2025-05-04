#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
投票パターンの特定とクラスター分析を行うスクリプト
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.cm as cm

# Add translation functions
def get_translation_dict():
    """Create a dictionary for Japanese to English translation"""
    return {
        # Labels and titles
        "投票者 × プロジェクト投票値ヒートマップ": "Voter × Project Vote Value Heatmap",
        "プロジェクト": "Project",
        "投票者": "Voter",
        "プロジェクト間の投票値相関": "Correlation Between Project Vote Values",
        "クラスター数とシルエットスコアの関係": "Relationship Between Number of Clusters and Silhouette Score",
        "クラスター数": "Number of Clusters",
        "シルエットスコア": "Silhouette Score",
        "最適クラスター数": "Optimal Number of Clusters",
        "投票パターンのクラスタリング結果": "Clustering Results of Voting Patterns",
        "主成分": "Principal Component",
        "クラスター": "Cluster",
        "の平均投票パターン": "'s Average Voting Pattern",
        "サイズ": "Size",
        "平均投票値": "Average Vote Value",
        "小票境界線": "Small Vote Boundary",
        "クラスター別の小票(1-2票)使用パターン": "Small Vote (1-2) Usage Pattern by Cluster",
        "小票を使用した投票者の割合": "Percentage of Voters Using Small Votes",
        
        # Report translations
        "投票パターン分析レポート": "Voting Pattern Analysis Report",
        "基本統計情報": "Basic Statistical Information",
        "総投票者数": "Total Number of Voters",
        "最適クラスター数": "Optimal Number of Clusters",
        "最大シルエットスコア": "Maximum Silhouette Score",
        "プロジェクト間の相関分析": "Correlation Analysis Between Projects",
        "正の相関が強いプロジェクトペア": "Project Pairs with Strong Positive Correlation",
        "負の相関が強いプロジェクトペア": "Project Pairs with Strong Negative Correlation",
        "投票者の行動分析": "Voter Behavior Analysis",
        "平均の最大投票/他投票比率": "Average Maximum Vote/Other Votes Ratio",
        "小票（1-2票）を使用した平均プロジェクト数": "Average Number of Projects Where Small Votes (1-2) Were Used",
        "未投票（0票）の平均プロジェクト数": "Average Number of Unvoted Projects (0 votes)",
        "極端な投票比率（5倍以上）を持つ投票者数": "Number of Voters with Extreme Voting Ratio (5x or more)",
        "クラスター分析結果": "Cluster Analysis Results",
        "サイズ": "Size",
        "名": "voters",
        "主要プロジェクト": "Main Project",
        "平均": "average",
        "票": "votes",
        "次点プロジェクト": "Secondary Project",
        "投票比率（主要/次点）": "Voting Ratio (Main/Secondary)",
        "プロジェクト別平均投票値": "Average Vote Value by Project",
        "小票使用パターン": "Small Vote Usage Pattern",
        "仮説への含意": "Implications for Hypotheses",
        "中立バイアス仮説の評価": "Evaluation of Neutral Bias Hypothesis",
        "支持": "Support",
        "不支持": "Not Supported",
        "戦略的投票仮説の評価": "Evaluation of Strategic Voting Hypothesis",
        "真の選好反映仮説の評価": "Evaluation of True Preference Reflection Hypothesis",
        "総合的結論": "Overall Conclusion",
        
        # Process messages
        "投票パターン分析を開始...": "Starting voting pattern analysis...",
        "データ読み込み完了": "Data loading complete",
        "名の投票者": "voters",
        "件のプロジェクト": "projects",
        "投票パターン行列の作成完了": "Voting pattern matrix creation complete",
        "投票パターンの相関分析完了": "Voting pattern correlation analysis complete",
        "クラスタリング分析完了": "Clustering analysis complete",
        "最適クラスター数": "optimal number of clusters",
        "投票戦略パターンの特定完了": "Vote strategy pattern identification complete",
        "可視化グラフの生成完了": "Visualization graph generation complete",
        "分析レポートの生成完了": "Analysis report generation complete",
        "すべての結果は": "All results have been saved to",
        "ディレクトリに保存されました": "directory"
    }

def translate_project_name(name):
    """Translate project names to English"""
    project_translations = {
        # Exact translations for all project names from candidates.csv
        "政を祭に変える #vote_forプロジェクト": "Politics to Festival #vote_for Project",
        "淡路島クエストカレッジ": "Awaji Island Quest College",
        "イナトリアートセンター計画": "Inatori Art Center Plan",
        "JINEN TRAVEL": "JINEN TRAVEL",  # Keep as is if already in English
        "ビオ田んぼプロジェクト": "Bio Rice Field Project",
        "パラ旅応援団": "Para Travel Support Team",
        "10代・20代の「いま、やりたい」を後押しする拠点　ちばユースセンターPRISM": "Chiba Youth Center PRISM - Support for Teens and 20s"
    }
    
    return project_translations.get(name, name)  # Return original if no translation

def translate_text(text, translation_dict=None):
    """Translate text using the translation dictionary"""
    if translation_dict is None:
        translation_dict = get_translation_dict()
    
    return translation_dict.get(text, text)  # Return original if no translation

# Update directory path to use absolute path to avoid issues
output_dir = './output'
os.makedirs(output_dir, exist_ok=True)

def load_data():
    """Load voting data and project data"""
    votes_df = pd.read_csv('../votes.csv')
    candidates_df = pd.read_csv('../candidates.csv')
    
    # Create a wide-to-long format transformation for voters and their votes to each candidate
    # Each row in votes.csv has columns for each candidate (candidate_0, candidate_1, etc.)
    voter_data = []
    
    for _, row in votes_df.iterrows():
        voter_id = row['voter_id']
        vote_id = row['vote_id']
        
        for i in range(7):  # 7 candidates in the data
            col_name = f'candidate_{i}'
            if col_name in row:
                vote_value = row[col_name]
                voter_data.append({
                    'voter_id': voter_id,
                    'candidate_id': i,
                    'vote_value': vote_value
                })
    
    votes_long_df = pd.DataFrame(voter_data)
    
    # Update candidate dataframe
    candidates_df = candidates_df.rename(columns={
        'candidate_id': 'id',
        'title': 'title'
    })
    
    # Translate project names to English
    if 'title' in candidates_df.columns:
        candidates_df['title'] = candidates_df['title'].apply(translate_project_name)
    
    return votes_long_df, candidates_df

def create_voter_pattern_matrix(votes_df, candidates_df):
    """Create a voting pattern matrix for each voter"""
    # Initialize voter pattern matrix
    voter_ids = votes_df['voter_id'].unique()
    project_names = candidates_df.set_index('id')['title']
    
    # Create voter × project matrix
    pattern_dict = {}
    
    for voter_id in voter_ids:
        voter_votes = votes_df[votes_df['voter_id'] == voter_id]
        voter_pattern = {}
        
        # Fill in vote values for each project
        for _, vote_row in voter_votes.iterrows():
            candidate_id = vote_row['candidate_id']
            if candidate_id in project_names.index:
                project_name = project_names[candidate_id]
                voter_pattern[project_name] = vote_row['vote_value']
        
        pattern_dict[voter_id] = voter_pattern
    
    # Convert to DataFrame
    pattern_df = pd.DataFrame.from_dict(pattern_dict, orient='index')
    
    # Replace NaN values with 0 (no vote)
    pattern_df = pattern_df.fillna(0)
    
    return pattern_df

def analyze_correlations(pattern_df):
    """投票パターン間の相関分析"""
    # プロジェクト間の相関行列
    correlation_matrix = pattern_df.corr()
    
    # 投票者の最大投票先とその他投票先の関係分析
    voter_analysis = []
    
    for voter_id, row in pattern_df.iterrows():
        # 最大投票値とそのプロジェクト
        max_vote = row.max()
        max_project = row.idxmax()
        
        # 最大以外の投票値の統計
        other_votes = row[row.index != max_project]
        avg_other_votes = other_votes.mean()
        min_other_vote = other_votes.min()
        
        # 最大投票と他投票の比率
        vote_ratio = max_vote / avg_other_votes if avg_other_votes > 0 else float('inf')
        
        # 小票（1-2）の数
        small_votes = len(row[(row >= 1) & (row <= 2)])
        
        # 未投票（0票）の数
        zero_votes = len(row[row == 0])
        
        voter_analysis.append({
            'voter_id': voter_id,
            'max_vote': max_vote,
            'max_project': max_project,
            'avg_other_votes': avg_other_votes,
            'min_other_vote': min_other_vote,
            'vote_ratio': vote_ratio,
            'small_votes': small_votes,
            'zero_votes': zero_votes
        })
    
    voter_analysis_df = pd.DataFrame(voter_analysis)
    return correlation_matrix, voter_analysis_df

def perform_clustering(pattern_df):
    """投票パターンのクラスタリング分析"""
    # スケーリング
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(pattern_df)
    
    # 次元削減（可視化用）
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled_data)
    
    # クラスタリングの最適クラスター数を決定
    silhouette_scores = []
    kmeans_results = {}
    
    for k in range(2, 8):  # 2から7クラスタを試す
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_data)
        score = silhouette_score(scaled_data, clusters)
        silhouette_scores.append(score)
        kmeans_results[k] = clusters
    
    # 最適クラスター数
    optimal_k = range(2, 8)[np.argmax(silhouette_scores)]
    optimal_clusters = kmeans_results[optimal_k]
    
    # 結果をデータフレームに追加
    clustering_df = pattern_df.copy()
    clustering_df['cluster'] = optimal_clusters
    clustering_df['pca_x'] = pca_result[:, 0]
    clustering_df['pca_y'] = pca_result[:, 1]
    
    return clustering_df, optimal_k, silhouette_scores

def identify_voting_strategies(clustering_df, pattern_df):
    """投票戦略パターンの特定"""
    # クラスターごとの特徴を分析
    cluster_stats = []
    
    for cluster_id in clustering_df['cluster'].unique():
        cluster_pattern = clustering_df[clustering_df['cluster'] == cluster_id].drop(['cluster', 'pca_x', 'pca_y'], axis=1)
        
        # 各プロジェクトの平均投票値
        avg_votes = cluster_pattern.mean()
        
        # 標準偏差
        std_votes = cluster_pattern.std()
        
        # メインプロジェクト（最大平均投票値）
        main_project = avg_votes.idxmax()
        main_vote_avg = avg_votes[main_project]
        
        # セカンダリプロジェクト（2番目に高い平均投票値）
        second_project = avg_votes.drop(main_project).idxmax()
        second_vote_avg = avg_votes[second_project]
        
        # 投票比率（メイン/セカンダリ）
        vote_ratio = main_vote_avg / second_vote_avg if second_vote_avg > 0 else float('inf')
        
        # 小票の使用パターン
        small_votes_pattern = {}
        for project in pattern_df.columns:
            votes = cluster_pattern[project]
            small_votes_count = len(votes[(votes >= 1) & (votes <= 2)])
            small_votes_pattern[project] = small_votes_count / len(cluster_pattern) * 100  # パーセント
        
        # クラスターサイズ
        cluster_size = len(cluster_pattern)
        
        cluster_stats.append({
            'cluster_id': cluster_id,
            'size': cluster_size,
            'size_percent': cluster_size / len(clustering_df) * 100,
            'main_project': main_project,
            'main_vote_avg': main_vote_avg,
            'second_project': second_project,
            'second_vote_avg': second_vote_avg,
            'vote_ratio': vote_ratio,
            'avg_votes': dict(avg_votes),
            'std_votes': dict(std_votes),
            'small_votes_pattern': small_votes_pattern
        })
    
    return pd.DataFrame(cluster_stats)

def generate_visualizations(pattern_df, correlation_matrix, clustering_df, optimal_k, silhouette_scores, cluster_stats):
    """分析結果の可視化"""
    # Get translation dictionary
    trans_dict = get_translation_dict()
    
    # 1. 投票値の分布ヒートマップ
    plt.figure(figsize=(14, 10))
    sns.heatmap(pattern_df, cmap='YlGnBu')
    plt.title(translate_text('投票者 × プロジェクト投票値ヒートマップ', trans_dict))
    plt.xlabel(translate_text('プロジェクト', trans_dict))
    plt.ylabel(translate_text('投票者', trans_dict))
    plt.tight_layout()
    plt.savefig(f'{output_dir}/voter_project_heatmap.png', dpi=300)
    plt.close()
    
    # 2. プロジェクト間の相関行列
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
    plt.title(translate_text('プロジェクト間の投票値相関', trans_dict))
    plt.tight_layout()
    plt.savefig(f'{output_dir}/project_correlation_matrix.png', dpi=300)
    plt.close()
    
    # 3. シルエットスコアのエルボープロット
    plt.figure(figsize=(10, 6))
    plt.plot(range(2, 8), silhouette_scores, marker='o')
    plt.axvline(x=optimal_k, color='red', linestyle='--', 
                label=f"{translate_text('最適クラスター数', trans_dict)}: {optimal_k}")
    plt.title(translate_text('クラスター数とシルエットスコアの関係', trans_dict))
    plt.xlabel(translate_text('クラスター数', trans_dict))
    plt.ylabel(translate_text('シルエットスコア', trans_dict))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/silhouette_score_plot.png', dpi=300)
    plt.close()
    
    # 4. クラスタリング結果の散布図
    plt.figure(figsize=(12, 10))
    
    # クラスターごとに色分け
    colors = cm.rainbow(np.linspace(0, 1, optimal_k))
    
    for cluster_id, color in zip(range(optimal_k), colors):
        cluster_data = clustering_df[clustering_df['cluster'] == cluster_id]
        plt.scatter(cluster_data['pca_x'], cluster_data['pca_y'], 
                    color=color, label=f"{translate_text('クラスター', trans_dict)} {cluster_id}", alpha=0.7)
    
    plt.title(f"{translate_text('投票パターンのクラスタリング結果', trans_dict)} (k={optimal_k})")
    plt.xlabel(f"{translate_text('主成分', trans_dict)} 1")
    plt.ylabel(f"{translate_text('主成分', trans_dict)} 2")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/voting_pattern_clusters.png', dpi=300)
    plt.close()
    
    # 5. クラスターごとの投票パターンプロファイル
    for cluster_id in clustering_df['cluster'].unique():
        cluster_stats_row = cluster_stats[cluster_stats['cluster_id'] == cluster_id].iloc[0]
        avg_votes = pd.Series(cluster_stats_row['avg_votes'])
        
        plt.figure(figsize=(14, 8))
        
        # バーの色を設定：メインプロジェクトは特別色に
        colors = ['orange' if project == cluster_stats_row['main_project'] else
                 'lightblue' if project == cluster_stats_row['second_project'] else
                 'steelblue' for project in avg_votes.index]
        
        plt.bar(avg_votes.index, avg_votes.values, color=colors)
        plt.axhline(y=2, color='red', linestyle='--', 
                    label=f"{translate_text('小票境界線', trans_dict)} (2 {translate_text('票', trans_dict)})")
        
        plt.title(f"{translate_text('クラスター', trans_dict)} {cluster_id} {translate_text('の平均投票パターン', trans_dict)} ({translate_text('サイズ', trans_dict)}: {cluster_stats_row['size_percent']:.1f}%)")
        plt.xlabel(translate_text('プロジェクト', trans_dict))
        plt.ylabel(translate_text('平均投票値', trans_dict))
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{output_dir}/cluster_{cluster_id}_profile.png', dpi=300)
        plt.close()
    
    # 6. クラスター間の小票使用パターン比較
    small_votes_data = []
    for _, row in cluster_stats.iterrows():
        for project, value in row['small_votes_pattern'].items():
            small_votes_data.append({
                'cluster': row['cluster_id'],
                'project': project,
                'small_votes_percent': value
            })
    
    small_votes_df = pd.DataFrame(small_votes_data)
    
    plt.figure(figsize=(15, 8))
    sns.barplot(x='project', y='small_votes_percent', hue='cluster', data=small_votes_df)
    plt.title(translate_text('クラスター別の小票(1-2票)使用パターン', trans_dict))
    plt.xlabel(translate_text('プロジェクト', trans_dict))
    plt.ylabel(translate_text('小票を使用した投票者の割合', trans_dict) + ' (%)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title=translate_text('クラスター', trans_dict))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/small_votes_by_cluster.png', dpi=300)
    plt.close()

def generate_report(correlation_matrix, voter_analysis_df, clustering_df, optimal_k, silhouette_scores, cluster_stats):
    """分析結果のテキストレポート生成"""
    # Get translation dictionary
    trans_dict = get_translation_dict()
    
    with open(f'{output_dir}/voting_patterns_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"# {translate_text('投票パターン分析レポート', trans_dict)}\n\n")
        
        f.write(f"## {translate_text('基本統計情報', trans_dict)}\n\n")
        f.write(f"- {translate_text('総投票者数', trans_dict)}: {len(clustering_df)}\n")
        f.write(f"- {translate_text('最適クラスター数', trans_dict)}: {optimal_k}\n")
        f.write(f"- {translate_text('最大シルエットスコア', trans_dict)}: {max(silhouette_scores):.4f}\n\n")
        
        f.write(f"## {translate_text('プロジェクト間の相関分析', trans_dict)}\n\n")
        
        # 強い正の相関ペア
        pos_corr = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                col1 = correlation_matrix.columns[i]
                col2 = correlation_matrix.columns[j]
                corr = correlation_matrix.loc[col1, col2]
                if corr > 0.5:  # 閾値: 中〜強い正の相関
                    pos_corr.append((col1, col2, corr))
        
        # 強い負の相関ペア
        neg_corr = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                col1 = correlation_matrix.columns[i]
                col2 = correlation_matrix.columns[j]
                corr = correlation_matrix.loc[col1, col2]
                if corr < -0.3:  # 閾値: 中〜強い負の相関
                    neg_corr.append((col1, col2, corr))
        
        if pos_corr:
            f.write(f"### {translate_text('正の相関が強いプロジェクトペア', trans_dict)}\n\n")
            for col1, col2, corr in sorted(pos_corr, key=lambda x: x[2], reverse=True):
                f.write(f"- {col1} {translate_text('と', trans_dict)} {col2}: {corr:.4f}\n")
            f.write("\n")
        
        if neg_corr:
            f.write(f"### {translate_text('負の相関が強いプロジェクトペア', trans_dict)}\n\n")
            for col1, col2, corr in sorted(neg_corr, key=lambda x: x[2]):
                f.write(f"- {col1} {translate_text('と', trans_dict)} {col2}: {corr:.4f}\n")
            f.write("\n")
        
        f.write(f"## {translate_text('投票者の行動分析', trans_dict)}\n\n")
        
        # 全体の平均投票比率
        f.write(f"- {translate_text('平均の最大投票/他投票比率', trans_dict)}: {voter_analysis_df['vote_ratio'].mean():.2f}\n")
        f.write(f"- {translate_text('小票（1-2票）を使用した平均プロジェクト数', trans_dict)}: {voter_analysis_df['small_votes'].mean():.2f}\n")
        f.write(f"- {translate_text('未投票（0票）の平均プロジェクト数', trans_dict)}: {voter_analysis_df['zero_votes'].mean():.2f}\n\n")
        
        # 極端な投票者（例：最大投票と他の差が大きい）
        extreme_voters = voter_analysis_df[voter_analysis_df['vote_ratio'] > 5]  # 閾値: 5倍以上
        f.write(f"- {translate_text('極端な投票比率（5倍以上）を持つ投票者数', trans_dict)}: {len(extreme_voters)} ({len(extreme_voters)/len(voter_analysis_df)*100:.1f}%)\n\n")
        
        f.write(f"## {translate_text('クラスター分析結果', trans_dict)}\n\n")
        
        for _, row in cluster_stats.iterrows():
            cluster_id = row['cluster_id']
            f.write(f"### {translate_text('クラスター', trans_dict)} {cluster_id}\n\n")
            f.write(f"- {translate_text('サイズ', trans_dict)}: {row['size']}{translate_text('名', trans_dict)} ({row['size_percent']:.1f}%)\n")
            f.write(f"- {translate_text('主要プロジェクト', trans_dict)}: {row['main_project']} ({translate_text('平均', trans_dict)} {row['main_vote_avg']:.2f}{translate_text('票', trans_dict)})\n")
            f.write(f"- {translate_text('次点プロジェクト', trans_dict)}: {row['second_project']} ({translate_text('平均', trans_dict)} {row['second_vote_avg']:.2f}{translate_text('票', trans_dict)})\n")
            f.write(f"- {translate_text('投票比率（主要/次点）', trans_dict)}: {row['vote_ratio']:.2f}\n\n")
            
            f.write(f"#### {translate_text('プロジェクト別平均投票値', trans_dict)}\n\n")
            for project, value in sorted(row['avg_votes'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {project}: {value:.2f}\n")
            
            f.write(f"\n#### {translate_text('小票使用パターン', trans_dict)}\n\n")
            for project, value in sorted(row['small_votes_pattern'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {project}: {value:.1f}%\n")
            
            f.write("\n")
        
        # 仮説への含意
        f.write(f"## {translate_text('仮説への含意', trans_dict)}\n\n")
        
        # 中立バイアス仮説の評価
        small_votes_high = False
        for _, row in cluster_stats.iterrows():
            # いずれかのクラスターで複数プロジェクトに対して小票使用率が高い場合
            high_small_vote_projects = sum(1 for v in row['small_votes_pattern'].values() if v > 50)
            if high_small_vote_projects >= 3:  # 3プロジェクト以上で50%以上の投票者が小票を使用
                small_votes_high = True
                break
        
        # 戦略的投票の評価
        strategic_voting = len(neg_corr) > 0 or extreme_voters.shape[0] / voter_analysis_df.shape[0] > 0.2
        
        # クラスターの明確な分離
        clear_clustering = max(silhouette_scores) > 0.3
        
        f.write(f"### {translate_text('中立バイアス仮説の評価', trans_dict)}\n\n")
        if small_votes_high:
            f.write(f"- **{translate_text('支持', trans_dict)}**: There are clusters where small votes (1-2) are used at a high rate for multiple projects, suggesting that many voters cast votes for projects they have little interest in.\n")
        else:
            f.write(f"- **{translate_text('不支持', trans_dict)}**: The voting pattern analysis shows that small votes tend to be concentrated on specific projects, which does not strongly indicate the neutral bias characteristic of indiscriminate dispersal of small votes.\n")
        
        f.write(f"\n### {translate_text('戦略的投票仮説の評価', trans_dict)}\n\n")
        if strategic_voting:
            f.write(f"- **{translate_text('支持', trans_dict)}**: The negative correlations between projects and the presence of voters with extreme voting ratios suggest that voters may be intentionally adjusting their votes to prioritize certain projects.\n")
        else:
            f.write(f"- **{translate_text('不支持', trans_dict)}**: The negative correlations between projects are weak, and there are few voters with extreme voting patterns, so there is little evidence of widespread strategic voting.\n")
        
        f.write(f"\n### {translate_text('真の選好反映仮説の評価', trans_dict)}\n\n")
        if clear_clustering:
            f.write(f"- **{translate_text('支持', trans_dict)}**: The formation of clear clusters in voting patterns suggests that different groups of voters have different true preferences, which are reflected in their voting.\n")
        else:
            f.write(f"- **{translate_text('不支持', trans_dict)}**: The low separation of voting pattern clusters suggests that the existence of clear voter groups cannot be confirmed, indicating that voting may not consistently reflect true preferences.\n")
        
        # 結論
        f.write(f"\n## {translate_text('総合的結論', trans_dict)}\n\n")
        
        if small_votes_high and not strategic_voting and not clear_clustering:
            f.write("The results of the voting pattern analysis tend to **support the neutral bias hypothesis**. A pattern is observed where many voters cast small votes for multiple projects, suggesting the existence of formal voting for projects of low interest. The lack of clear evidence of strategic voting and strong preference pattern formation is also consistent with this hypothesis.\n")
        elif strategic_voting and clear_clustering:
            f.write("The results of the voting pattern analysis tend to support **a combination of the strategic voting hypothesis and the true preference reflection hypothesis**. Voters are divided into clear clusters, and there are negative correlations between projects, suggesting that voters may be voting strategically while also based on their true preferences to prioritize certain projects.\n")
        elif clear_clustering and not strategic_voting:
            f.write("The results of the voting pattern analysis tend to **support the true preference reflection hypothesis**. The formation of clear clusters in voting patterns suggests that voters show different voting patterns according to their preferences, indicating that the system appropriately captures voters' true preferences.\n")
        else:
            f.write("The results of the voting pattern analysis suggest that **multiple factors may be coexisting**. Elements of neutral bias, strategic voting, and true preference reflection are observed partially, suggesting the existence of complex voting behavior that cannot be explained by a single hypothesis. More detailed analysis or additional data may be needed to better understand voting behavior.\n")
    
    # CSVファイルに結果を保存
    voter_analysis_df.to_csv(f'{output_dir}/voter_analysis.csv', index=False)
    cluster_stats.to_csv(f'{output_dir}/cluster_stats.csv', index=False)
    
    # クラスタリング結果をオリジナルの投票パターンと合わせて保存
    pattern_with_clusters = clustering_df.drop(['pca_x', 'pca_y'], axis=1)
    pattern_with_clusters.to_csv(f'{output_dir}/vote_patterns_with_clusters.csv')

def main():
    """Main function to run the analysis"""
    print("Starting voting pattern analysis...")
    
    # Load data
    votes_df, candidates_df = load_data()
    print(f"Data loading complete: {len(votes_df['voter_id'].unique())} voters, {len(candidates_df)} projects")
    
    # Create voting pattern matrix
    pattern_df = create_voter_pattern_matrix(votes_df, candidates_df)
    print(f"Voting pattern matrix creation complete: {pattern_df.shape}")
    
    # Correlation analysis
    correlation_matrix, voter_analysis_df = analyze_correlations(pattern_df)
    print("Voting pattern correlation analysis complete")
    
    # Cluster analysis
    clustering_df, optimal_k, silhouette_scores = perform_clustering(pattern_df)
    print(f"Clustering analysis complete: optimal number of clusters = {optimal_k}")
    
    # Identify voting strategies
    cluster_stats = identify_voting_strategies(clustering_df, pattern_df)
    print("Vote strategy pattern identification complete")
    
    # Generate visualizations
    generate_visualizations(pattern_df, correlation_matrix, clustering_df, 
                           optimal_k, silhouette_scores, cluster_stats)
    print("Visualization graph generation complete")
    
    # Generate report
    generate_report(correlation_matrix, voter_analysis_df, clustering_df, 
                   optimal_k, silhouette_scores, cluster_stats)
    print("Analysis report generation complete")
    
    print(f"All results have been saved to {output_dir} directory")

if __name__ == "__main__":
    main() 