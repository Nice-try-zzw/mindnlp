# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Fasttext_embedding"""

import os
import re
from itertools import islice
import numpy as np
from mindspore import nn
from mindspore import ops
from mindspore import Tensor
from mindspore.dataset.text.utils import Vocab
from mindnlp.utils import cache_file, unzip
from mindnlp.abc.modules.embedding import TokenEmbedding
from mindnlp.configs import DEFAULT_ROOT


class Fasttext(TokenEmbedding):
    r"""
    Create vocab and Embedding from a given pre-trained vector file.
    """
    urls = {
        "1M": "https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M.vec.zip",
        "1M-subword": "https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M-subword.vec.zip",
    }

    dims = [300]

    def __init__(self, vocab: Vocab, init_embed, requires_grad: bool = True, dropout=0.5, train_state: bool = True):
        r"""
        Initializer.

        Args:
            vocab (Vocab) : Passins into Vocab for initialization.
            init_embed : Passing into Tensor, Embedding, Numpy.ndarray, etc.,
                        use this value to initialize Embedding directly.
            requires_grad (bool): Whether this parameter needs to be gradient to update.
            dropout (float): Dropout of the output of Embedding.
            train_state (bool): The network is in a state of training or inference.
                                True:train state;False:inference state.
        """
        super().__init__(vocab, init_embed)

        self._word_vocab = vocab
        self.vocab_size = init_embed.shape[0]
        self.embed = init_embed
        self._embed_dim = init_embed.shape[1]
        self._embed_size = init_embed.shape
        self.requires_grad = requires_grad
        self.dropout_layer = nn.Dropout(1 - dropout)
        self.train_state = train_state

    @classmethod
    def from_pretrained(cls, name='1M', dims=300, root=DEFAULT_ROOT,
                        special_tokens=("<unk>", "<pad>"), special_first=False):
        r"""
        Creates Embedding instance from given 2-dimensional FloatTensor.

        Args:
            name (str): The name of the pretrained vector.
            dims (int): The dimension of the pretrained vector.
            root (str): Default storage directory.
            special_tokens (tuple<str,str>): List of special participles.<unk>:Mark the words that don't exist;
            <pad>:Align all the sentences.
            special_first (bool): Indicates whether special participles from special_tokens will be added to
            the top of the dictionary. If True, add special_tokens to the beginning of the dictionary,
            otherwise add them to the end.
        Returns:
            - ** cls ** - Returns a embedding instance generated through a pretrained word vector.
            - ** vocab ** - Vocabulary extracted from the file.

        """
        if name not in cls.urls:
            raise ValueError(f"The argument 'name' must in {cls.urls.keys()}, but got {name}.")
        if dims not in cls.dims:
            raise ValueError(f"The argument 'dims' must in {cls.dims}, but got {dims}.")
        cache_dir = os.path.join(root, "embeddings", "Fasttext")

        url = cls.urls[name]
        download_file_name = re.sub(r".+/", "", url)
        fasttext_file_name = f"wiki-news-{dims}d-{name}.vec"
        path, _ = cache_file(filename=download_file_name, cache_dir=cache_dir, url=url)
        decompress_path = os.path.join(cache_dir, fasttext_file_name)
        if not os.path.exists(decompress_path):
            unzip(path, cache_dir)

        fasttext_file_path = os.path.join(cache_dir, fasttext_file_name)

        embeddings = []
        tokens = []
        with open(fasttext_file_path, encoding='utf-8') as file:
            for line in islice(file, 1, None):
                word, embedding = line.split(maxsplit=1)
                tokens.append(word)
                embeddings.append(np.fromstring(embedding, dtype=np.float32, sep=' '))

        embeddings.append(np.random.rand(dims))
        embeddings.append(np.zeros((dims,), np.float32))

        vocab = Vocab.from_list(tokens, list(special_tokens), special_first)
        embeddings = np.array(embeddings).astype(np.float32)
        return cls(vocab, Tensor(embeddings), True, 0.5), vocab

    def construct(self, ids):
        r"""
        Use ids to query embedding
        Args:
            ids : Ids to query.

        Returns:
            - ** compute result ** - Tensor, returns the Embedding query results.

        """
        tensor_ids = Tensor(ids)
        out_shape = tensor_ids.shape + (self._embed_dim,)
        flat_ids = tensor_ids.reshape((-1,))
        output_for_reshape = ops.gather(self.embed, flat_ids, 0)
        output = ops.reshape(output_for_reshape, out_shape)
        return self.dropout(output)
