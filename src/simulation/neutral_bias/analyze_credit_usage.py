#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
投票者のクレジット使用率と残クレジット分析を行うスクリプト
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Add dictionary for Japanese to English translation
def get_translation_dict():
    """Create a dictionary for Japanese to English translation"""
    return {
        # Project names (if needed)
        # Labels and titles
        "投票者のクレジット使用率分布": "Distribution of Voter Credit Usage Rate",
        "使用率 (%)": "Usage Rate (%)",
        "投票者数": "Number of Voters",
        "90%使用率": "90% Usage Rate",
        "投票者の残クレジット分布": "Distribution of Remaining Credits",
        "残クレジット": "Remaining Credits",
        "残り10クレジット": "10 Credits Remaining",
        "クレジット使用率と投票プロジェクト数の関係": "Relationship Between Credit Usage Rate and Number of Voted Projects",
        "使用率 (%)": "Usage Rate (%)",
        "投票したプロジェクト数": "Number of Projects Voted",
        "残クレジットと未投票プロジェクト数の関係（追加投票可能者）": "Relationship Between Remaining Credits and Unvoted Projects (Potential Additional Voters)",
        "未投票プロジェクト数": "Number of Unvoted Projects",
        "残クレジット": "Remaining Credits",
        
        # Report translations
        "クレジット使用率分析レポート": "Credit Usage Analysis Report",
        "基本統計情報": "Basic Statistical Information",
        "総投票者数": "Total Number of Voters",
        "平均クレジット使用率": "Average Credit Usage Rate",
        "平均残クレジット": "Average Remaining Credits",
        "90%以上のクレジットを使用した投票者": "Voters Who Used More Than 90% of Credits",
        "残クレジットが10以下の投票者": "Voters With 10 or Fewer Remaining Credits",
        "追加投票可能性分析": "Additional Voting Possibility Analysis",
        "追加投票が可能だった投票者": "Voters Who Could Have Cast Additional Votes",
        "追加可能だった平均投票数": "Average Number of Additional Possible Votes",
        "未投票だった平均プロジェクト数": "Average Number of Unvoted Projects",
        "相関分析": "Correlation Analysis",
        "クレジット使用率と投票プロジェクト数の相関係数": "Correlation Coefficient Between Credit Usage Rate and Number of Voted Projects",
        "中立バイアス仮説に関する考察": "Considerations on the Neutral Bias Hypothesis",
        "クレジット使用率分析結果は**中立バイアス仮説を支持**しています": "Credit usage analysis results **support the neutral bias hypothesis**",
        "大多数の投票者がクレジットをほぼ使い切っている": "The majority of voters used almost all their credits",
        "残クレジットが少量のユーザーが多数を占める": "Users with few remaining credits make up the majority",
        "追加投票可能だったにも関わらず投票しなかったケースが少ない": "Few cases where voters could have cast additional votes but did not",
        "これらはクレジット使い切り行動の存在を示唆し、中立バイアス仮説と整合します": "These suggest the existence of credit maximization behavior, consistent with the neutral bias hypothesis",
        "クレジット使用率分析結果は**中立バイアス仮説を完全には支持していません**": "Credit usage analysis results **do not fully support the neutral bias hypothesis**",
        "クレジット使用率90%以上の投票者は": "Voters with credit usage rate over 90% is",
        "に留まり、クレジット使い切り行動が普遍的とは言えない": ", indicating that credit maximization behavior is not universal",
        "残クレジットが10以下の投票者は": "Voters with 10 or fewer remaining credits is",
        "であり、過半数に達していない": ", which does not reach a majority",
        "追加投票可能だったにも関わらず投票しなかったケースが": "Cases where voters could have cast additional votes but did not is",
        "と多く、真の無関心の可能性を示唆": ", suggesting the possibility of true indifference",
        "これらの結果は、投票行動にはクレジット使い切り以外の要因も影響していることを示唆しています": "These results suggest that factors other than credit maximization also influence voting behavior",
        "クレジット使用率分析を開始...": "Starting credit usage analysis...",
        "データ読み込み完了": "Data loading complete",
        "名の投票者": "voters",
        "件のプロジェクト": "projects",
        "クレジット使用状況の分析完了": "Credit usage analysis complete",
        "追加投票可能性の分析完了": "Additional voting possibility analysis complete",
        "名が追加投票可能だった": "voters could have cast additional votes",
        "可視化グラフの生成完了": "Visualization graphs generation complete",
        "分析レポートの生成完了": "Analysis report generation complete",
        "すべての結果は": "All results have been saved to",
        "ディレクトリに保存されました": "directory",
        "残クレジット分布の詳細分析": "Detailed Analysis of Remaining Credits Distribution",
        "残クレジット範囲": "Remaining Credits Range",
        "投票者割合": "Percentage of Voters",
        "可能だった追加投票数": "Possible Additional Votes",
        "意図的投票終了の可能性": "Possibility of Intentional Voting Termination",
        "残クレジット1-9の投票者": "Voters with 1-9 Remaining Credits",
        "残クレジット5-9の投票者": "Voters with 5-9 Remaining Credits",
        "残クレジット8-9の投票者": "Voters with 8-9 Remaining Credits",
        "追加投票可能な投票者割合の分析": "Analysis of Voters Who Could Have Cast Additional Votes",
        "最大限追加可能な投票数": "Maximum Additional Possible Votes",
        "追加投票の選択肢が有意にも関わらず投票を終了した割合": "Percentage Who Terminated Voting Despite Having Significant Voting Options",
    }

