import json
import csv
import os

# JSONファイルを読み込む
with open('election.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 候補者情報の抽出
candidates = data['candidates']
candidate_titles = [c['title'] for c in candidates]

# 投票データの出力 - 行ごとの投票データ
with open('votes.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['voter_id', 'vote_id'] + [f'candidate_{i}' for i in range(len(candidates))]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for vote in data['votes']:
        row = {
            'voter_id': vote['voter'],
            'vote_id': vote['id']
        }
        
        for v in vote['votes']:
            candidate_idx = v['candidate']
            row[f'candidate_{candidate_idx}'] = v['vote']
        
        writer.writerow(row)

# 候補者情報の出力
with open('candidates.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['candidate_id', 'title', 'description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for i, candidate in enumerate(candidates):
        writer.writerow({
            'candidate_id': i,
            'title': candidate['title'],
            'description': candidate['description']
        })

# 各候補に対する合計得票数を計算
vote_totals = {}
vote_counts = {}
for i in range(len(candidates)):
    vote_totals[i] = 0
    vote_counts[i] = 0

for vote in data['votes']:
    for v in vote['votes']:
        candidate_idx = v['candidate']
        vote_value = v['vote']
        
        if vote_value > 0:  # 正の票のみカウント
            vote_totals[candidate_idx] += vote_value
            vote_counts[candidate_idx] += 1

# 集計結果の出力
with open('vote_summary.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['candidate_id', 'title', 'total_votes', 'vote_count', 'average_vote']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for i in range(len(candidates)):
        avg_vote = vote_totals[i] / vote_counts[i] if vote_counts[i] > 0 else 0
        writer.writerow({
            'candidate_id': i,
            'title': candidate_titles[i],
            'total_votes': vote_totals[i],
            'vote_count': vote_counts[i],
            'average_vote': round(avg_vote, 2)
        })

print("CSVファイルの作成が完了しました。")
print(f"- votes.csv: 個別の投票データ")
print(f"- candidates.csv: 候補者情報")
print(f"- vote_summary.csv: 投票の集計結果") 