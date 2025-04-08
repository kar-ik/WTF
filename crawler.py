import os
import scrapy
import sys
import random
import json
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from twisted.internet import reactor, defer

REPORTS_DIR = "reports"
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
]

class WebCrawler(CrawlSpider):
    name = "web_crawler"
    custom_settings = {
        "DEPTH_LIMIT": 5,
        "DEPTH_PRIORITY": 1,
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "COOKIES_ENABLED": False,
        "USER_AGENT": random.choice(USER_AGENTS),
        "ROBOTSTXT_OBEY": False,
    }

    def __init__(self, target_url=None, report_filename="crawl_report.json", *args, **kwargs):
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        parsed_url = urlparse(target_url)
        self.allowed_domains = [parsed_url.netloc]
        self.start_urls = [target_url]
        self.report_filename = report_filename
        self.results = []  
        super(WebCrawler, self).__init__(*args, **kwargs)
        self._compile_rules()

    def _compile_rules(self):
        self.rules = (
            Rule(LinkExtractor(allow_domains=self.allowed_domains), callback=self.parse_page, follow=True),
        )
        super()._compile_rules()

    def parse_page(self, response):
        page_data = {}
        page_data["url"] = response.url
        content_type = response.headers.get("Content-Type", b"").decode("utf-8")
        page_data["content_type"] = content_type
        if "text/html" in content_type:
            links = response.xpath("//a/@href").getall()
            page_data["links"] = links

            forms = []
            for form in response.xpath("//form"):
                form_info = {
                    "action": form.xpath("@action").get(),
                    "method": form.xpath("@method").get(),
                    "inputs": []
                }
                for input_field in form.xpath(".//input"):
                    form_info["inputs"].append({
                        "name": input_field.xpath("@name").get(),
                        "type": input_field.xpath("@type").get()
                    })
                forms.append(form_info)
            page_data["forms"] = forms

            hidden_elements = response.xpath("//input[@type='hidden']/@name").getall()
            page_data["hidden_elements"] = hidden_elements
        else:
            page_data["non_html"] = True
        self.results.append(page_data)

    def closed(self, reason):
        report_path = os.path.join(REPORTS_DIR, self.report_filename)
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=4)
        self.logger.info(f"Crawl finished. Report saved to {report_path}")

def run_crawler_for_target(target_url):
    process = CrawlerProcess()
    parsed = urlparse(target_url)
    domain = parsed.netloc
    report_filename = f"crawl_{domain.replace(':', '_')}.json"
    process.crawl(WebCrawler, target_url=target_url, report_filename=report_filename)
    process.start()
    print(f"[*] Crawling completed for {target_url}. Report saved in {REPORTS_DIR}/{report_filename}")

def run_crawler_for_targets(target_urls):
    runner = CrawlerRunner()
    
    @defer.inlineCallbacks
    def crawl():
        deferreds = []
        for target_url in target_urls:
            parsed = urlparse(target_url)
            domain = parsed.netloc
            report_filename = f"crawl_{domain.replace(':', '_')}.json"
            deferreds.append(runner.crawl(WebCrawler, target_url=target_url, report_filename=report_filename))
        yield defer.DeferredList(deferreds)
        reactor.stop()
    crawl()
    reactor.run()

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://example.com"
    run_crawler_for_target(target_url)
