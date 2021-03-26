from collections import defaultdict
import re
import csv
from nltk.corpus import stopwords

punctuation = [".", ",", ")", "(", "?", "!", "¿", "¡", ":", ";"]
patterns = ["@@[0-9]*", "@ ", "@\.", "^\. ", "^, ", "^: ", "^- "]

sw = stopwords.words("spanish")

def get_clusters(G):
    """
    Get clusters stored in graph.       
    :param G: graph
    :return graph partitioned by classes {c:nodes_c} 
    """
    c2n = defaultdict(lambda: [])
    for node in G.nodes():
        c2n[G.nodes()[node]['cluster']].append(node)
        
    classes = [set(c2n[c]) for c in c2n]
    classes.sort(key=lambda x:-len(x)) # sort by size
        
    return classes

def has_digit(w):
    """
    :param w: string to be analyzed
    :return whether w contains a digit
    """
    return any(char.isdigit() for char in str(w))

def is_float(w):
    """
    :param w: string to be analyzed
    :return whether w is a number
    """
    try:
        float(w)
    except:
        return False
    return True

def is_valid(word):
    """
    Computes whether a string is valid
    :param word: string to be analyzed
    :return whether word is or contains a number or contains one of the invalid patterns
    """
    has_pattern = False
    has_number = is_float(word) or has_digit(word)
    for pattern in patterns:
        if not re.search(pattern, word) == None:
            has_pattern = True
            break
    return not has_number and not has_pattern

def get_cluster(clusters, node):
    """
    Get the cluster of a specific node 
    :param clusters: clusters partition of graph      
    :param node: node of graph; should be in clusters 
    :return the node cluster 
    """
    for c in range(len(clusters)):
        if node in clusters[c]:
            return c
        
    return -1

def read_sentences(context_table_path, variety=None, mask_tw=None, window_size=20, exact_word=None):
  """
  Extract the sentences out of the context_table
  :param context_table_path: path to the context table
  :param variety: Indicates sentences of which varieties should be considered.
  :param mask_tw: Indicates with which string should the target word be masked. If 'None' then it is not masked.
  :param window_size: size of the context to consider 
  :param exact_word: Indicate which exact word to extract, since in some CT there could be more than one tw. If 'None' all target words are processed
  :return the sentences extracted
  """
  testSentences=[]
  with open(context_table_path, 'r') as csvFile:
        reader = csv.DictReader(csvFile, delimiter="\t")
        for row in reader:
            testSentence = dict(row)

            if variety != None and not testSentence["dates"] in variety:
                continue

            target_index = int(testSentence["indexes"])
            target_sentence = testSentence["sentences"].split(" ")
            prev_sentence = testSentence["preceding_sentences"].split(" ")
            prev_len = len(prev_sentence)

            target_word = target_sentence[target_index]

            if exact_word != None and len(testSentence["descriptions"].split("-")) > 1:
              continue

            target_word = target_word if mask_tw == None else mask_tw

            target_sentence[target_index] = target_word
            
            norm_prev_sentence = []

            for word in prev_sentence:
              w = word.lower()
              if w in sw:
                prev_len -= 1
              elif w in punctuation:
                prev_len -= 1
              elif not is_valid(w):
                prev_len -= 1
              elif is_float(w):
                prev_len -= 1
              else:
                norm_prev_sentence.append(word)

            norm_target_sentence = []
            for i in range(len(target_sentence)):
              word = target_sentence[i]
              w = word.lower()
              if i < target_index:
                if w in sw:
                  target_index -= 1
                elif w in punctuation:
                  target_index -= 1
                elif not is_valid(w):
                  target_index -= 1
                elif is_float(w):
                  target_index -= 1
                else:
                  norm_target_sentence.append(word)
              else:
                if not w in sw and not w in punctuation and is_valid(w) and not is_float(w):
                  norm_target_sentence.append(word)
            
            foll_sent = testSentence["following_sentences"].split(" ")
            norm_foll_sent = [w for w in foll_sent if is_valid(w) and not w.lower() in sw and not is_float(w) and not w in punctuation]

            text = norm_prev_sentence + norm_target_sentence + norm_foll_sent
            index = prev_len + target_index
            
            '''

            
            text = prev_sentence + target_sentence + testSentence["following_sentences"].split(" ")
            '''

            lower_window_size = max(index-window_size, 0)
            upper_window_size = min(index+window_size, len(text))
            window = text[lower_window_size:index] + text[index:upper_window_size+1]

            testSentences.append({"target_word":target_word, "window": window, "node": testSentence["identifiers"]})

  return testSentences
