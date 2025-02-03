import os
import re
import requests
import subprocess
from bs4 import BeautifulSoup
from termcolor import colored
import shodan
import unittest

headers = {"User-Agent": "Mozilla/5.0"}
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

SHODAN_API_KEY = "shodan_api_key_here"  

def run_amass(domain):
    print(colored(f"Running Amass for subdomain enumeration on {domain}", "blue"))
    output_file = f"{REPORT_DIR}/amass_{domain}.txt"
    subprocess.run(["amass", "enum", "-d", domain, "-o", output_file])
    with open(output_file, "r") as file:
        subdomains = file.readlines()
    print(colored(f"Found {len(subdomains)} subdomains:", "green"))
    for sub in subdomains:
        print(sub.strip())

def shodan_scan(target):
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        result = api.host(target)
        print(colored(f"Shodan results for {target}:", "blue"))
        print(f"IP: {result['ip_str']}")
        print(f"Organization: {result.get('org', 'N/A')}")
        print(f"Operating System: {result.get('os', 'N/A')}")
        for item in result['data']:
            print(f"Port: {item['port']}, Service: {item.get('product', 'Unknown')}")
    except shodan.APIError as e:
        print(colored(f"Shodan API Error: {e}", "red"))

def run_tests(target):
    print(colored(f"Running security tests for {target}", "blue"))
    run_amass(target)
    shodan_scan(target)

    print(colored("Running unit tests...", "blue"))
    test_suite = unittest.defaultTestLoader.discover(start_dir="tests", pattern="test_cases.py")  
    test_result = unittest.TextTestRunner().run(test_suite)
    if test_result.wasSuccessful():
        print(colored("All tests passed!", "green"))
    else:
        print(colored(f"{len(test_result.errors)} tests failed!", "red"))
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
        target_url = input("Enter the target domain (e.g., example.com): ")
        run_tests(target_url)
    elif choice == "2":
        update_tool()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
