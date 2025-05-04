# ディレクトリ構造整理計画

## 現状の問題点

現在のディレクトリ構造には以下の問題点があります：

1. 複数の分析出力ディレクトリ（`output/`, `analysis_output/`, `analysis_results/`）が存在し、混乱の原因になっている
2. `neutral_bias_simulation/` 内に `neutral_bias_simulation/` という同名のサブディレクトリが存在する
3. `docs/assets/images/` と `analysis_results/` 及び `comparison_simulation/` に重複する画像ファイルが存在する
4. 同様の分析スクリプトが複数のバージョンで存在する（例: `buried_voices_visualizer.py` と `fix_buried_voices_visualizer.py`）
5. ルートディレクトリに多数のPythonスクリプトが散在している
6. コードの修正やバージョンアップデートが明確に管理されていない

## 整理の基本方針

1. **機能別ディレクトリ構造**: コード、データ、ドキュメント、結果を明確に分ける
2. **シンプルな階層**: 深すぎる階層を避け、わかりやすい構造にする
3. **リンク維持**: final_reportなどの参照リンクが壊れないよう注意する
4. **冗長性排除**: 重複ファイルの整理と統合
5. **最新コード優先**: 更新・修正されたコードを優先的に採用する

## 実施順序の更新

以下の順序で整理を行います:

1. **コードの整理** (`code_cleanup_plan.md` 参照)
   - 重複するコードの整理
   - 最新バージョンの採用
   - 命名規則の統一

2. **ディレクトリ構造の再編成**
   - 新しいディレクトリ構造の作成
   - 整理されたファイルの適切な配置
   - リンクの更新

## 新しいディレクトリ構造

```
qv-analysis/
├── README.md                      # プロジェクト概要
├── final_report.md                # 最終レポート
├── LICENSE                        # ライセンス情報
├── .gitignore                     # Git無視設定
├── .github/                       # GitHub関連設定
├── data/                          # 元データファイル
│   ├── votes.csv                  # 投票データ
│   ├── candidates.csv             # 候補者データ
│   ├── vote_summary.csv           # 投票サマリー
│   └── election.json              # 元の選挙データ
├── src/                           # ソースコード
│   ├── analysis/                  # 分析スクリプト
│   │   ├── analyze_votes.py       # 投票分析
│   │   ├── analyze_vote_distribution.py # 投票分布分析
│   │   ├── analyze_votes_buried.py # 埋もれた声分析
│   │   ├── compare_voting_methods.py # 投票方法比較
│   │   ├── generate_statistics.py  # 統計生成
│   │   ├── sensitivity_analysis.py # 感度分析
│   │   └── buried_voices_visualizer.py # 埋もれた声可視化（更新版）
│   ├── simulation/                # シミュレーションコード
│   │   ├── neutral_bias/          # 中立バイアスシミュレーション
│   │   │   ├── simulate_utility_max_model.py
│   │   │   ├── analyze_credit_usage.py
│   │   │   ├── analyze_vote_patterns.py
│   │   │   └── identify_voting_patterns.py
│   │   └── comparison/            # 比較シミュレーション
│   │       └── simulate_unbiased_voting.py
│   └── utils/                     # ユーティリティスクリプト
│       ├── convert_to_csv.py      # CSVコンバーター
│       ├── check_duplicate_votes.py # 重複投票チェック
│       └── count_voters.py        # 投票者カウント
├── docs/                          # ドキュメント
│   ├── index.html                 # メインHTML
│   ├── .nojekyll                  # Jekyll無効化
│   ├── DEVELOPMENT.md             # 開発ドキュメント
│   └── assets/                    # アセット
│       ├── js/                    # JavaScript
│       ├── css/                   # スタイルシート
│       └── images/                # 画像ファイル
└── results/                       # 分析結果
    ├── figures/                   # 画像ファイル（グラフ、チャートなど）
    │   ├── basic_analysis/        # 基本分析の画像
    │   ├── comparison/            # 比較分析の画像
    │   └── neutral_bias/          # 中立バイアス分析の画像
    ├── tables/                    # テーブルデータ
    │   ├── budget_allocation_table.txt
    │   └── project_name_mapping.txt
    ├── reports/                   # 詳細なレポート
    │   ├── ANALYSIS.md            # 総合分析レポート
    │   ├── FINDINGS.md            # 発見事項
    │   ├── HYPOTHESIS.md          # 仮説
    │   └── DESIGN_RECOMMENDATIONS.md # 設計推奨事項
    └── data/                      # 生成されたデータファイル
        ├── vote_summary_with_budget.csv
        ├── voting_statistics.csv
        ├── buried_voices.csv
        └── voting_methods_comparison.csv
```

