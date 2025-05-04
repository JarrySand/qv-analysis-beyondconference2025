# コード整理計画

ディレクトリ構造を再編成する前に、現在のコードベースに存在する重複や古いバージョンのファイルを整理する必要があります。この文書では、識別された重複コードと、それらを整理するための計画を概説します。

## 識別された重複/更新コード

| 旧ファイル | 更新/代替ファイル | 状態 | 推奨アクション |
|------------|-------------------|------|----------------|
| `buried_voices_visualizer.py` | `fix_buried_voices_visualizer.py` | 更新あり - アルゴリズム改善 | `fix_` バージョンを残し、元ファイルを削除または archive |
| `analyze_votes.py` | `analyze_votes_buried.py` | 機能特化 - 埋もれた声に特化した分析 | 両方を維持し、機能を明確に区別。前者は一般的な投票分析、後者は埋もれた声の分析に特化 |
| `simulate_unbiased_voting.py` | `neutral_bias_simulation/simulate_utility_max_model.py` | 異なる機能 - アプローチの違い | 両方維持、前者は1票を0票に変換する簡易シミュレーション、後者は効用最大化モデルに基づく詳細なシミュレーション |
| `analyze_vote_distribution.py` | `neutral_bias_simulation/analyze_vote_distribution.py` | 類似機能で改良あり - 国際化対応 | 後者の拡張版を維持。国際化対応と追加機能を持つ |

## 詳細分析結果

### 1. `buried_voices_visualizer.py` vs `fix_buried_voices_visualizer.py`
- **主な違い**: 埋もれた声の検出アルゴリズムが改善されている
- **元のアルゴリズム**: `vote_value >= 4 and i != max_candidate`
- **改善されたアルゴリズム**: `vote_value > max_vote * 0.7 and vote_value >= 3 and i != max_candidate`
- **改善点**: より柔軟な閾値設定により、投票値の相対的な強さも考慮している
- **推奨アクション**: 修正版のアルゴリズムを採用し、名前から`fix_`を削除して統一する

### 2. `analyze_votes.py` vs `analyze_votes_buried.py`
- **機能の違い**: 
  - `analyze_votes.py`: 一般的な投票分析、分布グラフ作成、予算配分計算
  - `analyze_votes_buried.py`: 埋もれた声に特化した分析、特定候補（#vote_forプロジェクト）の詳細分析
- **推奨アクション**: 機能が重複していないため両方維持し、`analyze_votes_buried.py`を`buried_voices_analyzer.py`にリネームして機能を明確化

### 3. `simulate_unbiased_voting.py` vs `neutral_bias_simulation/simulate_utility_max_model.py`
- **アプローチの違い**:
  - `simulate_unbiased_voting.py`: 1票を0票に変換するシンプルなシミュレーション
  - `simulate_utility_max_model.py`: 選好強度から理論的投票パターンを生成する複雑なモデル
- **特徴**:
  - 前者: 複数のシナリオ（一定割合、投票者パターン別、統計的異常検出）を実装
  - 後者: 効用最大化理論に基づくシミュレーションと実データとの比較分析
- **推奨アクション**: 異なるアプローチなので両方維持し、名前を明確化する

### 4. `analyze_vote_distribution.py` vs `neutral_bias_simulation/analyze_vote_distribution.py`
- **主な違い**:
  - 基本機能は同じ（投票分布分析と中立バイアス検出）
  - `neutral_bias_simulation/`版は国際化対応（日英翻訳）機能が追加されている
  - ファイル読み込み方法とデータ変換処理に違いあり
- **推奨アクション**: 国際化対応版を優先し、必要な機能を統合してアップデートする

## コード整理手順

1. **埋もれた声可視化スクリプトの統合**
   - `fix_buried_voices_visualizer.py`のコードをベースに、わかりやすい名前で統合版を作成

2. **投票分析スクリプトの整理**
   - `analyze_votes.py`と`analyze_votes_buried.py`の機能を明確に区別
   - 後者を`buried_voices_analyzer.py`にリネームして目的を明確化

3. **中立バイアスシミュレーションの整理**
   - 両方のシミュレーションアプローチを維持
   - 名前と機能の説明をわかりやすく整理

4. **投票分布分析スクリプトの統合**
   - 国際化対応版をベースに統合版を作成
   - 冗長なコードを排除し、必要な機能をすべて含める

## 確認が必要なディレクトリ間の重複

以下のディレクトリ間で機能の重複やファイルの重複がある可能性があります：

1. ルートディレクトリと `neutral_bias_simulation/` の間の重複分析スクリプト
2. `output/`, `analysis_output/`, `analysis_results/` 間の出力データ/画像の重複
3. `docs/assets/images/` と前述の出力ディレクトリ間の画像の重複

## 次のステップ

1. 各重複ファイルの詳細な内容確認とリファクタリング
2. コード整理の実施
3. 整理されたコードベースでのディレクトリ構造再編成の実施

## タイムライン

1. **Day 1**: 重複ファイルの詳細分析と計画確定
2. **Day 2**: 重要なスクリプトの更新と統合
3. **Day 3**: 残りのスクリプト整理とテスト
4. **Day 4**: ドキュメント更新とレビュー

## 注意点

- 変更前に各ファイルのバックアップを作成する
- 変更後は影響を受ける可能性のあるスクリプトをテストする
- すべての変更を Git でコミットし、明確なコミットメッセージを残す 