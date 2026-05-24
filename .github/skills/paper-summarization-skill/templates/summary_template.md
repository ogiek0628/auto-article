# 論文要約テンプレート

## 形式

```json
{
  "paper_id": "ARXIV_ID",
  "title_ja": "日本語タイトル",
  "title_en": "English Title",
  "original_url": "https://arxiv.org/abs/ARXIV_ID",
  "summary_section": {
    "ja": "日本語での要約（150-300文字）",
    "en": "English summary from paper"
  },
  "key_points": {
    "ja": [
      "重要なポイント1",
      "重要なポイント2",
      "重要なポイント3"
    ],
    "en": [
      "Key point 1",
      "Key point 2",
      "Key point 3"
    ]
  },
  "technical_level": {
    "level": "初級|中級|上級",
    "prerequisites": ["前提知識1", "前提知識2"],
    "reason": "このレベルと判断した理由"
  },
  "keywords": {
    "ja": ["キーワード1", "キーワード2", "キーワード3"],
    "en": ["keyword1", "keyword2", "keyword3"]
  },
  "practical_applications": [
    "実用的な応用例1",
    "実用的な応用例2"
  ],
  "metadata": {
    "authors": ["Author 1", "Author 2"],
    "published_date": "2024-06-15",
    "arxiv_categories": ["cs.LG", "cs.AI"],
    "summarized_at": "2024-06-20T10:30:00Z"
  }
}
```

## 具体例

```json
{
  "paper_id": "2406.12345",
  "title_ja": "Transformerの注意機構を改善する新手法",
  "title_en": "Improving Attention Mechanisms in Transformers",
  "original_url": "https://arxiv.org/abs/2406.12345",
  "summary_section": {
    "ja": "このペーパーでは、Transformer のマルチヘッドアテンション機構の計算効率を向上させる新しい手法を提案しています。従来手法では注意スコア計算に O(n²) の計算量が必要でしたが、低ランク分解を用いることで O(n) に削減可能であることを示しました。実験結果から、計算速度を40%削減しながら精度低下は1%以下に抑えられることが確認されています。",
    "en": "This paper proposes a novel method to improve the computational efficiency of multi-head attention mechanisms in Transformers..."
  },
  "key_points": {
    "ja": [
      "マルチヘッドアテンションの計算複雑度を O(n²) から O(n) に削減",
      "低ランク分解により、精度を保ちながらメモリ使用量を削減",
      "大規模言語モデルの推論速度を大幅に改善可能"
    ]
  },
  "technical_level": {
    "level": "中級",
    "prerequisites": ["Transformer の基礎知識", "線形代数（ランク、固有値）"],
    "reason": "注意機構の仕組みを理解している必要があるが、線形代数は基本的な範囲に限定"
  },
  "keywords": {
    "ja": ["Transformer", "注意機構", "計算効率化"],
    "en": ["Transformer", "Attention Mechanism", "Computational Efficiency"]
  },
  "practical_applications": [
    "大規模言語モデル（LLM）の推論高速化",
    "エッジデバイス上での Transformer モデル実行",
    "リアルタイムアプリケーション（質問応答、翻訳）での利用"
  ],
  "metadata": {
    "authors": ["John Smith", "Jane Doe"],
    "published_date": "2024-06-15",
    "arxiv_categories": ["cs.LG", "cs.AI"],
    "summarized_at": "2024-06-20T10:30:00Z"
  }
}
```

## 日本語要約のコツ

### ◎ よい例
- 「注意機構の計算効率を改善した」→ 何を改善したかが明確
- 「従来手法比で40%高速化」→ 定量的な成果を記載
- 「初心者向け」「中級者向け」など難易度明記

### ✗ 悪い例
- 「最先端の手法です」→ 具体性なし
- 「革新的です」→ 評価的すぎる
- テクニカル用語の日本語訳に統一がない

## 活用法

このテンプレートは以下で使用：
1. **記事生成スキル**に入力
2. **GitHubページ**での公開
3. **社内ナレッジベース**への保存
