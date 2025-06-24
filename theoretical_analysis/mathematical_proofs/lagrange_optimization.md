# ラグランジュ法による最適化問題の解析
## Quadratic Voting における個人の効用最大化

---

## 🎯 問題設定

### 個人の最適化問題

投票者 $i$ は以下の制約付き最適化問題を解く：

$$
\begin{align}
\max_{v_{i1}, v_{i2}, \ldots, v_{i7}} \quad & U_i = \sum_{j=1}^{7} u_{ij} \sqrt{v_{ij}} \\
\text{subject to} \quad & \sum_{j=1}^{7} v_{ij}^2 \leq 99 \\
& v_{ij} \geq 0 \quad \forall j \in \{1,2,\ldots,7\}
\end{align}
$$

### 記号の定義

- $U_i$: 投票者 $i$ の効用
- $u_{ij}$: 投票者 $i$ のプロジェクト $j$ に対する選好強度
- $v_{ij}$: 投票者 $i$ のプロジェクト $j$ への投票数
- $99$: 最大クレジット数（投票コストの上限）

### 基本仮定

1. **選好の独立性**: 各プロジェクトへの選好は独立
2. **効用関数の形**: $U_i = \sum_{j=1}^{7} u_{ij} \sqrt{v_{ij}}$（QVの標準形）
3. **予算制約**: $\sum_{j=1}^{7} v_{ij}^2 \leq 99$（投票コスト制約）
4. **非負制約**: $v_{ij} \geq 0$（負の投票は不可）

---

## 🧮 ラグランジュ関数の構築

### ラグランジュ関数

制約付き最適化問題をラグランジュ関数で表現する：

$$
L(v_{i1}, \ldots, v_{i7}, \lambda, \mu_1, \ldots, \mu_7) = \sum_{j=1}^{7} u_{ij} \sqrt{v_{ij}} - \lambda \left( \sum_{j=1}^{7} v_{ij}^2 - 99 \right) - \sum_{j=1}^{7} \mu_j v_{ij}
$$

### ラグランジュ乗数の意味

- $\lambda \geq 0$: 予算制約のラグランジュ乗数（クレジットの限界効用）
- $\mu_j \geq 0$: プロジェクト $j$ の非負制約のラグランジュ乗数

---

## 📐 KKT条件の導出

### 1次条件（定常条件）

各投票数 $v_{ij}$ に関する偏微分：

$$
\frac{\partial L}{\partial v_{ij}} = \frac{u_{ij}}{2\sqrt{v_{ij}}} - 2\lambda v_{ij} - \mu_j = 0 \quad \forall j
$$

### 相補スラック条件

$$
\begin{align}
\mu_j v_{ij} &= 0 \quad \forall j \\
\lambda \left( \sum_{j=1}^{7} v_{ij}^2 - 99 \right) &= 0
\end{align}
$$

### 実行可能性条件

$$
\begin{align}
\sum_{j=1}^{7} v_{ij}^2 &\leq 99 \\
v_{ij} &\geq 0 \quad \forall j
\end{align}
$$

### 双対実行可能性

$$
\begin{align}
\lambda &\geq 0 \\
\mu_j &\geq 0 \quad \forall j
\end{align}
$$

---

## 🔍 場合分けによる解析

### Case 1: 内点解（$v_{ij} > 0$, $\mu_j = 0$）

相補スラック条件より $\mu_j = 0$ なので、1次条件は：

$$
\frac{u_{ij}}{2\sqrt{v_{ij}}} = 2\lambda v_{ij}
$$

これを $v_{ij}$ について解く：

$$
u_{ij} = 4\lambda v_{ij}^{3/2}
$$

$$
v_{ij}^{3/2} = \frac{u_{ij}}{4\lambda}
$$

$$
v_{ij} = \left( \frac{u_{ij}}{4\lambda} \right)^{2/3}
$$

