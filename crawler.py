import scrapy

class WebCrawler(scrapy.Spider):
    name = "web_crawler"
    start_urls = ["http://example.com"] 

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
