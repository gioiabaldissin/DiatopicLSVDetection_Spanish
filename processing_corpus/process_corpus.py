import os
import warnings
warnings.filterwarnings("ignore")
from docopt import docopt
import logging
import time
import numpy as np
import gzip
import math
import sys


import zipfile
import csv
import pandas as pd
from os import path
import re
from collections import defaultdict
import random

from scipy.sparse import dok_matrix
from scipy import sparse
from scipy.sparse import csr_matrix, load_npz, save_npz, spdiags, linalg


import pickle

from nltk.corpus import stopwords


def has_digit(w):
    return any(char.isdigit() for char in str(w))

def is_float(w):
    try:
        float(w)
    except:
        return False
    return True

def create_freqlist_w2i():

    logging.info("Create w2i")

    punctuation = [".", ",", ")", "(", "?", "!", "¿", "¡", ":", ";"]
    patterns = ["@@[0-9]*", "@ ", "@\.", "^\. ", "^, ", "^: ", "^- "]

    sw = stopwords.words("spanish")

    for file in os.listdir(corpus_path):
        if file.endswith(".zip"):
            logging.critical(file)
            archive = zipfile.ZipFile(os.path.join(corpus_path, file), "r")
            content = archive.namelist()
            for c in content:
                word_lemmas = {}
                freq_list = defaultdict(lambda: 0)
                for chunk in pd.read_csv(archive.open(c), sep="\t", encoding="latin-1", names=["_", "__", "word", "lemma", "pos"], chunksize=1000):

                    for i, row in chunk.iterrows():
                        try:
                            word = row["word"]
                            lemma = row["lemma"]
                            no_add = False

                            if word in sw:
                                continue

                            if is_float(word):
                                continue

                            if has_digit(word):
                                continue

                            if str(word).startswith("http"):
                                continue

                            if word in punctuation:
                                continue

                            for pattern in patterns:
                                if not re.search(pattern, lemma) == None:
                                    no_add = True
                                    break
                            if no_add:
                                continue

                            freq_list[word] += 1
                            word_lemmas[word] = lemma

                        except Exception as e:
                            logging.critical(e)
                            logging.critical(word)
                
                freq_list = {k:v for k,v in freq_list.items() if v > 1}
                word_lemmas = {k:v for k,v in word_lemmas.items() if k in freq_list.keys()} 

                with open(output_path + file + "_" + c  + '_freq_list.pickle', 'wb') as handle:
                    pickle.dump(freq_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

                with open(output_path + file + "_" + c  + '_word_lemmas.pickle', 'wb') as handle:
                    pickle.dump(word_lemmas, handle, protocol=pickle.HIGHEST_PROTOCOL)

                word_lemmas = {}

                w2i = {w: i for i, w in enumerate(sorted(freq_list.keys())) }

                with open(output_path + file + "_" + c + '_w2i.pickle', 'wb') as handle:
                    pickle.dump(w2i, handle, protocol=pickle.HIGHEST_PROTOCOL)

def create_cooc(corpus_text_path):
    
    window_size = 20
    cooc_mat = defaultdict(lambda: 0)
    count = 0

    zipfiles = os.listdir(corpus_text_path)
    for file in zipfiles:
        if not file.endswith(".zip"):
            continue
        archive = zipfile.ZipFile(corpus_text_path + file, "r")

        content = archive.namelist()
        for c in content:
            sentences = archive.open(c).readlines()
            count += len(sentences)
            for sentence in sentences:
                for i, word in enumerate(sentence):
                    lower_window_size = max(i-window_size, 0)
                    upper_window_size = min(i+window_size, len(sentence))
                    window = sentence[lower_window_size:i] + sentence[i+1:upper_window_size+1]
                    
                    if len(window)==0: # Skip one-word sentences
                        continue

                    if word in vocabulary:
                        windex = w2i[word]
                    
                        for contextWord in window:
                            contextWord = contextWord.rstrip()
                            if len(contextWord) == 0:
                                continue
                            if contextWord in vocabulary:
                                cooc_mat[(windex,w2i[contextWord])] += 1

    cooc_mat_sparse = dok_matrix((len(vocabulary),len(vocabulary)), dtype=float)
    cooc_mat_sparse._update(cooc_mat)

    cooc_mat_csr = csr_matrix(cooc_mat_sparse)

    sparse.save_npz(matrix_path, cooc_mat_csr) 
                 
if __name__ == "__main__":
    corpus_text_path = sys.argv[1]
    corpus_path = sys.argv[2]
    output_path = sys.argv[3]

    matrix_path = output_path + "matrix.npz"

    #create_freqlist_w2i()

    with open(output_path + 'all_w2i.pickle', 'rb') as handle:
        w2i = pickle.load(handle)

    with open(output_path + 'all_freq_list.pickle', 'rb') as handle:
        freq_list = pickle.load(handle)

    vocabulary = list(freq_list.keys())

    create_cooc(corpus_text_path)


    logging.info("DONE")