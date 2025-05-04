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