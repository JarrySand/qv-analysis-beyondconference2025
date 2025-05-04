# 投票パターンバイアス検証研究

## 研究の背景と目的

本研究では、Quadratic Voting（QV）における投票パターンに見られる特徴的な分布、特に小票（1-2票）の使用頻度に注目し、その原因と投票結果への影響を多角的に検証します。

## 観察された現象

- 投票者の半数以上が全7プロジェクトに投票している
- 画像から見る限り、小票（特に1-2票）の使用頻度が高い可能性
- プロジェクト間で得票パターンに差異が見られる

## 仮説群（複数の代替説明）

### 仮説1: 中立バイアス仮説
投票者は関心の低いプロジェクトにも形式的に少数の票を投じる傾向があり、これが投票結果に影響を与えている可能性。

**想定されるメカニズム**:
- クレジット使い切り行動: 残りクレジットの最適配分
- 完全無評価への心理的抵抗: 0票を避ける傾向
- UI/UXの影響: 投票インターフェースが全プロジェクト評価を促進

### 仮説2: 効用最大化仮説
投票者は限られたクレジット（99ポイント）の中で、自身の選好を最も効果的に表現できる投票配分を選択している可能性。

**理論的枠組み**:
- 投票者は各プロジェクトに対する潜在的な「真の選好強度」を持っている
- この選好強度を表現するために、限られたクレジット内で最適な配分を行う
- 投票値とコストの二次関数的関係の中で効用を最大化する配分を選択

**数理モデル**:
```
最大化: ∑(i=1～N) u_i * v_i
制約条件: ∑(i=1～N) v_i^2 ≤ C

ここで:
u_i = プロジェクトiに対する潜在的選好強度（効用係数）
v_i = プロジェクトiへの投票値（1～9）
C = 総クレジット（99）
N = プロジェクト数（7）
```

**最適解の特性**:
- 選好強度に比例した投票値の割り当て：v_i ∝ u_i
- 選好が低いプロジェクトには0票（理論的には）
- クレジット制約が厳しい場合、すべての投票値が均等に抑制される

**予測される投票パターン**:
- 大きな選好差がない場合は、比較的均等な投票配分
- 強い選好を持つプロジェクトがある場合、そのプロジェクトに大票、他に小票
- 投票値が0から1になる「閾値効果」（心理的または実用的な理由から）

### 仮説3: 真の選好反映仮説
小票の多さは投票者の真の選好を反映しており、関心度の差を適切に表現している可能性。

**根拠**:
- 小さい票数でも意識的な差別化を行っている可能性
- 全プロジェクトへの広範な関心が実際に存在する可能性
- QV方式の「二次コスト」を意識した合理的選択の結果である可能性

### 仮説4: 投票戦略仮説
投票者が特定のプロジェクトを有利にするために意図的に他プロジェクトへの投票を調整している可能性。

**考えられる動機**:
- 特定プロジェクトの相対的優位性確保
- グループによる協調投票行動
- 自己のクレジット制約下での最適化行動

### 仮説5: システム理解度仮説
投票システムの理解度の差が投票パターンに影響を与えている可能性。

**考慮すべき要素**:
- QV方式の複雑さと投票者の理解度の関係
- 初回投票経験者と経験者との投票パターンの差異
- 説明やガイダンスの効果

## 効用最大化モデルの詳細分析

### 最適投票戦略の理論的導出

効用最大化仮説の下では、投票者は以下の最適化問題を解く：

```
最大化: U = ∑(i=1～N) u_i * v_i - λ(∑(i=1～N) v_i^2 - C)
```

ラグランジュ乗数法を用いて解くと：

```
∂U/∂v_i = u_i - 2λv_i = 0
よって v_i = u_i/(2λ)
```

制約条件を満たすようにλを決定すると：

```
∑(i=1～N) (u_i/(2λ))^2 = C
λ = (1/2)√(∑(i=1～N) u_i^2/C)
```

