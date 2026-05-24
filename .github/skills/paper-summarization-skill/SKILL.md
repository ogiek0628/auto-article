---
name: paper-summarization-skill
description: |
  取得した論文を要約・日本語化するスキル。
  「論文を要約して」「論文を日本語で説明して」「キーポイントを日本語で抽出」
  のようなリクエストで発火します。論文の英語要約をCopilotの言語能力で
  日本語に変換し、わかりやすいサマリーを生成します。
license: MIT
---

# AI系論文要約・翻訳スキル

## 目的
取得した英語論文を分かりやすい日本語の要約に変換し、キーポイントを抽出するスキルです。

## 使用方法

### 1. 要約依頼と実行
Copilot Chatで以下のように依頼します：

```
「論文データから3つ選んで日本語で要約して」
「最新のLLM論文の重要ポイントをまとめて」
「このTransformer論文を初心者向けに説明して」
```

### 2. スクリプト実行
[summarize_papers.py](./scripts/summarize_papers.py) を実行：

```bash
python .github/skills/paper-summarization-skill/scripts/summarize_papers.py \
  --input data/papers.json \
  --output data/summaries.json \
  --max-papers 5
```

### 3. 入力形式
`data/papers.json` から取得（paper-research-skillの出力形式）

### 4. 出力形式
`data/summaries.json` に以下形式で保存：

```json
[
  {
    "paper_id": "2406.12345",
    "title_ja": "日本語タイトル",
    "title_en": "Original English Title",
    "summary_ja": "日本語での3-5行の要約",
    "key_points": [
      "重要ポイント1",
      "重要ポイント2",
      "重要ポイント3"
    ],
    "keywords_ja": ["キーワード1", "キーワード2"],
    "difficulty_level": "初級/中級/上級",
    "url": "https://arxiv.org/abs/2406.12345"
  }
]
```

## 要約の品質基準

### 内容
- ✅ 150-300文字の簡潔な日本語要約
- ✅ 初心者にも理解できる言葉遣い
- ✅ 「なぜ重要か」が分かる説明
- ✅ 学術的な正確性を保つ

### キーポイント
- 最大5個までの重要概念
- 論文の中心的な貢献を抽出
- 実用的な応用例があれば記載

### 難易度判定
- 前提知識が少ない → 「初級」
- ML基礎知識が必要 → 「中級」
- 専門的背景が必要 → 「上級」

## 利用テンプレート

[Summary Template](./templates/summary_template.md) を参照してください。

## 注意点
- 翻訳ではなく「要約」です（完全な日本語訳ではありません）
- Copilotの言語モデルを活用するため、専門用語は英語表記で統一
- 複数論文の要約は順次処理（一度に1〜3件推奨）
