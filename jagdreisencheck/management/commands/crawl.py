from django.core.management.base import BaseCommand
from scraper_engine.scraper_engine.spiders import ScraperEngineSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class Command(BaseCommand):
    help = "Let's get ready to rumble!"

    def handle(self, *args, **options):
        process = CrawlerProcess(get_project_settings())

        process.crawl(ScraperEngineSpider)
        process.start()