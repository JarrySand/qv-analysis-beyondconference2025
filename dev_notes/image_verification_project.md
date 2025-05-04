# QV分析レポート 図表検証プロジェクト

## 問題の概要

`final_report.md`で参照されている図表のうち、一部が存在していないことが確認されました。これらの画像は分析レポートの重要な部分であり、修復する必要があります。

## 不足している図表

### 完全に不足しているもの
1. `/results/figures/neutral_bias/credit_usage_rate_distribution.png`
2. `/results/figures/neutral_bias/remaining_credits_distribution.png`
3. `/results/figures/neutral_bias/utility_max_comparison.png`
4. `/results/figures/comparison/voting_methods_gini_comparison.png`

### ファイル名が異なるもの
1. `/results/figures/comparison/voting_methods_lorenz_curve.png` → 実際は `lorenz_curves.png`
2. `/results/figures/comparison/buried_voices_fixed.png` → 類似ファイルとして `buried_voices.png`、`buried_voices_comparison.png`、`buried_voices_ratio.png` が存在

## 調査の結果

問題のファイルについて詳細な調査を行いました。

### コードの確認

1. **クレジット使用率と残りクレジット分布**:
   - `src/simulation/neutral_bias/analyze_credit_usage.py`でこれらの画像を生成するコードを発見
   - このスクリプトは`run_all_analysis.py`に含まれていない追加スクリプト
   - スクリプトは存在するが実行されていない

2. **効用最大化モデル比較**:
   - `src/simulation/neutral_bias/simulate_utility_max_model.py`でこの画像を生成するコードを発見
   - このスクリプトも`run_all_analysis.py`に含まれていない追加スクリプト
   - スクリプトは存在するが実行されていない

3. **ジニ係数比較**:
   - `src/analysis/compare_voting_methods.py`内でローレンツ曲線は生成されているが、ジニ係数の専用グラフは存在しない
   - コード内ではジニ係数を計算しレポートに含めているが、専用の可視化は実装されていない

4. **ファイル名の不一致**:
   - `lorenz_curves.png`ファイルは存在するが、レポート内では`voting_methods_lorenz_curve.png`として参照
   - `buried_voices.png`は存在するが、レポート内では`buried_voices_fixed.png`として参照

### バックアップの確認

- バックアップフォルダ`qv-analysis-backup-v2`に不足しているファイルの一部が存在
- バックアップからファイルをコピーするか、元のスクリプトを再実行するかの選択が必要

## 問題の原因

調査の結果、以下の原因が確認されました：

1. **メイン分析フローからの除外**:
   - 中立バイアスのシミュレーションスクリプトが`run_all_analysis.py`に含まれていない
   - これらは別途実行が必要な追加分析スクリプトだった可能性が高い

2. **ファイル名の不一致**:
   - レポート作成時に想定していたファイル名と実際の生成ファイル名が異なる
   - 以前のバージョンでの名前をレポートに使用した可能性

3. **未実装の可視化**:
   - ジニ係数比較の専用グラフは計画されていたが実装されていなかった可能性
   - 代わりにローレンツ曲線グラフとテキストレポートでジニ係数を表現している

## 解決計画

### 1. 欠落スクリプトの実行

1. **クレジット使用率と残りクレジット関連のグラフ生成**:
   ```
   python src/simulation/neutral_bias/analyze_credit_usage.py
   ```

2. **効用最大化モデル比較グラフの生成**:
   ```
   python src/simulation/neutral_bias/simulate_utility_max_model.py
   ```

### 2. ジニ係数比較グラフの新規作成

1. `src/analysis/compare_voting_methods.py`を拡張して、ジニ係数の比較グラフを追加実装
   - QV方式と一人一票方式のジニ係数を棒グラフで比較する可視化を追加
   - 既存のライブラリとデータ構造を活用して最小限の変更で実装

### 3. ファイル名の不一致解決

1. **レポート内の参照を実際のファイル名に更新**:
   - `voting_methods_lorenz_curve.png` → `lorenz_curves.png`
   - `buried_voices_fixed.png` → `buried_voices.png`または`buried_voices_comparison.png`

### 4. バックアップからの復元（代替案）

1. 問題の画像がバックアップに存在する場合、コピーして復元:
   ```
   copy qv-analysis-backup-v2\results\figures\neutral_bias\credit_usage_rate_distribution.png results\figures\neutral_bias\
   copy qv-analysis-backup-v2\results\figures\neutral_bias\remaining_credits_distribution.png results\figures\neutral_bias\
   copy qv-analysis-backup-v2\results\figures\neutral_bias\utility_max_comparison.png results\figures\neutral_bias\
   ```

## 実装計画

### 1. ジニ係数比較グラフ生成コードの追加

`src/analysis/compare_voting_methods.py`に以下のコードを追加：

```python
# 6. ジニ係数比較の可視化
plt.figure(figsize=(8, 6))
gini_values = [qv_gini, opov_gini]
labels = ['Quadratic Voting', 'One Person One Vote']
colors = ['royalblue', 'darkorange']

plt.bar(labels, gini_values, color=colors)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
plt.ylabel('Gini Coefficient')
plt.title('Inequality Comparison: Gini Coefficient')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('results/figures/comparison/voting_methods_gini_comparison.png', dpi=300, bbox_inches='tight')
print("Saved Gini coefficient comparison graph!")
plt.close()
```

### 2. 欠落スクリプト実行用のバッチファイル作成

`run_missing_analysis.bat`ファイルを作成して、欠落している分析を実行：

```batch
@echo off
echo === QV分析 欠落画像生成スクリプト ===
echo 1. クレジット使用率分析の実行
python src/simulation/neutral_bias/analyze_credit_usage.py
echo.
echo 2. 効用最大化モデル分析の実行
python src/simulation/neutral_bias/simulate_utility_max_model.py
echo.
echo 3. 投票方法比較分析の再実行（ジニ係数グラフ追加）
python src/analysis/compare_voting_methods.py
echo.
echo 欠落画像の生成が完了しました
pause
```

## 次のステップ

1. ジニ係数比較グラフを生成するコードを実装
2. 欠落スクリプト実行用のバッチファイルを作成
3. ファイルが生成されたか検証
4. 必要に応じて`final_report.md`の参照パスを修正
5. 最終検証を実施

## 成功基準

- 全ての参照画像がレポート内のパスと一致している
- 画像の内容が分析結果を正確に表現している
- 次回実行時に同じ問題が発生しないよう、分析スクリプトの実行フローが整理されている 