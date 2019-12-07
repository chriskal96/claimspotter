import numpy as np
import os
from model import ClaimBusterModel
from models import bert2
from utils.data_loader import DataLoader
from utils import transformations as transf
from flags import FLAGS
from absl import logging
import tensorflow as tf


class ClaimBusterAPI:
    def __init__(self):
        logging.set_verbosity(logging.ERROR)
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join([str(z) for z in FLAGS.gpu])
        os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

        self.return_strings = ['Non-factual statement', 'Unimportant factual statement', 'Salient factual statement']
        self.tokenizer = bert2.bert_tokenization.FullTokenizer(os.path.join(FLAGS.bert_model_loc, "vocab.txt"),
                                                               do_lower_case=True)

        transf.load_dependencies()

        self.model = ClaimBusterModel()
        self.model.warm_up()
        self.model.load_custom_model()

    def subscribe_cmdline_query(self):
        print('Enter a sentence to process')
        return self._retrieve_model_preds(self._prc_sentence_list([input().strip('\n\r\t ')]))

    def single_sentence_query(self, sentence):
        return self._retrieve_model_preds(self._prc_sentence_list([sentence.strip('\n\r\t ')]))

    def batch_sentence_query(self, sentence_list):
        sentence_list = [x.strip('\n\r\t ') for x in sentence_list]
        return self._retrieve_model_preds(self._prc_sentence_list(sentence_list))

    def _prc_sentence_list(self, sentence_list):
        sentence_features = [self._extract_info(x) for x in sentence_list]
        return tf.data.Dataset.from_tensor_slices(self._create_bert_features(sentence_features)).batch(
            FLAGS.batch_size)

    def _retrieve_model_preds(self, dataset):
        ret = []
        for x in dataset:
            ret = ret + self.model.preds_on_batch(x)
        return ret

    def _create_bert_features(self, sentence_list):
        features = [self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(x))
                    for x in sentence_list]
        return DataLoader.pad_seq(features)

    @staticmethod
    def _extract_info(sentence):
        sentence = transf.transform_sentence_complete(sentence)
        sent = transf.get_sentiment(sentence)

        return sentence, sent
