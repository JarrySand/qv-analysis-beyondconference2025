import pandas as pd
import numpy as np

# データの読み込み
votes = pd.read_csv('votes.csv')

# 各投票者の最大投票ポイントを特定
max_votes = {}
buried_voices = {i: 0 for i in range(7)}  # 7つの候補者に対応
strong_votes_count = {i: 0 for i in range(7)}  # 4以上の投票を受けた数
max_votes_count = {i: 0 for i in range(7)}  # 最大投票として受けた数

for _, voter_row in votes.iterrows():
    max_vote = 0
    max_candidate = None
    
    # 各候補への投票を確認
    for i in range(7):
        col_name = f'candidate_{i}'
        if col_name in voter_row and not pd.isna(voter_row[col_name]):
            vote_value = voter_row[col_name]
            
            # 4以上の票を集計
            if vote_value >= 4:
                strong_votes_count[i] += 1
            
            # 最大投票の更新
            if vote_value > max_vote:
                max_vote = vote_value
                max_candidate = i
    
    # この投票者の最大投票を記録
    if max_candidate is not None:
        max_votes_count[max_candidate] += 1

# 各候補に対する強い投票で、最大投票ではないものを計算
for _, voter_row in votes.iterrows():
    max_vote = 0
    max_candidate = None
    
    # まず最大投票を特定
    for i in range(7):
        col_name = f'candidate_{i}'
        if col_name in voter_row and not pd.isna(voter_row[col_name]):
            vote_value = voter_row[col_name]
            if vote_value > max_vote:
                max_vote = vote_value
                max_candidate = i
    
    # 埋もれた声を計算
    for i in range(7):
        col_name = f'candidate_{i}'
        if col_name in voter_row and not pd.isna(voter_row[col_name]):
            vote_value = voter_row[col_name]
            if vote_value >= 4 and i != max_candidate:
                buried_voices[i] += 1

print('候補別の強い投票（4以上）の数:')
for i in range(7):
    print(f'候補{i}: {strong_votes_count[i]}票')

print('\n候補別の最大投票として受けた数:')
for i in range(7):
    print(f'候補{i}: {max_votes_count[i]}票')

print('\n候補別の埋もれた声の数:')
for i in range(7):
    print(f'候補{i}: {buried_voices[i]}票')

# 特に候補0（#vote_forプロジェクト）についての詳細な分析
votes_for_candidate0 = []
for _, voter_row in votes.iterrows():
    if 'candidate_0' in voter_row and not pd.isna(voter_row['candidate_0']):
        votes_for_candidate0.append(voter_row['candidate_0'])

print(f'\n#vote_forプロジェクトへの投票分布:')
unique, counts = np.unique(votes_for_candidate0, return_counts=True)
for val, count in zip(unique, counts):
    print(f'{val}票: {count}人')

# 候補0に4以上の票を入れた人で、他の候補に最大票を入れた人の数を確認
candidate0_strong_but_other_max = 0
for _, voter_row in votes.iterrows():
    if 'candidate_0' in voter_row and not pd.isna(voter_row['candidate_0']):
        vote_value = voter_row['candidate_0']
        if vote_value >= 4:
            # 最大投票を特定
            max_vote = vote_value
            max_candidate = 0
            for i in range(1, 7):
                col_name = f'candidate_{i}'
                if col_name in voter_row and not pd.isna(voter_row[col_name]):
                    if voter_row[col_name] > max_vote:
                        max_vote = voter_row[col_name]
                        max_candidate = i
            
            if max_candidate != 0:
                candidate0_strong_but_other_max += 1
                
print(f'\n#vote_forプロジェクトに4以上の票を入れたが他の候補に最大票を入れた人: {candidate0_strong_but_other_max}人') 