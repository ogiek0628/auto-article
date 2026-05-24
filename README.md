# Auto Article - AI論文自動収集・記事化システム

GitHub Copilot + Agent Skills を活用した、AI系論文の自動収集・要約・記事化システムです。

## 🎯 目的

- 📰 arXIV から最新AI論文を自動取得
- 🌍 英語論文を日本語で簡潔に要約
- ✍️ マークダウン形式のブログ記事を自動生成
- 🚀 GitHub Pages や Qiita への公開準備

## 🏗️ システム構成

### 3つのAgent Skill

```
┌─────────────────────────────────────────┐
│   paper-research-skill                   │
│   論文検索・取得（arXIV API）            │
└──────────┬──────────────────────────────┘
           ↓ data/papers.json
┌─────────────────────────────────────────┐
│  paper-summarization-skill               │
│  要約・日本語化（Copilot Chat）         │
└──────────┬──────────────────────────────┘
           ↓ data/summaries.json
┌─────────────────────────────────────────┐
│  article-generation-skill                │
│  ブログ記事生成（マークダウン）         │
└──────────┬──────────────────────────────┘
           ↓ articles/*.md
┌─────────────────────────────────────────┐
│  GitHub Pages / Qiita                    │
│  公開・シェア                             │
└─────────────────────────────────────────┘
```

## 📁 ディレクトリ構造

```
.github/
├── skills/
│   ├── paper-research-skill/
│   │   ├── SKILL.md                    # スキル定義
│   │   ├── scripts/
│   │   │   └── fetch_papers.py         # arXIV API連携
│   │   └── references/
│   │       └── arxiv_api_guide.md      # API仕様書
│   ├── paper-summarization-skill/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── summarize_papers.py
│   │   └── templates/
│   │       └── summary_template.md
│   └── article-generation-skill/
│       ├── SKILL.md
│       ├── scripts/
│       │   └── generate_article.py
│       └── templates/
│           └── article_template.md
└── workflows/
    └── auto-article.yml               # GitHub Actions 定義

data/
├── papers.json                         # 取得した論文情報
└── summaries.json                      # 要約済み論文情報

articles/
├── index.md                            # 記事一覧
├── 20240620_transformer_*.md           # 生成された記事
└── metadata.json                       # 記事メタデータ
```

## 🚀 クイックスタート

### 1. 環境構築

```bash
# リポジトリをクローン
git clone https://github.com/your-org/auto-article.git
cd auto-article

# 依存パッケージをインストール
python setup_env.py
# または
pip install -r requirements.txt
```

### 2. Copilot の設定

VS Code で以下の設定を確認：

```json
{
  "chat.useAgentSkills": true
}
```

### 3. 論文取得（手動実行例）

```bash
python .github/skills/paper-research-skill/scripts/fetch_papers.py \
  --keywords "Transformer,BERT,GPT" \
  --max-results 10 \
  --days 30 \
  --output data/papers.json
```

**ネットワークが不安定な場合はオフラインモード:**

```bash
python .github/skills/paper-research-skill/scripts/fetch_papers.py \
  --offline \
  --output data/papers.json
```

### 4. 要約テンプレート生成

```bash
python .github/skills/paper-summarization-skill/scripts/summarize_papers.py \
  --input data/papers.json \
  --output data/summaries.json
```

**次のステップ**: Copilot Chat を開いて以下を実行

```
「data/summaries.json の論文を日本語で要約して」
```

### 5. 記事生成

```bash
python .github/skills/article-generation-skill/scripts/generate_article.py \
  --input data/summaries.json \
  --output articles
```

## 💬 Copilot Chat での利用例

### 例1: 論文検索

```
「過去30日間のTransformer関連論文を10件取得してください」

Copilotが自動的に paper-research-skill を読み込み、
スクリプトを実行して data/papers.json を生成します
```

### 例2: 要約・翻訳

