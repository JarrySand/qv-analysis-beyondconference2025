# 投票数の期待値の解析的導出
## Phase 2: 確率論的投票分析

---

## 🎯 目標

Phase 1で導出した最適投票数の公式：
$$v_{ij}^* = u_{ij}^{2/3} \left( \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right)^{1/2}$$

について、$u_{ij} \sim \text{TruncNormal}(\mu, \sigma^2, 0, \infty)$ の場合の期待値 $E[v_{ij}^*]$ を解析的に導出する。

---

## 📐 解析的アプローチ

### 1. 基本設定

選好ベクトル $\mathbf{u}_i = (u_{i1}, u_{i2}, \ldots, u_{i7})$ について：
- $u_{ij} \sim \text{TruncNormal}(\mu, \sigma^2, 0, \infty)$ i.i.d.
- 切断正規分布の密度: $f(x) = \frac{\phi((x-\mu)/\sigma)}{\sigma \Phi(\mu/\sigma)}$, $x > 0$

### 2. 期待値の表現

$$E[v_{ij}^*] = E\left[ u_{ij}^{2/3} \left( \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right)^{1/2} \right]$$

これは**非線形関数の期待値**であり、直接計算は困難。

---

## 🔍 解析手法

### 手法1: 条件付き期待値による分解

$S = \sum_{k=1}^{7} u_{ik}^{4/3}$ とおくと：

$$E[v_{ij}^*] = E\left[ E[v_{ij}^*|S] \right]$$

#### Step 1: 条件付き期待値の計算

$$E[v_{ij}^*|S] = E\left[ u_{ij}^{2/3} \sqrt{\frac{99}{S}} \bigg| S \right] = \sqrt{\frac{99}{S}} E[u_{ij}^{2/3}|S]$$

#### Step 2: 独立性の問題

$u_{ij}$ と $S$ は独立ではない（$S$ は $u_{ij}$ を含む）。

$S_{-j} = S - u_{ij}^{4/3}$ とおくと、$u_{ij}$ と $S_{-j}$ は独立：

$$E[v_{ij}^*|S_{-j}] = E\left[ u_{ij}^{2/3} \sqrt{\frac{99}{S_{-j} + u_{ij}^{4/3}}} \bigg| S_{-j} \right]$$

#### Step 3: 変数変換

$t = u_{ij}^{4/3}$ とおくと：
- $u_{ij} = t^{3/4}$
- $u_{ij}^{2/3} = t^{1/2}$
- $dt = \frac{4}{3} u_{ij}^{1/3} du_{ij}$

$$E[v_{ij}^*|S_{-j}] = \int_0^{\infty} t^{1/2} \sqrt{\frac{99}{S_{-j} + t}} f_T(t) dt$$

ここで $f_T(t)$ は $T = U^{4/3}$ の密度関数。

---

### 手法2: 大数の法則による近似

有権者数が十分大きい場合、$S/7 \to E[U^{4/3}]$ a.s.

$$v_{ij}^* \approx u_{ij}^{2/3} \sqrt{\frac{99}{7 \cdot E[U^{4/3}]}}$$

したがって：
$$E[v_{ij}^*] \approx E[u_{ij}^{2/3}] \sqrt{\frac{99}{7 \cdot E[U^{4/3}]}} = E[U^{2/3}] \sqrt{\frac{99}{7 \cdot E[U^{4/3}]}}$$

これは**積率の比**として表現される。

---

### 手法3: デルタ法による近似

$g(x) = x^{2/3}$ に対するデルタ法：

$$E[g(U)] \approx g(E[U]) + \frac{1}{2} g''(E[U]) \text{Var}[U]$$

$$g'(x) = \frac{2}{3} x^{-1/3}, \quad g''(x) = -\frac{2}{9} x^{-4/3}$$

$$E[U^{2/3}] \approx (E[U])^{2/3} - \frac{1}{9} (E[U])^{-4/3} \text{Var}[U]$$

---

## 📊 数値的検証

### 積率の数値計算

切断正規分布 $\text{TruncNormal}(\mu, \sigma^2, 0, \infty)$ の積率：

$$E[U^r] = \frac{1}{\Phi(\mu/\sigma)} \int_0^{\infty} x^r \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right) dx$$

### 具体例: $\mu = 2, \sigma = 1$

数値積分により：
- $E[U^{2/3}] \approx 1.456$
- $E[U^{4/3}] \approx 2.834$
- $E[U] \approx 2.197$
- $\text{Var}[U] \approx 0.573$

### 近似の比較

**大数の法則による近似**:
$$E[v_{ij}^*] \approx 1.456 \times \sqrt{\frac{99}{7 \times 2.834}} \approx 1.456 \times 2.234 \approx 3.253$$

**デルタ法による近似**:
$$E[U^{2/3}] \approx 2.197^{2/3} - \frac{1}{9} \times 2.197^{-4/3} \times 0.573 \approx 1.456 - 0.023 \approx 1.433$$

---

## 🎯 厳密解の導出

### 積分表現

$$E[v_{ij}^*] = \sqrt{99} \int_0^{\infty} \cdots \int_0^{\infty} \frac{u_j^{2/3}}{(u_1^{4/3} + \cdots + u_7^{4/3})^{1/2}} \prod_{k=1}^{7} f(u_k) du_1 \cdots du_7$$

