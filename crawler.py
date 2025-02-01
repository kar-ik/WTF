import scrapy

class WebCrawler(scrapy.Spider):
    name = "web_crawler"
    allowed_domains = ["example.com"]  

    def start_requests(self):
        target_url = "http://example.com"
        yield scrapy.Request(url=target_url, callback=self.parse)

    def parse(self, response):
        links = response.css('a::attr(href)').getall()
        print("\n--- Links Found ---")
        for link in links:
            print(f"Link: {link}")
        
        forms = response.css('form')
        print("\n--- Forms Found ---")
        for form in forms:
            action = form.css('::attr(action)').get()
            method = form.css('::attr(method)').get()
            print(f"Form action: {action}, method: {method}")
            
            inputs = form.css('input')
            for input_field in inputs:
                input_name = input_field.css('::attr(name)').get()
                input_type = input_field.css('::attr(type)').get()
                print(f"Input name: {input_name}, type: {input_type}")

        hidden_elements = response.css("input[type='hidden']")
        print("\n--- Hidden Elements Found ---")
        for hidden in hidden_elements:
            print(f"Hidden field: {hidden.css('::attr(name)').get()}")
