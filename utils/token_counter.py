from sentencepiece import SentencePieceProcessor

from Constants import Constants
import tiktoken

class TokenCounter:
    def __init__(self,
                 count_typ='estimate'):
        self.tokenizer_model = None
        self.count_typ = count_typ  # count_typ options are 'estimate', 'local' 'openAI'

    def count_tokens(self, text: str) -> int:
        if self.count_typ == 'estimate':
            return int(round((len(text)/Constants.AVG_TOKEN_CHARACKTER_COUNT), 0))
        elif self.count_typ == 'local':
            if self.tokenizer_model is None:
                self.tokenizer_model = SentencePieceProcessor(model_file=Constants.TOKENIZER_LOCAL_MODEL_PATH)
            return self._local_tokenizer(text)
        elif self.count_typ == 'openAI':
            return self._open_ai_tokenizer(string=text, model_name=Constants.TOKENIZER_MODEL)

    def _local_tokenizer(self, text: str) -> int:
        tokens = self.tokenizer_model.EncodeAsIds(text)
        return len(tokens)

    @staticmethod
    def _open_ai_tokenizer(string: str, model_name: str = "gpt-4o-mini") -> int:
        """Returns the number of tokens in a text string."""
        encoding_name = tiktoken.encoding_for_model(model_name).name
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

