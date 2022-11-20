class TestShortPhrase:

    def test_short_phrase(self):
        phrase = input("Set a phrase (please note that it should be shorter than 15 symbols): ")
        assert len(phrase) < 15, f"Phrase '{phrase}' consists of {len(phrase)} symbols! It should be shorter" \
                                 f" than 15 symbols."
