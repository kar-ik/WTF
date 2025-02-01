import re
import requests
from bs4 import BeautifulSoup
from termcolor import colored
import os
import subprocess
from crawler import crawl_page

headers = {"User-Agent": "Mozilla/5.0"}

target_url = "http://example.com"
crawl_page(target_url)

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def safe_request(url, params=None):
    """Helper function for making requests with error handling and timeouts."""
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response
    except requests.RequestException as e:
        print(colored(f"Error during request to {url}: {str(e)}", "red"))
        return None

def sql_injection_test(url):
    payload = "' OR '1'='1"
    response = safe_request(url, params={"id": payload})
    if response:
        if "mysql" in response.text.lower() or "syntax" in response.text.lower():
            return True, "SQL Injection vulnerability detected!"
    return False, "No SQL Injection vulnerability detected."

def xss_test(url):
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "'\"><script>alert('XSS')</script>"
    ]
    for payload in xss_payloads:
        response = safe_request(url + payload)
        if response and payload in response.text:
            return True, "XSS vulnerability detected!"
    return False, "No XSS vulnerability detected."

def csrf_test(url):
    response = safe_request(url)
    if response:
        soup = BeautifulSoup(response.text, 'lxml')
        forms = soup.find_all('form')
        csrf_tokens = ["csrf_token", "csrfmiddlewaretoken", "authenticity_token"]
        csrf_protected = any(
            any(form.find('input', {'name': token}) for token in csrf_tokens) for form in forms
        )
        return (False, "CSRF protection found.") if csrf_protected else (True, "Potential CSRF vulnerability detected!")
    return False, "Error checking CSRF vulnerability."

def insecure_headers_test(url):
    response = safe_request(url)
    if response:
        headers_list = response.headers
        insecure_headers = []
        if "X-Frame-Options" not in headers_list:
            insecure_headers.append("X-Frame-Options missing")
        if "Content-Security-Policy" not in headers_list:
            insecure_headers.append("Content-Security-Policy missing")
        return (True, ", ".join(insecure_headers)) if insecure_headers else (False, "No insecure headers detected.")
    return False, "Error checking headers."

def directory_bruteforce(url):
    directories = ['admin', 'login', 'dashboard', 'config', 'uploads']
    found_directories = []
    for directory in directories:
        test_url = f"{url}/{directory}/"
        response = safe_request(test_url)
        if response and response.status_code == 200:
            found_directories.append(test_url)
    return (True, f"Accessible directories: {', '.join(found_directories)}") if found_directories else (False, "No accessible directories found.")

def generate_report(test_results, target):
    sanitized_target = re.sub(r'[^a-zA-Z0-9]', '_', target)
    report_path = f"{REPORT_DIR}/report_{sanitized_target}_{int(time.time())}.html"
    
    with open(report_path, "w") as report:
        report.write(f"<html><head><title>Security Test Report for {target}</title></head><body>")
        report.write(f"<h1>Security Test Report for {target}</h1>")
        report.write("<ul>")
        for test_name, result, message in test_results:
            color = "green" if not result else "red"
            report.write(f"<li style='color:{color};'><strong>{test_name}:</strong> {message}</li>")
        report.write("</ul>")
        report.write("</body></html>")
    
    return report_path

def run_tests(url):
    print(colored(f"Running security tests for {url}", "blue"))
    test_results = []
    
    for test_func, test_name in [(sql_injection_test, "SQL Injection"), (xss_test, "XSS"),
                                 (csrf_test, "CSRF"), (insecure_headers_test, "Insecure Headers"),
                                 (directory_bruteforce, "Directory Bruteforcing")]:
        result, message = test_func(url)
        print(colored(message, "green" if not result else "red"))
        test_results.append((test_name, result, message))
    
    report_path = generate_report(test_results, url)
    print(f"Report saved to {report_path}")

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
        run_tests(target_url)  
    elif choice == "2":
        update_tool()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
