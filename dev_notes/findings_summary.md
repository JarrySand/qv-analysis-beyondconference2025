# 列名不整合の調査結果

## 問題の概要

リファクタリング後、`vote_distribution_analyzer.py`で「id」列を参照しようとしたところ、その列名が「candidate_id」に変更されていたことで発生したKeyError。

## 詳細な調査

コードベース全体を検索した結果、複数のファイルで「id」と「candidate_id」の不整合が見つかりました。

### 特に修正が必要な箇所

1. **src/simulation/neutral_bias/identify_voting_patterns.py**:
   - 147行目: カラム名のマッピングで `'candidate_id': 'id'` と変換している
   - 161行目: `candidates_df.set_index('id')['title']` を使用

2. **src/simulation/neutral_bias/bias_simulator_base.py**:
   - 163行目: `qv_results = qv_results.merge(self.candidates_df[['id', 'title']], left_on='candidate_id', right_on='id')`
   - 197行目: `on=['candidate_id', 'id', 'title']` という列のリストを使用

3. **src/simulation/comparison/simulate_unbiased_voting.py**:
   - 58行目: `'id': 'id'`
   - 185, 202, 217, 234行目: `candidates_df[['id', 'name']]` を使用
   - 187, 204, 219, 236行目: `right_on='id'` と指定

### 既に修正済みの箇所

1. **src/analysis/vote_distribution_analyzer.py**:
   - 151行目: `self.candidates_df[['candidate_id', 'title']]` を使用するよう修正済み
   - 343行目: `self.candidates_df[self.candidates_df['candidate_id'] == idx]['title'].values[0]` を使用するよう修正済み

## 推奨される対応

1. 一貫性のため、すべての候補者データフレームでは `candidate_id` を主キーとして使用する
2. 既存の `id` 列の参照をすべて `candidate_id` に変更する
3. 特に上記の「特に修正が必要な箇所」に挙げられたファイルを優先的に修正する

## 検証方法

修正後、すべてのスクリプトが正常に動作することを検証するには：

1. 各スクリプトを個別に実行する
2. verify_refactoring.pバッチ処理を実行して、エンドツーエンドの処理が正常に完了することを確認する

これにより、リファクタリング後のコード整合性を確保します。 