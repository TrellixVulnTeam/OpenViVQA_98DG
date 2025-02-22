import torch

from data_utils.vocabs.vocab import Vocab
from data_utils.utils import preprocess_sentence
from builders.vocab_builder import META_VOCAB

from collections import defaultdict, Counter
import json
from typing import List

@META_VOCAB.register()
class ClassificationVocab(Vocab):
    # This class is especially designed for ViVQA dataset by treating the VQA as a classification task. 
    # For more information, please visit https://arxiv.org/abs/1708.02711

    def __init__(self, config):
        super(ClassificationVocab, self).__init__(config)

    def make_vocab(self, json_dirs):
        self.freqs = Counter()
        itoa = set()
        self.max_question_length = 0
        for json_dir in json_dirs:
            json_data = json.load(open(json_dir))
            for ann in json_data["annotations"]:
                question = preprocess_sentence(ann["question"], self.tokenizer)
                for answer in ann["answers"]:
                    answer = ann["answer"]
                    answer = "_".join(answer.split())
                    self.freqs.update(question)
                    itoa.add(answer)
                if len(question) + 2 > self.max_question_length:
                        self.max_question_length = len(question) + 2

        self.itoa = {ith: answer for ith, answer in enumerate(itoa)}
        self.atoi = defaultdict()
        self.atoi.update({answer: ith for ith, answer in self.itoa.items()})
        self.total_answers = len(self.atoi)

    def encode_answer(self, answer: str) -> torch.Tensor:
        return torch.tensor([self.atoi[answer]], dtype=torch.long)

    def decode_answer(self, answer_vecs: torch.Tensor) -> List[str]:
        answers = []
        list_answers = answer_vecs.tolist()
        for answer_idx in list_answers:
            answers.append(" ".join(self.itoa[answer_idx].split("_")))

        return answers