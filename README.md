# Quadratic Voting 分析プロジェクト

## プロジェクト概要

このプロジェクトは、Quadratic Voting（二次投票）の投票結果を分析するためのツールです。ソーシャルセクターの若手起業家を対象としたイベントでの投票データを分析し、効果的な資金配分をサポートします。

## イベント詳細

- **対象**: ソーシャルセクターの若手起業家
- **イベント名**: Beyond Conference 2025
- **開催日**: 2025年4月26日
- **開催場所**: 淡路島
- **投票形式**: ピッチプレゼン後にオーディエンスによるリアルタイム投票
- **投票者**: 他のソーシャルセクター起業家、自治体職員、企業CSR担当者など
- **賞金**: 投票結果に応じて25万円のプール資金が提供される
- **使用ツール**: [qv.geek.sg](https://qv.geek.sg)
- **投票リンク**: https://api.qv.geek.sg/election/0a9885d5-43b4-4b80-b69f-406092002a38
- **投票UID**: 0a9885d5-43b4-4b80-b69f-406092002a38

## 分析目的

このプロジェクトでは、Quadratic Votingによる投票データを分析し、以下の点を明らかにします：

1. 各プロジェクトの支持度合い
2. 投票パターンの分析
3. 資金配分の最適化提案

## 技術スタック

- データ収集: 
  - qv.geek.sgのAPIエンドポイント (`https://api.qv.geek.sg/election/{uid}`) からのデータ取得
  - 投票結果はJSONファイルとして保存済み
- データ分析: Python (pandas, numpy, scipy)
- 可視化: matplotlib

## 主な機能

- 投票データ（election.json）のCSV形式への変換
- 投票パターンの分析
- 予算配分の計算（二次投票方式）
- 統計レポート生成（CSV、テキスト、HTML形式）
- データ可視化（棒グラフ、円グラフ）
- 投票方式の比較シミュレーション（QV vs 一人一票方式）

## ファイル構成

- `convert_to_csv.py` - JSONデータをCSVに変換
- `analyze_votes.py` - 投票データの分析と予算配分計算
- `generate_statistics.py` - 詳細な統計レポート生成
- `check_duplicate_votes.py` - 重複投票分析ツール
- `count_voters.py` - 投票者数の分析ツール
- `comparison_simulation/` - 投票方式比較シミュレーション関連ファイル
  - `compare_voting_methods.py` - QVと一人一票方式の比較分析

## 利用方法

1. election.jsonファイルを配置
2. 各スクリプトを順番に実行:
   ```
   python convert_to_csv.py
   python analyze_votes.py
   python generate_statistics.py
   ```
3. `analysis_results/` ディレクトリに分析結果が生成されます

### 投票方式比較シミュレーション

QV方式と一人一票方式の比較シミュレーションを実行するには:
```
python compare_voting_methods.py
```
比較結果は `comparison_simulation/` ディレクトリに保存されます。このシミュレーションでは、実際の投票データをもとに、各投票者が最も高い点数を入れたプロジェクトに一票を投じたと仮定した場合の投票結果をシミュレートします。これにより、QV方式と従来の一人一票方式の違いを可視化できます。

## 依存ライブラリ

- pandas
- numpy
- scipy
- matplotlib (グラフ生成用)

インストール:
```
pip install pandas numpy scipy matplotlib
```

## ライセンス

MIT 