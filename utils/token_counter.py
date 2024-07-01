from sentencepiece import SentencePieceProcessor

from Constants import Constants


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
                self.tokenizer_model = SentencePieceProcessor(model_file=Constants.TOKENIZER_MODEL)
            return self._local_tokenizer(text)
        elif self.count_typ == 'openAI':
            raise NotImplemented('Not Yet Implemented')

    def _local_tokenizer(self, text: str) -> int:
        tokens = self.tokenizer_model.EncodeAsIds(text)
        return len(tokens)
