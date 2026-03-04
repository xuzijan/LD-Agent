# Mock metric module for offline validation (no word2vec required)
# Full metric files: https://drive.google.com/file/d/122sh6_nsu9ZHuefQeAPEpnX0X6jJdPXA/view

class NLGEval:
    def __init__(self, no_glove=False, metrics_to_omit=None):
        pass

    def compute_metrics(self, references, hypothesis):
        """Return (dict, list) - mock values for offline validation."""
        n = len(hypothesis) if isinstance(hypothesis, list) else 1
        return (
            {"Bleu_1": 0.1, "Bleu_2": 0.1, "Bleu_3": 0.1, "Bleu_4": 0.1, "ROUGE_L": 0.1},
            [{"Bleu_1": 0.1, "Bleu_2": 0.1, "Bleu_3": 0.1, "Bleu_4": 0.1, "ROUGE_L": 0.1}] * n,
        )
