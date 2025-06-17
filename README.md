# QV分析

二次投票（Quadratic Voting, QV）データを処理・分析するためのツールキット。

## 概要

このリポジトリには、二次投票データを分析するためのPythonスクリプト集が含まれています。システムは生のJSON投票データを処理し、CSV形式に変換した上で、基本統計、投票方法の比較、感度分析、「埋もれた声」の分析など、様々な分析を実行します。特に、二次投票（QV）と従来の一人一票方式の違いを明確にする比較分析に重点を置いています。

## 主な機能

- プロジェクト名翻訳の一元管理システム
- JSONから標準CSV形式への変換
- 二次投票データの複数分析メソッド
- 投票パターンと「埋もれた声」の可視化
- **二次投票と一人一票方式の詳細比較分析**
- 異なる閾値（閾値1：すべての選好、閾値4：強い選好のみ）での埋もれた声分析と比較
- パラメータ調整のための感度分析
- 中立バイアスのシミュレーションと分析

## プロジェクト構造

```
qv-analysis/
├── data/                          # データファイル
│   ├── candidates.csv             # 英語翻訳付きの候補者情報
│   ├── election.json              # 元の投票データ（JSON形式）
│   ├── project_name_mapping.csv   # プロジェクト名の日英マッピング
│   ├── vote_summary.csv           # 投票サマリーデータ
│   └── votes.csv                  # 変換済み投票データ
│
├── docs/                          # ドキュメント
│   ├── assets/                    # ウェブサイト用アセット
│   │   ├── css/                   # スタイルシート
│   │   ├── images/                # 画像ファイル
│   │   └── js/                    # JavaScript
│   └── index.html                 # 分析結果公開サイト
│
├── results/                       # 分析結果
│   ├── data/                      # 生成されたデータファイル
│   │   ├── buried_voices.csv      # 埋もれた声分析データ（閾値4）
│   │   ├── buried_voices_comparison.csv # 閾値間の埋もれた声比較データ
│   │   ├── vote_statistics.csv
│   │   ├── voter_statistics.csv   # 投票者統計データ
│   │   ├── voting_statistics.csv  # 投票統計データ
│   │   ├── one_person_one_vote_results.csv  # 一人一票シミュレーション結果
│   │   ├── voting_methods_comparison.csv    # 投票方式比較データ
│   │   └── ...
│   ├── figures/                   # 生成されたグラフ
│   │   ├── basic_analysis/        # 基本分析グラフ
│   │   ├── buried_voices/         # 埋もれた声分析グラフ
│   │   │   ├── threshold_1/       # 閾値1（すべての投票）の分析結果
│   │   │   │   ├── buried_voices.png           # 埋もれた声グラフ
│   │   │   │   ├── buried_voices_ratio.png     # 埋もれた声の割合
│   │   │   │   ├── votes_vs_max_votes.png      # 全投票と最大投票の比較
│   │   │   │   └── ...                         # 個別候補者分析結果
│   │   │   ├── threshold_4/       # 閾値4（強い選好のみ）の分析結果
│   │   │   │   ├── buried_voices.png           # 埋もれた声グラフ
│   │   │   │   ├── buried_voices_ratio.png     # 埋もれた声の割合
│   │   │   │   ├── votes_vs_max_votes.png      # 全投票と最大投票の比較 
│   │   │   │   └── ...                         # 個別候補者分析結果
│   │   │   ├── buried_voices_comparison.png    # 閾値間の埋もれた声比較
│   │   │   └── buried_voices_ratio_comparison.png # 閾値間の埋もれた声割合比較
│   │   ├── comparison/            # 投票方式比較分析グラフ
│   │   │   ├── voting_methods_vote_comparison.png      # 投票数比較
│   │   │   ├── voting_methods_budget_comparison.png    # 予算配分比較
│   │   │   ├── voting_methods_percentage_comparison.png # パーセンテージ比較
│   │   │   ├── voting_methods_gini_comparison.png      # 不平等度比較
│   │   │   ├── lorenz_curves.png                       # ローレンツ曲線
│   │   │   └── preference_intensity_heatmap.png        # 選好強度ヒートマップ
│   │   └── neutral_bias/          # 中立バイアス分析グラフ
│   ├── reports/                   # 分析レポート
│   │   ├── budget_allocation_table.txt        # 予算配分表
│   │   ├── project_name_mapping.txt           # プロジェクト名マッピング
│   │   ├── results_summary.txt                # 結果サマリー
│   │   ├── statistics_report.html             # 統計レポート（HTML）
│   │   ├── statistics_report.txt              # 統計レポート（テキスト）
│   │   ├── voting_methods_comparison.txt      # 投票方式比較レポート
│   │   └── ...
│   └── tables/                    # 生成されたテーブル（廃止予定）
│       └── ...
│
├── src/                           # ソースコード
│   ├── analysis/                  # 分析スクリプト
│   │   ├── analyze_votes.py       # 基本投票分析
│   │   ├── buried_voices_analyzer.py
│   │   ├── buried_voices_probabilistic.py
│   │   ├── buried_voices_visualizer.py
│   │   ├── compare_voting_methods.py  # 投票方式比較スクリプト
│   │   ├── generate_statistics.py
│   │   ├── sensitivity_analysis.py
│   │   └── vote_distribution_analyzer.py
│   │
│   ├── simulation/                # シミュレーションスクリプト
│   │   ├── comparison/            # 投票方式比較
│   │   │   └── simulate_unbiased_voting.py  # 一人一票シミュレーション
│   │   └── neutral_bias/          # 中立バイアス分析
│   │       ├── analyze_credit_usage.py
│   │       ├── analyze_vote_patterns.py
│   │       ├── bias_simulator_base.py
│   │       ├── fixed_rate_simulator.py
│   │       ├── identify_voting_patterns.py
│   │       └── simulate_utility_max_model.py
│   │
│   └── utils/                     # ユーティリティスクリプト
│       ├── check_duplicate_votes.py
│       ├── convert_to_csv.py      # データ変換ユーティリティ
│       └── count_voters.py
│
├── reports_analysis/              # 分析レポート（詳細版）
│   ├── ANALYSIS_basic.md           # 基本分析レポート
│   ├── ANALYSIS_comparison.md      # 投票方式比較分析レポート
│   └── ANALYSIS_neutral.md         # 中立バイアス分析レポート
├── candidate_name_change_workflow.md  # 候補者名変更の手順
├── final_report.md                   # 総合分析レポート
├── REPORTS_ANALYSIS_UPDATE_SUMMARY.md # レポート更新サマリー
├── requirements.txt                  # 必要なPythonパッケージリスト
├── run_all_analysis.py               # 完全な分析パイプラインを実行
└── run_data_processing.py            # データ変換ステップのみを実行
```

