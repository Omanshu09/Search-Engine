from backend.indexing.tokenizer import Tokenizer


def test_tokenize_lowercases_and_splits():
    tok = Tokenizer(remove_stopwords=False)
    assert tok.tokenize("Hello, World!") == ["hello", "world"]


def test_tokenize_removes_stopwords():
    tok = Tokenizer(remove_stopwords=True)
    assert "the" not in tok.tokenize("the quick brown fox")
