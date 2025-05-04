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
6. **docs/**ディレクトリ保持**: 既存のdocsディレクトリの内容はそのまま残し、変更を加えない

## 実施順序の更新

以下の順序で整理を行います:

1. **コードの整理** (`code_cleanup_plan.md` 参照) ✅
   - 重複するコードの整理
   - 最新バージョンの採用
   - 命名規則の統一

2. **ディレクトリ構造の再編成** 🔄
   - 新しいディレクトリ構造の作成
   - 整理されたファイルの適切な配置
   - リンクの更新

## 新しいディレクトリ構造（最終更新版）

```
qv-analysis/
├── README.md                      # プロジェクト概要
├── final_report.md                # 最終レポート
├── .gitignore                     # Git無視設定
├── .github/                       # GitHub関連設定
├── data/                          # 元データファイル ✅
│   ├── votes.csv                  # 投票データ ✅
│   ├── candidates.csv             # 候補者データ ✅
│   ├── vote_summary.csv           # 投票サマリー ✅
│   └── election.json              # 元の選挙データ ✅
├── src/                           # ソースコード ✅
│   ├── analysis/                  # 分析スクリプト ✅
│   │   ├── vote_distribution_analyzer.py   # 投票分布分析（国際化対応版） ✅
│   │   ├── buried_voices_analyzer.py       # 埋もれた声分析（統合版） ✅
│   │   ├── buried_voices_visualizer.py     # 埋もれた声可視化（改善アルゴリズム版） ✅
│   │   ├── buried_voices_probabilistic.py  # 埋もれた声確率論的アプローチ ✅
│   │   ├── compare_voting_methods.py       # 投票方法比較 ✅
│   │   ├── generate_statistics.py          # 統計生成 ✅
│   │   ├── sensitivity_analysis.py         # 感度分析 ✅
│   │   └── analyze_votes.py                # 一般的な投票分析 ✅
│   ├── simulation/                # シミュレーションコード ✅
│   │   ├── neutral_bias/          # 中立バイアスシミュレーション ✅
│   │   │   ├── bias_simulator_base.py      # シミュレーション基本クラス ✅
│   │   │   ├── fixed_rate_simulator.py     # 固定割合シミュレーター ✅
│   │   │   ├── simulate_utility_max_model.py # 効用最大化モデル ✅
│   │   │   ├── analyze_credit_usage.py     # クレジット使用分析 ✅
│   │   │   ├── analyze_vote_patterns.py    # 投票パターン分析 ✅
│   │   │   └── identify_voting_patterns.py # 投票パターン識別 ✅
│   │   └── comparison/            # 比較シミュレーション ✅
│   │       └── simulate_unbiased_voting.py # 中立バイアス除去シミュレーション ✅
│   └── utils/                     # ユーティリティスクリプト ✅
│       ├── convert_to_csv.py      # CSVコンバーター ✅
│       ├── check_duplicate_votes.py # 重複投票チェック ✅
│       └── count_voters.py        # 投票者カウント ✅
├── docs/                          # ドキュメント（変更なし・既存コンテンツ維持）
├── reports_analysis/              # 詳細分析レポート ✅
│   ├── ANALYSIS_basic.md          # 基本分析レポート ✅
│   ├── ANALYSIS_neutral.md        # 中立バイアス分析レポート ✅
│   └── ANALYSIS_comparison.md     # 比較分析レポート ✅
└── results/                       # 分析結果 ✅
    ├── figures/                   # 画像ファイル（グラフ、チャートなど） ✅
    │   ├── basic_analysis/        # 基本分析の画像 ✅
    │   │   ├── budget_allocation.png ✅
    │   │   ├── voters_voting_pattern.png ✅
    │   │   ├── candidate_correlation.png ✅
    │   │   ├── total_votes.png ✅
    │   │   └── vote_pattern_candidate_*.png ✅
    │   ├── comparison/            # 比較分析の画像 ✅
    │   │   ├── buried_voices.png ✅
    │   │   ├── buried_voices_comparison.png ✅
    │   │   ├── buried_voices_fixed.png ✅
    │   │   ├── preference_intensity_*.png ✅
    │   │   ├── voting_methods_*.png ✅
    │   │   ├── multiple_distributions_comparison.png ✅
    │   │   └── utility_max_comparison.png ✅
    │   └── neutral_bias/          # 中立バイアス分析の画像 ✅
    ├── tables/                    # テーブルデータ ✅
    │   ├── budget_allocation_table.txt ✅
    │   ├── project_name_mapping.txt ✅
    │   ├── results_summary.txt ✅
    │   └── statistics_report.txt ✅
    ├── reports/                   # 詳細なレポート ✅
    │   ├── FINDINGS.md            # 発見事項 ✅
    │   ├── HYPOTHESIS.md          # 仮説 ✅
    │   ├── DESIGN_RECOMMENDATIONS.md # 設計推奨事項 ✅
    │   └── voting_methods_comparison_report.txt ✅
    └── data/                      # 生成されたデータファイル ✅
        ├── vote_summary_with_budget.csv ✅
        ├── voting_statistics.csv ✅
        ├── buried_voices.csv ✅
        ├── buried_voices_fixed.csv ✅
        ├── voting_methods_comparison.csv ✅
        ├── one_person_one_vote_results.csv ✅
        └── buried_voices_analysis.json ✅
```

## 移行計画（進捗状況反映）

### 1. 準備作業

1. ✅ 現在のリポジトリの完全なバックアップを作成する (qv-analysis-backup/ フォルダに保存済み)
2. ✅ コード整理計画（`code_cleanup_plan.md`）に従ってコードを整理する
3. ✅ 新しいディレクトリ構造を作成する

### 2. データの移動

1. データファイルの移動 ✅
   - データCSVファイル（votes.csv, candidates.csv, vote_summary.csv）→ `data/` ✅
   - JSONファイル（election.json）→ `data/` ✅
   - 分析結果JSON（buried_voices_analysis.json）→ `results/data/` ✅

2. 画像ファイルの整理 ✅
   - 基本分析の画像（budget_allocation.png など）→ `results/figures/basic_analysis/` ✅
   - 比較分析の画像（buried_voices.png, voting_methods_*.png など）→ `results/figures/comparison/` ✅
   - 中立バイアス分析の画像 ✅

3. テキストデータを `results/tables/` に移動 ✅
   - budget_allocation_table.txt ✅
   - project_name_mapping.txt ✅
   - results_summary.txt ✅
   - statistics_report.txt ✅

4. 分析レポートを `results/reports/` に移動 ✅
   - ANALYSIS.md ✅
   - FINDINGS.md ✅
   - HYPOTHESIS.md ✅
   - DESIGN_RECOMMENDATIONS.md ✅
   - voting_methods_comparison_report.txt ✅
   - ANALYSIS_basic.md ✅ (重複を避けるため名前変更)

### 3. コードの整理とファイル移動

1. ✅ 整理済みの分析スクリプトを `src/analysis/` に移動
   - ✅ buried_voices_visualizer.py (埋もれた声可視化、改善アルゴリズム版)
   - ✅ buried_voices_analyzer.py (埋もれた声分析、機能拡張版)
   - ✅ vote_distribution_analyzer.py (投票分布分析、国際化対応版)
   - ✅ analyze_votes.py → `src/analysis/`
   - ✅ compare_voting_methods.py → `src/analysis/`
   - ✅ generate_statistics.py → `src/analysis/`
   - ✅ sensitivity_analysis.py → `src/analysis/`

2. ✅ 整理済みのシミュレーションコードを `src/simulation/` のサブディレクトリに移動
   - ✅ bias_simulator_base.py (シミュレーション基本クラス)
   - ✅ fixed_rate_simulator.py (固定割合シミュレーター)
   - ✅ simulate_utility_max_model.py → `src/simulation/neutral_bias/`
   - ✅ analyze_credit_usage.py → `src/simulation/neutral_bias/`
   - ✅ analyze_vote_patterns.py → `src/simulation/neutral_bias/`
   - ✅ identify_voting_patterns.py → `src/simulation/neutral_bias/`
   - ✅ simulate_unbiased_voting.py → `src/simulation/comparison/`

3. ✅ ユーティリティスクリプトの移動
   - ✅ convert_to_csv.py → `src/utils/`
   - ✅ check_duplicate_votes.py → `src/utils/`
   - ✅ count_voters.py → `src/utils/`

4. ✅ スクリプト内のファイルパス参照を新しいディレクトリ構造に合わせて更新
   - ✅ sensitivity_analysis.py の出力先パス更新
   - ✅ CSVファイルとレポートファイル移動
   - ✅ final_report.md 内のリンク修正
   - ✅ reports_analysis内の各分析レポート（ANALYSIS_basic.md, ANALYSIS_neutral.md, ANALYSIS_comparison.md）の画像パス更新
   - ✅ Python分析スクリプト（analyze_vote_patterns.py, analyze_credit_usage.py, identify_voting_patterns.py, simulate_utility_max_model.py, compare_voting_methods.py, buried_voices_probabilistic.py, buried_voices_analyzer.py）の出力先パス更新
   - ✅ その他のPythonスクリプト（vote_distribution_analyzer.py, simulate_unbiased_voting.py, analyze_votes.py, generate_statistics.py）の出力先パス更新

### 4. リンクの修正

`final_report.md` 内のリンクを新しいパスに修正します。 ✅

- ✅ `/analysis_results/ANALYSIS.md` → `/reports_analysis/ANALYSIS_basic.md`
- ✅ `/analysis_results/voters_voting_pattern.png` → `/results/figures/basic_analysis/voters_voting_pattern.png`
- ✅ `/neutral_bias_simulation/output/vote_distribution.png` → `/results/figures/neutral_bias/vote_distribution.png`
- ✅ `/comparison_simulation/voting_methods_budget_comparison.png` → `/results/figures/comparison/voting_methods_budget_comparison.png`

### 5. docs ディレクトリの整理

**注意: docs/ディレクトリの内容は変更せず、そのまま残します。** ✅
- ✅ 既存のHTMLファイル、アセット、画像などは現状を維持
- ✅ 相対パスリンクの修正は不要（ドキュメントは変更なし）

### 6. テスト

1. ✅ すべての分析スクリプトが新しいディレクトリ構造で正常に動作することを確認
2. ✅ final_report.md のリンクが正しく動作することを確認
3. ✅ docs のウェブサイトが正しく表示されることを確認

## 注意点

1. **リンクの一貫性**: 特に `final_report.md` 内のリンクが壊れないよう注意する ✅
2. **パス依存性**: スクリプト内でハードコードされたパスがある場合は修正する ✅
3. **Git履歴**: 大きなファイル移動は Git の履歴を追跡しにくくする可能性があるので、コミットメッセージで明確に説明する
4. **コード更新**: まずコードの整理を行ってから構造変更を行うことで、作業の重複を避ける ✅
5. **docs/ディレクトリ保持**: docs/ディレクトリ内のファイルは既存のまま残し、変更しない ✅

## 実施スケジュール（更新版）

1. **Day 1**: ✅ コードの整理（重複ファイルの分析と統合）
2. **Day 2**: ✅ ディレクトリ構造作成とデータ移動
3. **Day 3**: ✅ コード配置と参照パス修正
4. **Day 4**: ✅ リンク修正とテスト
5. **Day 5**: ✅ 最終チェックとドキュメント更新

この計画により、ディレクトリ構造がより整理され、プロジェクトのメンテナンスや今後の拡張が容易になります。また、コードの重複も排除され、最新の修正が適切に反映されます。