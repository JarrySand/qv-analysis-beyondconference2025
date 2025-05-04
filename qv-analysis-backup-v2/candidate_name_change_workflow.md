# 候補者名変更のワークフロー

このドキュメントでは、QV分析システムにおける候補者名（プロジェクト名）の変更方法について説明します。

## 概要

候補者名の変更は、以下のフローで行います：

1. `data/candidates.csv` ファイルを編集
2. `src/utils/convert_to_csv.py` を実行して、他のCSVファイルを更新

このフローにより、一か所での変更が全システムに反映されます。

## 詳細な手順

### 1. candidates.csvの編集

`data/candidates.csv` は候補者情報の基本データソースです。このファイルには、日本語名と英語名の両方が含まれています。

ファイル構造:
```
candidate_id,title,title_en,description
0,10代・20代の「いま、やりたい」を後押しする拠点　ちばユースセンターPRISM,Chiba Youth Center PRISM,説明文...
1,政を祭に変える #vote_forプロジェクト,#vote_for Project,説明文...
...
```

変更したい場合:
- `title` 列：日本語のプロジェクト名
- `title_en` 列：英語のプロジェクト名

### 2. CSVファイルの更新

変更を反映するには、以下のコマンドを実行します：

```bash
python src/utils/convert_to_csv.py
```

このスクリプトが行うこと:
- `data/candidates.csv` から日本語名と英語名のマッピングを読み込む
- `data/election.json` から元データを読み込む
- 以下のファイルを更新/生成する:
  - `data/votes.csv`: 個別の投票データ
  - `data/candidates.csv`: 候補者情報（英語名を含む）
  - `data/vote_summary.csv`: 投票の集計結果（英語名を含む）
  - `data/project_name_mapping.csv`: プロジェクト名の日英対応表

### 3. 分析スクリプトの実行

名前の変更が完了したら、分析スクリプトを実行して結果を更新できます：

```bash
python src/analysis/analyze_votes.py
python src/analysis/buried_voices_visualizer.py
```

これらのスクリプトは、更新された `data/candidates.csv` の `title_en` 列を使用して、英語の名前でグラフや分析結果を生成します。

## 技術的背景

以前のシステムでは、プロジェクト名の日英変換が各スクリプトに個別にハードコードされていました。現在のアプローチでは：

1. `data/candidates.csv` を唯一の情報源（Single Source of Truth）として使用
2. すべてのCSVファイルに `title_en` 列を含める
3. 分析スクリプトは直接 `title_en` 列を使用する

このアプローチにより、名前の変更が必要な場合、`data/candidates.csv` のみを編集すれば、変更がシステム全体に反映されます。

## 注意点

- `data/candidates.csv` が存在しない場合、`convert_to_csv.py` はデフォルトのマッピングを使用します
- プロジェクト名の一貫性を保つために、常に `convert_to_csv.py` を通してCSVファイルを生成してください 