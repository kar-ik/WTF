import os
import re
import sys
import json
import csv
import requests
import subprocess
import ipaddress
import shodan
import socket
import time
from urllib.parse import urlparse, quote
from bs4 import BeautifulSoup
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()

headers = {"User-Agent": "Mozilla/5.0"}
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
if SHODAN_API_KEY:
    api = shodan.Shodan(SHODAN_API_KEY)
    print(colored("Shodan API Key Loaded Successfully!", "green"))
else:
    print(colored("Skipping Shodan scan (API key not provided)", "yellow"))
    exit(1)

def print_banner():
    banner = r"""
$$       $$$       $$   $$$$$$$$$$$$   $$$$$$$$
 $$     $$ $$     $$         $$        $$  
  $$   $$   $$   $$          $$        $$$$$$
   $$ $$     $$ $$           $$        $$
    $$$       $$$            $$        $$
                          
      Web Application Security Testing Framework
         (Built for Ethical Hacking & Pentesting)
    """
    print(colored(banner, "cyan"))

SQL_PAYLOADS = [
    "'", '"', "--", "1' OR '1'='1", "admin' --", "admin' #",
    "' OR 1=1 --", "' UNION SELECT null, version() --", "' OR sleep(5) --"
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>", 
    '"><script>alert("XSS")</script>',
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    "<iframe src=javascript:alert(1)>"
]

SECURITY_HEADERS = {
    "X-Frame-Options": "Missing or improperly set",
    "Content-Security-Policy": "Missing or weak",
    "Strict-Transport-Security": "Missing"
}

def shodan_lookup(domain):
    try:
        ip = socket.gethostbyname(domain)
        print(f"[+] Resolved {domain} to {ip}")

        result = api.host(ip)

        print(f"\n[+] Shodan Data for {ip}:")
        print("Organization:", result.get('org', 'n/a'))
        print("Operating System:", result.get('os', 'n/a'))

        print("\n[+] Open Ports & Services:")
        for service in result['data']:
            print(f"- Port: {service['port']}, Service: {service.get('product', 'Unknown')}")

        vulns = result.get('vulns', [])
        if vulns:
            print("\n[+] Known Vulnerabilities (CVEs):")
            for cve in vulns:
                print(f"  - {cve}")
        else:
            print("\n[+] No known CVEs found.")

    except Exception as e:
        print(f"[!] Shodan Lookup failed: {e}")

def normalize_url(raw_url):
    """Remove unwanted prefixes and whitespace; ensure proper scheme."""
    url = raw_url.replace("[+] Crawled:", "").replace("[*] Crawled:", "").strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url
        
def is_valid_subdomain(subdomain, domain):
    return re.fullmatch(rf"[a-zA-Z0-9.-]+\.{re.escape(domain)}", subdomain)

def run_sublist3r(target):
    parsed = urlparse(target)
    domain = parsed.netloc if parsed.netloc else parsed.path
    if not domain:
        print(colored("Error: Please enter a valid domain", "red"))
        return []
    print(colored(f"[*] Running Sublist3r for subdomain enumeration on {domain}", "blue"))
    output_file = os.path.join(REPORT_DIR, f"subdomain.{domain}.txt")
    try:
        engines = "nmap,bing,baidu,yahoo,crtsh,netcraft,threatcrowd,ssl,passivedns"
        subprocess.run(["sublist3r", "-d", domain, "-o", output_file, "-e", engines], check=True)
        with open(output_file, "r") as f:
            subdomains = [line.strip() for line in f if is_valid_subdomain(line.strip(), domain)]
        print(colored(f"[*] Found {len(subdomains)} valid subdomains for {domain}:", "green"))
        for sub in subdomains:
            print(colored(f"    {sub}", "green"))
        return subdomains
    except subprocess.CalledProcessError as e:
        print(colored(f"[!] Sublist3r failed: {e}", "red"))
        return []
    except Exception as e:
        print(colored(f"[!] Unexpected error during Sublist3r scan: {e}", "red"))
        return []