したがって、最適投票値は：

```
v_i = u_i/√(∑(i=1～N) u_i^2/C)
```

これにより、潜在的選好強度（u_i）に比例した投票値の配分が理論的に導かれる。

### 理論的な投票値分布

仮に投票者間で選好強度がランダムに分布すると仮定すると：

1. 各投票者は上記の最適化に基づき投票値を決定
2. 全投票者の投票値をプールすると、ある種の連続分布が形成される
3. この分布の形状は選好強度分布に依存する

特に、選好強度が[0,10]の一様分布の場合、投票値も同様の形状を持つ傾向があるが、クレジット制約により高投票値が抑制される。

### 現実の制約要因

理論モデルと現実の乖離を生む可能性のある要因：

1. **認知的制約**: 複雑な最適化計算ではなく、ヒューリスティックな配分
2. **離散化効果**: 投票値は整数（1-9）に限定される
3. **心理的閾値**: 関心が低いものでも0ではなく1を選択する傾向
4. **界面的要因**: UI/UXが全プロジェクトへの投票を促進
5. **社会的規範**: 全プロジェクトを評価すべきという規範的圧力

## 直接検証可能なデータ分析

### 1. クレジット使用率分析

**目的**: 投票者がどの程度クレジットを使い切っているかを検証し、「クレジット使い切り行動」の存在を確認する

**具体的手法**:
```python
# 各投票者のクレジット使用状況を分析
total_credits = 99  # 各投票者に割り当てられた総クレジット
voter_credit_usage = []

for voter_id in votes_df['voter_id'].unique():
    voter_votes = []
    for i in range(len(candidates_df)):
        col_name = f'candidate_{i}'
        if col_name in votes_df.columns:
            vote = votes_df.loc[votes_df['voter_id'] == voter_id, col_name].values[0]
            if not pd.isna(vote):
                voter_votes.append(vote)
    
    # 使用クレジット計算（票の二乗の合計）
    credits_used = sum([vote**2 for vote in voter_votes])
    remaining_credits = total_credits - credits_used
    
    voter_credit_usage.append({
        'voter_id': voter_id,
        'credits_used': credits_used,
        'usage_rate': credits_used / total_credits * 100,
        'remaining_credits': remaining_credits,
        'voted_projects': len(voter_votes),
        'unused_projects': len(candidates_df) - len(voter_votes)
    })

# 使用率の分布分析
usage_df = pd.DataFrame(voter_credit_usage)
```

**検証ポイント**:
- 使用率の分布パターン（高使用率に集中しているか）
- 残クレジットの分布（少量のクレジットが残る傾向があるか）
- クレジット使用率と投票プロジェクト数の相関

### 2. 効用最大化モデルのシミュレーション分析

**目的**: 理論的な効用最大化モデルが予測する投票分布と実際の投票分布を比較し、効用最大化仮説の妥当性を検証する

**具体的手法**:
```python
# 選好強度をシミュレートし、理論的投票値を計算
def simulate_optimal_votes(n_simulations=1000, n_projects=7, max_credits=99):
    simulated_votes = []
    
    for _ in range(n_simulations):
        # ランダムな選好強度を生成
        preferences = np.random.uniform(0, 10, n_projects)
        
        # 最適投票値の計算
        denominator = np.sqrt(np.sum(preferences**2) / max_credits)
        optimal_votes = preferences / denominator
        
        # 投票値の離散化（1-9の整数値に丸める）
        discretized_votes = np.clip(np.round(optimal_votes), 0, 9)
        
        # 投票値0を投票なしとして除外
        positive_votes = discretized_votes[discretized_votes > 0]
        
        simulated_votes.extend(positive_votes)
    
    # 投票値分布の集計
    vote_counts = pd.Series(simulated_votes).value_counts().sort_index()
    return vote_counts
```

**検証ポイント**:
- シミュレーションによる投票値分布と実際の分布の比較
- 特に1票と2票の理論的比率と実際の比率の差異
- クレジット使用率のシミュレーションと実際の使用率の比較

