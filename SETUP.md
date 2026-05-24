# GitHub Copilot + Agent Skills 設定ガイド

このプロジェクトを GitHub Copilot で最大限活用するための設定手順です。

## ✅ 前提条件

- GitHub Copilot Pro / Pro+ / Business / Enterprise（有料プラン）
- VS Code 1.108 以上
- Python 3.9 以上

## 📋 設定手順

### 1. VS Code の設定

`.vscode/settings.json` を開いて、以下を追加：

```json
{
  "chat.useAgentSkills": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

### 2. リポジトリで Agent Skills 有効化

- リポジトリを VS Code で開く
- Copilot Chat を開く（`Ctrl+Shift+I` / `Cmd+Shift+I`）
- チャットで `/skills` と入力
- 以下の3つのスキルが表示されることを確認：
  - `paper-research-skill`
  - `paper-summarization-skill`
  - `article-generation-skill`

### 3. GitHub Actions 設定（オプション）

自動実行を有効にするには：

```bash
git add .github/workflows/auto-article.yml
git commit -m "Enable auto-article workflow"
git push origin main
```

GitHub のリポジトリページで `Actions` タブから実行可能になります。

## 🎯 使い方

### パターン1: 手動操作（推奨・初級者向け）

#### ステップ1: 論文を取得

Copilot Chat で：

```
論文を取得してください。キーワードは「Transformer」「LLM」「Attention」で、
過去30日間で、最大5件までお願いします
```

→ Copilotが自動的に `paper-research-skill` を読み込み実行

#### ステップ2: 論文を要約

```
取得した論文を日本語で要約してください
```

→ `paper-summarization-skill` が発動

#### ステップ3: 記事を生成

```
記事を生成して、Qiita形式でお願いします
```

→ `article-generation-skill` が実行

### パターン2: スクリプト直接実行（上級者向け）

```bash
# 1. 論文取得
python .github/skills/paper-research-skill/scripts/fetch_papers.py \
  --keywords "Vision Transformer,ViT" \
  --max-results 5

# 2. 要約テンプレート生成
python .github/skills/paper-summarization-skill/scripts/summarize_papers.py

# 3. 記事生成
python .github/skills/article-generation-skill/scripts/generate_article.py
```

### パターン2-B: オフラインモード（ネットワーク不安定時）

arXIV API へのアクセスが遅い、またはネットワークが不安定な場合、**オフラインモード**を使用できます：

```bash
# 1. 論文取得（オフラインモード - サンプルデータを使用）
python .github/skills/paper-research-skill/scripts/fetch_papers.py --offline

# 2. 要約テンプレート生成
python .github/skills/paper-summarization-skill/scripts/summarize_papers.py

# 3. 記事生成
python .github/skills/article-generation-skill/scripts/generate_article.py
```

**オフラインモードの特徴:**

- インターネット接続不要
- API タイムアウトが発生しない
- サンプル論文データを使用して機能テスト可能
- 本番環境での API 実行前の動作確認に最適

### パターン3: GitHub Actions 自動実行

リポジトリの `Actions` タブから：

1. `Auto Article - Weekly Update` を選択
2. `Run workflow` をクリック
3. パラメータを入力（またはデフォルト使用）
4. `Run workflow` 実行

数分後、PR が自動作成されます。

## 🔍 トラブルシューティング

### Q: Agent Skills が読み込まれない

**A:** 以下を確認してください：

1. ✅ `chat.useAgentSkills` が `true` に設定されている
2. ✅ VS Code を再読み込み（`Cmd/Ctrl+Shift+P` → `Developer: Reload Window`）
3. ✅ チャットで `/skills` を入力して、スキルリストを表示
4. ✅ 各スキルの `description` が Copilot の判断に影響：
   「論文を取得してください」→ paper-research-skill が発動

### Q: Python スクリプト実行時にエラーが出る

**A:** 依存パッケージをインストール：

```bash
pip install -r requirements.txt
```

または：

```bash
python setup_env.py
```

### Q: arXIV API がレート制限される

**A:** スクリプトに組み込まれた遅延（3秒／リクエスト）で対応。  
大量取得の場合は `--delay` パラメータを増加。

### Q: 日本語翻訳の品質が低い

**A:** Copilot Chat で論文ごとに詳細指示を与えてください：

```
この論文を初心者向けに、150文字程度で日本語要約してください。
キーポイントは3つまで、実用例も1-2個含めてください
```

## 🛠 カスタマイズ例

### 検索キーワードをプロジェクト特定に変更

`.github/workflows/auto-article.yml` で：

```yaml
default: "Diffusion Model,Stable Diffusion,Image Generation"
```

### 記事フォーマットを変更

`.github/skills/article-generation-skill/scripts/generate_article.py` で  
`_generate_markdown()` メソッドを編集

### 公開先を Qiita に自動投稿

GitHub Actions に Qiita 認証を追加し、投稿スクリプトを作成  
（要: Qiita API キー）

## 📚 詳細ドキュメント

各スキルの詳細は、スキルディレクトリの `SKILL.md` を参照：

- [論文取得スキル](./.github/skills/paper-research-skill/SKILL.md)
- [要約スキル](./.github/skills/paper-summarization-skill/SKILL.md)
- [記事生成スキル](./.github/skills/article-generation-skill/SKILL.md)

## 💡 ベストプラクティス

### ✅ 推奨方法

- **Copilot Chat を活用**: スクリプト実行より断然簡単
- **段階的に実行**: 論文取得 → 確認 → 要約 → 確認 → 記事化
- **定期実行の活用**: GitHub Actions で週1回の自動更新
- **PR レビュー**: 自動生成後、内容をチェックしてからマージ

### ❌ 避けるべき方法

- 大量キーワードで一度に実行（API制限に引っかかる）
- 手動スクリプト実行と GitHub Actions の同時実行
- 翻訳品質チェックなしで公開

## 🎓 学習リソース

Agent Skills について学びたい場合：

1. [GitHub 公式ドキュメント](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
2. [VS Code Agent Skills ガイド](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
3. [Qiita 記事：30分で理解する Agent Skills](https://qiita.com/ALeX_EXVS/items/943fd31eb4e1639cd5b9)

---

**問題が発生した場合**: Issues でお知らせください！
