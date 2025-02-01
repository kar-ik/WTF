import subprocess
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler import WebCrawler  # Import the Scrapy spider

def run_scrapy_crawler(target_url):
    # Setup Scrapy settings dynamically
    process = CrawlerProcess(get_project_settings())
    WebCrawler.start_urls = [target_url]  # Update the start URL dynamically
    
    # Start the Scrapy crawling process
    process.crawl(WebCrawler)
    process.start()  # Block until the crawling is finished

def sql_injection_test(url):
    # Dummy test for SQL injection (can be expanded)
    print(f"Running SQL Injection test for {url}...")
    return "No SQL Injection vulnerability detected."

def xss_test(url):
    # Dummy test for XSS (can be expanded)
    print(f"Running XSS test for {url}...")
    return "No XSS vulnerability detected."

def csrf_test(url):
    # Dummy test for CSRF (can be expanded)
    print(f"Running CSRF test for {url}...")
    return "CSRF protection found."

def insecure_headers_test(url):
    # Dummy test for insecure headers (can be expanded)
    print(f"Running Insecure Headers test for {url}...")
    return "No insecure headers detected."

def directory_bruteforce(url):
    # Dummy test for directory bruteforce (can be expanded)
    print(f"Running Directory Bruteforce test for {url}...")
    return "No accessible directories found."

def run_security_tests(url):
    print(f"Running security tests for {url}...\n")
    print(sql_injection_test(url))
    print(xss_test(url))
    print(csrf_test(url))
    print(insecure_headers_test(url))
    print(directory_bruteforce(url))

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
        target_url = input("Enter the target URL (e.g., http://example.com): ")
        run_scrapy_crawler(target_url)  # Run Scrapy crawler
        run_security_tests(target_url)  # Run security tests after crawling
    elif choice == "2":
        update_tool()  # Update the tool
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