### 3. 選好差別化の測定

**目的**: 投票者が投票を通じてプロジェクト間をどの程度差別化しているかを測定し、効用最大化仮説と中立バイアス仮説を比較する

**具体的手法**:
```python
# 各投票者のプロジェクト間差別化度を計算
differentiation_metrics = []

for voter_id in votes_df['voter_id'].unique():
    voter_votes = []
    for i in range(len(candidates_df)):
        col_name = f'candidate_{i}'
        if col_name in votes_df.columns:
            vote = votes_df.loc[votes_df['voter_id'] == voter_id, col_name].values[0]
            if not pd.isna(vote):
                voter_votes.append(vote)
    
    if len(voter_votes) > 1:
        # 差別化指標の計算
        vote_std = np.std(voter_votes)  # 標準偏差
        vote_range = max(voter_votes) - min(voter_votes)  # 範囲
        vote_entropy = -sum([(v/sum(voter_votes))*np.log2(v/sum(voter_votes)) for v in voter_votes if v > 0])  # エントロピー
        
        differentiation_metrics.append({
            'voter_id': voter_id,
            'vote_std': vote_std,
            'vote_range': vote_range,
            'vote_entropy': vote_entropy,
            'vote_count': len(voter_votes)
        })

diff_df = pd.DataFrame(differentiation_metrics)
```

**検証ポイント**:
- 差別化指標（標準偏差、範囲、エントロピー）の分布
- 高差別化投票者と低差別化投票者の特性比較
- 投票値の分散と最大投票値の関係

### 4. 投票値分布の厳密分析

**目的**: 各投票値（1-9）の出現頻度を分析し、少数票の過剰使用の有無を統計的に検証する

**具体的手法**:
```python
# 投票値の分布分析
vote_values = []
for col in [f'candidate_{i}' for i in range(len(candidates_df))]:
    if col in votes_df.columns:
        # 欠損値を除外
        votes = votes_df[col].dropna().values
        vote_values.extend(votes)

# 投票値別の頻度カウント
vote_counts = pd.Series(vote_values).value_counts().sort_index()
vote_percentages = vote_counts / len(vote_values) * 100

# 効用最大化モデルからの理論的分布との比較
theoretical_distribution = simulate_optimal_votes()
theoretical_percentages = theoretical_distribution / theoretical_distribution.sum() * 100

# 分布間の差異の測定
distribution_diff = vote_percentages - theoretical_percentages

# カイ二乗検定で分布の偏りを検定
from scipy.stats import chisquare
observed = vote_counts.values
expected = theoretical_distribution.reindex(vote_counts.index).values
chi2_stat, p_value = chisquare(observed, expected)
```

**検証ポイント**:
- 1-2票の出現頻度が理論的予測より有意に高いか低いか
- 投票値の分布パターンが効用最大化モデルから予測される分布と一致するか
- プロジェクト間での投票値分布の差異

## 検証アプローチ

### 1. データ特性の多面的分析

1. **投票値分布の詳細分析**:
   - 各投票値（1-9）の出現頻度の分析と理論分布との比較
   - プロジェクト間・投票者間での分布の差異検証
   - 複数の理論モデル（均等分布、効用最大化モデル、べき乗分布等）との比較

2. **投票パターンのクラスター分析**:
   - 投票者の行動パターンによるセグメント化
   - 各セグメントの特徴と投票傾向の関連性分析
   - 極端な投票パターン（全票同一値等）の特定と分析

3. **クレジット使用状況の分析**:
   - 総使用クレジット数の分布分析
   - クレジット使用パターンと投票傾向の相関関係
   - 最大・最小投票値とクレジット使用率の関係
   - 効用最大化の観点からの最適性評価

### 2. 効用最大化モデルの検証

