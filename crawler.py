import scrapy
import sys
from scrapy.crawler import CrawlerProcess

class WebCrawler(scrapy.Spider):
    name = "web_crawler"

    def __init__(self, target_url=None, *args, **kwargs):
        super(WebCrawler, self).__init__(*args, **kwargs)
        self.start_urls = [target_url] if target_url else ["http://example.com"]

    def parse(self, response):
        links = response.xpath("//a/@href").getall()
        print("\n--- Links Found ---")
        for link in links:
            print(f"Link: {link}")
        
        forms = response.xpath("//form")
        print("\n--- Forms Found ---")
        for form in forms:
            action = form.xpath("@action").get()
            method = form.xpath("@method").get()
            print(f"Form action: {action}, method: {method}")
            
            inputs = form.xpath(".//input")
            for input_field in inputs:
                input_name = input_field.xpath("@name").get()
                input_type = input_field.xpath("@type").get()
                print(f"Input name: {input_name}, type: {input_type}")
        
        hidden_elements = response.xpath("//input[@type='hidden']")
        print("\n--- Hidden Elements Found ---")
        for hidden in hidden_elements:
            print(f"Hidden field: {hidden.xpath('@name').get()}")

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://example.com"
    process = CrawlerProcess()
    process.crawl(WebCrawler, target_url=target_url)
    process.start()
