# Utility Maximization Hypothesis Verification Report

## Simulation Settings

- Number of Simulations: 1000
- Number of Projects: 7
- Maximum Credits: 99
- Preference Intensity Distribution: Uniform Distribution [0, 10]

## Basic Statistical Comparison

| Metric | Theoretical Value | Actual Value | Difference |
|---|---|---|---|
| 1-Vote Percentage | 11.36% | 14.87% | 3.51% |
| 2-Vote Percentage | 40.31% | 16.92% | -23.40% |
| 3-5 Vote Percentage | 33.39% | 39.76% | 6.38% |
| 6-9 Vote Percentage | 0.00% | 12.82% | 12.82% |
| Entropy | 1.2636 | 2.0898 | 0.8261 |

## Statistical Test Results

- Chi-Square Value: 146.3175
- Degrees of Freedom: 3
- p-Value: 0.00000000

Conclusion: 実際の投票分布は効用最大化モデルの理論分布と有意に異なります (p < 0.05)

## Summary and Interpretation

- 実際の投票では、理論モデルが予測するよりも**1票の使用が3.51%多い**です。
  - これは「関心の低いプロジェクトにも形式的に投票する」という中立バイアス仮説を支持する可能性があります。
- 中間票（3-5票）の使用が理論値より6.38%多く、投票者は選好の差別化を重視している可能性があります。

### Utility Maximization Hypothesis Verification Results

効用最大化仮説よりも**中立バイアス仮説**がより説明力を持つ可能性があります。
投票者は理論的に予測されるよりも多くの1票を投じており、「関心の低いプロジェクトにも形式的に投票する」
という行動パターンが観察されています。

今後の研究としては、より複雑な選好強度分布モデルを検討し、実際の投票行動をより正確に説明できる
理論モデルの構築が期待されます。
