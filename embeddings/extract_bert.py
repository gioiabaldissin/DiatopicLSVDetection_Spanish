import numpy as np
import torch
from transformers import BertForMaskedLM, BertTokenizer, BertModel


def extract_embeddings(sentences, pretrained="bert-base-multilingual-cased"): 
  """
  Extract BERT embeddings for these sentences
  :param sentences: sentences to extract the embeddings to
  :param pretrained: BERT model. By default is "bert-base-multilingual-cased"
  However it is also tested with "dccuchile/bert-base-spanish-wwm-cased".
  In theory any pretrained BertTokenizer/BertModel should work. See more on 
  https://huggingface.co/transformers/pretrained_models.html
  """

  tokenizer = BertTokenizer.from_pretrained(pretrained)
  model = BertModel.from_pretrained(pretrained, output_hidden_states = True)
  context_vectors = []

  for test_sentence in sentences:
    target_word = test_sentence["target_word"]
    window = test_sentence["window"]

    targetWords=[]
    targetWords.append(tokenizer.tokenize(target_word))
    targetWords=targetWords[0]

    marked_text = "[CLS] " + " ".join(window) + " [SEP]"
    tokenized_text = tokenizer.tokenize(marked_text)
    
    
    #Search the indices of the tokenized target word in the tokenized text
    targetWordIndices=[]

    for i in range(0, len(tokenized_text)):
        if tokenized_text[i] == targetWords[0]:
            for l in range(0, len(targetWords)):
                if tokenized_text[i+l] == targetWords[l]:
                    targetWordIndices.append(i+l)
                if len(targetWordIndices) == len(targetWords):
                    break             
    
    #Create BERT Token Embeddings        
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    segments_ids = [1] * len(tokenized_text)

    # Convert inputs to PyTorch tensors
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensors = torch.tensor([segments_ids])
    
    model.eval() 
    with torch.no_grad():
        outputs = model(tokens_tensor, segments_tensors)
        hidden_states = outputs[2]

    
    token_embeddings = torch.stack(hidden_states, dim=0)
    token_embeddings = torch.squeeze(token_embeddings, dim=1)
    token_embeddings = token_embeddings.permute(1,0,2)
    
    vectors=[]
    for number in targetWordIndices:
        token=token_embeddings[number]
        sum_vec=np.sum([
                        np.array(token[-1]),
                        np.array(token[-2]),
                        np.array(token[-3]),
                        np.array(token[-4])
                        ], 
                       axis=0)
        vectors.append(np.array(sum_vec))

    context_vectors.append(np.sum(vectors, axis=0, dtype=float))

  return context_vectors