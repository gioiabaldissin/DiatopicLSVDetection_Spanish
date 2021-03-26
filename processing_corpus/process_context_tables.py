import pandas as pd
from collections import defaultdict
import random
import os
from os import path
import re

import sys

target_words = {
    "guagua" : [["CU"], ["AR"], ["PE"]], 
    "colectivo":[["AR", "VE"], ["ES"], ["PE", "MX", "CO"]], 
    "carro":[ ["CU"], ["ES"]],
    "coche":[["ES"], ["PE"]],
    "plomero":[["AR", "CO", "CU", "MX", "PE", "VE"], ["ES"]], 
    "botar":[ ["CO", "CU", "MX", "PE", "VE"], ["ES"]], 
    "tirar":[["VE", "CU"], ["ES"]],
    "timón":[["CO", "CU", "PE"], ["ES"]], 
    "volante":[["AR", "CO", "MX", "PE", "VE"], ["ES"]],
    "bolo":[["AR"], ["CU"], ["MX"]], 
    "amarrar":[["AR", "CU", "PE", "VE"], ["CO", "MX"], ["ES"]],
    "atar":[["ES"]], 
    "saco":[["AR","CO","CU","MX","PE","VE"], ["ES"]], 
    "vereda":[["AR", "PE", "VE"], ["MX"], ["ES"]], 
    "chamaco":[["CU"], ["MX"]],
    "pollera":[["ES", "VE"], ["MX"], ["AR"]], 
    "vidriera":[["ES"], ["AR", "CU", "VE"]], 
    "escaparate":[["CO", "CU", "VE"], ["ES"]], 
    "argolla":[["ES"], ["AR", "CO", "MX", "PE"]], 
    "cartera":[["ES"], ["AR", "CO", "CU", "MX", "PE", "VE"]], 
    "vaina":[["MX", "CO", "PE", "VE"], ["ES"]], 
    "baúl":[["AR", "CO", "CU"], ["ES"]], 
    "churro":[["ES"], ["CO", "AR"], ["MX"]], 
    "banco": [["ES"]],
    "gato": [["ES"]],
    "bolso": [["ES"]],
    "fontanero": [["ES"]],
    "franela": [["VE", "CO"], ["ES"]],
    "camiseta": [["ES"]],
    "sindicar": [["CO", "PE", "AR"], ["ES"]],
    "acusar": [["ES"], ["AR"]],
    "falda": [["ES"]],
    "pibe": [["AR"]]
}

variety_code = {
        "ES": 0,
        "CU": 1,
        "AR": 3,
        "CO": 2,
        "VE": 6,
        "MX": 5,
        "PE": 4
    }

def normalize_sentence(sentence):

    sentence = sentence.replace(" .", ".")
    sentence = sentence.replace(" ,", ",")
    sentence = sentence.replace(" )", ")")
    sentence = sentence.replace("( ", "(")
    sentence = sentence.replace(" ?", "?")
    sentence = sentence.replace(" !", "!")
    sentence = sentence.replace("¿ ", "¿")
    sentence = sentence.replace("¡ ", "¡")
    sentence = sentence.replace(" :", ":")
    sentence = sentence.replace(" ;", ";")
    sentence = sentence.replace("\t", " ")
    sentence = sentence.replace(" a el ", " al ")
    sentence = sentence.replace(" de el ", " del ")
    sentence = re.sub("@@[0-9]*", "", sentence)
    sentence = re.sub("@ ", "", sentence)
    sentence = re.sub("@\.", "", sentence)
    sentence = re.sub("^\. ", "", sentence)
    sentence = re.sub("^, ", "", sentence)
    sentence = re.sub("^: ", "", sentence)
    sentence = re.sub("^- ", "", sentence)
    
    return sentence

def update_index(index, sentence):

    current_index = index

    punctuation = [".", ",", ")", "(", "?", "!", "¿", "¡", ":", ";"]
    contractions_left = ["a","de"]
    contractions_right = ["el"]
    patterns = ["@@[0-9]*", "@ ", "@\.", "^\. ", "^, ", "^: ", "^- "]

    parts = sentence.split(" ")

    for i in range(index):
        if parts[i] in punctuation:
            current_index -= 1
        elif parts[i] in contractions_left:
            try:
                if parts[i + 1] in contractions_right:
                    current_index -= 1
            except:
                continue
        else:
            for pattern in patterns:
                if not re.search(pattern, parts[i]) == None:
                    current_index -= 1
                    break
             

    return current_index

def normalize(df):
  for i, row in df.iterrows():
    try:
        df.loc[i, "sentences"] = normalize_sentence(row["sentences"]) 
        df.loc[i, "indexes"] = update_index(row["indexes"], row["sentences"])
        df.loc[i, "preceding_sentences"] = normalize_sentence(row["preceding_sentences"]) 
        df.loc[i, "following_sentences"] = normalize_sentence(row["following_sentences"]) 
    except:
        print(i)
  return df

def select_target_variations():
    result = defaultdict([])
    for tw, variations_list in target_words.items():
        current_var = []
        for variations in variations_list:
            current_var.append(random.choice(variations))
        result[tw] = current_var

    return result

def select_context(df, variation, n=50):
    df = df[df["dates"] == variation]
    return df.sample(n = min(n, len(df)), replace = False)


if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    #variations = select_target_variations()

    for filename in os.listdir(input_path):
        df = pd.read_csv(input_path + filename, error_bad_lines=False, sep="\t")
        df = df.drop_duplicates(subset="sentences")
        df.fillna("", inplace=True)
        tw = filename.split(".")[0].split("_")[2]
        #discover variations
        for variation in df.dates.unique():
            current_df = select_context(normalize(df), variation, n=15)
            current_df.to_csv(output_path + filename, mode='a', header=not os.path.exists(output_path + filename), index=False, sep="\t")