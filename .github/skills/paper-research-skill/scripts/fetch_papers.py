#!/usr/bin/env python3
"""
AI系論文自動取得スクリプト

既定は OpenAlex から収集し、必要に応じて arXIV へフォールバックします。
ローカル実行で安定して実データ収集できることを重視した実装です。
"""

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PaperFetcher:
    """複数ソース(OpenAlex/arXIV)から論文を取得するクラス"""

    OPENALEX_URL = "https://api.openalex.org/works"
    ARXIV_URL = "https://export.arxiv.org/api/query"

    TIMEOUT = 20
    MAX_RETRIES = 2
    ARXIV_DELAY = 3
    AI_HINTS = [
        "llm",
        "language model",
        "transformer",
        "neural",
        "machine learning",
        "deep learning",
        "vision-language",
        "multimodal",
        "nlp",
        "computer vision",
    ]

    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch_papers(
        self,
        keywords: List[str],
        max_results: int,
        days: int,
        source: str = "auto",
    ) -> List[Dict]:
        all_papers: List[Dict] = []
        seen_ids = set()

        for keyword in keywords:
            print(f"🔍 検索中: {keyword}")

            papers: List[Dict] = []
            if source == "openalex":
                papers = self._fetch_openalex(keyword, max_results, days)
            elif source == "arxiv":
                papers = self._fetch_arxiv(keyword, max_results, days)
            else:
                # auto: OpenAlexを先に試し、0件ならarXIVへフォールバック
                papers = self._fetch_openalex(keyword, max_results, days)
                if not papers:
                    print("  ↪ OpenAlex で0件のため arXIV を試行")
                    papers = self._fetch_arxiv(keyword, max_results, days)

            for p in papers:
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    all_papers.append(p)

        return all_papers

    def _fetch_openalex(self, keyword: str, max_results: int, days: int) -> List[Dict]:
        now_date = datetime.now(timezone.utc).date().isoformat()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
        params = {
            "search": keyword,
            "filter": f"from_publication_date:{cutoff},to_publication_date:{now_date},language:en",
            "per-page": max_results,
            "sort": "publication_date:desc",
        }
        try:
            response = self.session.get(self.OPENALEX_URL, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            results = payload.get("results", [])

            papers = []
            for item in results:
                paper = self._parse_openalex(item, keyword)
                if not paper:
                    continue
                papers.append(paper)
                print(f"  ✓ {paper['title'][:60]}...")

            return papers
        except requests.RequestException as e:
            print(f"  ❌ OpenAlex エラー: {e}")
            return []

    def _fetch_arxiv(self, keyword: str, max_results: int, days: int) -> List[Dict]:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        date_filter = cutoff_date.strftime("%Y%m%d0000")
        today = datetime.now(timezone.utc).strftime("%Y%m%d0000")
        search_query = f"all:{keyword} AND submittedDate:[{date_filter} TO {today}]"

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        try:
            response = self.session.get(self.ARXIV_URL, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            papers = []
            for entry in feed.entries:
                paper = self._parse_arxiv(entry)
                papers.append(paper)
                print(f"  ✓ {paper['title'][:60]}...")

            if papers:
                time.sleep(self.ARXIV_DELAY)

            return papers
        except requests.RequestException as e:
            print(f"  ❌ arXIV エラー: {e}")
            return []

    def _is_relevant(self, title: str, abstract: str, keyword: str) -> bool:
        text = f"{title} {abstract}".lower()
        keyword_tokens = [t for t in keyword.lower().replace("-", " ").split() if len(t) > 2]
        has_keyword = any(tok in text for tok in keyword_tokens) if keyword_tokens else True
        if has_keyword:
            return True
        # キーワードに一致しない場合のみ、AIヒントによる救済を試す
        return any(h in text for h in self.AI_HINTS)

    def _parse_openalex(self, item: Dict, keyword: str):
        openalex_id = item.get("id", "").rsplit("/", 1)[-1]
        title = (item.get("title") or item.get("display_name") or "Untitled").strip()
        published = item.get("publication_date") or f"{item.get('publication_year', 1970)}-01-01"

        # 念のため未来日付データを除外
        try:
            pub_date = datetime.strptime(published, "%Y-%m-%d").date()
            if pub_date > datetime.now(timezone.utc).date():
                return None
        except ValueError:
            return None

        authorships = item.get("authorships", [])
        authors = [a.get("author", {}).get("display_name") for a in authorships]
        authors = [a for a in authors if a]

        abstract = self._restore_abstract(item.get("abstract_inverted_index", {}))
        if not abstract:
            abstract = "Abstract is not provided by source."

        if not self._is_relevant(title, abstract, keyword):
            return None

        url = (
            (item.get("primary_location") or {}).get("landing_page_url")
            or item.get("doi")
            or item.get("id")
            or ""
        )

        concepts = item.get("concepts", [])
        categories = [c.get("display_name", "") for c in concepts[:5] if c.get("display_name")]

        return {
            "id": openalex_id,
            "title": title,
            "authors": authors,
            "published": published,
            "summary": abstract,
            "url": url,
            "categories": categories,
            "source": "openalex",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def _restore_abstract(self, inverted_index: Dict) -> str:
        if not inverted_index:
            return ""
        positions = []
        for word, indexes in inverted_index.items():
            for idx in indexes:
                positions.append((idx, word))
        positions.sort(key=lambda x: x[0])
        return " ".join(word for _, word in positions)

    def _parse_arxiv(self, entry) -> Dict:
        paper_id = entry.id.split("/abs/")[-1]
        authors = [author.name for author in entry.get("authors", [])]
        title = entry.title.replace("\n", " ").strip()
        summary = entry.summary.replace("\n", " ").strip()
        categories = [tag["term"] for tag in entry.get("tags", [])]
        return {
            "id": paper_id,
            "title": title,
            "authors": authors,
            "published": entry.published[:10],
            "summary": summary,
            "url": f"https://arxiv.org/abs/{paper_id}",
            "categories": categories,
            "source": "arxiv",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def save_papers(self, papers: List[Dict], output_path: str):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        print(f"\n✅ {len(papers)}件の論文を保存: {output_path}")


def sample_papers() -> List[Dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "id": "sample-1",
            "title": "A Survey of Large Language Models",
            "authors": ["Han et al."],
            "published": "2026-05-09",
            "summary": "This paper surveys recent progress in large language models and discusses key design dimensions.",
            "url": "https://doi.org/10.1007/s11704-026-60308-3",
            "categories": ["Artificial Intelligence", "Natural Language Processing"],
            "source": "sample",
            "fetched_at": now,
        },
        {
            "id": "sample-2",
            "title": "Efficient Adaptation for Vision-Language Models",
            "authors": ["Doe", "Kim"],
            "published": "2026-04-20",
            "summary": "This work proposes an efficient adaptation method for multimodal foundation models.",
            "url": "https://example.org/paper/sample-2",
            "categories": ["Computer Vision", "Machine Learning"],
            "source": "sample",
            "fetched_at": now,
        },
    ]


def main():
    parser = argparse.ArgumentParser(description="AI系論文を自動取得")
    parser.add_argument("--keywords", type=str, default="Transformer,LLM,neural network", help="検索キーワード（カンマ区切り）")
    parser.add_argument("--max-results", type=int, default=10, help="取得件数上限（キーワードごと）")
    parser.add_argument("--days", type=int, default=30, help="過去N日間で絞込み")
    parser.add_argument("--output", type=str, default="data/papers.json", help="出力ファイルパス")
    parser.add_argument("--source", type=str, choices=["auto", "openalex", "arxiv"], default="auto", help="収集ソース")
    parser.add_argument("--offline", action="store_true", help="オフラインモード（サンプルデータを使用）")
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    fetcher = PaperFetcher()

    if args.offline:
        print("📴 オフラインモード: サンプルデータを使用")
        papers = sample_papers()
    else:
        papers = fetcher.fetch_papers(
            keywords=keywords,
            max_results=args.max_results,
            days=args.days,
            source=args.source,
        )

    if not papers:
        print("\n⚠️ 論文が取得できませんでした。--source openalex または --offline を試してください。")

    fetcher.save_papers(papers, args.output)


if __name__ == "__main__":
    main()
