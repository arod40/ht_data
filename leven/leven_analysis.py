import matplotlib.pyplot as plt
from itertools import product
from tqdm import tqdm
import numpy as np
from numpy.random import randint
from pathlib import Path


def random_aggregate(no_samples):
    indices = randint(0, len(list(Path("closests").iterdir())) + 1, no_samples)
    print("indices are:", " ".join([str(x) for x in indices]))
    distances = []
    for idx in tqdm(indices):
        distances.extend(1 - np.load(f"closests/closest-{idx}.npy").astype(np.float32))
    return distances


def aggregate(samples):
    # assume the first row of the first batch is of the length of the matrix
    triu_max = len(np.load(f"closests/closest-{samples[0]}.npy").astype(np.float32)[0])

    # calculate size of triu matrix non-zero elems
    total_size = triu_max * (triu_max + 1) // 2
    distances = np.zeros((total_size,))

    current = 0
    for idx in tqdm(samples):
        batch = np.load(f"closests/closest-{idx}.npy").astype(np.float32)
        for i, row in enumerate(batch):
            dist_triu_row = 1 - row[i:]
            distances[current : current + len(dist_triu_row)] = dist_triu_row
            current += len(dist_triu_row)
    return distances


if __name__ == "__main__":
    # PLOT HISTOGRAM OF THE ENTIRE UPPER TRIANGLE OF THE DISTANCE MATRIX
    no_batches = len(list(Path("closests").iterdir()))
    plt.hist(aggregate(range(no_batches)), bins=100)
    plt.show()
