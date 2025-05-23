# Utility Maximization Hypothesis Verification Report

## Simulation Settings

- Number of Simulations: 1000
- Number of Projects: 7
- Maximum Credits: 99
- Preference Intensity Distribution: Uniform Distribution [0, 10]

## Basic Statistical Comparison

| Metric | Theoretical Value | Actual Value | Difference |
|---|---|---|---|
| 1-Vote Percentage | 14.89% | 14.87% | -0.02% |
| 2-Vote Percentage | 16.10% | 16.92% | 0.82% |
| 3-5 Vote Percentage | 56.72% | 39.76% | -16.95% |
| 6-9 Vote Percentage | 12.30% | 12.82% | 0.52% |
| Entropy | 1.8573 | 2.0898 | 0.2325 |

## Statistical Test Results

- Chi-Square Value: 1409.6795
- Degrees of Freedom: 8
- p-Value: 0.00000000

Conclusion: 実際の投票分布は効用最大化モデルの理論分布と有意に異なります (p < 0.05)

## Summary and Interpretation

- 実際の投票では、理論モデルが予測するよりも**1票の使用が0.02%少ない**です。
  - これは投票者が単純なコスト最適化行動をとっていないことを示唆しています。

### Utility Maximization Hypothesis Verification Results

効用最大化仮説は部分的に支持されますが、投票者は**単純なコスト最適化よりも選好表現を優先**している可能性が高いです。
特に「選好強度の小さいプロジェクトには小票（1票）を投じる」という理論予測とは異なり、
実際には投票者は中票（3-5票）を多用し、プロジェクト間の選好差を明確に表現しています。

今後の研究としては、より複雑な選好強度分布モデルを検討し、実際の投票行動をより正確に説明できる
理論モデルの構築が期待されます。