## 使い方

### 前提条件

- Python 3.6+

### インストール

1. リポジトリをクローン
2. 必要な依存パッケージをインストール:
   ```
   pip install -r requirements.txt
   ```

### 使用方法

#### 完全な分析の実行

分析パイプライン全体を実行するには:

```
python run_all_analysis.py
```

これにより、以下のスクリプトが正しい順序で実行されます:
1. データ変換（JSONからCSV）
2. 基本投票分析
3. 埋もれた声の可視化
4. 統計分析
5. 埋もれた声の確率論的分析
6. **投票方法の比較**（二次投票 vs 一人一票）
7. 投票分布分析
8. 埋もれた声の詳細分析
9. 感度分析

#### データ処理のみの実行

分析を実行せずにデータを処理するには:

```
python run_data_processing.py
```

これは、候補者名を更新し、CSVファイルを再生成する必要がある場合に便利です。

### プロジェクト名の変更

プロジェクト名の翻訳を変更するには:

1. `data/candidates.csv` を編集して英語訳を更新
2. `python run_data_processing.py` を実行して変更を反映
3. 生成されたCSVファイルに変更が反映されていることを確認

詳細については、`candidate_name_change_workflow.md` を参照してください。

## 分析手法

- **基本投票分析**: 投票パターンと分布を調査
- **埋もれた声分析**: 少数派からの強い支持を持つプロジェクトを特定
  - **閾値比較分析**: 強い選好（閾値4）と全ての選好（閾値1）の埋もれた声を比較
