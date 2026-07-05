from typing import Optional
import structlog

from app.crawlers.base import BaseCrawler
from app.crawlers.greenhouse import GreenhouseCrawler
from app.crawlers.lever import LeverCrawler
from app.crawlers.wellfound import WellfoundCrawler
from app.crawlers.remoteok import RemoteOKCrawler
from app.crawlers.yc_jobs import YCJobsCrawler

logger = structlog.get_logger()

CRAWLER_REGISTRY = {
    "greenhouse": GreenhouseCrawler,
    "lever": LeverCrawler,
    "wellfound": WellfoundCrawler,
    "remoteok": RemoteOKCrawler,
    "yc_jobs": YCJobsCrawler,
}


def get_crawler(source: str) -> Optional[BaseCrawler]:
    crawler_class = CRAWLER_REGISTRY.get(source)
    if crawler_class:
        return crawler_class()
    logger.warning("unknown_crawler_source", source=source)
    return None


async def crawl_all_sources(**kwargs) -> list[dict]:
    all_jobs = []
    for source, crawler_class in CRAWLER_REGISTRY.items():
        try:
            crawler = crawler_class()
            jobs = await crawler.crawl(**kwargs)
            normalized = [crawler.normalize(job) for job in jobs]
            all_jobs.extend(normalized)
            logger.info("crawl_complete", source=source, count=len(normalized))
        except Exception as e:
            logger.error("crawl_failed", source=source, error=str(e))
    return all_jobs