def sql_injection_test(url):
    """Test for SQL Injection vulnerabilities using multiple payloads."""
    try:
        for payload in SQL_PAYLOADS:
            test_url = f"{url}?id={payload}" if '?' not in url else f"{url}&id={payload}"
            response = requests.get(test_url, headers=headers, timeout=5)
            sql_errors = [
                "SQL syntax", "mysql_fetch", "syntax error", 
                "You have an error in your SQL syntax", "Unclosed quotation mark",
                "near", "Warning: mysql", "Microsoft OLE DB"
            ]
            if any(error in response.text for error in sql_errors):
                return True, f"SQL Injection detected with payload: {payload}"
        return False, "No SQL Injection vulnerability detected"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

def xss_test(url):
    """Test for XSS vulnerabilities with multiple payloads."""
    try:
        for payload in XSS_PAYLOADS:
            test_url = f"{url}?q={payload}" if '?' not in url else f"{url}&q={payload}"
            response = requests.get(test_url, headers=headers, timeout=5)
            if payload in response.text:
                return True, f"XSS vulnerability detected with payload: {payload}"
        return False, "No XSS vulnerability detected"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

def csrf_test(url):
    """Test for CSRF vulnerabilities by checking for a CSRF token in forms."""
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if '<input type="hidden" name="csrf_token"' not in response.text:
            return True, "Potential CSRF vulnerability detected (No CSRF token found)"
        return False, "CSRF protection detected"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

def insecure_headers_test(url):
    """Test for missing security headers."""
    try:
        response = requests.get(url, headers=headers, timeout=5)
        missing = [h for h in SECURITY_HEADERS if h not in response.headers]
        if missing:
            return True, f"Missing headers: {', '.join(missing)}"
        return False, "All important security headers are present"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

def directory_bruteforce(url):
    """Test for accessible directories by appending common paths."""
    directories = ['/admin', '/login', '/uploads', '/config']
    accessible = []
    for d in directories:
        try:
            response = requests.get(url + d, timeout=3)
            if response.status_code == 200:
                accessible.append(d)
        except requests.exceptions.RequestException:
            continue
    if accessible:
        return True, f"Accessible directories: {', '.join(accessible)}"
    else:
        return False, "No accessible directories found"
        
def run_security_tests_on_url(url):
    print(colored(f"\n[+] Running security tests on {url}", "yellow"))
    results = {
        "SQL Injection": sql_injection_test(url),
        "XSS": xss_test(url),
        "CSRF": csrf_test(url),
        "Insecure Headers": insecure_headers_test(url),
        "Directory Bruteforce": directory_bruteforce(url)
    }
    return results

