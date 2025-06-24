#!/usr/bin/env python3
"""
切断正規分布の積率計算
Phase 2: 解析的確率論による投票分布の導出

必要な積率:
- E[U^(2/3)]: 投票数の期待値計算用
- E[U^(4/3)]: 分母の期待値計算用  
- E[U^(8/3)]: 分散計算用
- E[U^(10/3)]: 高次モーメント用
"""

import numpy as np
from scipy import integrate
from scipy.stats import norm
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

class TruncatedNormalMoments:
    """切断正規分布の積率計算クラス"""
    
    def __init__(self, mu: float, sigma: float):
        """
        Parameters:
        -----------
        mu : float
            正規分布の平均
        sigma : float  
            正規分布の標準偏差
        """
        self.mu = mu
        self.sigma = sigma
        self.alpha = mu / sigma  # 標準化パラメータ
        self.Z = norm.cdf(self.alpha)  # 正規化定数
        
    def pdf(self, x: float) -> float:
        """切断正規分布の確率密度関数"""
        if x <= 0:
            return 0.0
        return norm.pdf(x, self.mu, self.sigma) / self.Z
    
    def integrand(self, x: float, power: float) -> float:
        """積率計算用の被積分関数"""
        if x <= 0:
            return 0.0
        return (x ** power) * self.pdf(x)
    
    def calculate_moment(self, power: float, max_val: float = 50.0) -> Tuple[float, float]:
        """
        E[U^power] を数値積分で計算
        
        Parameters:
        -----------
        power : float
            べき乗の指数
        max_val : float
            積分の上限（実質的に無限大）
            
        Returns:
        --------
        moment : float
            積率の値
        error : float
            積分誤差の推定値
        """
        result, error = integrate.quad(
            self.integrand, 
            0, 
            max_val, 
            args=(power,),
            epsabs=1e-12,
            epsrel=1e-10
        )
        return result, error
    
    def calculate_all_moments(self) -> Dict[str, Dict[str, float]]:
        """Phase 2で必要なすべての積率を計算"""
        
        powers = [2/3, 4/3, 8/3, 10/3, 1, 2]  # 必要なべき乗
        power_names = ['2/3', '4/3', '8/3', '10/3', '1', '2']
        
        results = {}
        
        print(f"切断正規分布の積率計算")
        print(f"パラメータ: μ = {self.mu}, σ = {self.sigma}")
        print(f"標準化パラメータ α = μ/σ = {self.alpha:.4f}")
        print(f"正規化定数 Φ(α) = {self.Z:.6f}")
        print("-" * 50)
        
        for power, name in zip(powers, power_names):
            moment, error = self.calculate_moment(power)
            results[f'E[U^{name}]'] = {
                'value': moment,
                'error': error,
                'power': power
            }
            print(f"E[U^{name:>4}] = {moment:10.6f} ± {error:.2e}")
        
        # 基本統計量も計算
        mean = results['E[U^1]']['value']
        second_moment = results['E[U^2]']['value']
        variance = second_moment - mean**2
        
        results['mean'] = {'value': mean, 'error': 0, 'power': 1}
        results['variance'] = {'value': variance, 'error': 0, 'power': 0}
        results['std'] = {'value': np.sqrt(variance), 'error': 0, 'power': 0}
        
        print("-" * 50)
        print(f"平均:     {mean:.6f}")
        print(f"分散:     {variance:.6f}")
        print(f"標準偏差: {np.sqrt(variance):.6f}")
        
        return results

def compare_parameters(mu_values: List[float], sigma_values: List[float]) -> pd.DataFrame:
    """異なるパラメータでの積率を比較"""
    
    results = []
    
    for mu in mu_values:
        for sigma in sigma_values:
            calc = TruncatedNormalMoments(mu, sigma)
            moments = calc.calculate_all_moments()
            
            row = {
                'mu': mu,
                'sigma': sigma,
                'alpha': mu/sigma,
                'E[U^(2/3)]': moments['E[U^2/3]']['value'],
                'E[U^(4/3)]': moments['E[U^4/3]']['value'],
                'E[U^(8/3)]': moments['E[U^8/3]']['value'],
                'mean': moments['mean']['value'],
                'variance': moments['variance']['value']
            }
            results.append(row)
            print(f"\n{'='*60}")
    
    return pd.DataFrame(results)

def theoretical_voting_expectation(mu: float, sigma: float, n_projects: int = 7) -> Dict[str, float]:
    """
    理論的投票期待値の近似計算
    
    大数の法則による近似:
    v_ij* ≈ u_ij^(2/3) * sqrt(99 / (7 * E[U^(4/3)]))
    """
    
    calc = TruncatedNormalMoments(mu, sigma)
    moments = calc.calculate_all_moments()
    
    E_U_2_3 = moments['E[U^2/3]']['value']
    E_U_4_3 = moments['E[U^4/3]']['value']
    
    # 大数の法則による近似
    denominator_approx = n_projects * E_U_4_3
    scaling_factor = np.sqrt(99 / denominator_approx)
    
    # 期待投票数の近似
    E_v_approx = E_U_2_3 * scaling_factor
    
    # 総投票数の期待値（1人当たり）
    total_votes_per_person = n_projects * E_v_approx
    
    # 理論的クレジット使用量
    theoretical_credits = n_projects * (E_v_approx ** 2)
    
    results = {
        'E[U^(2/3)]': E_U_2_3,
        'E[U^(4/3)]': E_U_4_3,
        'scaling_factor': scaling_factor,
        'E[v_ij*]_approx': E_v_approx,
        'total_votes_per_person': total_votes_per_person,
        'theoretical_credits': theoretical_credits,
        'credit_efficiency': theoretical_credits / 99
    }
    
    print(f"\n理論的投票期待値の計算")
    print(f"パラメータ: μ = {mu}, σ = {sigma}")
    print("-" * 40)
    print(f"E[U^(2/3)]        = {E_U_2_3:.6f}")
    print(f"E[U^(4/3)]        = {E_U_4_3:.6f}")
    print(f"スケーリング因子  = {scaling_factor:.6f}")
    print(f"E[v_ij*] (近似)   = {E_v_approx:.6f}")
    print(f"1人当たり総投票数 = {total_votes_per_person:.6f}")
    print(f"理論クレジット使用= {theoretical_credits:.6f}")
    print(f"クレジット効率    = {theoretical_credits/99:.1%}")
    
    return results

