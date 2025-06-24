# 確率論的投票分析の理論的基盤
## Phase 2: 解析的確率論による投票分布の導出

**開始日**: 2025年1月12日  
**Phase**: 2/4 - 解析的確率論  
**前提**: Phase 1の最適解 $v_{ij}^* = u_{ij}^{2/3} \left( \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right)^{1/2}$

---

## 🎯 Phase 2の目標

### 主要目標
1. **選好の確率分布を考慮した投票分布の解析的導出**
2. **期待値 $E[v_{ij}^*]$ の閉形式表現**
3. **分散 $\text{Var}[v_{ij}^*]$ の理論的計算**
4. **集計統計量の理論分布**
5. **実データとの比較可能な理論値の算出**

### 確率論的設定
- **選好分布**: $u_{ij} \sim \text{TruncNormal}(\mu, \sigma^2, 0, \infty)$
- **有権者数**: $N \to \infty$ （大数の法則適用）
- **プロジェクト数**: $J = 7$
- **クレジット**: $C = 99$

---

## 📐 理論的枠組み

### 基本確率構造

各有権者 $i$ の選好ベクトル $\mathbf{u}_i = (u_{i1}, u_{i2}, \ldots, u_{i7})$ について：

$$u_{ij} \sim \text{TruncNormal}(\mu, \sigma^2, 0, \infty) \quad \text{i.i.d.}$$

切断正規分布の密度関数：
$$f(x) = \frac{\phi\left(\frac{x-\mu}{\sigma}\right)}{\sigma \Phi\left(\frac{\mu}{\sigma}\right)}, \quad x > 0$$

ここで $\phi$, $\Phi$ は標準正規分布の密度・累積分布関数。

### 最適投票数の確率的表現

Phase 1の結果より、有権者 $i$ のプロジェクト $j$ への最適投票数：

$$v_{ij}^* = g_j(\mathbf{u}_i) = u_{ij}^{2/3} \left( \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right)^{1/2}$$

これは**確率変数の非線形変換**であり、解析的な分布導出が必要。

---

## 🔍 解析的アプローチ

### 1. 積率生成関数法

選好の積率を利用した期待値計算：

$$E[v_{ij}^*] = E\left[ u_{ij}^{2/3} \left( \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right)^{1/2} \right]$$

### 2. 変数変換法

$Y_k = u_{ik}^{4/3}$ とおくと：
$$S = \sum_{k=1}^{7} Y_k, \quad v_{ij}^* = u_{ij}^{2/3} \sqrt{\frac{99}{S}}$$

### 3. 条件付き期待値法

$$E[v_{ij}^*] = E\left[ E[v_{ij}^*|S] \right]$$

---

## 📊 切断正規分布の積率

### 必要な積率

Phase 2の解析に必要な積率：

1. **$E[U^{2/3}]$**: 投票数の期待値計算
2. **$E[U^{4/3}]$**: 分母の期待値計算
3. **$E[U^{8/3}]$**: 分散計算
4. **$E[U^{10/3}]$**: 高次モーメント

### 切断正規分布の積率公式

$U \sim \text{TruncNormal}(\mu, \sigma^2, 0, \infty)$ に対して：

$$E[U^r] = \sigma^r \sum_{k=0}^{\infty} \frac{(\mu/\sigma)^k}{k!} \frac{\Gamma(r+k+1)}{\Gamma(k+1)} \left(\frac{1}{\sqrt{2\pi}}\right) \frac{1}{\Phi(\mu/\sigma)}$$

ただし、$r = 2/3, 4/3$ などの非整数べき乗では数値積分が必要：

$$E[U^{2/3}] = \frac{1}{\Phi(\mu/\sigma)} \int_0^{\infty} x^{2/3} \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right) dx$$

---

## 🎲 期待値の解析的導出

### Step 1: 条件付き期待値の計算

$S = \sum_{k=1}^{7} u_{ik}^{4/3}$ が与えられた場合：

$$E[v_{ij}^*|S] = E\left[ u_{ij}^{2/3} \sqrt{\frac{99}{S}} \bigg| S \right] = \sqrt{\frac{99}{S}} E[u_{ij}^{2/3}|S]$$

### Step 2: 独立性の利用

$u_{ij}$ と $S$ は独立ではないが、$u_{ij}$ と $S_{-j} = S - u_{ij}^{4/3}$ は独立：