- **投票方法比較**: QVと他の投票システムを対比
- **感度分析**: パラメータ変更が結果にどう影響するかをテスト
- **中立バイアス分析**: 理想的な投票モデルとの比較によるバイアス検出
- **投票者クラスター分析**: 投票パターンに基づく投票者グループの識別
- **効用最大化モデル分析**: 理論的投票行動との比較検証

## プロジェクト概要

このプロジェクトは、Quadratic Voting（二次投票）の投票結果を分析するためのツールです。ソーシャルセクターの若手起業家を対象とした複数回の投票イベント（Beyond Conference 2025本会議および追加オンライン投票）での投票データを統合し、効果的な資金配分をサポートします。

## イベント詳細

- **対象**: ソーシャルセクターの若手起業家
- **イベント名**: Beyond Conference 2025
- **投票実施日程**:
  - **第1回**: 2025年4月26日（Beyond Conference 2025本会議）
    - **開催場所**: 淡路島
    - **投票形式**: ピッチプレゼン後にオーディエンスによるリアルタイム投票
  - **第2回**: 2025年6月9日（オンライン追加投票）
    - **開催場所**: オンライン
    - **投票形式**: オンラインミーティング形式での追加投票
- **投票者**: 他のソーシャルセクター起業家、自治体職員、企業CSR担当者など
- **賞金**: 投票結果に応じて25万円のプール資金が提供される
- **使用ツール**: [qv.geek.sg](https://qv.geek.sg)
- **投票リンク**: https://api.qv.geek.sg/election/0a9885d5-43b4-4b80-b69f-406092002a38
- **投票UID**: 0a9885d5-43b4-4b80-b69f-406092002a38

## 分析目的

このプロジェクトでは、複数回実施されたQuadratic Votingによる投票データを統合し、以下の点を明らかにします：

1. 各プロジェクトの支持度合い（複数回投票の統合結果）
2. 投票パターンの分析
3. 資金配分の最適化提案
4. 投票行動における潜在的バイアスの特定
5. **二次投票と一人一票方式の実質的な違いと影響**

## 技術スタック

- データ収集: 
  - qv.geek.sgのAPIエンドポイント (`https://api.qv.geek.sg/election/{uid}`) からのデータ取得
  - 複数回の投票結果を統合してJSONファイルとして保存
  - 最終統合データ: 179名の投票者、976票の投票データ
- データ分析: Python (pandas, numpy, scipy)
- 可視化: matplotlib, seaborn, plotly

## 主な機能

- 投票データ（election.json）のCSV形式への変換
- 投票パターンの分析
- 予算配分の計算（二次投票方式）
- 統計レポート生成（CSV、テキスト、HTML形式）
- データ可視化（棒グラフ、円グラフ、ヒートマップ、散布図）
- 投票方式比較シミュレーション（QV vs 一人一票方式）
- 投票者行動の詳細分析（クラスター分析、相関分析）
- 理論モデルとの比較検証（効用最大化、中立バイアス検証）

## 分析結果の公開サイト
今後実装予定


## 分析レポート

詳細な分析結果は以下のレポートで確認できます：

- **[総合分析レポート](final_report.md)**: 全分析結果の統合レポート
- **[基本分析レポート](reports_analysis/ANALYSIS_basic.md)**: 投票データの基本統計と分析
- **[比較分析レポート](reports_analysis/ANALYSIS_comparison.md)**: QV方式と一人一票方式の詳細比較
- **[中立バイアス分析レポート](reports_analysis/ANALYSIS_neutral.md)**: 投票行動の理論的検証
- **[レポート更新サマリー](REPORTS_ANALYSIS_UPDATE_SUMMARY.md)**: データ更新に伴う修正内容の詳細

## ライセンス

MIT 