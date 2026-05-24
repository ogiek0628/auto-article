#!/usr/bin/env python3
"""
論文記事生成スクリプト
要約データからマークダウン形式の記事を自動生成
"""

import json
import argparse
import os
from datetime import datetime, timezone
from typing import List, Dict
import re


class ArticleGenerator:
    """論文記事生成クラス"""
    
    def __init__(self):
        self.articles = []
    
    def generate_articles(self, summaries: List[Dict]) -> List[Dict]:
        """要約データから記事を生成"""
        articles = []
        
        for summary in summaries:
            article = self._generate_article(summary)
            articles.append(article)
        
        return articles
    
    def _generate_article(self, summary: Dict) -> Dict:
        """1つの要約から記事を生成"""
        
        title_ja = summary.get("title_ja", "")
        title_en = summary.get("title_en", "")
        paper_id = summary.get("paper_id", "")
        url = summary.get("original_url", "")
        authors = summary.get("metadata", {}).get("authors", [])
        published_date = summary.get("metadata", {}).get("published_date", "")
        categories = summary.get("metadata", {}).get("arxiv_categories", [])
        level = summary.get("technical_level", {}).get("level", "中級")
        key_points = summary.get("key_points", {}).get("ja", [])
        summary_text = summary.get("summary_section", {}).get("ja", "")
        applications = summary.get("practical_applications", [])
        
        # ファイル名生成（日付 + keyword）
        date_str = published_date.replace("-", "")
        keywords = self._extract_keywords(title_en)
        filename = f"{date_str}_{keywords}.md"
        
        # マークダウンコンテンツ生成
        markdown = self._generate_markdown(
            title_ja=title_ja,
            title_en=title_en,
            paper_id=paper_id,
            url=url,
            authors=authors,
            published_date=published_date,
            categories=categories,
            level=level,
            key_points=key_points,
            summary_text=summary_text,
            applications=applications
        )
        
        return {
            "filename": filename,
            "title": title_ja,
            "content": markdown,
            "paper_id": paper_id,
            "published_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_keywords(self, title: str) -> str:
        """タイトルから キーワードを抽出"""
        # 最初の2-3個の単語を取得
        words = title.lower().split()[:2]
        keywords = "_".join(words)
        # 記号を削除
        keywords = re.sub(r'[^a-z0-9_]', '', keywords)
        return keywords
    
    def _generate_markdown(
        self,
        title_ja: str,
        title_en: str,
        paper_id: str,
        url: str,
        authors: List[str],
        published_date: str,
        categories: List[str],
        level: str,
        key_points: List[str],
        summary_text: str,
        applications: List[str]
    ) -> str:
        """マークダウンコンテンツを生成"""
        
        level_emoji = {"初級": "🟢", "中級": "🟡", "上級": "🔴"}
        emoji = level_emoji.get(level, "🟡")
        
        authors_str = ", ".join(authors) if authors else "Unknown"
        
        markdown = f"""---
title: "【AI論文紹介】{title_ja}"
description: "{title_ja}についての詳細解説"
date: {published_date}
tags: ["AI", "機械学習", "論文紹介"]
difficulty: "{level}"
arxiv_id: "{paper_id}"
---

# 【AI論文紹介】{title_ja}

**原論文**: [{paper_id} - {title_en}]({url})  
**著者**: {authors_str}  
**公開日**: {published_date}  
**難易度**: {emoji} {level}

## 概要

このペーパーについての簡潔な説明です。

> {summary_text}

## 📌 キーポイント

"""
        
        for i, point in enumerate(key_points, 1):
            markdown += f"- **ポイント{i}**: {point}\n"
        
        markdown += f"""

## 🌍 実用性と応用例

このペーパーの技術は、以下のような場面で活用可能です：

"""
        
        for app in applications:
            markdown += f"- {app}\n"
        
        markdown += f"""

## 📚 技術背景

### 対象カテゴリ
{", ".join(categories) if categories else "AI/機械学習"}

### 前提知識
- 機械学習の基礎知識
- Transformerについての理解（推奨）

## ✅ まとめ

このペーパーの重要な点：
1. 研究の新規性
2. 実用的な価値
3. 今後の応用可能性

---

## 参考資料

**元論文リンク**: {url}

---

_この記事は自動生成されました。  
誤りの指摘や改善提案は Issues でお願いします。_
"""
        
        return markdown
    
    def save_articles(self, articles: List[Dict], output_dir: str):
        """記事をファイルに保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        for article in articles:
            filepath = os.path.join(output_dir, article["filename"])
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(article["content"])
            
            print(f"✓ 記事生成: {article['filename']}")
        
        # インデックスファイル生成
        self._generate_index(articles, output_dir)
        
        # メタデータ保存
        self._save_metadata(articles, output_dir)
        
        print(f"\n✅ {len(articles)}件の記事を生成: {output_dir}")
    
    def _generate_index(self, articles: List[Dict], output_dir: str):
        """記事インデックスファイルを生成"""
        index = "# 📚 AI論文紹介記事一覧\n\n"
        
        for article in articles:
            filename = article["filename"]
            title = article["title"]
            index += f"- [{title}]({filename})\n"
        
        index_path = os.path.join(output_dir, "index.md")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index)
        
        print(f"✓ インデックス生成: index.md")
    
    def _save_metadata(self, articles: List[Dict], output_dir: str):
        """記事メタデータを保存"""
        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_articles": len(articles),
            "articles": [
                {
                    "filename": a["filename"],
                    "title": a["title"],
                    "paper_id": a["paper_id"]
                }
                for a in articles
            ]
        }
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✓ メタデータ保存: metadata.json")


def main():
    parser = argparse.ArgumentParser(
        description="論文要約から記事を生成"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/summaries.json",
        help="入力ファイル（paper-summarization-skillの出力）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="articles",
        help="出力ディレクトリ"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="markdown",
        choices=["markdown"],
        help="出力フォーマット"
    )
    
    args = parser.parse_args()
    
    # 入力ファイル確認
    if not os.path.exists(args.input):
        print(f"❌ 入力ファイルが見つかりません: {args.input}")
        return
    
    with open(args.input, 'r', encoding='utf-8') as f:
        summaries = json.load(f)
    
    # 記事生成
    generator = ArticleGenerator()
    articles = generator.generate_articles(summaries)
    
    # 保存
    generator.save_articles(articles, args.output)


if __name__ == "__main__":
    main()