# ディレクトリ作成
output_dir = 'results/figures/neutral_bias'
os.makedirs(output_dir, exist_ok=True)

def load_data():
    """投票データとプロジェクトデータを読み込む"""
    votes_df = pd.read_csv('data/votes.csv')
    candidates_df = pd.read_csv('data/vote_summary.csv')
    
    # Translate project names to English if they exist in Japanese
    if 'title' in candidates_df.columns:
        candidates_df['title'] = candidates_df['title'].apply(translate_project_name)
    
    return votes_df, candidates_df

def translate_project_name(name):
    """Translate project names to English"""
    project_translations = {
        # Add specific project name translations here as they appear in your data
        # For example:
        # "プロジェクト名1": "Project Name 1",
        # "プロジェクト名2": "Project Name 2",
        "ちばユースセンターPRISM": "Chiba Youth Center PRISM",
        "JINEN TRAVEL": "JINEN TRAVEL",  # Keep as is if already in English
        "ユースマンスプロジェクト": "Youth Month Project",
        "若者の参加を広げる会議": "Conference for Expanding Youth Participation",
        "学生と行政の協働プロジェクト": "Student-Administration Collaboration Project",
        "市民メディアラボ": "Citizen Media Lab",
        "青少年育成交流事業": "Youth Development Exchange Program"
    }
    
    return project_translations.get(name, name)  # Return original if no translation

def translate_text(text, translation_dict=None):
    """Translate text using the translation dictionary"""
    if translation_dict is None:
        translation_dict = get_translation_dict()
    
    return translation_dict.get(text, text)  # Return original if no translation

def analyze_credit_usage(votes_df, candidates_df):
    """クレジット使用状況を分析"""
    # 各投票者のクレジット使用状況を集計
    total_credits = 99  # 割り当てられた総クレジット
    voter_credit_usage = []

    for voter_id in votes_df['voter_id'].unique():
        voter_votes = []
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in votes_df.columns:
                # この投票者の該当列の値を取得（NaNの場合もある）
                vote_values = votes_df.loc[votes_df['voter_id'] == voter_id, col_name].values
                if len(vote_values) > 0 and not pd.isna(vote_values[0]):
                    # フィルター: 負の値は除外
                    if vote_values[0] >= 0:
                        voter_votes.append(vote_values[0])
        
        # 使用クレジット計算（票の二乗の合計）
        credits_used = sum([vote**2 for vote in voter_votes])
        remaining_credits = total_credits - credits_used
        
        voter_credit_usage.append({
            'voter_id': voter_id,
            'credits_used': credits_used,
            'usage_rate': credits_used / total_credits * 100,
            'remaining_credits': remaining_credits,
            'voted_projects': len(voter_votes),
            'unused_projects': len(candidates_df) - len(voter_votes)
        })

    # データフレームに変換
    credit_df = pd.DataFrame(voter_credit_usage)
    return credit_df

