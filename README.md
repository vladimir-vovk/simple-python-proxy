Simple proxy server with python. Adds characters to words with specified length.

# Usage
1. Install python 2.7
2. Install BeautifulSoup:

  ```
  easy_install-2.7 beautifulsoup4
  ```
3. Run proxy from command line:

  ```
  python simple-proxy.py
  ```
4. Open [localhost:1234](http://localhost:1234/) in your favorite browser.

## Proxy optional arguments:
```
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Proxy port
  --host HOST           Proxy host
  -d DOMAIN, --domain DOMAIN
                        Domain name
  -l LENGTH, --length LENGTH
                        Add chars to words with specified length
  -c CHARS, --chars CHARS
                        Chars to add after words with specified length
```