def run_crawler(target):
    print(colored(f"[+] Crawling target: {target}", "blue"))
    try:
        subprocess.run(["python3", "crawler.py", target], check=True, timeout=600)
    except subprocess.TimeoutExpired:
        print(colored(f"[*] Crawler timed out for target: {target}", "red"))
        return []
    parsed = urlparse(target)
    domain = parsed.netloc if parsed.netloc else parsed.path
    report_file = os.path.join(REPORT_DIR, f"crawl_{domain.replace(':','_')}.json")
    if os.path.exists(report_file):
        try:
            with open(report_file, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(colored(f"Error reading JSON report for {target}: {e}", "red"))
            return []
    else:
        print(colored(f"Report file not found for {target}", "red"))
        return []

def check_result(msg):
    if isinstance(msg, tuple):
        msg = msg[1]  

    lower = msg.lower()
    if "vulnerable" in lower:
        return "VULNERABLE"
    elif "secure" in lower or "not vulnerable" in lower:
        return "SECURE"
    else:
        return "UNKNOWN"

def save_final_results(target, all_targets, results_dict):
    parsed = urlparse(target)
    safe_target = parsed.netloc if parsed.netloc else parsed.path
    safe_target = safe_target.replace("/", "_")
    
    txt_file = os.path.join(REPORT_DIR, f"final_scanning.{safe_target}.txt")
    csv_file = os.path.join(REPORT_DIR, f"final_scanning.{safe_target}.csv")
    
    with open(txt_file, "w") as f:
        f.write(f"Final scan results for {target}\n")
        f.write("=" * 50 + "\n")
        for url in all_targets:
            f.write(f"URL: {url}\n")
            if url in results_dict:
                for test, msg in results_dict[url].items():
                    f.write(f"   {test}: {msg}\n")
            else:
                f.write("   No results found.\n")
            f.write("-" * 50 + "\n")
    print(colored(f"[✓] Final TXT results saved to {txt_file}", "green"))
    
    header = ["URL", "SQL Injection", "XSS", "CSRF", "Insecure Headers", "Directory Bruteforce"]
    summary_counts = {key: {"PASS":0, "FAIL":0} for key in header[1:]}
    total_urls = len(all_targets)
    
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for url in all_targets:
            res = results_dict.get(url, {})
            row = [url]
            for test in header[1:]:
                msg = res.get(test, "No results")
                status = check_result(msg)
                row.append(status)
                if status == "PASS":
                    summary_counts[test]["PASS"] += 1
                else:
                    summary_counts[test]["FAIL"] += 1
            writer.writerow(row)
    print(colored(f"[✓] Final CSV results saved to {csv_file}", "green"))
    
    print(colored("\n[+] Scan Summary:", "magenta"))
    print(f"Total URLs tested: {total_urls}")
    for test in header[1:]:
        pass_count = summary_counts[test]["PASS"]
        fail_count = summary_counts[test]["FAIL"]
        print(f"{test}: PASS = {pass_count}, FAIL = {fail_count}")

def run_tests(target):
    parsed = urlparse(target)
    domain = parsed.netloc if parsed.netloc else parsed.path
    if not domain:
        print(colored("Error: Please enter a valid domain", "red"))
        return
    
    print(colored(f"\n[+] Starting tests on {target}", "yellow"))

    shodan_lookup(domain)

    subdomains = run_sublist3r(target)
    
    run_crawler(target)
    
    subdomain_urls = [f"http://{sub}" if not sub.startswith("http") else sub for sub in subdomains]
    def extract_urls():
        crawler_file = os.path.join(REPORT_DIR, f"crawler.{domain}.txt")
        urls = []
        if os.path.exists(crawler_file):
            with open(crawler_file, "r") as f:
                urls = re.findall(r'https?://[^\s]+', f.read())
        return urls
    crawled_urls = extract_urls()
    
    all_targets = list(set([f"http://{domain}"] + subdomain_urls + crawled_urls))
    print(colored(f"\n[+] Total URLs to test: {len(all_targets)}", "cyan"))
    
    results_dict = {}
    for i, url in enumerate(all_targets, start=1):
        print(colored(f"\n[{i}/{len(all_targets)}] Testing {url}", "blue"))
        results_dict[url] = run_security_tests_on_url(url)
        time.sleep(0.5)
    
    save_final_results(target, all_targets, results_dict)
    print(colored("\n[✓] Scan Complete!\n", "green"))

def update_tool():
    try:
        if not os.path.exists('.git'):
            print("This tool is not a Git repository.")
            return
        print("Checking for updates...")
        subprocess.run(['git', 'fetch'], check=True)
        status = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, text=True, check=True)
        if "up to date" in status.stdout.lower():
            print("Your tool is already up-to-date.")
        else:
            subprocess.run(['git', 'pull'], check=True)
            print("Tool updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error updating: {e}")

def main_menu():
    while True:
        print_banner()
        print(colored("\n[+] Web Application Security Testing Framework [+]\n", "yellow"))
        print(colored("1. Run security tests", "green"))
        print(colored("2. Update tool", "green"))
        print(colored("3. Exit", "red"))
        choice = input(colored("\nEnter your choice: ", "cyan"))
        if choice == "1":
            target = input(colored("Enter the target domain (e.g., example.com): ", "cyan")).strip()
            if not target.startswith("http://") and not target.startswith("https://"):
                target = "http://" + target
            run_tests(target)
            input(colored("\nPress Enter to return to the main menu...", "cyan"))
        elif choice == "2":
            update_tool()
            input(colored("\nPress Enter to return to the main menu...", "cyan"))
        elif choice == "3":
            print(colored("Exiting the tool. Goodbye!", "red"))
            break
        else:
            print(colored("Invalid choice. Please try again.", "red"))

if __name__ == "__main__":
    main_menu()
