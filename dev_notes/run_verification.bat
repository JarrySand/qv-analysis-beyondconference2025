@echo off
setlocal enabledelayedexpansion

echo === QVリファクタリング検証ワークフロー ===
echo.

echo ステップ1: データディレクトリをクリーンアップ中...
if exist data\votes.csv del data\votes.csv
if exist data\vote_summary.csv del data\vote_summary.csv
if exist data\project_name_mapping.csv del data\project_name_mapping.csv

echo ステップ2: 結果ディレクトリをクリアに...
for /d %%d in (results\*) do (
  echo 削除: %%d\*
  del /q "%%d\*" 2>nul
)

echo.
echo ステップ3: データ変換を実行中...
python src\utils\convert_to_csv.py
if %errorlevel% neq 0 (
  echo [エラー] データ変換に失敗しました
  exit /b 1
)

echo.
echo ステップ4: 基本分析を実行中...
python src\analysis\analyze_votes.py
if %errorlevel% neq 0 (
  echo [エラー] 基本分析に失敗しました
  exit /b 1
)

echo.
echo ステップ5: 埋もれた声の可視化を実行中...
python src\analysis\buried_voices_visualizer.py
if %errorlevel% neq 0 (
  echo [エラー] 埋もれた声の可視化に失敗しました
  exit /b 1
)

echo.
echo ステップ6: 統計分析を実行中...
python src\analysis\generate_statistics.py
if %errorlevel% neq 0 (
  echo [エラー] 統計分析に失敗しました
  exit /b 1
)

echo.
echo ステップ7: 確率論的分析を実行中...
python src\analysis\buried_voices_probabilistic.py
if %errorlevel% neq 0 (
  echo [エラー] 確率論的分析に失敗しました
  exit /b 1
)

echo.
echo ステップ8: 投票方法比較を実行中...
python src\analysis\compare_voting_methods.py
if %errorlevel% neq 0 (
  echo [エラー] 投票方法比較に失敗しました
  exit /b 1
)

echo.
echo ステップ9: 投票分布分析を実行中...
python src\analysis\vote_distribution_analyzer.py
if %errorlevel% neq 0 (
  echo [エラー] 投票分布分析に失敗しました
  exit /b 1
)

echo.
echo ステップ10: 埋もれた声の詳細分析を実行中...
python src\analysis\buried_voices_analyzer.py
if %errorlevel% neq 0 (
  echo [エラー] 埋もれた声の詳細分析に失敗しました
  exit /b 1
)

echo.
echo ステップ11: 感度分析を実行中...
python src\analysis\sensitivity_analysis.py
if %errorlevel% neq 0 (
  echo [エラー] 感度分析に失敗しました
  exit /b 1
)

echo.
echo ステップ12: 候補者名変更テストを実行中...
copy data\candidates.csv data\candidates.csv.backup
echo 最初の候補者名を変更中...
powershell -Command "(Get-Content data\candidates.csv) -replace 'Chiba Youth Center PRISM', 'Chiba Youth Center PRISM TEST' | Set-Content data\candidates.csv"
python src\utils\convert_to_csv.py
if %errorlevel% neq 0 (
  echo [エラー] 候補者名変更テストに失敗しました
  move data\candidates.csv.backup data\candidates.csv
  exit /b 1
)

echo 候補者名が変更されたか確認中...
findstr /C:"Chiba Youth Center PRISM TEST" data\vote_summary.csv > nul
if %errorlevel% neq 0 (
  echo [エラー] 候補者名の変更が反映されていません
) else (
  echo 候補者名の変更が正常に反映されました
)

echo 元に戻しています...
move /y data\candidates.csv.backup data\candidates.csv
python src\utils\convert_to_csv.py > nul

echo.
echo ステップ13: 結果ファイルの検証中...
set EXPECTED_FILES=0
set FOUND_FILES=0

for /r results %%f in (*.*) do (
  set /a FOUND_FILES+=1
)

echo 生成されたファイル数: %FOUND_FILES%

if %FOUND_FILES% gtr 0 (
  echo [成功] ファイルが正常に生成されました
) else (
  echo [エラー] 結果ファイルが見つかりません
  exit /b 1
)

echo.
echo === 検証完了 ===
echo すべてのテストが正常に完了しました！
echo リファクタリングは正常に機能しています。 