def analyze_potential_votes(credit_df, candidates_df):
    """残クレジットで追加投票可能だったケースを分析"""
    # 残クレジットで投票可能だったユーザーを特定
    potential_voters = []
    
    for _, voter in credit_df.iterrows():
        remaining_credits = voter['remaining_credits']
        
        # Here is the key change: ensure we have a valid number of unused projects
        # In this case, let's assume all projects are available for additional voting
        # If your actual data has unused_projects field that's valid, use that instead
        total_projects = len(candidates_df)
        unused_projects = total_projects  # We're assuming all projects could receive more votes
        
        # 残クレジットで可能な最大追加投票数（整数）
        max_additional_votes = int(remaining_credits ** 0.5)
        
        # 追加で投票できる最大プロジェクト数（未投票プロジェクト数と残クレジットで1点ずつ投票できる数の最小値）
        max_additional_projects = min(unused_projects, int(remaining_credits))
        
        # 残クレジットによる追加可能投票値のカテゴリ
        remaining_category = categorize_remaining_credits(remaining_credits)
        
        # 未投票プロジェクトがあり、かつ最低1票は投じられるケース
        if remaining_credits >= 1:
            potential_voters.append({
                'voter_id': voter['voter_id'],
                'remaining_credits': remaining_credits,
                'max_possible_additional_votes': max_additional_votes,
                'max_additional_projects': max_additional_projects,
                'unused_projects': unused_projects,
                'credits_used': voter['credits_used'],
                'usage_rate': voter['usage_rate'],
                'remaining_category': remaining_category
            })
        else:
            # 残クレジットが1未満だが、分析のために追加
            potential_voters.append({
                'voter_id': voter['voter_id'],
                'remaining_credits': remaining_credits,
                'max_possible_additional_votes': 0,
                'max_additional_projects': 0, 
                'unused_projects': unused_projects,
                'credits_used': voter['credits_used'],
                'usage_rate': voter['usage_rate'],
                'remaining_category': remaining_category
            })
    
    # データフレームに変換
    potential_df = pd.DataFrame(potential_voters)
    
    # 残クレジット範囲ごとの分析結果を計算
    remaining_analysis = analyze_remaining_credits_distribution(potential_df)
    
    return potential_df, remaining_analysis

def categorize_remaining_credits(remaining):
    """残クレジットをカテゴライズ"""
    if remaining < 1:
        return "0"
    elif remaining <= 4:
        return "1-4"
    elif remaining <= 7:
        return "5-7"
    elif remaining <= 9:
        return "8-9"
    else:
        return "10+"

