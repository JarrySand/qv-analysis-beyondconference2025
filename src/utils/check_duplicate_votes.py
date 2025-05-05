import json
import pandas as pd

# JSONファイルを読み込む
with open('election.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 重複投票者のチェック
voter_counts = {}
for vote in data["votes"]:
    voter_id = vote["voter"]
    if voter_id in voter_counts:
        voter_counts[voter_id] += 1
    else:
        voter_counts[voter_id] = 1

# 複数回投票したユーザーを特定
duplicate_voters = {voter: count for voter, count in voter_counts.items() if count > 1}

# 重複投票者の各投票データの詳細を表示
if duplicate_voters:
    print("===== 重複投票の詳細 =====")
    for voter_id, count in duplicate_voters.items():
        print(f"\nVoter ID: {voter_id}, 投票回数: {count}")
        
        # この投票者の全投票データを取得
        voter_votes = [vote for vote in data["votes"] if vote["voter"] == voter_id]
        
        for i, vote in enumerate(voter_votes, 1):
            print(f"  投票 {i}:")
            print(f"    Vote ID: {vote['id']}")
            
            # 各候補への投票を表示
            print("    投票内容:")
            for v in vote["votes"]:
                candidate_idx = v["candidate"]
                candidate_name = data["candidates"][candidate_idx]["title"]
                vote_value = v["vote"]
                print(f"      候補 {candidate_idx} ({candidate_name}): {vote_value}点")
                
    print("\n===== 重複投票パターンの分析 =====")
    
    # votes.csvからの検証（変換後のデータ）
    votes_df = pd.read_csv('votes.csv')
    candidates_df = pd.read_csv('candidates.csv')
    
    for voter_id in duplicate_voters.keys():
        voter_rows = votes_df[votes_df['voter_id'] == voter_id]
        print(f"\nVoter ID: {voter_id}, CSV内の行数: {len(voter_rows)}")
        
        if len(voter_rows) == 1:
            print("  注意: JSONには複数投票がありますが、CSVでは1行のみ存在します。")
        
        # 各行の投票内容を表示
        for idx, row in voter_rows.iterrows():
            print(f"  Vote ID: {row['vote_id']}")
            for i in range(len(candidates_df)):
                col_name = f'candidate_{i}'
                if col_name in row:
                    vote_value = row[col_name]
                    if not pd.isna(vote_value):
                        candidate_name = candidates_df.iloc[i]['title']
                        print(f"    候補 {i} ({candidate_name}): {vote_value}点") 