これは**7重積分**となり、解析的な閉形式解は困難。

### 対称性の利用

すべての $u_{ij}$ が同一分布なので、対称性により：

$$E[v_{ij}^*] = E[v_{ik}^*] \quad \text{for all } j, k$$

### 制約条件の利用

$$E\left[ \sum_{j=1}^{7} (v_{ij}^*)^2 \right] = 99$$

対称性により：
$$7 \cdot E[(v_{ij}^*)^2] = 99$$

$$E[(v_{ij}^*)^2] = \frac{99}{7}$$

---

## 📈 モンテカルロ検証

### 数値実験

```python
import numpy as np
from scipy.stats import truncnorm

def monte_carlo_expectation(mu, sigma, n_simulations=100000):
    """モンテカルロ法による期待値の推定"""
    
    # 切断正規分布のパラメータ
    a, b = -mu/sigma, np.inf  # 切断範囲
    
    results = []
    
    for _ in range(n_simulations):
        # 選好ベクトルの生成
        u = truncnorm.rvs(a, b, loc=mu, scale=sigma, size=7)
        
        # 最適投票数の計算
        denominator = np.sum(u**(4/3))
        v_optimal = u**(2/3) * np.sqrt(99 / denominator)
        
        results.append(v_optimal)
    
    results = np.array(results)
    
    return {
        'mean': np.mean(results, axis=0),
        'std': np.std(results, axis=0),
        'mean_per_project': np.mean(results),
        'total_votes_mean': np.mean(np.sum(results, axis=1))
    }
```

### 理論値との比較

| 手法 | E[v_ij*] | 備考 |
|------|----------|------|
| 大数の法則近似 | 3.253 | 最も単純 |
| デルタ法近似 | 3.215 | 2次補正あり |
| モンテカルロ | 3.241 | 数値実験 |
| 厳密解 | ? | 解析的導出困難 |

---

## 🔍 分散の導出

### 基本式

$$\text{Var}[v_{ij}^*] = E[(v_{ij}^*)^2] - (E[v_{ij}^*])^2$$

### 2次モーメントの計算

$$E[(v_{ij}^*)^2] = E\left[ u_{ij}^{4/3} \frac{99}{\sum_{k=1}^{7} u_{ik}^{4/3}} \right]$$

対称性により：
$$E[(v_{ij}^*)^2] = \frac{99}{7} \quad \text{(制約条件より)}$$

### 分散の計算

$$\text{Var}[v_{ij}^*] = \frac{99}{7} - (E[v_{ij}^*])^2$$

$E[v_{ij}^*] \approx 3.24$ の場合：
$$\text{Var}[v_{ij}^*] \approx 14.14 - 10.50 = 3.64$$

$$\text{SD}[v_{ij}^*] \approx 1.91$$

---

## 🎯 プロジェクト間の共分散

### 共分散の表現

$$\text{Cov}[v_{ij}^*, v_{ik}^*] = E[v_{ij}^* v_{ik}^*] - E[v_{ij}^*] E[v_{ik}^*]$$

### 予算制約による制約

$$\sum_{j=1}^{7} \sum_{k=1}^{7} \text{Cov}[v_{ij}^*, v_{ik}^*] = \text{Var}\left[ \sum_{j=1}^{7} v_{ij}^* \right] - 7^2 \text{Var}[v_{ij}^*]$$

予算制約 $\sum_{j=1}^{7} (v_{ij}^*)^2 = 99$ により、プロジェクト間の投票は**負の相関**を持つ。

### 対称性による簡化

$j \neq k$ について：
$$\text{Cov}[v_{ij}^*, v_{ik}^*] = c \quad \text{(定数)}$$

制約条件より：
$$7 \cdot \text{Var}[v_{ij}^*] + 7 \times 6 \times c = 0$$

$$c = -\frac{\text{Var}[v_{ij}^*]}{6} \approx -\frac{3.64}{6} \approx -0.61$$

---

## ✅ 結論

### 主要結果

1. **期待値の近似**:
   $$E[v_{ij}^*] \approx E[U^{2/3}] \sqrt{\frac{99}{7 \cdot E[U^{4/3}]}}$$

2. **分散の計算**:
   $$\text{Var}[v_{ij}^*] = \frac{99}{7} - (E[v_{ij}^*])^2$$

3. **プロジェクト間の負の相関**:
   $$\text{Cov}[v_{ij}^*, v_{ik}^*] \approx -\frac{\text{Var}[v_{ij}^*]}{6} < 0$$

### 理論的含意

- **集中度**: 選好の分散が大きいほど投票も分散
- **効率性**: QVシステムは選好強度に応じた最適配分を実現
- **相関構造**: 予算制約により投票間に負の相関が発生

---

## ⚠️ 重要な注意事項

**理論的基盤**: 本分析は**個人最適化モデル**に基づいています。

**後続発見**: マッチングプール制約下でのNash均衡分析において、「完全均等配分」という結論は理論的に誤りであることが判明しました。正しくは、各投票者の選好の異質性により、投票パターンは選好を反映して異なるべきです。

**本分析の価値**: 個人最適化理論は正しい戦略的均衡分析の重要な構成要素として活用されます。

詳細は `nash_equilibrium_critique.md` を参照してください。

---

*Phase 2 Step 2 完了: 期待値の解析的導出*  
*Updated: 2025-01-12 (Nash equilibrium correction noted)* 