```
「data/summaries.json の論文を日本語で要約してください」

paper-summarization-skill を読み込み、
各論文の日本語要約とキーポイントを生成します
```

### 例3: 記事生成

```
「要約データからブログ記事を生成して」

article-generation-skill を読み込み、
マークダウン形式の記事を articles/ に出力します
```

## 🔄 自動実行（GitHub Actions）

`.github/workflows/auto-article.yml` により、以下が自動実行：

- **スケジュール実行**: 毎週月曜 09:00 UTC
- **手動トリガー**: workflow_dispatch で任意のタイミング実行
- **入力パラメータ**:
  - `keywords`: 検索キーワード（デフォルト: "Transformer,LLM,neural network"）
  - `max_results`: 取得件数（デフォルト: 10）

### 実行結果

自動実行後、以下が作成：

1. `data/papers.json` - 取得論文
2. `data/summaries.json` - 要約テンプレート
3. `articles/*.md` - 生成記事
4. Pull Request - マージ前のレビュー用

## 📊 出力フォーマット

### papers.json

```json
[
  {
    "id": "2406.12345",
    "title": "Improving Attention in Transformers",
    "authors": ["Author1", "Author2"],
    "published": "2024-06-15",
    "summary": "Abstract text...",
    "url": "https://arxiv.org/abs/2406.12345",
    "categories": ["cs.LG", "cs.AI"],
    "fetched_at": "2024-06-20T10:30:00"
  }
]
```

### summaries.json

```json
[
  {
    "paper_id": "2406.12345",
    "title_ja": "[要翻訳] タイトル",
    "title_en": "English Title",
    "summary_section": {
      "ja": "[Copilot Chatで翻訳してください]",
      "en": "Abstract text..."
    },
    "key_points": {
      "ja": ["[要翻訳]"],
      "en": ["Key point 1"]
    },
    "technical_level": {
      "level": "初級|中級|上級",
      "prerequisites": ["[要判定]"],
      "reason": "[要入力]"
    }
  }
]
```

### articles/\*.md

マークダウン形式のブログ記事

```markdown
# 【AI論文紹介】論文タイトルの日本語版

**原論文**: [2406.12345](https://arxiv.org/abs/2406.12345)  
**著者**: Author1, Author2  
**難易度**: 🟡 中級

## 概要

...
```

## ⚙️ カスタマイズ

### キーワード変更

GitHub Actions で手動実行時：

```
Actions > Auto Article - Weekly Update > Run workflow
  → keywords に検索したいキーワードを入力
  → Run workflow
```

### 定期実行スケジュール変更

`.github/workflows/auto-article.yml` の `cron` 値を変更：

```yaml
schedule:
  - cron: "0 9 * * 1" # 月曜 09:00 UTC → 好きな日時に変更
```

[Cron Expression Generator](https://crontab.guru)

### 対象API変更

現在: arXIV API

希望があれば、以下も追加可能：

- Semantic Scholar API
- Google Scholar スクレイピング
- OpenAlex API

## 📚 参考資料

### Agent Skills 仕様

- [agentskills.io](https://agentskills.io)
- [GitHub Copilot - About Agent Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)

### arXIV API

- [arXIV API Documentation](https://arxiv.org/help/api/)

### GitHub Copilot 活用

- [GitHub Copilot Chat の使い方](https://docs.github.com/en/copilot/using-copilot/using-copilot-chat)

## 🤝 貢献

改善提案やバグ報告は Issues でお願いします。

## 📝 ライセンス

MIT License

---

**Quick Links:**

- 📖 [Agent Skills Guide](.github/skills/paper-research-skill/SKILL.md)
- 🔧 [API Configuration](.github/skills/paper-research-skill/references/arxiv_api_guide.md)
- 📝 [Article Templates](.github/skills/article-generation-skill/templates/article_template.md)
- 🛠️ [Setup Guide](./SETUP.md)
