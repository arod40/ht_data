from sys import argv
from pandas import read_csv
from leven import levenshtein
from tqdm import tqdm
from pathlib import Path
import multiprocessing
from joblib import Parallel, delayed
import numpy as np
from math import ceil

cpu_count = multiprocessing.cpu_count()


def func(p1, data_index):
    return [levenshtein(p1, p2) / max(len(p1), len(p2)) for p2 in data_index]


def find_closests_parallel(data_index, dump_to_dir, batch_size, slice=(0, None)):
    lower, upper = slice
    slice_data_index = data_index[lower:upper]
    batches = ceil(len(slice_data_index) / batch_size)

    for batch in tqdm(list(range(batches))):
        b_low, b_high = batch * batch_size, (batch + 1) * batch_size
        parallel = Parallel(n_jobs=cpu_count, backend="multiprocessing")
        results = np.stack(
            parallel(
                delayed(func)(p, data_index) for p in slice_data_index[b_low:b_high]
            )
        )
        np.save(dump_to_dir / f"closest-{batch}.npy", results)


if __name__ == "__main__":
    csv_path = Path(argv[1])
    dump_to_dir = Path(argv[2])
    dropna_variant = argv[3]
    dump_index = argv[4] # set to dump_index to store a csv with the indices
    slice = int(argv[5]), int(argv[6]) if len(argv) == 7 else None

    assert csv_path.exists()
    assert dump_to_dir.exists()

    slice_dir = dump_to_dir / f"{slice[0]}-{slice[1]}"
    slice_dir.mkdir(exist_ok=True)

    df = read_csv(csv_path)
    if dropna_variant == "108k":
        df = df.dropna()
    elif dropna_variant == "350k":
        df = df[df['title'].notna()]
        df = df[df['post'].notna()]

    if dump_index == "dump_index":
        df['index'].to_csv(dump_to_dir/"index.csv")

    data_index = df.post.to_numpy()

    print("Working with data of shape: ", data_index.shape)

    find_closests_parallel(data_index, slice_dir, cpu_count, slice)