def analyze_remaining_credits_distribution(potential_df):
    """残クレジットの分布を詳細に分析"""
    total_voters = len(potential_df)
    
    # 特定の残クレジット範囲の投票者数と割合
    remaining_1_9 = len(potential_df[(potential_df['remaining_credits'] >= 1) & (potential_df['remaining_credits'] <= 9)])
    remaining_1_9_pct = remaining_1_9 / total_voters * 100
    
    remaining_5_9 = len(potential_df[(potential_df['remaining_credits'] >= 5) & (potential_df['remaining_credits'] <= 9)])
    remaining_5_9_pct = remaining_5_9 / total_voters * 100
    
    remaining_8_9 = len(potential_df[(potential_df['remaining_credits'] >= 8) & (potential_df['remaining_credits'] <= 9)])
    remaining_8_9_pct = remaining_8_9 / total_voters * 100
    
    # カテゴリ別の分析
    categories = ["0", "1-4", "5-7", "8-9", "10+"]
    category_counts = potential_df['remaining_category'].value_counts().reindex(categories, fill_value=0)
    category_percentages = (category_counts / total_voters * 100).round(2)
    
    # カテゴリごとの理論的追加投票可能値
    category_vote_potential = {
        "0": "0票",
        "1-4": "1-2票",
        "5-7": "2-3票",
        "8-9": "3+票",
        "10+": "3+票"
    }
    
    # 残クレジット範囲ごとの詳細情報
    remaining_ranges = []
    for category in categories:
        remaining_ranges.append({
            'range': category,
            'count': int(category_counts[category]),
            'percentage': category_percentages[category],
            'potential_votes': category_vote_potential[category]
        })
    
    # 「意図的投票終了」の可能性がある投票者の割合
    # 定義: 5以上の残クレジットがありながら投票を終了した投票者
    intentional_termination = remaining_5_9_pct
    
    # 追加投票の選択肢が多いにも関わらず投票を終了した割合
    significant_options = remaining_8_9_pct
    
    return {
        'remaining_1_9': remaining_1_9,
        'remaining_1_9_pct': remaining_1_9_pct,
        'remaining_5_9': remaining_5_9,
        'remaining_5_9_pct': remaining_5_9_pct,
        'remaining_8_9': remaining_8_9,
        'remaining_8_9_pct': remaining_8_9_pct,
        'remaining_ranges': remaining_ranges,
        'intentional_termination': intentional_termination,
        'significant_options': significant_options
    }

def generate_visualizations(credit_df, potential_df, remaining_analysis):
    """分析結果の可視化"""
    # Get translation dictionary
    trans_dict = get_translation_dict()
    
    # 1. クレジット使用率の分布
    plt.figure(figsize=(10, 6))
    sns.histplot(credit_df['usage_rate'], bins=20, kde=True)
    plt.axvline(x=90, color='red', linestyle='--', label='90% Usage Rate')
    plt.title(translate_text('投票者のクレジット使用率分布', trans_dict))
    plt.xlabel(translate_text('使用率 (%)', trans_dict))
    plt.ylabel(translate_text('投票者数', trans_dict))
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/credit_usage_rate_distribution.png', dpi=300)
    plt.close()

    # 2. 残クレジットの分布
    plt.figure(figsize=(10, 6))
    sns.histplot(credit_df['remaining_credits'], bins=20, kde=True)
    plt.axvline(x=10, color='red', linestyle='--', label='10 Credits Remaining')
    plt.title(translate_text('投票者の残クレジット分布', trans_dict))
    plt.xlabel(translate_text('残クレジット', trans_dict))
    plt.ylabel(translate_text('投票者数', trans_dict))
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/remaining_credits_distribution.png', dpi=300)
    plt.close()

    # 3. 使用率と投票プロジェクト数の関係
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='usage_rate', y='voted_projects', data=credit_df)
    plt.title(translate_text('クレジット使用率と投票プロジェクト数の関係', trans_dict))
    plt.xlabel(translate_text('使用率 (%)', trans_dict))
    plt.ylabel(translate_text('投票したプロジェクト数', trans_dict))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/usage_rate_vs_projects.png', dpi=300)
    plt.close()

    # 4. 残クレジットと未投票プロジェクト数のヒートマップ（追加投票可能者）
    if not potential_df.empty:
        plt.figure(figsize=(10, 8))
        potential_pivot = pd.crosstab(
            pd.cut(potential_df['remaining_credits'], bins=[0, 5, 10, 20, 50, 100]), 
            potential_df['unused_projects']
        )
        sns.heatmap(potential_pivot, annot=True, fmt='d', cmap='YlGnBu')
        plt.title(translate_text('残クレジットと未投票プロジェクト数の関係（追加投票可能者）', trans_dict))
        plt.xlabel(translate_text('未投票プロジェクト数', trans_dict))
        plt.ylabel(translate_text('残クレジット', trans_dict))
        plt.tight_layout()
        plt.savefig(f'{output_dir}/remaining_vs_unused_heatmap.png', dpi=300)
        plt.close()

    # 5. 残クレジット範囲の分布
    plt.figure(figsize=(10, 6))
    categories = ["0", "1-4", "5-7", "8-9", "10+"]
    counts = [r['count'] for r in remaining_analysis['remaining_ranges']]
    percentages = [r['percentage'] for r in remaining_analysis['remaining_ranges']]
    
    ax = sns.barplot(x=categories, y=counts)
    
    # Add percentages on top of bars
    for i, p in enumerate(ax.patches):
        height = p.get_height()
        ax.text(p.get_x() + p.get_width()/2., height + 0.5,
                f'{percentages[i]:.1f}%', ha="center")
    
    plt.title(translate_text('残クレジット分布の詳細分析', trans_dict))
    plt.xlabel(translate_text('残クレジット範囲', trans_dict))
    plt.ylabel(translate_text('投票者数', trans_dict))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/remaining_credits_detailed.png', dpi=300)
    plt.close()
    
    # 6. 最大追加可能プロジェクト数の分布
    plt.figure(figsize=(12, 8))
    
    # Filter out voters who have no remaining credits or can't cast additional votes
    filtered_df = potential_df[potential_df['max_possible_additional_votes'] > 0]
    
    if not filtered_df.empty:
        # Create a cleaner histogram with fixed bins
        plt.hist(filtered_df['max_possible_additional_votes'], 
                 bins=range(1, 11),  # Fixed bins from 1 to 10
                 align='left',
                 rwidth=0.8,
                 color='steelblue')
        
        # Count number of voters for each value
        value_counts = filtered_df['max_possible_additional_votes'].value_counts().sort_index()
        total_voters = len(potential_df)
        
        # Add count and percentage labels on top of the bars
        for i, count in value_counts.items():
            percentage = (count / total_voters) * 100
            plt.text(i, count + 1, f'{count} ({percentage:.1f}%)', ha='center')
        
        plt.title(translate_text('追加投票可能な投票者割合の分析', trans_dict))
        plt.xlabel(translate_text('最大限追加可能な投票数', trans_dict))
        plt.ylabel(translate_text('投票者数', trans_dict))
        plt.xticks(range(1, 10))  # Force x-axis to show 1-9
        plt.xlim(0.5, 9.5)  # Set x-axis limits to center the bars
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/max_additional_projects_distribution.png', dpi=300)
        plt.close()

