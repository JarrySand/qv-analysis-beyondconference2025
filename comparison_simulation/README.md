# 投票方式比較シミュレーション

このフォルダには、Quadratic Voting（QV）方式と従来の一人一票方式の比較シミュレーション結果が含まれています。

## 概要

このシミュレーションでは、実際の投票データをもとに「もし一人一票方式だったら」という仮想シナリオを作成し、QV方式との違いを分析しています。シミュレーションでは、各投票者が最も高い点数を入れたプロジェクトに一票を投じたと仮定し、その結果と実際のQV方式での結果を比較しています。

## コンセプト

このシミュレーションは以下の点を検証するために実施されました：

1. 投票強度（選好の強さ）を表現できる仕組みが結果にどう影響するか
2. 予算配分の公平性（ジニ係数による不平等度の測定）
3. 少数派の声が反映される度合い

## ファイル構成

- `compare_voting_methods.py` - 比較シミュレーションを実行するPythonスクリプト
- `voting_methods_comparison.csv` - QV方式と一人一票方式の比較データ
- `one_person_one_vote_results.csv` - 一人一票方式のシミュレーション結果
- `voting_methods_comparison_report.txt` - 詳細な比較レポート
- 各種グラフ：
  - `voting_methods_vote_comparison.png` - 投票数の比較
  - `voting_methods_budget_comparison.png` - 予算配分の比較
  - `voting_methods_percentage_comparison.png` - パーセンテージの比較
  - `voting_methods_gini_comparison.png` - ジニ係数の比較
  - `voting_methods_lorenz_curve.png` - ローレンツ曲線（不平等度可視化）

## 主な発見

シミュレーションの結果、以下の点が明らかになりました：

1. QV方式では予算配分がより均等になる傾向がある（ジニ係数：QV=0.0774 vs 一人一票=0.2013）
2. 一人一票方式では上位プロジェクトへの集中度が高くなる
3. QV方式は投票者の選好強度を反映するため、少数派でも強い支持があるプロジェクトが適切に評価される

## 使用方法

スクリプトを再実行するには、プロジェクトルートフォルダから以下のコマンドを実行してください：

```
python compare_voting_methods.py
```

実行には以下のファイルが必要です：
- votes.csv
- candidates.csv
- vote_summary.csv
- election.json 