$$E[v_{ij}^*|S_{-j}] = E\left[ u_{ij}^{2/3} \sqrt{\frac{99}{S_{-j} + u_{ij}^{4/3}}} \bigg| S_{-j} \right]$$

### Step 3: 変数変換

$t = u_{ij}^{4/3}$ とおくと、$u_{ij} = t^{3/4}$, $u_{ij}^{2/3} = t^{1/2}$：

$$E[v_{ij}^*|S_{-j}] = E\left[ t^{1/2} \sqrt{\frac{99}{S_{-j} + t}} \bigg| S_{-j} \right]$$

---

## 📈 近似手法

### 1. デルタ法による近似

$g(x) = x^{2/3}$ に対するデルタ法：

$$E[g(U)] \approx g(E[U]) = (E[U])^{2/3}$$

$$\text{Var}[g(U)] \approx [g'(E[U])]^2 \text{Var}[U] = \left[\frac{2}{3}(E[U])^{-1/3}\right]^2 \text{Var}[U]$$

### 2. 大数の法則による近似

有権者数 $N \to \infty$ の場合：

$$\frac{1}{N}\sum_{k=1}^{7} u_{ik}^{4/3} \to E[U^{4/3}] \quad \text{a.s.}$$

したがって：
$$v_{ij}^* \approx u_{ij}^{2/3} \sqrt{\frac{99}{7 \cdot E[U^{4/3}]}}$$

### 3. 中心極限定理の適用

$$\sqrt{N}\left(\frac{1}{N}\sum_{i=1}^{N} v_{ij}^*(\mathbf{u}_i) - E[v_{ij}^*]\right) \xrightarrow{d} N(0, \text{Var}[v_{ij}^*])$$

---

## 🔢 数値積分による厳密計算

### 必要な積分

$$I_{2/3} = E[U^{2/3}] = \int_0^{\infty} x^{2/3} f(x) dx$$

$$I_{4/3} = E[U^{4/3}] = \int_0^{\infty} x^{4/3} f(x) dx$$

### 数値積分の実装

Python/SciPyを使用した数値積分：

```python
from scipy import integrate
from scipy.stats import norm
import numpy as np

def integrand_2_3(x, mu, sigma):
    return x**(2/3) * norm.pdf(x, mu, sigma) / norm.cdf(mu/sigma)

def integrand_4_3(x, mu, sigma):
    return x**(4/3) * norm.pdf(x, mu, sigma) / norm.cdf(mu/sigma)

# 数値積分の実行
I_2_3, _ = integrate.quad(integrand_2_3, 0, np.inf, args=(mu, sigma))
I_4_3, _ = integrate.quad(integrand_4_3, 0, np.inf, args=(mu, sigma))
```

---

## 🎯 集計統計量の理論分布

### プロジェクト別総投票数

有権者数 $N$ のとき、プロジェクト $j$ への総投票数：

$$V_j = \sum_{i=1}^{N} v_{ij}^*$$

大数の法則により：
$$\frac{V_j}{N} \to E[v_{ij}^*] \quad \text{a.s.}$$

中心極限定理により：
$$\sqrt{N}\left(\frac{V_j}{N} - E[v_{ij}^*]\right) \xrightarrow{d} N(0, \text{Var}[v_{ij}^*])$$

### プロジェクト間の相関

$$\text{Cov}[v_{ij}^*, v_{ik}^*] = E[v_{ij}^* v_{ik}^*] - E[v_{ij}^*]E[v_{ik}^*]$$

予算制約により、プロジェクト間の投票は**負の相関**を持つ。

---

## 📋 Phase 2の実行計画

### Step 1: 基本積率の計算 ✓
- 切断正規分布の積率公式の整備
- 数値積分による厳密計算

### Step 2: 期待値の導出 (次)
- $E[v_{ij}^*]$ の解析的表現
- 近似手法との比較

### Step 3: 分散・共分散の計算
- $\text{Var}[v_{ij}^*]$ の導出
- プロジェクト間相関の解析

### Step 4: 集計統計量の理論分布
- 総投票数の期待値・分散
- 理論分布の特性

### Step 5: パラメータ感度分析
- $\mu, \sigma$ の変化に対する感度
- 理論値の安定性検証

---

## 🚀 次のステップ

Phase 2の最初のステップとして、**切断正規分布の積率計算**から開始します。

これにより、Phase 1の決定論的解析を確率論的分析に拡張し、実データとの比較可能な理論値を導出します。

---

*Phase 2 開始: 確率論的投票分析の理論的基盤を構築完了* 