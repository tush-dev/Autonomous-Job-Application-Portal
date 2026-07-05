from app.crawlers.base import BaseCrawler


class GreenhouseCrawler(BaseCrawler):
    async def crawl(self, **kwargs) -> list[dict]:
        return []

    def normalize(self, raw_job: dict) -> dict:
        return self.normalize_common(raw_job)


class LeverCrawler(BaseCrawler):
    async def crawl(self, **kwargs) -> list[dict]:
        return []

    def normalize(self, raw_job: dict) -> dict:
        return self.normalize_common(raw_job)


class WellfoundCrawler(BaseCrawler):
    async def crawl(self, **kwargs) -> list[dict]:
        return []

    def normalize(self, raw_job: dict) -> dict:
        return self.normalize_common(raw_job)


class RemoteOKCrawler(BaseCrawler):
    async def crawl(self, **kwargs) -> list[dict]:
        return []

    def normalize(self, raw_job: dict) -> dict:
        return self.normalize_common(raw_job)


class YCJobsCrawler(BaseCrawler):
    async def crawl(self, **kwargs) -> list[dict]:
        return []

    def normalize(self, raw_job: dict) -> dict:
        return self.normalize_common(raw_job)


class LinkedInCrawler(BaseCrawler):
    async def crawl(self, **kwargs) -> list[dict]:
        return []

    def normalize(self, raw_job: dict) -> dict:
        return self.normalize_common(raw_job)


class RSSFeedCrawler(BaseCrawler):
    async def crawl(self, **kwargs) -> list[dict]:
        return []

    def normalize(self, raw_job: dict) -> dict:
        return self.normalize_common(raw_job)
