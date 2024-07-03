import requests
from bs4 import BeautifulSoup
import re
import warnings
from colorama import init, Fore

# Initialize colorama for colored output
init(autoreset=True)

# ANSI escape codes for colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Function to print the banner
def print_banner():
    print(Fore.LIGHTGREEN_EX + "   ______________________________________            _________                                                ")
    print(Fore.LIGHTGREEN_EX + "  /   _____\\_   _____\\__    ___\\______   \\          /   _____/ ________________  ______ ______   ___________ ")
    print(Fore.LIGHTGREEN_EX + "  \\_____  \\ |    __)   |    |   |     ___/  ______  \\_____  \\_/ ___\\_  __ \\__  \\ \\____ \\\\____ \\_/ __ \\_  __ \\")
    print(Fore.LIGHTGREEN_EX + "  /        \\|     \\    |    |   |    |     /_____/  /        \\  \\___|  | \\// __ \\|  |_> |  |_> \\  ___/|  | \\/")
    print(Fore.LIGHTGREEN_EX + " /_______  /\\___  /    |____|   |____|             /_______  /\\___  |__|  (____  |   __/|   __/ \\___  |__|   ")
    print(Fore.LIGHTGREEN_EX + "         \\/     \\/                                         \\/     \\/           \\/|__|   |__|        \\/       ")
    print(Fore.YELLOW + "══════════════════════╦═════════════════════════════════╦")
    print(Fore.YELLOW + "══════════════════════|═════════════════════════════════|")
    print(Fore.YELLOW + "| • " + Fore.MAGENTA + "AUTHOR" + Fore.YELLOW + "            |   " + Fore.MAGENTA + "0xWhoami35" + Fore.YELLOW + "                    |")
    print(Fore.YELLOW + "| • " + Fore.MAGENTA + "GITHUB" + Fore.YELLOW + "            |   " + Fore.MAGENTA + "https://github.com/0xWhoami35" + Fore.YELLOW + " |")
    print(Fore.YELLOW + "| • " + Fore.MAGENTA + "CONTACT" + Fore.YELLOW + "           |   " + Fore.MAGENTA + "https://t.me/nyenyenye1337" + Fore.YELLOW + "    |")
    print(Fore.YELLOW + "|═════════════════════|═════════════════════════════════|")

# Function to scrape domain names from the URL with specified page number
def scrape_domains(url, page, headers):
    url_with_page = url.format(page)
    response = requests.get(url_with_page, headers=headers, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch URL:", response.status_code)
        return None

# Function to process the HTML content and extract domain names
def process_domains(content, headers):
    domain_paths = re.findall(r'<a href="/domain/(.*?)">', content)
    domain_names = set(domain_paths)  # Ensure domain names are unique

    with open("responses.txt", "a") as file:
        for domain_path in domain_paths:
            domain_url = f"https://leakix.net/domain/{domain_path}"
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    response = requests.get(domain_url, headers=headers, verify=False)
                if response.ok:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_content = soup.get_text()

                    # Extract host, username, password, protocol, and port
                    host = re.findall(r'"host":\s*"([^"]+)"', text_content)
                    username = re.findall(r'"username":\s*"([^"]+)"', text_content)
                    password = re.findall(r'"password":\s*"([^"]+)"', text_content)
                    protocol = re.findall(r'"protocol":\s*"([^"]+)"', text_content)
                    port = re.findall(r'"port":\s*(\d+)', text_content)

                    # Format and save the extracted information without "Response for ..."
                    if host:
                        file.write(f"Host: {host[0]}\n")
                    if username:
                        file.write(f"Username: {username[0]}\n")
                    if password:
                        file.write(f"Password: {password[0]}\n")
                    if protocol:
                        file.write(f"Protocol: {protocol[0]}\n")
                    if port:
                        file.write(f"Port: {port[0]}\n")
                    file.write("\n\n")
                    print(f"{GREEN}Response for {domain_url} saved in responses.txt{RESET}")
                else:
                    print(f"{RED}Failed to fetch response for {domain_url}{RESET}")
            except SSLError:
                print(f"{RED}SSL certificate verification failed for {domain_url}. Skipping...{RESET}")
            except ConnectionError:
                print(f"{RED}Connection error occurred for {domain_url}. Skipping...{RESET}")

# Function to get the last scraped page number
def get_last_page_number():
    try:
        with open("last_page.txt", "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0

# Function to save the current page number
def save_current_page_number(page):
    with open("last_page.txt", "w") as file:
        file.write(str(page))

# Main function to orchestrate the scraping and processing
def main():
    print_banner()

    base_url = "https://leakix.net/search?page={}&q=%2Bplugin%3AVsCodeSFTPPlugin&scope=leak"
    cookie = input(f"{RED}Enter Cookie (if you don't have cookie, the limit is 10 pages): {RESET}")  # Prompt the user to enter the cookie value
    headers = {
        'Cookie': cookie
    }
    last_page = get_last_page_number()
    try:
        # Prompt the user to enter the page value
        page_value = int(input(f"{RED}Enter Page Value (Maximum page is 50): {RESET}"))
        for page in range(last_page + 1, page_value + 1):  # Scraping pages from the last saved page to the entered page value
            print(f"Scraping page {page}...")
            content = scrape_domains(base_url, page, headers)
            if content:
                process_domains(content, headers)
                save_current_page_number(page)
            else:
                print(f"{RED}No content found on page {page}{RESET}")
    except KeyboardInterrupt:
        print(f"{RED}Scraping interrupted. Last scraped page: {page}{RESET}")
        save_current_page_number(page)

if __name__ == "__main__":
    main()
                           
