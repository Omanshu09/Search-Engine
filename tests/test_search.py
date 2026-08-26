from backend.core.query_processor import QueryProcessor


def test_query_processor_normalizes_query():
    qp = QueryProcessor()
    processed = qp.process("  Hello WORLD  ")
    assert processed.normalized_text == "hello world"
    assert processed.keywords == ["hello", "world"]


# Full SearchEngine.search() hits the network (seed discovery + crawling),
# so it's exercised via manual/integration testing rather than unit tests here.
