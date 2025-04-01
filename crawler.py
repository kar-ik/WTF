import os
import subprocess
import scrapy
import sys
import random
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

if not os.path.exists('reports'):
    os.makedirs('reports')

def save_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def run_amass(target):
    print(f"[+] Running Amass on {target} with increased depth...")
    amass_command = f"amass enum -d {target} -max-depth 5 -o reports/amass_output.txt"
    subprocess.run(amass_command, shell=True)
    print(f"[*] Amass output saved to reports/amass_output.txt")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
]

class WebCrawler(CrawlSpider):
    name = "web_crawler"
    custom_settings = {
        "DEPTH_LIMIT": 10,
        "DEPTH_PRIORITY": 1,
        "DOWNLOAD_DELAY": random.uniform(1, 3),  
        "COOKIES_ENABLED": False,
        "USER_AGENT": random.choice(USER_AGENTS),
        "ROBOTSTXT_OBEY": False  
    }

    rules = (
        Rule(LinkExtractor(), callback="parse_page", follow=True),  
    )

    def __init__(self, target_url=None, *args, **kwargs):
        super(WebCrawler, self).__init__(*args, **kwargs)
        
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url  

        self.start_urls = [target_url]

    def parse_page(self, response):
        links = response.xpath("//a/@href").getall()
        content = "\n--- Links Found ---\n"
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

        save_to_file("reports/web_crawler_output.txt", content)

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://example.com"

    run_amass(target_url)

    process = CrawlerProcess()
    process.crawl(WebCrawler, target_url=target_url)
    process.start()

    print("[*] All results saved in the 'reports' folder.")
