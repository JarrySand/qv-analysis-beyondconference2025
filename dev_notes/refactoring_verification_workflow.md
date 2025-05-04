# リファクタリング検証ワークフロー

このドキュメントでは、以下の3つの大きな改修が適切に実装されたかを検証するためのワークフローを提供します：

1. ディレクトリ構造整理計画 (`directory_restructuring_plan.md`)
2. コード整理計画 (`code_cleanup_plan.md`)
3. 候補者名変更ワークフロー (`candidate_name_change_workflow.md`)

## 3. 検証作業の準備

```powershell
# 1. 不要なCSVファイルのみ削除（candidates.csvは残す）
Remove-Item -Path data\votes.csv, data\vote_summary.csv, data\project_name_mapping.csv -ErrorAction SilentlyContinue

# 2. results/ディレクトリを空にする
Remove-Item -Path results\* -Recurse -Force -ErrorAction SilentlyContinue
```

## 4. 機能検証

### 4.1 分析スクリプトの実行テスト

```powershell
# 全分析パイプラインを実行
python run_all_analysis.py
```

以下を確認します：
- エラーなく実行が完了すること
- 期待される出力ファイルが `results/` ディレクトリ内に生成されること

### 4.2 生成されたファイルの確認

```powershell
# 生成されたCSVファイルを確認
Get-ChildItem -Path data -Filter *.csv

# 生成された結果ファイルを確認
Get-ChildItem -Path results -Recurse | Measure-Object
```

### 4.3 候補者名変更フローのテスト

```powershell
# 候補者名の変更テスト
Copy-Item -Path data\candidates.csv -Destination data\candidates.csv.backup
# (ここで candidates.csv を編集し、テスト用に一つの候補者名を変更)
python src\utils\convert_to_csv.py
# 変更が反映されたか確認
Compare-Object -ReferenceObject (Get-Content data\vote_summary.csv) -DifferenceObject (Get-Content data\vote_summary.csv.backup)
# テスト後、元に戻す
Move-Item -Path data\candidates.csv.backup -Destination data\candidates.csv -Force
python src\utils\convert_to_csv.py
```

以下を確認します：
- `convert_to_csv.py` がエラーなく実行されること
- 変更した候補者名が関連するCSVファイルに反映されていること

### 4.4 リンク参照の検証

```powershell
# final_report.md 内のリンクを確認
Select-String -Path final_report.md -Pattern "/results/"
```

以下を確認します：
- `final_report.md` 内のリンクが新しいディレクトリ構造に合わせて更新されていること

## 5. レポート生成

上記のテストを実行した後、以下のような検証レポートを作成します：

| 検証項目 | 期待される結果 | 実際の結果 | ステータス |
|----------|----------------|------------|------------|
| 基本ディレクトリ構造 | 主要ディレクトリが存在 | | |
| src/ サブディレクトリ | 3つのサブディレクトリが存在 | | |
| results/ サブディレクトリ | 4つのサブディレクトリが存在 | | |
| 重複ファイルの整理 | 重複ファイルが整理されている | | |
| 分析スクリプト実行 | エラーなく完了 | | |
| 候補者名変更機能 | 変更が反映される | | |
| リンク参照 | 新構造に合わせて更新 | | |
| 全体実行テスト | すべて正常に完了 | | |

## 6. 補足作業

### 6.1 古いファイルやディレクトリの確認

```powershell
# 古い出力ディレクトリが残っていないか確認
Get-ChildItem -Directory | Where-Object { $_.Name -like "*output*" }
Get-ChildItem -Directory | Where-Object { $_.Name -like "*analysis_*" }
```

整理前のディレクトリ（`output/`, `analysis_output/`, `analysis_results/`）が残っていないことを確認します。

### 6.2 バックアップの保存

検証が完了したら、必要に応じてバックアップ (`qv-analysis-backup-v2/`) の処理を検討します：
- バックアップを保持する期間の決定
- 不要になったバックアップの削除方法 