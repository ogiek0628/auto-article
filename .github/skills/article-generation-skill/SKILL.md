---
name: article-generation-skill
description: |
  論文のまとめを記事形式に整形するスキル。
  「記事を生成して」「Qiita形式の記事にして」「ブログ記事として整形」
  のようなリクエストで発火します。要約データからマークダウン形式の
  公開可能な記事を自動生成します。
license: MIT
---

# AI系論文記事生成スキル

## 目的
要約された論文情報からマークダウン形式のブログ記事を自動生成し、
Qiitaなど公開プラットフォームに投稿可能な状態にするスキルです。

## 使用方法

### 1. 記事生成の依頼
Copilot Chatで以下のように依頼します：

```
「要約データから記事を生成して」
「data/summaries.json をブログ記事に変換」
「Qiita用のマークダウン記事を作成して」
```

### 2. スクリプト実行
[generate_article.py](./scripts/generate_article.py) を実行：

```bash
python .github/skills/article-generation-skill/scripts/generate_article.py \
  --input data/summaries.json \
  --output articles \
  --format markdown
```

### 3. 入力形式
`data/summaries.json` から取得（paper-summarization-skillの出力形式）

### 4. 出力ファイル構成

```
articles/
├── index.md                      # 全記事の一覧
├── 20240620_transformer_attention.md
├── 20240620_llm_optimization.md
└── metadata.json               # 記事メタデータ
```

### 5. 記事フォーマット

記事は以下の構造で生成：

```markdown
# 【AI論文紹介】論文タイトルの日本語版

**原論文**: arxiv ID | **著者**: 著者名 | **公開日**: YYYY-MM-DD

## はじめに
この論文の重要性、背景を簡潔に説明

## 📌 キーポイント
- キーポイント1
- キーポイント2
- キーポイント3

## 论文の概要
日本語要約

## 🛠 技術詳細
どの技術が使われているか、どう改善されたか

## 💡 実用性と応用例
実際にどこで使えるのか

## 難易度・前提知識
- 難易度: 初級/中級/上級
- 必要な前提知識:

## 📚 参考資料
- 原論文: URL
- 関連論文: URL

## まとめ
要点の整理と読者への推奨
```

## SEO最適化

### タグ設定
```
tags: ["AI", "機械学習", "Transformer", "LLM"]
```

### ファイル名規則
```
YYYYMMDD_keyword_keyword.md
例: 20240620_transformer_attention.md
```

## 公開チェックリスト

記事生成後、以下を確認：

- [ ] タイトルが明確で検索されやすい
- [ ] 日本語が自然で分かりやすい
- [ ] 外部リンク（原論文など）が正しい
- [ ] コード例や図が必要な場合は記載
- [ ] タグが3-5個、適切に設定
- [ ] 難易度表示が正確

## 利用テンプレート

[Article Template](./templates/article_template.md) を参照してください。

## 公開先ガイド

### Qiita
- マークダウンファイルをコピー
- タグを `technical`, `AI`, `論文紹介` 等に設定
- 最初の100文字が説明になるよう調整

### ZennまたはNote
- SEO対策済みのフォーマット使用
- 改行・画像挿入を追加

### GitHub Pagesへの自動公開
- GitHub Actions で自動ビルド・デプロイ
- 毎日定時更新（オプション）

## 注意点

- 原論文へのリンクは必ず記載
- 著者・出版日の著作権表記を含める
- 論文内容の改変や部分的な転載はしない
- インターネット公開前に内容確認
