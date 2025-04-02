# WTF
Website Testing Framework
__________________________________________________________________________________________________________________
This Python-based framework automates the security testing of web applications for the following vulnerabilities:
- **SQL Injection**
- **Cross-Site Scripting (XSS)**
- **Cross-Site Request Forgery (CSRF)**
- **Insecure HTTP Headers**
- **Directory Bruteforcing**

## Features
- Runs common security tests on any given URL.
- Outputs a detailed HTML report of vulnerabilities found.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/kar-ik/WTF.git
    ```

2. Install dependencies:
    ```bash
    apt install python3-scrapy
    go install -v github.com/owasp-amass/amass/v4/...@master
    cd go && mv amass /usr/bin
    ```

3. Run the framework:
    ```bash
    python framework.py
    ```

## Example Usage

```bash
Enter the target URL (e.g., http://example.com): http://example.com
