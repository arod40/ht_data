from itertools import product
from pandas import read_csv
from leven import levenshtein
from heapq import heappush, heappop
from tqdm import tqdm
from pathlib import Path
import multiprocessing
from joblib import Parallel, delayed
import numpy as np

cpu_count = multiprocessing.cpu_count()

def func(p1, data_index):
    return [levenshtein(p1,p2) / max(len(p1), len(p2)) for p2 in data_index]

def find_closests_parallel(csv_path, dump_to_dir, batch_size, slice=(0,-1)):
    lower, upper =  slice
    data_index = read_csv(csv_path).dropna().post.to_numpy()[lower:upper]
    batches = len(data_index) // batch_size + 1
    
    for batch in tqdm(list(range(batches))):
        b_low, b_high = batch*batch_size, (batch + 1)*batch_size
        parallel = Parallel(n_jobs=cpu_count, backend="multiprocessing")
        results = np.stack(parallel(delayed(func)(p, data_index) for p in data_index[b_low: b_high]))
        np.save(dump_to_dir / f"closest-{batch}.npy", results)

    