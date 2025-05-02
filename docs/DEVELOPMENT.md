# 開発ガイド

このドキュメントでは、QV分析プロジェクトのGitHub Pagesサイトをローカルで開発・テストする方法について説明します。

## 前提条件

- Node.js (v14以上)
- npm または yarn

## ローカル開発環境のセットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/tkgshn/qv-analysis-beyondconference2025.git
cd qv-analysis-beyondconference2025
```

2. 必要なツールのインストール
```bash
npm install -g htmlhint
npm install -g live-server
```

## ローカルでのサイト実行

`docs` ディレクトリ内のファイルをローカルサーバーで実行するには：

```bash
cd docs
live-server
```

これにより、ブラウザが自動的に開き、ローカルサーバー上でサイトが表示されます（通常は http://127.0.0.1:8080）。

## ファイル構造

```
docs/
├── index.html          # メインHTMLファイル
├── assets/
│   ├── css/
│   │   └── styles.css  # スタイルシート
│   ├── js/
│   │   └── charts.js   # インタラクティブチャート用JavaScript
│   └── images/         # 画像ファイル
└── .nojekyll           # GitHub Pagesの設定ファイル
```

## HTMLの検証

変更を加えた後、HTMLの検証を行うには：

```bash
htmlhint ./docs/**/*.html
```

## インタラクティブチャートの編集

`charts.js` ファイルには、Plotly.jsを使用した8つのインタラクティブチャートが実装されています：

1. `createBuriedVoicesChart()` - 埋もれた声の可視化
2. `createPreferenceIntensityHeatmap()` - 投票強度の分布ヒートマップ
3. `createPreferenceComparisonChart()` - 選好強度の比較
4. `createBudgetAllocationChart()` - 予算配分の比較
5. `createGiniCoefficientChart()` - ジニ係数による不平等度分析
6. `createLorenzCurveChart()` - ローレンツ曲線
7. `createPercentageComparisonChart()` - パーセンテージ比較
8. `createVoteComparisonChart()` - 得票数比較

各チャートは、サンプルデータを使用して実装されています。実際のデータを使用する場合は、各関数内のデータ配列を更新してください。

## CI/CDワークフロー

このプロジェクトには、GitHub Actionsを使用した簡易的なCI/CDワークフローが設定されています：

1. masterブランチへのプッシュまたはPRがトリガーとなります
2. HTMLの検証が実行されます
3. masterブランチへのプッシュの場合、GitHub Pagesへの自動デプロイが行われます

## プルリクエスト作成時の注意点

1. 新しい機能やバグ修正を行う場合は、新しいブランチを作成してください
2. 変更を加える前に、最新のmasterブランチからプルしてください
3. HTMLの検証が通ることを確認してください
4. チャートの変更を行う場合は、ローカルでの動作確認を行ってください
5. コミットメッセージは変更内容を明確に記述してください

## トラブルシューティング

- **ローカルサーバーが起動しない場合**：Node.jsのバージョンが最新であることを確認してください
- **チャートが表示されない場合**：ブラウザのコンソールでエラーを確認し、Plotly.jsが正しく読み込まれているか確認してください
- **GitHub Pagesにデプロイされない場合**：リポジトリの設定でGitHub Pagesのソースが正しく設定されているか確認してください（Settings > Pages > Source > gh-pages branch）
