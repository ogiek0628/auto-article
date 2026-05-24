# トラブルシューティング＆実装ガイド

このドキュメントは、arXIV API の問題が発生した場合の対策と、オンライン動作への移行ガイドです。

## 🔧 API タイムアウト問題が発生した場合

### 原因

arXIV API ( `export.arxiv.org` ) は以下の理由でタイムアウトすることがあります：

1. **ネットワーク遅延** - 地理的な距離、ISP の制限
2. **サーバー負荷** - arXIV サーバーが処理中
3. **API レート制限** - 短時間に大量リクエスト
4. **DNS 解決遅延** - DNS サーバーの応答が遅い

### 解決策

#### ✅ 推奨: オフラインモードを使用

開発・テスト時はオフラインモードが最適です：

```bash
python .github/skills/paper-research-skill/scripts/fetch_papers.py --offline
```

#### オプション1: VPN/プロキシを使用

```bash
# プロキシ経由でアクセス（会社ネットワーク等）
python .github/skills/paper-research-skill/scripts/fetch_papers.py \
  --keywords "LLM" \
  --max-results 5
```

#### オプション2: タイムアウト値を手動調整

スクリプト内で `TIMEOUT = 60` に変更（デフォルト: 30秒）：

```python
# fetch_papers.py の行24
TIMEOUT = 60  # 60秒に増やす
```

#### オプション3: キーワード数を減らす

一度に複数キーワードで検索するとタイムアウトしやすいため：

```bash
# ✗ 避ける（複数キーワード同時）
python fetch_papers.py --keywords "Transformer,LLM,Vision,Diffusion"

# ✓ 推奨（1キーワードずつ）
python fetch_papers.py --keywords "Transformer"
```

## 📡 実際の arXIV API を使う（本番環境向け）

開発完了後、実際のarXIV APIを使用する設定：

### ステップ1: 依存パッケージ確認

```bash
pip install -r requirements.txt
```

### ステップ2: API 実行テスト

```bash
# 最初は30秒のタイムアウトで試す
python .github/skills/paper-research-skill/scripts/fetch_papers.py \
  --keywords "Transformer" \
  --max-results 3 \
  --days 30
```

成功すれば `data/papers.json` にデータが保存されます。

### ステップ3: GitHub Actions で自動実行設定

`.github/workflows/auto-article.yml` で定期実行スケジュールを設定：

```yaml
schedule:
  - cron: "0 2 * * 1" # 毎週月曜 午前2時（UTC）
```

### ステップ4: API リクエスト数の最適化

本番環境では以下を推奨：

```python
# デフォルト設定（推奨）
--keywords "Transformer"        # 1キーワード
--max-results 5                 # 少数（5-10件）
--days 30                       # 1ヶ月間
```

## 📊 API レート制限への対策

arXIV API は以下の制限があります：

- **レート制限**: 3秒に1リクエスト（自動遵守）
- **一度のリクエスト**: 最大1000件まで
- **取得制限**: 1ホストあたり30,000リクエスト/日（十分）

スクリプトは自動的にこれを守っているため、通常は問題ありません：

```python
DELAY = 3  # 3秒待機
MAX_RETRIES = 3  # 3回までリトライ
TIMEOUT = 30  # 30秒でタイムアウト
```

## 🌐 ネットワーク最適化

### DNS キャッシング

Mac/Linux:

```bash
sudo dscacheutil -flushcache
```

### 接続プーリング

スクリプト内で自動設定：

```python
adapter = HTTPAdapter(max_retries=retry_strategy)
self.session.mount("http://", adapter)
```

## ✅ API への移行チェックリスト

```
□ requirements.txt をインストール
□ --offline モードで動作確認
□ オンラインで fetch_papers.py を実行
□ data/papers.json に複数論文が取得された
□ summarize_papers.py が正常に実行
□ generate_article.py が記事を生成
□ articles/*.md に複数の記事が存在
□ GitHub Actions ワークフローを有効化
□ 第1回の自動実行を待つ or 手動実行で確認
```

## 🐛 その他のエラー

### feedparser エラー

```
AttributeError: 'list' object has no attribute 'get'
```

**原因**: arXIV の応答フォーマットが変更

**解決**: feedparser を最新版にアップデート

```bash
pip install --upgrade feedparser
```

### URLエラー

```
urllib3.exceptions.InvalidURL: Invalid URL '...'
```

**原因**: 検索クエリに特殊文字が含まれている

**解決**: キーワードを簡潔に（英数字のみ）

```bash
--keywords "Transformer,LLM"  # OK
--keywords "「視覚」Transformer"  # NG
```

## 📝 ログ確認

スクリプトの詳細ログが必要な場合：

```bash
# 標準出力を ファイルに保存
python fetch_papers.py > api_log.txt 2>&1
```

その後 `api_log.txt` を確認して、どこで失敗しているか特定できます。

---

**質問や問題がある場合**: Issues で報告してください！
