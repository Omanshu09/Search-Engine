from backend.crawler.url_manager import URLManager


def test_url_manager_dedupes():
    manager = URLManager()
    assert manager.enqueue("https://example.com") is True
    assert manager.enqueue("https://example.com") is False


def test_url_manager_normalizes_relative_url():
    manager = URLManager()
    normalized = manager.normalize("/page", base_url="https://example.com")
    assert normalized == "https://example.com/page"


def test_url_manager_strips_tracking_params():
    manager = URLManager()
    normalized = manager.normalize("https://example.com/page?utm_source=x&id=5")
    assert "utm_source" not in normalized
    assert "id=5" in normalized


def test_html_parser_extracts_title_text_and_links():
    from backend.crawler.html_parser import HTMLParser

    html = """
    <html><head><title>Test Page</title></head>
    <body><nav>skip me</nav><p>Hello world</p><a href="/about">About</a></body></html>
    """
    parsed = HTMLParser().parse(html, base_url="https://example.com")
    assert parsed.title == "Test Page"
    assert "Hello world" in parsed.text
    assert "skip me" not in parsed.text
    assert "https://example.com/about" in parsed.links


# Crawler.crawl_url() and discover_seed_urls() hit the network, so they're
# exercised via manual/integration testing rather than unit tests here.
