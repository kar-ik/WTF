import os
import re
import requests
import subprocess
import ipaddress
import shodan
import unittest
from bs4 import BeautifulSoup
from termcolor import colored
from dotenv import load_dotenv
load_dotenv()

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

headers = {"User-Agent": "Mozilla/5.0"}
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

if not SHODAN_API_KEY:
    print("Error: Shodan API key not found. Set it as an environment variable or GitHub Secret.")
    exit(1)

api = shodan.Shodan(SHODAN_API_KEY)
print(colored("Shodan API Key Loaded Successfully!", "green"))

def is_valid_subdomain(subdomain, domain):
    """ Ensure subdomains belong to the target domain. """
    return re.fullmatch(rf"[a-zA-Z0-9.-]+\.{re.escape(domain)}", subdomain)

def run_amass(domain):
    """ Run Amass for subdomain enumeration, ensuring only target subdomains are included. """
    print(colored(f"Running Amass for subdomain enumeration on {domain}", "blue"))
    output_file = f"{REPORT_DIR}/amass_{domain}.txt"

    subprocess.run(["amass", "enum", "-d", domain, "-o", output_file])

    with open(output_file, "r") as file:
        subdomains = [line.strip() for line in file.readlines()]

    filtered_subdomains = [sub for sub in subdomains if is_valid_subdomain(sub, domain)]

    print(colored(f"Filtered {len(filtered_subdomains)} valid subdomains:", "green"))
    for sub in filtered_subdomains:
        print(sub)

    return filtered_subdomains  

def is_in_target_range(ip, target_cidr):
    """ Check if an IP address belongs to the target's IP range. """
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(target_cidr)
    except ValueError:
        return False

def shodan_scan(target):
    """ Perform a Shodan scan and filter results to only show target-related data. """
    try:
        print(colored(f"Scanning {target} on Shodan...", "blue"))
        result = api.host(target)

        target_ip = result['ip_str']
        target_asn = result.get('asn', '')

        if target_asn and not target_asn.startswith("AS"):
            print(colored(f"Skipping unrelated ASN {target_asn}", "yellow"))
            return

        TARGET_IP_RANGE = "192.168.1.0/1"  

        if not is_in_target_range(target_ip, TARGET_IP_RANGE):
            print(colored(f"Skipping {target_ip} (not in target's range)", "yellow"))
            return

        print(colored(f"Shodan results for {target}:", "blue"))
        print(f"IP: {target_ip}")
        print(f"Organization: {result.get('org', 'N/A')}")
        print(f"Operating System: {result.get('os', 'N/A')}")

        for item in result['data']:
            print(f"Port: {item['port']}, Service: {item.get('product', 'Unknown')}")

    except shodan.APIError as e:
        print(colored(f"Shodan API Error: {e}", "red"))

def run_tests(target):
    """ Run all security tests on the given target. """
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
    """ Check for updates and pull the latest code if available. """
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
    """ Display the main menu for the security testing tool. """
    while True:
        print_banner()
        print(colored("\n[+] Web Application Security Testing Framework [+]\n", "yellow"))
        print(colored("1. Run security tests", "green"))
        print(colored("2. Update tool", "green"))
        print(colored("3. Exit", "red"))

        choice = input(colored("\nEnter your choice: ", "cyan"))
        if choice == "1":
            target_url = input(colored("Enter the target domain (e.g., example.com): ", "cyan"))
            run_tests(target_url)
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
