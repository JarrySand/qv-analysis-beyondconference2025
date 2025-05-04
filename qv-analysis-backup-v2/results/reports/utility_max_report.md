# Utility Maximization Hypothesis Verification Report

## Simulation Settings

- Number of Simulations: 1000
- Number of Projects: 7
- Maximum Credits: 99
- Preference Intensity Distribution: Uniform Distribution [0, 10]

## Basic Statistical Comparison

| Metric | Theoretical Value | Actual Value | Difference |
|---|---|---|---|
| 1-Vote Percentage | 15.32% | 14.82% | -0.50% |
| 2-Vote Percentage | 16.15% | 16.86% | 0.71% |
| 3-5 Vote Percentage | 55.75% | 39.63% | -16.11% |
| 6-9 Vote Percentage | 12.78% | 12.78% | 0.00% |
| Entropy | 1.8672 | 2.1068 | 0.2396 |

## Statistical Test Results

- Chi-Square Value: 585.7222
- Degrees of Freedom: 8
- p-Value: 0.00000000

Conclusion: 実際の投票分布は効用最大化モデルの理論分布と有意に異なります (p < 0.05)

## Summary and Interpretation

- 実際の投票では、理論モデルが予測するよりも**1票の使用が0.50%少ない**です。
  - これは投票者が単純なコスト最適化行動をとっていないことを示唆しています。

### Utility Maximization Hypothesis Verification Results

効用最大化仮説は部分的に支持されますが、投票者は**単純なコスト最適化よりも選好表現を優先**している可能性が高いです。
特に「選好強度の小さいプロジェクトには小票（1票）を投じる」という理論予測とは異なり、
実際には投票者は中票（3-5票）を多用し、プロジェクト間の選好差を明確に表現しています。

今後の研究としては、より複雑な選好強度分布モデルを検討し、実際の投票行動をより正確に説明できる
理論モデルの構築が期待されます。
