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
import argparse
import threading
import gc
import platform

# タイムアウト処理用関数
def kill_process(process, script_path):
    """指定時間後にプロセスを強制終了する"""
    print(f"\n[タイムアウト] スクリプトの実行時間が長すぎます: {script_path}")
    if platform.system() == "Windows":
        # Windowsでは子プロセスも含めて強制終了
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
    else:
        process.kill()

def run_script(script_path, description, timeout=600):
    """
    Pythonスクリプトを実行し、結果を表示する
    
    Parameters:
    -----------
    script_path : str
        実行するスクリプトへのパス
    description : str
        実行するスクリプトの説明
    timeout : int
        スクリプト実行のタイムアウト（秒）
    """
    print(f"\n{'='*80}")
    print(f"実行: {description}")
    print(f"スクリプト: {script_path}")
    print(f"タイムアウト: {timeout}秒")
    print(f"{'='*80}\n")
    
    # スクリプトが存在するかチェック
    if not os.path.exists(script_path):
        print(f"[エラー] スクリプトが見つかりません: {script_path}")
        return False
    
    # 実行前にメモリを解放
    gc.collect()
    
    start_time = time.time()
    
    try:
        print(f"[デバッグ] スクリプト実行開始: {script_path}")
        
        # 環境変数を設定
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'  # 出力エンコーディングを確実にUTF-8に
        env['PYTHONLEGACYWINDOWSSTDIO'] = '1'  # Windowsでの標準入出力のUTF-8処理を強制
        env['PYTHONUTF8'] = '1'  # UTF-8モードを有効化
        
        # スクリプト実行（標準出力と標準エラー出力を表示）
        process = subprocess.Popen([sys.executable, "-X", "utf8", script_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True,
                                  cwd=os.path.dirname(os.path.abspath(__file__)),  # ワーキングディレクトリを確実に設定
                                  env=env,
                                  encoding='utf-8',    # 明示的にUTF-8エンコーディングを指定
                                  errors='replace')    # デコードエラー時に文字を置換
        
        # タイムアウト処理を設定
        timer = threading.Timer(timeout, kill_process, [process, script_path])
        timer.start()
        
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
        
        # タイマーを停止
        timer.cancel()
        
        # 終了コード確認
        return_code = process.poll()
        print(f"[デバッグ] スクリプト終了: {script_path}, リターンコード: {return_code}")
        if return_code == 0:
            elapsed_time = time.time() - start_time
            print(f"\n[成功] 正常終了 ({elapsed_time:.2f}秒)")
            return True
        else:
            print(f"\n[エラー] 終了コード: {return_code}")
            return False
            
    except Exception as e:
        print(f"\n[エラー] 実行エラー: {e}")
        return False
    finally:
        # 実行後にメモリを解放
        gc.collect()

def main():
    """メイン処理"""
    # コマンドライン引数の処理
    parser = argparse.ArgumentParser(description='QV分析の全プロセスを実行するスクリプト')
    parser.add_argument('--script', '-s', help='実行する特定のスクリプト (例: src/analysis/analyze_votes.py)')
    parser.add_argument('--timeout', '-t', type=int, default=600, help='スクリプト実行のタイムアウト秒数 (デフォルト: 600秒)')
    parser.add_argument('--continue-on-error', '-c', action='store_true', help='エラーが発生しても続行する')
    args = parser.parse_args()
    
    # 実行前の準備：必要なディレクトリの存在確認と作成
    required_dirs = [
        'results',
        'results/data',
        'results/figures',
        'results/figures/basic_analysis',
        'results/figures/neutral_bias',
        'results/figures/comparison',
        'results/reports'
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"[準備] ディレクトリを作成しています: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    # スクリプト実行順序と説明を定義
    # 依存関係を考慮して最適化した順序
    scripts = [
        # 0. votes.csvからvote_summary.csvを更新（追加）
        ("src/utils/update_vote_summary.py", "votes.csvからvote_summary.csvを更新"),
        
        # convert_to_csv.pyの実行は削除（手動でデータを用意する方式に変更）
        
        # 2. 基本分析（他の分析の前提となるもの）
        ("src/analysis/analyze_votes.py", "基本投票分析"),
        
        # 3. 基本的な可視化と分析（依存性が低いもの）
        ("src/analysis/generate_statistics.py", "投票統計分析"),
        ("src/analysis/vote_distribution_analyzer.py", "投票分布分析"),
        
        # 4. 埋もれた声関連の分析（基本分析後に実行）
        ("src/analysis/buried_voices_visualizer.py", "埋もれた声の可視化"),
        ("src/analysis/buried_voices_analyzer.py", "埋もれた声の詳細分析"),
        ("src/analysis/buried_voices_probabilistic.py", "埋もれた声の確率論的分析"),
        
        # 5. 比較分析（基本分析とデータ変換に依存）
        ("src/analysis/compare_voting_methods.py", "投票方法の比較"),
        
        # 6. 感度分析（他の分析結果を利用する可能性があるため後半に配置）
        ("src/analysis/sensitivity_analysis.py", "感度分析"),
        
        # 7. 追加の詳細分析（最後に実行）
        ("src/simulation/neutral_bias/analyze_credit_usage.py", "クレジット使用率分析"),
        ("src/simulation/neutral_bias/identify_voting_patterns.py", "投票パターンの特定とクラスタリング"),
        ("src/simulation/neutral_bias/analyze_vote_patterns.py", "投票パターンの詳細分析"),
        ("src/simulation/neutral_bias/simulate_utility_max_model.py", "効用最大化モデル分析", 900),  # 長時間実行のため15分に設定
    ]
    
    # 特定のスクリプトのみ実行する場合
    if args.script:
        if os.path.exists(args.script):
            # 該当するスクリプトの説明とタイムアウトを検索
            description = "指定スクリプト"
            timeout = args.timeout
            for script_info in scripts:
                if len(script_info) == 3:
                    script_path, desc, custom_timeout = script_info
                    if script_path == args.script:
                        description = desc
                        timeout = custom_timeout
                        break
                else:
                    script_path, desc = script_info
                    if script_path == args.script:
                        description = desc
                        break
            
            success = run_script(args.script, description, timeout)
            print(f"\n実行結果: {'成功' if success else '失敗'}")
            return
        else:
            print(f"\n[エラー] 指定されたスクリプトが見つかりません: {args.script}")
            return
    
    # 全スクリプト実行モード
    print("\n[開始] QV分析の全プロセスを開始します\n")
    print(f"[環境情報] Python: {sys.version}")
    print(f"[環境情報] 実行ディレクトリ: {os.getcwd()}")
    print(f"[環境情報] スクリプト実行タイムアウト: {args.timeout}秒")
    print(f"[環境情報] エラー時の動作: {'続行' if args.continue_on_error else '中断'}")
    
    # 各スクリプトの実行
    results = []
    for script_info in scripts:
        if len(script_info) == 3:
            script_path, description, custom_timeout = script_info
            timeout = custom_timeout
        else:
            script_path, description = script_info
            timeout = args.timeout
            
        if os.path.exists(script_path):
            success = run_script(script_path, description, timeout)
            results.append((script_path, description, success))
            
            # エラーが発生し、続行フラグがない場合は処理を中断
            if not success and not args.continue_on_error:
                print(f"\n[中断] エラーが発生したため処理を中断します: {script_path}")
                break
        else:
            print(f"\n[警告] スクリプトが見つかりません: {script_path}")
            results.append((script_path, description, False))
    
    # 結果サマリーを表示
    print("\n\n" + "="*80)
    print("[サマリー] 実行結果サマリー")
    print("="*80)
    
    all_success = True
    success_count = 0
    for script_path, description, success in results:
        status = "[成功]" if success else "[失敗]"
        print(f"{status} - {description} ({script_path})")
        if success:
            success_count += 1
        else:
            all_success = False
    
    if all_success:
        print("\n[完了] すべての分析が正常に完了しました！")
        print("結果は results ディレクトリに保存されています。")
    else:
        print(f"\n[警告] 一部の分析が失敗しました。({success_count}/{len(results)} 成功)")
        print("失敗したスクリプトは個別に実行してみてください。")
        print("または --continue-on-error オプションを付けて再実行することも可能です。")

if __name__ == "__main__":
    main() 