1. **パラメータ逆推定**:
   - 実際の投票パターンから、各投票者の潜在的選好強度を逆算
   - 逆算された選好強度の分布特性分析
   - 効用最大化仮説の下でのモデルフィット評価

2. **複数モデルの比較**:
   - 効用最大化モデル、中立バイアスモデル、均一分布モデルなど複数の理論モデルのAIC/BIC比較
   - クラスター別の最適モデル特定
   - ハイブリッドモデルの構築と評価

3. **シミュレーション実験**:
   - 様々な選好強度分布と制約条件下での理論的投票行動のシミュレーション
   - 実データとの比較による最適パラメータ推定
   - モンテカルロ法による結果の頑健性評価

### 3. 結果評価と含意

1. **仮説間での比較評価**:
   - 各仮説を支持/反証するエビデンスの総合評価
   - 複数仮説の相互作用の可能性検討
   - 最も説明力の高いモデルの特定

2. **現実的影響の評価**:
   - 投票者行動が予算配分にどの程度影響するか
   - 効用最大化と現実行動のギャップが結果に及ぼす影響
   - QV方式の頑健性評価

3. **実践的提言**:
   - 投票者の効用最大化を支援するUI/UX設計
   - 効率的なクレジット配分のためのガイダンス最適化
   - 投票者の選好表現を最大化するためのシステム改善提案

## 検証基準と判断指標

実データから以下の具体的な指標を計算し、仮説の妥当性を判断します：

1. **効用最大化仮説の支持基準**:
   - 投票値分布が効用最大化モデルの理論的予測と統計的に一致する（p>0.05）
   - 投票者の選好強度逆推定値と投票値の相関が強い（r>0.7）
   - クレジット使用率が理論的最適値に近い（差異<10%）
   - 投票値0と1の比率が理論モデルから大きく逸脱しない

2. **中立バイアス仮説の支持基準**:
   - 投票者の80%以上がクレジットの90%以上を使用している
   - 残クレジットが少量（10以下）のユーザーが過半数を占める
   - 1-2票の出現頻度が効用最大化モデルの予測値より統計的に有意に高い（p<0.05）
   - 追加投票可能だったのに投票しなかったケースが少ない（20%未満）

3. **真の選好反映仮説の支持基準**:
   - 投票値の分布がべき乗則などの自然な選好分布に適合する
   - クレジットが十分あるのに投票しなかったプロジェクトが多数存在する
   - 投票パターンが投票者間で大きく異なり、明確な個人差がある
   - 小票（1-2票）と大票（7-9票）の間に負の相関関係がない

4. **投票戦略仮説の支持基準**:
   - 特定プロジェクトへの高投票と他プロジェクトへの低投票に強い相関がある
   - 投票パターンが明確なクラスターを形成している
   - 投票値の分布が戦略的行動を示唆する非自然なパターンを示す

5. **システム理解度仮説の支持基準**:
   - クレジット使用率とプロジェクト投票数の間に強い相関がある
   - 極端なパターン（全て同じ票数など）が一定数存在する
   - 投票値分布が理論的予測から大きく逸脱している

## 実装計画

1. `analyze_credit_usage.py`: クレジット使用率と残クレジット分析
2. `analyze_vote_distribution.py`: 投票値の分布分析と理論分布との比較
3. `simulate_utility_max_model.py`: 効用最大化モデルのシミュレーションと実データとの比較
4. `identify_voting_patterns.py`: 投票パターンの特定とクラスター分析
5. `estimate_preference_strengths.py`: 投票データからの潜在選好強度の逆推定
6. `compare_theoretical_models.py`: 複数理論モデルの比較と評価
7. `visualize_comparative_results.py`: 結果の視覚化と解釈支援

## 期待される知見

1. QV方式における投票行動の理論と実践のギャップの定量化
2. 投票者の意思決定プロセスのより精緻なモデル化
3. 効用最大化を促進するUI/UX設計の指針
4. 集合的意思決定メカニズムの改善に向けた実証的知見 