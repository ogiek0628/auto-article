#!/usr/bin/env python3
"""
AI系論文自動取得スクリプト
arXIV APIを使用して論文情報を収集し、JSONで保存
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import argparse
import time
from datetime import datetime, timedelta
from typing import List, Dict
import feedparser
import os

class ArXivFetcher:
    """arXIV APIからの論文取得クラス"""
    
    BASE_URL = "http://export.arxiv.org/api/query"  # HTTP を使用（HTTPS より安定）
    DELAY = 3  # APIレート制限: 3秒に1リクエスト
    TIMEOUT = 30  # タイムアウト(秒)
    MAX_RETRIES = 3  # リトライ回数
    
    def __init__(self):
        self.session = requests.Session()
        # コネクションプールの設定
        # リトライ戦略の設定
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=1,  # 1秒, 2秒, 4秒でリトライ
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def fetch_papers(
        self,
        keywords: List[str],
        max_results: int = 10,
        days: int = 30,
        sort_by: str = "submittedDate"
    ) -> List[Dict]:
        """
        論文を検索して取得
        
        Args:
            keywords: 検索キーワードリスト
            max_results: 取得件数上限
            days: 過去N日間で絞込み
            sort_by: ソート順（submittedDate/relevance）
        
        Returns:
            論文情報のリスト
        """
        papers = []
        
        # 過去N日の日付を計算
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        date_filter = cutoff_date.strftime("%Y%m%d0000")
        today = datetime.utcnow().strftime("%Y%m%d0000")
        
        for keyword in keywords:
            print(f"🔍 検索中: {keyword}")
            
            # 検索クエリの構築
            search_query = f"all:{keyword} AND submittedDate:[{date_filter} TO {today}]"
            
            params = {
                "search_query": search_query,
                "start": 0,
                "max_results": max_results,
                "sortBy": sort_by,
                "sortOrder": "descending"
            }
            
            # リトライロジック付きで API を呼び出し
            success = False
            for attempt in range(1, self.MAX_RETRIES + 1):
                try:
                    response = self.session.get(
                        self.BASE_URL,
                        params=params,
                        timeout=self.TIMEOUT
                    )
                    response.raise_for_status()
                    
                    feed = feedparser.parse(response.content)
                    
                    for entry in feed.entries:
                        paper = self._parse_entry(entry)
                        papers.append(paper)
                        print(f"  ✓ {paper['title'][:50]}...")
                    
                    success = True
                    break  # 成功したらリトライループを抜ける
                    
                except requests.exceptions.Timeout:
                    print(f"  ⏱️ タイムアウト (試行 {attempt}/{self.MAX_RETRIES})")
                    if attempt < self.MAX_RETRIES:
                        wait_time = 2 ** attempt  # 2秒, 4秒, 8秒でバックオフ
                        print(f"  → {wait_time}秒後に再試行します...")
                        time.sleep(wait_time)
                    else:
                        print(f"  ❌ {self.MAX_RETRIES}回のリトライも失敗しました")
                        
                except requests.exceptions.RequestException as e:
                    print(f"  ❌ エラー (試行 {attempt}): {type(e).__name__}")
                    if attempt <  self.MAX_RETRIES:
                        wait_time = 2 ** attempt
                        print(f"  → {wait_time}秒後に再試行します...")
                        time.sleep(wait_time)
                    else:
                        print(f"  ❌ リトライ失敗: {e}")
            
            # APIレート制限に対応
            if success:
                time.sleep(self.DELAY)
        
        return papers
    
    def _parse_entry(self, entry) -> Dict:
        """
        arXIVのエントリをパース
        """
        paper_id = entry.id.split('/abs/')[-1]
        
        authors = [author.name for author in entry.get('authors', [])]
        
        # タイトルのクリーンアップ（改行削除）
        title = entry.title.replace('\n', ' ').strip()
        
        # 要約のクリーンアップ
        summary = entry.summary.replace('\n', ' ').strip()
        
        # カテゴリを取得
        categories = [tag['term'].split('/')[1] for tag in entry.get('tags', [])]
        
        return {
            "id": paper_id,
            "title": title,
            "authors": authors,
            "published": entry.published[:10],  # YYYY-MM-DD形式
            "summary": summary,
            "url": f"https://arxiv.org/abs/{paper_id}",
            "categories": categories,
            "fetched_at": datetime.utcnow().isoformat()
        }
    
    def save_papers(self, papers: List[Dict], output_path: str):
        """
        論文情報をJSONで保存
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ {len(papers)}件の論文を保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="AI系論文をarXIVから自動取得"
    )
    parser.add_argument(
        "--keywords",
        type=str,
        default="Transformer,LLM,neural network",
        help="検索キーワード（カンマ区切り）"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="取得件数上限（デフォルト: 10）"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="過去N日間で絞込み（デフォルト: 30）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/papers.json",
        help="出力ファイルパス"
    )
   parser.add_argument(
       "--offline",
       action="store_true",
       help="オフラインモード（サンプルデータを使用）"
   )
    
    args = parser.parse_args()
    
    keywords = [k.strip() for k in args.keywords.split(",")]
    
    fetcher = ArXivFetcher()
   
   # オフラインモード
   if args.offline:
       print("📴 オフラインモード: サンプルデータを使用します")
       papers = [
           {
               "id": "2406.12345",
               "title": "Improving Attention Mechanisms in Transformers with Low-Rank Decomposition",
               "authors": ["John Smith", "Jane Doe"],
               "published": "2024-06-15",
               "summary": "Novel method to improve computational efficiency of attention mechanisms.",
               "url": "https://arxiv.org/abs/2406.12345",
               "categories": ["cs.LG", "cs.AI"],
               "fetched_at": datetime.now().isoformat()
           },
           {
               "id": "2406.54321",
               "title": "Vision Transformers Meet Efficient Networks",
               "authors": ["Alice Chen", "Bob Williams"],
               "published": "2024-06-10",
               "summary": "Hybrid architecture combining Vision Transformers and efficient networks.",
               "url": "https://arxiv.org/abs/2406.54321",
               "categories": ["cs.CV", "cs.LG"],
               "fetched_at": datetime.now().isoformat()
           }
       ]
   else:
       papers = fetcher.fetch_papers(
           keywords=keywords,
           max_results=args.max_results,
           days=args.days
       )
   
   if not papers:
       print("\n⚠️  論文が取得できませんでした。")
       print("    インターネット接続を確認するか、--offline フラグを使用してください。")
       print(f"    例: python {__file__} --offline")
    
    fetcher.save_papers(papers, args.output)


if __name__ == "__main__":
    main()
