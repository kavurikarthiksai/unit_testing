import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self):
        self.index = defaultdict(str)
        self.visited = set()

    def crawl(self, url, base_url=None):
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url or url, href)
                    if full_url.startswith(base_url or url):
                        self.crawl(full_url, base_url=base_url or url)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results):
        if results:
            print("Search results:")
            for result in results:
                print(f"- {result}")
        else:
            print("No results found.")


# ========== UNIT TESTS ==========

import unittest
from unittest.mock import patch, MagicMock

class WebCrawlerTests(unittest.TestCase):
    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        sample_html = """
        <html><body>
            <h1>Welcome!</h1>
            <a href="/about">About Us</a>
            <a href="https://www.external.com">External Link</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        # Assert the main and internal page are visited
        self.assertIn("https://example.com", crawler.visited)
        self.assertIn("https://example.com/about", crawler.visited)

    @patch('requests.get')
    def test_crawl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        # Should have marked the URL as visited, but not indexed
        self.assertIn("https://example.com", crawler.visited)
        self.assertNotIn("https://example.com", crawler.index)

    def test_search(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "This has the keyword"
        crawler.index["page2"] = "No match here"

        results = crawler.search("keyword")
        self.assertEqual(results, ["page1"])

    @patch("builtins.print")
    def test_print_results(self, mock_print):
        crawler = WebCrawler()
        crawler.print_results(["https://test.com/result"])

        mock_print.assert_any_call("Search results:")
        mock_print.assert_any_call("- https://test.com/result")


# ========== MAIN RUNNER ==========

if __name__ == "__main__":
    print("Running unit tests...")
    unittest.main(exit=False)

    print("\nRunning main crawler...")
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "test"
    results = crawler.search(keyword)
    crawler.print_results(results)

# tesing---------------------------------
