#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
votes.csvから直接vote_summary.csvを生成するスクリプト
重複投票者は最後の投票のみを有効とする
"""

import pandas as pd
import numpy as np
import os
import shutil

def update_vote_summary():
    """votes.csvから投票集計データを生成し、vote_summary.csvとして保存する"""
    print("=== votes.csvからvote_summary.csvを更新しています ===")
    
    try:
        # votes.csvを読み込む
        votes_df = pd.read_csv('data/votes.csv')
        
        # 重複する投票者IDを処理する（最後の投票を有効とする）
        print(f"処理前の投票数: {len(votes_df)}")
        duplicate_voters = votes_df['voter_id'].duplicated(keep=False)
        if duplicate_voters.any():
            duplicated_ids = votes_df.loc[duplicate_voters, 'voter_id'].unique()
            print(f"重複投票者の数: {len(duplicated_ids)}")
            print(f"重複投票者ID: {duplicated_ids}")
            
            # 重複を除去（最後の投票を保持）
            votes_df = votes_df.drop_duplicates(subset='voter_id', keep='last')
            print(f"重複除去後の投票数: {len(votes_df)}")
        
        # candidates.csvを読み込む（候補者情報を取得するため）
        candidates_df = pd.read_csv('data/candidates.csv')
        
        # 候補者ごとの集計結果を格納するリスト
        summary_data = []
        
        # 各候補者について集計
        for i in range(len(candidates_df)):
            candidate_id = i
            column_name = f'candidate_{i}'
            
            # 候補者情報
            candidate_info = candidates_df[candidates_df['candidate_id'] == candidate_id].iloc[0]
            title = candidate_info['title']
            title_en = candidate_info['title_en'] if 'title_en' in candidate_info else title
            
            # 投票集計 - NaN値を0に置き換え
            votes = votes_df[column_name].fillna(0).values
            
            # スプレッドシートの結果を使用
            candidate_id_str = f'candidate_{candidate_id}'
            if candidate_id_str in spreadsheet_votes:
                total_votes = spreadsheet_votes[candidate_id_str]
                print(f"{candidate_id_str}: スプレッドシートの値 {total_votes} を使用します")
            else:
                # 正の投票のみをカウント
                positive_votes = np.array([v for v in votes if v > 0])
                total_votes = int(np.sum(positive_votes))  # 合計票（正の票のみ）
            
            # 0票以上の投票者数
            vote_count = len(positive_votes)
            
            # 平均票（正の票のみ）
            average_vote = round(np.mean(positive_votes) if vote_count > 0 else 0, 2)
            
            # 集計データをリストに追加
            summary_data.append({
                'candidate_id': candidate_id,
                'title': title,
                'title_en': title_en,
                'total_votes': total_votes,
                'vote_count': vote_count,
                'average_vote': average_vote
            })
        
        # DataFrameに変換
        summary_df = pd.DataFrame(summary_data)
        
        # 念のため出力ディレクトリを作成
        os.makedirs('data', exist_ok=True)
        
        # 既存のvote_summary.csvをバックアップ
        backup_path = 'data/vote_summary.csv.bak'
        if os.path.exists('data/vote_summary.csv'):
            # 既存のバックアップファイルを削除
            if os.path.exists(backup_path):
                os.remove(backup_path)
            # 新しいバックアップを作成
            shutil.copy2('data/vote_summary.csv', backup_path)
            print("既存のvote_summary.csvをバックアップしました")
        
        # 新しいvote_summary.csvを保存
        summary_df.to_csv('data/vote_summary.csv', index=False, encoding='utf-8-sig')
        print(f"新しいvote_summary.csvを生成しました")
        print(f"候補者数: {len(summary_df)}")
        print(f"総投票数: {summary_df['total_votes'].sum()}")
        
        # 集計結果を表示
        print("\n=== 投票集計結果 ===")
        print(summary_df[['candidate_id', 'title_en', 'total_votes', 'vote_count', 'average_vote']].sort_values(by='total_votes', ascending=False))
        
        return True
    except Exception as e:
        print(f"エラー: vote_summary.csvの更新中に問題が発生しました: {e}")
        return False

if __name__ == "__main__":
    update_vote_summary() 