def generate_report(credit_df, potential_df, remaining_analysis):
    """分析結果のテキストレポート生成"""
    # Get translation dictionary
    trans_dict = get_translation_dict()
    
    # 統計情報の計算
    total_voters = len(credit_df)
    high_usage_voters = len(credit_df[credit_df['usage_rate'] >= 90])
    high_usage_percentage = high_usage_voters / total_voters * 100
    
    low_remaining_voters = len(credit_df[credit_df['remaining_credits'] <= 10])
    low_remaining_percentage = low_remaining_voters / total_voters * 100
    
    potential_voters_count = len(potential_df)
    potential_percentage = potential_voters_count / total_voters * 100 if total_voters > 0 else 0
    
    avg_usage_rate = credit_df['usage_rate'].mean()
    avg_remaining = credit_df['remaining_credits'].mean()
    
    # 相関分析
    correlation = credit_df[['usage_rate', 'voted_projects']].corr().iloc[0, 1]
    
    # レポート生成
    report = f"# {translate_text('クレジット使用率分析レポート', trans_dict)}\n\n"
    
    report += f"## {translate_text('基本統計情報', trans_dict)}\n\n"
    report += f"- {translate_text('総投票者数', trans_dict)}: {total_voters}\n"
    report += f"- {translate_text('平均クレジット使用率', trans_dict)}: {avg_usage_rate:.2f}%\n"
    report += f"- {translate_text('平均残クレジット', trans_dict)}: {avg_remaining:.2f}\n"
    report += f"- {translate_text('90%以上のクレジットを使用した投票者', trans_dict)}: {high_usage_voters} ({high_usage_percentage:.2f}%)\n"
    report += f"- {translate_text('残クレジットが10以下の投票者', trans_dict)}: {low_remaining_voters} ({low_remaining_percentage:.2f}%)\n\n"
    
    report += f"## {translate_text('追加投票可能性分析', trans_dict)}\n\n"
    report += f"- {translate_text('残クレジット1-9の投票者', trans_dict)}: {remaining_analysis['remaining_1_9']} ({remaining_analysis['remaining_1_9_pct']:.2f}%)\n"
    report += f"- {translate_text('残クレジット5-9の投票者', trans_dict)}: {remaining_analysis['remaining_5_9']} ({remaining_analysis['remaining_5_9_pct']:.2f}%)\n"
    report += f"- {translate_text('残クレジット8-9の投票者', trans_dict)}: {remaining_analysis['remaining_8_9']} ({remaining_analysis['remaining_8_9_pct']:.2f}%)\n\n"
    
    report += f"### {translate_text('残クレジット分布の詳細分析', trans_dict)}\n\n"
    report += f"| {translate_text('残クレジット範囲', trans_dict)} | {translate_text('投票者数', trans_dict)} | {translate_text('投票者割合', trans_dict)} | {translate_text('可能だった追加投票数', trans_dict)} |\n"
    report += "| --- | --- | --- | --- |\n"
    
    for r in remaining_analysis['remaining_ranges']:
        report += f"| {r['range']} | {r['count']} | {r['percentage']:.2f}% | {r['potential_votes']} |\n"
    
    report += f"\n### {translate_text('意図的投票終了の可能性', trans_dict)}\n\n"
    report += f"- {translate_text('追加投票の選択肢が有意にも関わらず投票を終了した割合', trans_dict)}: {remaining_analysis['significant_options']:.2f}%\n"
    
    if remaining_analysis['intentional_termination'] > 25:
        report += f"\n**注目ポイント**: 投票者の{remaining_analysis['intentional_termination']:.2f}%は5ポイント以上の残クレジットがあり、少なくとも2票以上の追加投票が可能だったにも関わらず投票を終了しています。これは「クレジットを使い切る」という行動より「適切に選好を表現する」という目標を優先していることを示唆しています。\n"
    
    # CSVファイルに結果を保存
    credit_df.to_csv(f'{output_dir}/voter_credit_usage.csv', index=False)
    if not potential_df.empty:
        potential_df.to_csv(f'{output_dir}/potential_additional_votes.csv', index=False)

    return report