### Case 2: 境界解（$v_{ij} = 0$）

$v_{ij} = 0$ の場合、1次条件は：

$$
\lim_{v_{ij} \to 0^+} \frac{u_{ij}}{2\sqrt{v_{ij}}} - \mu_j = 0
$$

これが有限となるためには：

$$
u_{ij} = 0 \quad \text{または} \quad \mu_j = +\infty
$$

実際的には、$u_{ij}$ が十分小さい場合に $v_{ij} = 0$ となる。

---

## 🎯 最適解の導出

### ラグランジュ乗数 $\lambda$ の決定

予算制約が等号で成立すると仮定（通常の場合）：

$$
\sum_{j=1}^{7} v_{ij}^2 = 99
$$

内点解の場合：

$$
\sum_{j=1}^{7} \left( \frac{u_{ij}}{4\lambda} \right)^{4/3} = 99
$$

$$
\frac{1}{(4\lambda)^{4/3}} \sum_{j=1}^{7} u_{ij}^{4/3} = 99
$$

$$
\lambda = \frac{1}{4} \left( \frac{\sum_{j=1}^{7} u_{ij}^{4/3}}{99} \right)^{3/4}
$$

### 最適投票数の閉形式解

$$
v_{ij}^* = u_{ij}^{2/3} \left( \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right)^{1/2}
$$

### 境界解の条件

プロジェクト $j$ で $v_{ij} = 0$ となる条件は、内点解で計算した $v_{ij}^*$ が負になる場合、または選好 $u_{ij}$ が他のプロジェクトと比較して十分小さい場合。

---

## ✅ 解の検証

### 制約条件の満足

1. **予算制約**:
   $$
   \sum_{j=1}^{7} (v_{ij}^*)^2 = \sum_{j=1}^{7} u_{ij}^{4/3} \cdot \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} = 99 \quad \checkmark
   $$

2. **非負制約**: 
   $u_{ij} \geq 0$ ならば $v_{ij}^* \geq 0$ $\checkmark$

### 2次条件（十分条件）

効用関数 $U_i = \sum_{j=1}^{7} u_{ij} \sqrt{v_{ij}}$ はそれぞれの変数について凹関数：

$$
\frac{\partial^2 U_i}{\partial v_{ij}^2} = -\frac{u_{ij}}{4v_{ij}^{3/2}} < 0 \quad \text{for } v_{ij} > 0
$$

したがって、制約集合が凸集合であることと合わせて、KKT条件は最適性の十分条件となる。

---

## 🎯 主要結果

### 定理: 最適投票配分

選好ベクトル $\mathbf{u}_i = (u_{i1}, u_{i2}, \ldots, u_{i7})$ が与えられたとき、投票者 $i$ の最適投票配分は：

$$
v_{ij}^* = u_{ij}^{2/3} \left( \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right)^{1/2}
$$

### 重要な性質

1. **比例性**: $v_{ij}^* \propto u_{ij}^{2/3}$
2. **正規化**: $\sum_{j=1}^{7} (v_{ij}^*)^2 = 99$
3. **単調性**: $u_{ij} > u_{ik} \Rightarrow v_{ij}^* > v_{ik}^*$
4. **凹性**: 選好の増加に対する投票数の増加は逓減

---

## 📊 経済学的解釈

### 限界効用均等化

最適解では、すべてのプロジェクトで**クレジットあたりの限界効用**が等しくなる：

$$
\frac{\partial U_i / \partial v_{ij}}{2v_{ij}} = \frac{u_{ij}}{4v_{ij}^{3/2}} = \lambda \quad \forall j \text{ with } v_{ij} > 0
$$

### 投票の集中度

選好の分散が大きいほど、投票はより集中的になる。選好が均等に近いほど、投票は分散的になる。

---

*この解析により、個人レベルでの最適投票配分の数学的基礎が確立された。*
*次のステップでは、この解を用いて確率論的分析を行う。* 