## 移行計画

### 1. 準備作業

1. 現在のリポジトリの完全なバックアップを作成する
2. コード整理計画（`code_cleanup_plan.md`）に従ってコードを整理する
3. 新しいディレクトリ構造を作成する

### 2. データの移動

1. `data/` ディレクトリにCSVファイルとJSON投票データを移動
2. 画像ファイルを `results/figures/` の適切なサブディレクトリに整理
   - 基本分析の画像 → `results/figures/basic_analysis/`
   - 比較分析の画像 → `results/figures/comparison/`
   - 中立バイアス分析の画像 → `results/figures/neutral_bias/`
3. テキストデータを `results/tables/` に移動
4. 分析レポートを `results/reports/` に移動

### 3. コードの整理

1. 整理済みの分析スクリプトを `src/analysis/` に移動
2. 整理済みのシミュレーションコードを `src/simulation/` のサブディレクトリに移動
3. 整理済みのユーティリティスクリプトを `src/utils/` に移動
4. スクリプト内のファイルパス参照を新しいディレクトリ構造に合わせて更新

### 4. リンクの修正

`final_report.md` 内のリンクを新しいパスに修正します。例えば：

- `/analysis_results/ANALYSIS.md` → `/results/reports/ANALYSIS.md`
- `/analysis_results/voters_voting_pattern.png` → `/results/figures/basic_analysis/voters_voting_pattern.png`
- `/neutral_bias_simulation/output/vote_distribution.png` → `/results/figures/neutral_bias/vote_distribution.png`
- `/comparison_simulation/voting_methods_budget_comparison.png` → `/results/figures/comparison/voting_methods_budget_comparison.png`

### 5. docs ディレクトリの整理

1. `docs/assets/images/` 内の画像ファイルがメインの分析結果画像と重複している場合は、相対パスリンクを使用するよう修正
2. ウェブサイト表示に必要なファイルのみを残す

### 6. テスト

1. すべての分析スクリプトが新しいディレクトリ構造で正常に動作することを確認
2. final_report.md のリンクが正しく動作することを確認
3. docs のウェブサイトが正しく表示されることを確認

## 注意点

1. **リンクの一貫性**: 特に `final_report.md` 内のリンクが壊れないよう注意する
2. **パス依存性**: スクリプト内でハードコードされたパスがある場合は修正する
3. **Git履歴**: 大きなファイル移動は Git の履歴を追跡しにくくする可能性があるので、コミットメッセージで明確に説明する
4. **コード更新**: まずコードの整理を行ってから構造変更を行うことで、作業の重複を避ける

## 実施スケジュール（更新版）

1. **Day 1**: コードの整理（重複ファイルの分析と統合）
2. **Day 2**: ディレクトリ構造作成とデータ移動
3. **Day 3**: コード配置と参照パス修正
4. **Day 4**: リンク修正とテスト
5. **Day 5**: 最終チェックとドキュメント更新

この計画により、ディレクトリ構造がより整理され、プロジェクトのメンテナンスや今後の拡張が容易になります。また、コードの重複も排除され、最新の修正が適切に反映されます。 