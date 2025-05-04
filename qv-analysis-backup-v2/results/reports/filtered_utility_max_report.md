# Utility Maximization Hypothesis Verification Report

## Simulation Settings

- Number of Simulations: 1000
- Number of Projects: 7
- Maximum Credits: 99
- Preference Intensity Distribution: Uniform Distribution [0, 10]

## Basic Statistical Comparison

| Metric | Theoretical Value | Actual Value | Difference |
|---|---|---|---|
| 1-Vote Percentage | 15.32% | 17.62% | 2.30% |
| 2-Vote Percentage | 16.15% | 20.05% | 3.90% |
| 3-5 Vote Percentage | 55.75% | 47.13% | -8.62% |
| 6-9 Vote Percentage | 12.78% | 15.20% | 2.42% |
| Entropy | 1.8672 | 1.9631 | 0.0959 |

## Statistical Test Results

- Chi-Square Value: 585.7222
- Degrees of Freedom: 8
- p-Value: 0.00000000

Conclusion: 実際の投票分布は効用最大化モデルの理論分布と有意に異なります (p < 0.05)

## Summary and Interpretation

- 実際の投票では、理論モデルが予測するよりも**1票の使用が2.30%多い**です。
  - これは「関心の低いプロジェクトにも形式的に投票する」という中立バイアス仮説を支持する可能性があります。

### Utility Maximization Hypothesis Verification Results

効用最大化仮説よりも**中立バイアス仮説**がより説明力を持つ可能性があります。
投票者は理論的に予測されるよりも多くの1票を投じており、「関心の低いプロジェクトにも形式的に投票する」
という行動パターンが観察されています。

今後の研究としては、より複雑な選好強度分布モデルを検討し、実際の投票行動をより正確に説明できる
理論モデルの構築が期待されます。
