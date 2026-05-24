#!/usr/bin/env python3
"""
論文要約スクリプト
英語論文メタデータから日本語サマリ・キーポイントを自動生成
"""

import json
import argparse
import os
from typing import List, Dict
from datetime import datetime, timezone


class PaperSummarizer:
    """論文要約・翻訳クラス"""
    
    def __init__(self):
        self.level_keywords = {
            "初級": ["introduction", "overview", "basic", "tutorial"],
            "中級": ["method", "experiment", "analysis", "framework"],
            "上級": ["novel", "theoretical", "complex", "optimization"]
        }

        self.category_map = {
            "natural language processing": "自然言語処理",
            "artificial intelligence": "人工知能",
            "machine learning": "機械学習",
            "deep learning": "深層学習",
            "computer vision": "コンピュータビジョン",
            "transformer": "Transformer",
        }
    
    def estimate_difficulty(self, paper: Dict) -> str:
        """論文の難易度を推定"""
        content = (paper.get('title', '') + ' ' + paper.get('summary', '')).lower()
        
        for level, keywords in self.level_keywords.items():
            if any(kw in content for kw in keywords):
                return level
        
        return "中級"  # デフォルト
    
    def _title_to_ja(self, title_en: str) -> str:
        title = title_en
        replacements = {
            "A Survey of": "〜のサーベイ",
            "Survey of": "〜のサーベイ",
            "Large Language Models": "大規模言語モデル",
            "Vision": "視覚",
            "Efficient": "効率的",
            "Models": "モデル",
            "Model": "モデル",
            "Transformer": "Transformer",
        }
        for en, ja in replacements.items():
            title = title.replace(en, ja)
        if title == title_en:
            return f"{title_en}（日本語要約）"
        return title

    def _ja_summary(self, paper: Dict) -> str:
        title = paper.get("title", "この研究")
        abstract = paper.get("summary", "")
        categories = ", ".join(self._map_categories_ja(paper.get("categories", []))[:3])
        first = abstract[:220].strip()
        if not first:
            first = "本論文は手法の設計と評価に関する研究です。"
        return (
            f"本論文『{title}』は、{categories if categories else 'AI'}領域の課題に取り組む研究です。"
            f"概要として、{first}"
        )

    def _map_categories_ja(self, categories: List[str]) -> List[str]:
        mapped = []
        for c in categories:
            key = str(c).lower()
            mapped.append(self.category_map.get(key, c))
        return mapped

    def _applications(self, paper: Dict) -> List[str]:
        title = (paper.get("title") or "").lower()
        categories = " ".join([str(c).lower() for c in paper.get("categories", [])])
        text = f"{title} {categories}"

        apps = ["研究開発でのベースライン比較"]
        if "language" in text or "llm" in text or "natural language" in text:
            apps.extend(["チャットボット性能改善", "要約・検索支援の精度向上"])
        if "vision" in text or "image" in text:
            apps.extend(["画像理解システムの改善", "マルチモーダル製品への応用"])
        if "efficient" in text or "optimization" in text:
            apps.append("推論コスト削減と運用効率化")

        # 重複除去
        uniq = []
        for a in apps:
            if a not in uniq:
                uniq.append(a)
        return uniq[:4]

    def _key_points_ja(self, paper: Dict) -> List[str]:
        categories_ja = self._map_categories_ja(paper.get("categories", []))
        points = [
            f"研究テーマ: {paper.get('title', '未設定')}",
            f"対象領域: {', '.join(categories_ja[:3]) if categories_ja else 'AI全般'}",
            "実務への示唆: モデル設計・評価指標の改善に活用できる",
        ]
        return points

    def prepare_summary_template(self, papers: List[Dict]) -> List[Dict]:
        """日本語サマリを自動生成"""
        summaries = []
        
        for paper in papers:
            summary = {
                "paper_id": paper.get("id"),
                "title_en": paper.get("title"),
                "title_ja": self._title_to_ja(paper.get("title", "")),
                "original_url": paper.get("url"),
                "summary_section": {
                    "en": paper.get("summary", "")[:300],
                    "ja": self._ja_summary(paper)
                },
                "key_points": {
                    "en": [paper.get("title", "")],
                    "ja": self._key_points_ja(paper)
                },
                "technical_level": {
                    "level": self.estimate_difficulty(paper),
                    "prerequisites": ["機械学習の基礎", "論文読解の基礎"],
                    "reason": "タイトルと要約文に基づく自動判定"
                },
                "keywords": {
                    "en": paper.get("categories", []),
                    "ja": self._map_categories_ja(paper.get("categories", []))
                },
                "practical_applications": self._applications(paper),
                "metadata": {
                    "authors": paper.get("authors", []),
                    "published_date": paper.get("published"),
                    "arxiv_categories": paper.get("categories", []),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            }
            summaries.append(summary)
        
        return summaries
    
    def save_summaries(self, summaries: List[Dict], output_path: str):
        """要約情報をJSONで保存"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ {len(summaries)}件の日本語要約を生成: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="論文要約テンプレートを生成"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/papers.json",
        help="入力ファイル（paper-research-skillの出力）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/summaries.json",
        help="出力ファイルパス"
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=5,
        help="処理最大件数"
    )
    
    args = parser.parse_args()
    
    # 入力ファイルの読み込み
    if not os.path.exists(args.input):
        print(f"❌ 入力ファイルが見つかりません: {args.input}")
        return
    
    with open(args.input, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    # 最大件数で制限
    papers = papers[:args.max_papers]
    
    # 要約テンプレートを生成
    summarizer = PaperSummarizer()
    summaries = summarizer.prepare_summary_template(papers)
    
    # 保存
    summarizer.save_summaries(summaries, args.output)


if __name__ == "__main__":
    main()
