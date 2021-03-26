import pandas as pd
import os
import sys

if __name__ == "__main__":
    input_path = sys.argv[1]

    for filename in os.listdir(input_path):
        df = pd.read_csv(input_path + filename, error_bad_lines=False, sep="\t")
        
        # sacar TW name de nombre archivo
        tw = filename.split(".")[0].split("_")[2]

        os.remove(input_path + filename)
        
        for row_index, row in df.iterrows():
            lemma = row['lemmas']

            if tw == lemma:
                continue
            
            df.loc[row_index, 'lemmas'] = tw
            description = row['descriptions']
            df.loc[row_index, 'descriptions'] = description + " - " + lemma

        df.to_csv(input_path + filename, mode='a', header=not os.path.exists(input_path + filename), index=False, sep="\t")