def main():
    """メイン関数"""
    print(translate_text("クレジット使用率分析を開始..."))
    
    # データ読み込み
    votes_df, candidates_df = load_data()
    print(f"{translate_text('データ読み込み完了')}: {len(votes_df['voter_id'].unique())}{translate_text('名の投票者')}, {len(candidates_df)}{translate_text('件のプロジェクト')}")
    
    # クレジット使用状況の分析
    credit_df = analyze_credit_usage(votes_df, candidates_df)
    print(translate_text("クレジット使用状況の分析完了"))
    
    # 追加投票可能性の分析
    potential_df, remaining_analysis = analyze_potential_votes(credit_df, candidates_df)
    potential_count = len(potential_df[potential_df['max_possible_additional_votes'] > 0])
    print(f"{translate_text('追加投票可能性の分析完了')}: {potential_count}{translate_text('名が追加投票可能だった')}")
    
    # 可視化
    generate_visualizations(credit_df, potential_df, remaining_analysis)
    print(translate_text("可視化グラフの生成完了"))
    
    # レポート生成
    report = generate_report(credit_df, potential_df, remaining_analysis)
    with open(f"{output_dir}/credit_usage_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(translate_text("分析レポートの生成完了"))
    
    print(f"{translate_text('すべての結果は')} {output_dir} {translate_text('ディレクトリに保存されました')}")

if __name__ == "__main__":
    main() 