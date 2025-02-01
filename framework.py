import subprocess
from scrapy.crawler import CrawlerProcess
from crawler import WebCrawler 

def run_scrapy_crawler():
    process = CrawlerProcess(settings={
        "FEED_FORMAT": "json", 
        "FEED_URI": "output.json",
        "LOG_LEVEL": "INFO",  
    })
    
    process.crawl(WebCrawler) 
    process.start()  
    
def update_tool():
    try:
        if not os.path.exists('.git'):
            print("This tool is not a Git repository. Please clone it from the repository.")
            return
        print("Checking for updates...")
        subprocess.run(['git', 'fetch'], check=True)
        status = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, text=True, check=True)
        if "Your branch is up to date" in status.stdout:
            print("Your tool is already up-to-date.")
        else:
            subprocess.run(['git', 'pull'], check=True)
            print("Tool updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the update process: {str(e)}")

def main_menu():
    print("Security Testing Tool")
    print("1. Run security tests")
    print("2. Update tool")
    choice = input("Enter your choice: ")
    
    if choice == "1":
        run_scrapy_crawler() 
    elif choice == "2":
        update_tool()  
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
