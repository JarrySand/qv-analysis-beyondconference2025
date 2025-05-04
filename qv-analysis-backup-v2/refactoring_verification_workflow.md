# リファクタリング検証ワークフロー

このドキュメントでは、以下の3つの大きな改修が適切に実装されたかを検証するためのワークフローを提供します：

1. ディレクトリ構造整理計画 (`directory_restructuring_plan.md`)
2. コード整理計画 (`code_cleanup_plan.md`)
3. 候補者名変更ワークフロー (`candidate_name_change_workflow.md`)

## 1. ディレクトリ構造検証

### 1.1 基本構造の検証

```bash
# 基本的なディレクトリ構造が存在することを確認
ls -la
```

以下のディレクトリが存在することを確認します：
- `src/` - ソースコード
- `data/` - 元データファイル
- `results/` - 分析結果
- `reports_analysis/` - 詳細分析レポート
- `docs/` - ドキュメント（変更なし）

### 1.2 サブディレクトリ構造の検証

```bash
# src/ サブディレクトリの確認
ls -la src/

# results/ サブディレクトリの確認
ls -la results/
```

以下のサブディレクトリが存在することを確認します：
- `src/analysis/` - 分析スクリプト
- `src/simulation/` - シミュレーションコード
- `src/utils/` - ユーティリティスクリプト
- `results/figures/` - 画像ファイル
- `results/tables/` - テーブルデータ
- `results/reports/` - 詳細なレポート
- `results/data/` - 生成されたデータファイル

### 1.3 ファイルの移動確認

```bash
# 主要なデータファイルが正しい場所にあるか確認
ls -la data/
```

以下のファイルが `data/` に存在することを確認します：
- `votes.csv`
- `candidates.csv`
- `vote_summary.csv`
- `election.json`

## 2. コード整理の検証

### 2.1 重複ファイルの整理確認

```bash
# 埋もれた声分析関連のファイルを確認
ls -la src/analysis/ | grep buried_voices

# 投票分析関連のファイルを確認
ls -la src/analysis/ | grep vote
```

以下を確認します：
- `buried_voices_visualizer.py` が存在し、`fix_buried_voices_visualizer.py` が存在しないこと
- `buried_voices_analyzer.py` が存在し、`analyze_votes_buried.py` が存在しないこと
- `vote_distribution_analyzer.py` が国際化対応版として存在すること

### 2.2 シミュレーションコードの整理確認

```bash
# 中立バイアスシミュレーション関連のファイルを確認
ls -la src/simulation/neutral_bias/

# 比較シミュレーション関連のファイルを確認
ls -la src/simulation/comparison/
```

以下を確認します：
- `src/simulation/neutral_bias/` に必要なシミュレーションファイルが存在すること
- `src/simulation/comparison/` に `simulate_unbiased_voting.py` が存在すること

## 3. 機能検証

### 3.1 分析スクリプトの実行テスト

```bash
# 主要な分析スクリプトを実行
python src/analysis/analyze_votes.py
python src/analysis/buried_voices_visualizer.py
```

以下を確認します：
- エラーなく実行が完了すること
- 期待される出力ファイルが `results/` ディレクトリ内に生成されること

### 3.2 候補者名変更フローのテスト

```bash
# 候補者名の変更テスト
cp data/candidates.csv data/candidates.csv.backup
# (ここで candidates.csv を編集し、テスト用に一つの候補者名を変更)
python src/utils/convert_to_csv.py
# 変更が反映されたか確認
diff data/vote_summary.csv data/vote_summary.csv.backup
# テスト後、元に戻す
mv data/candidates.csv.backup data/candidates.csv
python src/utils/convert_to_csv.py
```

以下を確認します：
- `convert_to_csv.py` がエラーなく実行されること
- 変更した候補者名が関連するCSVファイルに反映されていること

### 3.3 リンク参照の検証

```bash
# final_report.md 内のリンクを確認
grep -n "/results/" final_report.md
```

以下を確認します：
- `final_report.md` 内のリンクが新しいディレクトリ構造に合わせて更新されていること

## 4. 全体実行テスト

```bash
# 全体の分析を実行
python run_all_analysis.py
```

以下を確認します：
- すべての分析が新しいディレクトリ構造で正常に実行されること
- 結果が適切なディレクトリに出力されること

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

```bash
# 古い出力ディレクトリが残っていないか確認
ls -la | grep output
ls -la | grep analysis_
```

整理前のディレクトリ（`output/`, `analysis_output/`, `analysis_results/`）が残っていないことを確認します。

### 6.2 バックアップの保存

検証が完了したら、必要に応じてバックアップ (`qv-analysis-backup/`) の処理を検討します：
- バックアップを保持する期間の決定
- 不要になったバックアップの削除方法 