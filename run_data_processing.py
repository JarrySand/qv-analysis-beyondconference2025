#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QV分析のデータ処理部分のみを実行するスクリプト
候補者名の変更と各種CSVデータの変換を行います
"""

import os
import subprocess
import time
import sys

def run_script(script_path, description):
    """
    Pythonスクリプトを実行し、結果を表示する
    
    Parameters:
    -----------
    script_path : str
        実行するスクリプトへのパス
    description : str
        実行するスクリプトの説明
    """
    print(f"\n{'='*80}")
    print(f"実行: {description}")
    print(f"スクリプト: {script_path}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    
    try:
        # スクリプト実行（標準出力と標準エラー出力を表示）
        process = subprocess.Popen([sys.executable, script_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
        
        # リアルタイム出力
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        # エラー出力があれば表示
        stderr = process.stderr.read()
        if stderr:
            print(f"エラー出力:\n{stderr}")
        
        # 終了コード確認
        return_code = process.poll()
        if return_code == 0:
            elapsed_time = time.time() - start_time
            print(f"\n✅ 正常終了 ({elapsed_time:.2f}秒)")
            return True
        else:
            print(f"\n❌ エラー終了 (コード: {return_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ 実行エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("\n📄 QV分析のデータ処理を開始します 📄\n")
    
    # データ処理スクリプト
    data_script = "src/utils/convert_to_csv.py"
    
    if os.path.exists(data_script):
        success = run_script(data_script, "データ変換（JSONからCSV形式へ）")
        
        if success:
            print("\n🔍 データ変換結果の確認")
            
            # CSVファイルの存在確認
            csv_files = [
                "data/candidates.csv", 
                "data/votes.csv", 
                "data/vote_summary.csv", 
                "data/project_name_mapping.csv"
            ]
            
            all_exists = True
            for file_path in csv_files:
                if os.path.exists(file_path):
                    print(f"✅ {file_path} が正常に生成されました")
                else:
                    print(f"❌ {file_path} が見つかりません")
                    all_exists = False
            
            if all_exists:
                print("\n🎉 データ処理が正常に完了しました！")
                print("次のステップ: run_all_analysis.py を実行して分析を行うことができます。")
            else:
                print("\n⚠️ 一部のCSVファイルが見つかりません。ログを確認してください。")
        else:
            print("\n⚠️ データ変換に失敗しました。ログを確認してください。")
    else:
        print(f"\n⚠️ スクリプトが見つかりません: {data_script}")

if __name__ == "__main__":
    main() 