def visualize_moment_sensitivity():
    """積率のパラメータ感度を可視化"""
    
    # パラメータ範囲
    mu_range = np.linspace(0.5, 3.0, 20)
    sigma_range = np.linspace(0.5, 2.0, 15)
    
    # 結果格納用
    results = {
        'mu_vals': [],
        'sigma_vals': [],
        'E_U_2_3': [],
        'E_U_4_3': [],
        'E_v_approx': []
    }
    
    print("パラメータ感度分析を実行中...")
    
    for mu in mu_range:
        for sigma in sigma_range:
            calc = TruncatedNormalMoments(mu, sigma)
            moments = calc.calculate_all_moments()
            voting_results = theoretical_voting_expectation(mu, sigma)
            
            results['mu_vals'].append(mu)
            results['sigma_vals'].append(sigma)
            results['E_U_2_3'].append(moments['E[U^2/3]']['value'])
            results['E_U_4_3'].append(moments['E[U^4/3]']['value'])
            results['E_v_approx'].append(voting_results['E[v_ij*]_approx'])
    
    # データフレーム化
    df = pd.DataFrame(results)
    
    # 可視化
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # E[U^(2/3)]のヒートマップ
    pivot1 = df.pivot_table(values='E_U_2_3', index='sigma_vals', columns='mu_vals')
    im1 = axes[0,0].imshow(pivot1, cmap='viridis', aspect='auto')
    axes[0,0].set_title('E[U^(2/3)]')
    axes[0,0].set_xlabel('μ')
    axes[0,0].set_ylabel('σ')
    plt.colorbar(im1, ax=axes[0,0])
    
    # E[U^(4/3)]のヒートマップ  
    pivot2 = df.pivot_table(values='E_U_4_3', index='sigma_vals', columns='mu_vals')
    im2 = axes[0,1].imshow(pivot2, cmap='viridis', aspect='auto')
    axes[0,1].set_title('E[U^(4/3)]')
    axes[0,1].set_xlabel('μ')
    axes[0,1].set_ylabel('σ')
    plt.colorbar(im2, ax=axes[0,1])
    
    # E[v_ij*]の近似値
    pivot3 = df.pivot_table(values='E_v_approx', index='sigma_vals', columns='mu_vals')
    im3 = axes[1,0].imshow(pivot3, cmap='plasma', aspect='auto')
    axes[1,0].set_title('E[v_ij*] (近似)')
    axes[1,0].set_xlabel('μ')
    axes[1,0].set_ylabel('σ')
    plt.colorbar(im3, ax=axes[1,0])
    
    # μ/σ比と期待投票数の関係
    df['alpha'] = df['mu_vals'] / df['sigma_vals']
    axes[1,1].scatter(df['alpha'], df['E_v_approx'], alpha=0.6, c=df['sigma_vals'], cmap='coolwarm')
    axes[1,1].set_xlabel('α = μ/σ')
    axes[1,1].set_ylabel('E[v_ij*] (近似)')
    axes[1,1].set_title('標準化パラメータと期待投票数')
    
    plt.tight_layout()
    plt.savefig('results/moment_sensitivity_analysis.png', dpi=300)
    plt.show()
    
    return df

if __name__ == "__main__":
    
    print("=" * 60)
    print("Phase 2: 切断正規分布の積率計算")
    print("=" * 60)
    
    # デフォルトパラメータでの計算
    mu_default, sigma_default = 2.0, 1.0
    
    print(f"\n1. デフォルトパラメータ (μ={mu_default}, σ={sigma_default}) での計算")
    calc_default = TruncatedNormalMoments(mu_default, sigma_default)
    moments_default = calc_default.calculate_all_moments()
    
    print(f"\n2. 理論的投票期待値の計算")
    voting_default = theoretical_voting_expectation(mu_default, sigma_default)
    
    print(f"\n3. パラメータ比較")
    mu_values = [1.0, 1.5, 2.0, 2.5]
    sigma_values = [0.5, 1.0, 1.5]
    comparison_df = compare_parameters(mu_values, sigma_values)
    
    print(f"\n4. 感度分析の実行")
    sensitivity_df = visualize_moment_sensitivity()
    
    # 結果をCSVで保存
    comparison_df.to_csv('results/moment_comparison.csv', index=False)
    sensitivity_df.to_csv('results/sensitivity_analysis.csv', index=False)
    
    print(f"\n計算完了！結果は以下に保存されました:")
    print(f"- results/moment_comparison.csv")
    print(f"- results/sensitivity_analysis.csv")
    print(f"- results/moment_sensitivity_analysis.png") 