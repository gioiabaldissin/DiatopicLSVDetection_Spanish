import zipfile
import csv
import pandas as pd
from os import path
import re
from collections import defaultdict
import random

import sys


def save_context_table(output_path, row):
    write_header = not path.exists(output_path)

    with open(output_path, mode='a+', encoding="utf-8") as csv_file:
        fieldnames = [
            'lemmas',
            'pos',
            'indexes',
            'preceding_sentences',
            'sentences',
            'following_sentences',
            'dates',
            'filenames',
            'identifiers',
            'descriptions']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter="\t")

        if write_header:
            writer.writeheader()
        writer.writerow(row)


def find_target_sentences_lemmatized(target_word, variety, input_path, input_file, target_pos=None):
    try:
        archive = zipfile.ZipFile(input_path + input_file, "r")
    except:
        print("No zipfile found for: " + variety)
        return

    content = archive.namelist()

    eos = ["$.", "$!", "$?", "$;"]
    #ignore = "@ @ @ @ @ @ @ @ @"

    # read all txt files inside the zip file
    print("Processing '" + target_word + "' in '" + variety + "'")
    for c in content:
        df = pd.read_csv(archive.open(c), sep="\t", encoding="latin-1")
        # get all indices of the tw in the current corpus file
        indices = df.index[df[df.columns[3]] == target_word].tolist()
        total = str(len(indices))
        j = 0
        #print("found " + total + " instances of '" + target_word + "'")

        for index in indices:
            j += 1
            try:
                
                pos = df.iloc[index, 4].strip()
                if not (target_pos == None or pos in target_pos):
                    continue
                prev_low = max([0, index - 70])
                prev_high = next(i for i in reversed(range(prev_low, index)) if df.iloc[i, 3] in eos)

                foll_high = min([len(df.index) - 1, index + 70])
                foll_low = next(i for i in range(index + 1, foll_high) if df.iloc[i, 3] in eos) + 1

                #print([index, prev_low, prev_high, foll_low, foll_high])

                prev = [word for word in df.iloc[prev_low:prev_high + 1, 2]]
                sentence = [word for word in df.iloc[prev_high + 1: foll_low, 2]]
                foll = [word for word in df.iloc[foll_low:foll_high, 2]]

                word_index = index - prev_high - 1

                current_context = {
                    "lemmas": target_word,
                    "pos": pos,
                    "indexes": word_index,
                    "preceding_sentences": " ".join(prev).replace("\t", " "),
                    "sentences": " ".join(sentence).replace("\t", " "),
                    "following_sentences": " ".join(foll).replace("\t", " "),
                    "dates": variety_code[variety],
                    "filenames": c,
                    "identifiers": input_file + "-" + c + "-" + str(index) + "-" + str(word_index),
                    "descriptions": "[" + variety + "] " + variety_full[variety]
                }
                #print("writing to file [" + str(j) + "/" + total + "]")
                if bool(re.search(r"@ (@ +)", current_context["preceding_sentences"]))\
                        or bool(re.search(r"@ (@ +)", current_context["sentences"])) \
                        or bool(re.search(r"@ (@ +)", current_context["following_sentences"])):
                    continue

                save_context_table(output_path + "context_table_" + target_word + ".csv", current_context)
                
                #break
            except MemoryError as e:
                print(str(e))

                continue
            except Exception as e:
                print(str(e))

                continue
        #break
        #print()


variety_full = {
    "ES": "Spain",
    "CU": "Cuba",
    "AR": "Argentina",
    "CO": "Colombia",
    "VE": "Venezuela",
    "MX": "Mexico",
    "PE": "Peru"
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

variations = {
    "CU": "wlp_CU-rag.zip",
    "AR": "wlp_AR-tez.zip",
    "CO": "wlp_CO-pem.zip",
    "VE": "wlp_VE-wsc.zip",
    "MX": "wlp_MX-vzo.zip",
    "PE": "wlp_PE-tae.zip",
    "ES": "wlp_ES-sbo.zip"
}

target_poss={
    "guagua": ["n", "nfp", "nfs"]
}

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

def select_target_variations():
    result = defaultdict(list)
    for tw, variations_list in target_words.items():
        current_var = []
        for variations in variations_list:
            r = random.choice(variations)
            current_var.append(r)
        result[tw] = current_var

    return result


if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    current_variations = select_target_variations()

    for target_word in target_words.keys():
        for variation in current_variations[target_word]:
            current_pos = None
            if target_word in target_poss:
                current_pos = target_poss[target_word]
            find_target_sentences_lemmatized(target_word, variation, input_path, variations[variation], current_pos)

    