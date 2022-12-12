import pandas as pd
import numpy as np
import sys
from leven import levenshtein

path = '/data/pereza/ht'
start = int(sys.argv[1])
end = int(sys.argv[2])
df = pd.read_csv(path + '/dataset.csv')
df = df[df['title'].notna()]
df = df[df['post'].notna()]
texts = (df['title'] + " " + df['post']).astype(str)
# for i in range(len(texts)):
#   texts[i] = (''.join(x for x in texts[i] if x.isalpha())).lower()

def get_scores(index, texts_arg, verbose = 1):
    scores = np.empty((len(texts_arg)))
    for i in range(len(texts_arg)):
        if(verbose==1):
            print(f"\r{i+1}/{len(texts)}",end = "")
        scores[i] = levenshtein(texts[index], texts_arg[i])
    return scores

n_samples = len(texts)
s_inx = 0
e_inx = n_samples - 1 - start
limit = end+1
all_dists = np.empty((int(  (((n_samples-start)*(n_samples-1-start)) - (n_samples-limit)*(n_samples-1-limit))/2    )), dtype=np.float32)
for i in range(start,limit):
    print(f"\r{i+1}/{limit}",end="")
    dist = get_scores(i, list(texts[i+1:]), verbose=0)
    all_dists[s_inx:e_inx] = dist
    s_inx += n_samples-(i+1)
    e_inx += n_samples-(i+2)
np.save(path + f'/leven/{start}_{end}.npy', all_dists)