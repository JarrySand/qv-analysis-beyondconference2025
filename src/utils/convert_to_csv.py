import json
import csv
import os
import pandas as pd

# 候補者情報を取得するための関数
def get_project_names_mapping():
    try:
        # 既存のcandidates.csvがある場合は読み込む
        existing_candidates = pd.read_csv('data/candidates.csv')
        # 日本語名→英語名の変換辞書を作成
        if 'title_en' in existing_candidates.columns:
            mapping = dict(zip(existing_candidates['title'], existing_candidates['title_en']))
            print("既存のcandidates.csvから英語名マッピングを読み込みました")
            return mapping
    except Exception as e:
        print(f"既存のcandidates.csvからの読み込みに失敗しました: {e}")
    
    # 既存のファイルがない場合またはエラーが発生した場合はデフォルトのマッピングを使用
    default_mapping = {
        '10代・20代の「いま、やりたい」を後押しする拠点　ちばユースセンターPRISM': 'Chiba Youth Center PRISM',
        'ちばユースセンターPRISM': 'Chiba Youth Center PRISM',
        '政を祭に変える #vote_forプロジェクト': '#vote_for Project',
        '#vote_forプロジェクト': '#vote_for Project',
        '淡路島クエストカレッジ': 'Awaji Island Quest College',
        'イナトリアートセンター計画': 'Inatori Art Center Plan',
        'JINEN TRAVEL': 'JINEN TRAVEL',
        'ビオ田んぼプロジェクト': 'Bio Rice Field Project',
        'パラ旅応援団': 'Para Travel Support Team'
    }
    print("デフォルトの英語名マッピングを使用します")
    return default_mapping

# 日英プロジェクト名変換辞書を取得
project_names = get_project_names_mapping()

# JSONファイルを読み込む
with open('data/election.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 候補者情報の抽出と英語名への変換
candidates = data['candidates']
candidate_titles = []
english_titles = []

for c in candidates:
    title = c['title']
    candidate_titles.append(title)
    # 英語名に変換（変換辞書に存在しない場合は元の名前を使用）
    english_title = project_names.get(title, title)
    english_titles.append(english_title)
    # JSONデータ内のタイトルを英語に更新
    c['title_en'] = english_title

# 投票データの出力 - 行ごとの投票データ
with open('data/votes.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
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

# 候補者情報の出力（英語名を含む）
with open('data/candidates.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['candidate_id', 'title', 'title_en', 'description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for i, candidate in enumerate(candidates):
        writer.writerow({
            'candidate_id': i,
            'title': candidate['title'],
            'title_en': candidate['title_en'],
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

# 集計結果の出力（英語名を使用）
with open('data/vote_summary.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['candidate_id', 'title', 'title_en', 'total_votes', 'vote_count', 'average_vote']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for i in range(len(candidates)):
        avg_vote = vote_totals[i] / vote_counts[i] if vote_counts[i] > 0 else 0
        writer.writerow({
            'candidate_id': i,
            'title': candidate_titles[i],
            'title_en': english_titles[i],
            'total_votes': vote_totals[i],
            'vote_count': vote_counts[i],
            'average_vote': round(avg_vote, 2)
        })

# 英語変換マッピングファイルを作成
with open('data/project_name_mapping.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['japanese_name', 'english_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for jp, en in project_names.items():
        if jp != en:  # 既に英語の場合は除外
            writer.writerow({
                'japanese_name': jp,
                'english_name': en
            })

print("CSVファイルの作成が完了しました。")
print(f"- data/votes.csv: 個別の投票データ")
print(f"- data/candidates.csv: 候補者情報（英語名を含む）")
print(f"- data/vote_summary.csv: 投票の集計結果（英語名を含む）")
print(f"- data/project_name_mapping.csv: プロジェクト名の日英対応表")
print("\n候補者名変更が必要な場合は、data/candidates.csvを編集してから再度このスクリプトを実行してください。") 