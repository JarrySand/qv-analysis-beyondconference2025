import json

# JSONファイルを読み込む
with open('election.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 全ての投票データの数
total_votes = len(data["votes"])

# ユニークな投票者IDの数
unique_voter_ids = set([vote["voter"] for vote in data["votes"]])
total_unique_voters = len(unique_voter_ids)

print(f"Total votes array length: {total_votes}")
print(f"Total unique voter IDs: {total_unique_voters}")

# votes.csvのユニークな投票者IDも確認
import pandas as pd
votes_df = pd.read_csv('votes.csv')
csv_unique_voters = len(votes_df['voter_id'].unique())
print(f"Unique voter IDs in votes.csv: {csv_unique_voters}")

# 重複投票者のチェック
voter_counts = {}
for vote in data["votes"]:
    voter_id = vote["voter"]
    if voter_id in voter_counts:
        voter_counts[voter_id] += 1
    else:
        voter_counts[voter_id] = 1

# 複数回投票したユーザーを表示
duplicate_voters = {voter: count for voter, count in voter_counts.items() if count > 1}
if duplicate_voters:
    print("\nVoters who voted multiple times:")
    for voter, count in duplicate_voters.items():
        print(f"Voter ID: {voter}, Vote count: {count}") 