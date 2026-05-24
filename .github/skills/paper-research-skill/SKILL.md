---
name: paper-research-skill
description: |
  AI系論文をarXIVやセマンティック検索から自動取得するスキル。
  「AI論文を検索して」「最新のLLM関連の論文を取得」「機械学習の論文を探して」
  のようなリクエストで発火します。キーワード指定で複数論文の情報を収集し、
  JSONフォーマットで保存します。
license: MIT
---

# AI系論文自動取得スキル

## 目的
arXIVやセマンティック検索を使用してAI関連の最新論文を自動取得し、
メタデータをJSON形式で保存するスキルです。

## 使用方法

### 1. 論文取得の依頼
Copilot Chatで以下のように依頼します：

```
「過去30日間のTransformer関連論文を取得して」
「LLMの最新5件の論文を探してください」
「生成AIに関する論文情報を集めて」
```

### 2. 実行スクリプト
[fetch_papers.py](./scripts/fetch_papers.py) スクリプトを実行します：

```bash
python .github/skills/paper-research-skill/scripts/fetch_papers.py \
  --keyword "Transformer" \
  --max-results 10 \
  --days 30
```

### 3. 出力形式
`data/papers.json` に以下の形式で保存：

```json
[
  {
    "id": "2406.12345",
    "title": "論文タイトル",
    "authors": ["著者1", "著者2"],
    "published": "2024-06-15",
    "summary": "論文の要約...",
    "url": "https://arxiv.org/abs/2406.12345",
    "categories": ["cs.AI", "cs.LG"],
    "citation_count": 5
  }
]
```

## 対応するリソース

- **API**: arXIV API、Semantic Scholar API
- **データソース**: [arXIV](https://arxiv.org)、[Semantic Scholar](https://semanticscholar.org)
- **言語**: 英語（タイトル、要約）
- **更新頻度**: 手動実行またはGitHub Actions（日次）

## 設定情報

詳細はこちらを参照：[API Guide](./references/arxiv_api_guide.md)

### パラメータ

| パラメータ | 説明 | デフォルト |
|-----------|------|----------|
| `keyword` | 検索キーワード（複数指定可） | - |
| `max-results` | 取得件数上限 | 10 |
| `days` | 過去N日間で絞込み | 30 |
| `sort-by` | ソート順（relevance/date） | relevance |

## 注意点

- arXIV APIのレート制限：3秒に1リクエスト
- 英語論文のみ対応（日本語化は別スキルで対応）
- 大量取得時は `--delay` パラメータで間隔を指定
