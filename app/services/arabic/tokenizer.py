from camel_tools.tokenizers.word import simple_word_tokenize


class ArabicTokenizer:

    def tokenize(self, text):

        return simple_word_tokenize(text)