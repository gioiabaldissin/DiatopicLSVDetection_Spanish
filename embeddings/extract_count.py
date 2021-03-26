from modules import modules_

import math
from scipy import sparse
from scipy.sparse import load_npz

varieties_code = {
    "0": "ES",
    "1": "CU",
    "2": "CO",
    "3": "AR",
    "4": "PE",
    "5": "MX",
    "6": "CU",
    "7": "VE"
}

def extract_count_vectors(sentences, freq_list, w2i, cooc_mat_sparse_norm, count):
  contexts = []
  for sentence in sentences:
    centroid = None
    for w in sentence["window"]:
        if (not w in w2i.keys()):
            continue
        index = w2i[w]

        ai = math.log(count/freq_list[w])
        current_context = cooc_mat_sparse_norm[index] * ai
        if centroid == None:
            centroid = current_context
        else:
            centroid += current_context
    
    contexts.append(centroid)

  m = sparse.vstack(contexts)
  print(m.shape)
  return m

def compute_vectors(target_word, pathTestSentences, variety, vectors_path, freq_list, w2i, joint=False, exact_target_word=True):
    vectors = []
    matrices = []
    sentences = []

    for current_variety in variety:
        current_cooc_mat = load_npz(vectors_path + "matrix_all_" + varieties_code[current_variety] + ".npz")
        matrices.append(current_cooc_mat)

    joint_matrix = matrices[0]

    for i in range(1,len(matrices)):
        joint_matrix += matrices[i]

    for i in range(len(variety)):
        current_variety = variety[i]

        current_sentences = modules_.read_sentences(pathTestSentences, variety=[current_variety], exact_word=target_word if exact_target_word else None)
        if len(current_sentences) == 0:
            continue

        current_vectors = extract_count_vectors(current_sentences, freq_list, w2i, joint_matrix if joint else matrices[i])

        vectors.append(current_vectors)
        sentences = sentences + current_sentences

    return sparse.vstack(vectors), sentences