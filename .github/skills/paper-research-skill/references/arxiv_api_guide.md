# arXIV API利用ガイド

## 概要

arXIVはセマンティック検索エンジンで、REST APIを通じて論文情報にアクセスできます。

## API仕様

### エンドポイント

```
http://export.arxiv.org/api/query
```

### クエリパラメータ

- `search_query`: 検索条件
- `start`: 開始インデックス（デフォルト：0）
- `max_results`: 取得件数（デフォルト：10、最大：30000）
- `sort_by`: ソート方法（`relevance`/`lastUpdatedDate`/`submittedDate`）
- `sort_order`: 並び順（`ascending`/`descending`）

### カテゴリー

AI/ML関連：

- `cat:cs.AI` - 人工知能
- `cat:cs.LG` - 機械学習
- `cat:cs.NE` - ニューラルネットワーク
- `cat:cs.CL` - 自然言語処理
- `cat:cs.CV` - コンピュータビジョン

### 検索例

```
# Transformerに関する論文
search_query=cat:cs.LG AND all:Transformer&max_results=100

# LLM関連（過去6ヶ月）
search_query=cat:cs.AI AND all:"language model" AND submittedDate:[202410010000 TO 202505010000]

# 特定著者
search_query=au:Yann LeCun
```

## レート制限

- 1秒あたり最大3リクエスト
- 推奨：リクエスト間に3秒以上の間隔

## レスポンス形式

XML形式で返却

```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2406.12345v1</id>
    <title>論文タイトル</title>
    <author><name>著者1</name></author>
    <published>2024-06-15T18:23:14Z</published>
    <summary>論文の要約...</summary>
  </entry>
</feed>
```

## Python実装例

```python
import requests
from feedparser import parse

def fetch_from_arxiv(keyword, max_results=10):
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{keyword}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    response = requests.get(url, params=params)
    feed = parse(response.content)
    return feed.entries
```

## 参考

- [arXIV API Documentation](https://arxiv.org/help/api/)
