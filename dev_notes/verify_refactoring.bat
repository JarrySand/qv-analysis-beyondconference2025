@echo off
echo ===== リファクタリング検証開始 =====
echo.

echo --- データディレクトリの確認 ---
if not exist data mkdir data
if not exist results mkdir results
if not exist results\figures mkdir results\figures
if not exist results\figures\basic_analysis mkdir results\figures\basic_analysis
if not exist results\data mkdir results\data

echo.
echo --- 基本解析スクリプトのテスト実行 ---
python src/analysis/vote_distribution_analyzer.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: vote_distribution_analyzer.pyの実行に失敗しました。
    exit /b %ERRORLEVEL%
)

echo.
echo --- 埋もれた声分析の実行 ---
python src/analysis/buried_voices_analyzer.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: buried_voices_analyzer.pyの実行に失敗しました。
    exit /b %ERRORLEVEL%
)

echo.
echo --- 投票方法比較の実行 ---
python src/analysis/compare_voting_methods.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: compare_voting_methods.pyの実行に失敗しました。
    exit /b %ERRORLEVEL%
)

echo.
echo --- 中立バイアスシミュレーションの実行 ---
python src/simulation/neutral_bias/identify_voting_patterns.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: identify_voting_patterns.pyの実行に失敗しました。
    exit /b %ERRORLEVEL%
)

echo.
echo --- 非バイアス投票シミュレーションの実行 ---
python src/simulation/comparison/simulate_unbiased_voting.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: simulate_unbiased_voting.pyの実行に失敗しました。
    exit /b %ERRORLEVEL%
)

echo.
echo ===== リファクタリング検証完了 =====
echo 全てのスクリプトが正常に実行されました。
echo 結果ファイルは results ディレクトリに保存されています。

echo.
echo ディレクトリ内のファイル一覧:
dir /b results\figures\basic_analysis
echo.
echo データファイル:
dir /b results\data 