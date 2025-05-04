#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QV分析の全プロセスを一括実行するスクリプト
データ処理スクリプトから順に、すべての分析スクリプトを実行します
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
    print("\n📊 QV分析の全プロセスを開始します 📊\n")
    
    # スクリプト実行順序と説明を定義
    scripts = [
        # 1. データ処理
        ("src/utils/convert_to_csv.py", "データ変換 (JSONからCSV形式へ)"),
        
        # 2. 基本分析
        ("src/analysis/analyze_votes.py", "基本投票分析"),
        ("src/analysis/buried_voices_visualizer.py", "埋もれた声の可視化"),
        
        # 3. 高度な分析
        ("src/analysis/generate_statistics.py", "投票統計分析"),
        ("src/analysis/buried_voices_probabilistic.py", "埋もれた声の確率論的分析"),
        ("src/analysis/compare_voting_methods.py", "投票方法の比較"),
        ("src/analysis/vote_distribution_analyzer.py", "投票分布分析"),
        ("src/analysis/buried_voices_analyzer.py", "埋もれた声の詳細分析"),
        
        # 4. 追加分析
        ("src/analysis/sensitivity_analysis.py", "感度分析")
    ]
    
    # 各スクリプトの実行
    results = []
    for script_path, description in scripts:
        if os.path.exists(script_path):
            success = run_script(script_path, description)
            results.append((script_path, description, success))
        else:
            print(f"\n⚠️ スクリプトが見つかりません: {script_path}")
            results.append((script_path, description, False))
    
    # 結果サマリーを表示
    print("\n\n" + "="*80)
    print("📋 実行結果サマリー")
    print("="*80)
    
    all_success = True
    for script_path, description, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{status} - {description} ({script_path})")
        if not success:
            all_success = False
    
    if all_success:
        print("\n🎉 すべての分析が正常に完了しました！")
        print("結果は results ディレクトリに保存されています。")
    else:
        print("\n⚠️ 一部の分析が失敗しました。ログを確認してください。")

if __name__ == "__main__":
    main() 