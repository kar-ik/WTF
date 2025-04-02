import os
import scrapy
import sys
import random
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse

REPORTS_DIR = "reports"
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def save_to_file(filename, content):
    with open(os.path.join(REPORTS_DIR, filename), 'a') as file:
        file.write(content + "\n")

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

    def __init__(self, target_url=None, *args, **kwargs):
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        parsed_url = urlparse(target_url)
        self.allowed_domains = [parsed_url.netloc]
        self.start_urls = [target_url]

        super(WebCrawler, self).__init__(*args, **kwargs)
        self._compile_rules() 

    def _compile_rules(self):
        self.rules = (
            Rule(LinkExtractor(allow_domains=self.allowed_domains), callback=self.parse_page, follow=True),
        )
        super()._compile_rules()

    def parse_page(self, response):
        content = f"\n[*] Crawled: {response.url}\n"
        content_type = response.headers.get("Content-Type", b"").decode("utf-8")

        if "text/html" in content_type:
            links = response.xpath("//a/@href").getall()
            content += "\n--- Links Found ---\n"
            for link in links:
                content += f"Link: {link}\n"

            forms = response.xpath("//form")
            content += "\n--- Forms Found ---\n"
            for form in forms:
                action = form.xpath("@action").get()
                method = form.xpath("@method").get()
                content += f"Form action: {action}, method: {method}\n"

                inputs = form.xpath(".//input")
                for input_field in inputs:
                    input_name = input_field.xpath("@name").get()
                    input_type = input_field.xpath("@type").get()
                    content += f"Input name: {input_name}, type: {input_type}\n"

            hidden_elements = response.xpath("//input[@type='hidden']")
            content += "\n--- Hidden Elements Found ---\n"
            for hidden in hidden_elements:
                content += f"Hidden field: {hidden.xpath('@name').get()}\n"
        else:
            content += "\nNon-HTML content, skipping parsing.\n"

        save_to_file("web_crawler_output.txt", content)

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://example.com"

    process = CrawlerProcess()
    process.crawl(WebCrawler, target_url=target_url)
    process.start()

    print("[*] Crawling completed. Results saved in the 'reports' folder.")
