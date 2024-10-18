import argparse, threading, os, subprocess, sys

try:
    import requests
    from colorama import init, Fore, Style
except (ImportError, ModuleNotFoundError):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", " requests"])
    import requests
    from colorama import init, Fore, Style
finally:
    import requests
    from colorama import init, Fore, Style

init(autoreset=True)

class XSSWarning:
    @staticmethod
    def print_yellow_warning(message):
        print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}\n")

    @staticmethod
    def print_xss_vulnerable(message):
        print(f"{Fore.RED}{message}{Style.RESET_ALL}\n")

def print_help():
    print("Usage: python xss_scanner.py [options]")
    print("\nOptions:")
    print("  -u, --url           Target URL to test for XSS vulnerabilities (required).")
    print("  -f, --file          File containing payloads (default: payload.txt).")
    print("  --ua, --user-agent  User-Agent to use for requests (default: Mozilla/5.0).")
    print("  -t, --threads       Number of threads to use (default: 1).")
    print("  -o, --output        Save output to a file (txt only).")
    print("  -h, --help          Show this help message and exit.")
    print(f"\n{Fore.RED}Don't forget to input URL with http:// or https:// and parameters.{Style.RESET_ALL}")
    print("\nExample:")
    print(f"  {Fore.GREEN}python xss_scanner.py --url \"https://example.com\?parameters=" --file \"payload.txt\" --user-agent \"Mozilla/5.0\" --threads 5 --output \"output.txt\"{Style.RESET_ALL}")

parser = argparse.ArgumentParser(description="Simple XSS Scanner by Xnuvers007", epilog=f"{Fore.RED}Don't forget to input URL with http:// or https:// and parameters.")
parser.add_argument("--url", "-u", required=True, help="Target URL to test for XSS vulnerabilities.")
parser.add_argument("--file", "-f", default="payload.txt", help="File containing payloads (default: payload.txt).")
parser.add_argument("--user-agent", "--ua", default="Mozilla/5.0", help="User-Agent to use for requests (default: Mozilla/5.0).")
parser.add_argument("--threads", "--threading", "--thread", "--t", type=int, default=1, help="Number of threads to use (default: 1).")
parser.add_argument("--output", "-o", help="Save output to a file (txt only).")

if len(sys.argv) == 1:
    print_help()
    sys.exit(0)

args = parser.parse_args()

try:
    with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
        payload = f.read().splitlines()
except FileNotFoundError:
    print(f"{Fore.RED}Error: The file '{args.file}' was not found.{Style.RESET_ALL}")
    sys.exit(1)

def scan_for_xss(url, headers):
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        if "alert(" in r.text or "confirm(" in r.text or "prompt(" in r.text:
            XSSWarning.print_xss_vulnerable(f"XSS Vulnerable (pop-up detected): {url}")

        if any(tag in r.text for tag in ["<script>", "<img", "onerror=", "onclick=", "onmouseover=", "onload=", "<a", "href=", "<form", "action=", "<input", "type=", "<button", "onclick=", "<h1"]):
            XSSWarning.print_xss_vulnerable(f"XSS Vulnerable (HTML tags detected): {url}")

        for i in payload:
            if i in r.text:
                XSSWarning.print_xss_vulnerable(f"XSS Vulnerable (reflected payload detected): {url}")

        if 'Content-Security-Policy' not in r.headers:
            XSSWarning.print_yellow_warning(f"Warning: Missing Content-Security-Policy header: {url}")
    else:
        XSSWarning.print_yellow_warning(f"Request failed with status code {r.status_code}: {url}")

    if args.output and args.output.endswith('.txt'):
        with open(args.output, "a") as file:
            file.write(f"{url}\n")
    else:
        print(f"{Fore.RED}Error: Output file must be a .txt file.{Style.RESET_ALL}")

def scan_with_threading():
    threads = []
    for i in payload:
        url = f"{args.url}{i}"
        headers = {"User-Agent": args.user_agent}
        thread = threading.Thread(target=scan_for_xss, args=(url, headers))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    if args.threads > 1:
        scan_with_threading()
    else:
        for i in payload:
            url = f"{args.url}{i}"
            headers = {"User-Agent": args.user_agent}
            scan_for_xss(url, headers)

    print(f"{Fore.GREEN}CPU Cores: {os.cpu_count()}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Memory Usage: {os.sys.getsizeof(os)} bytes{Style.RESET_ALL}")
