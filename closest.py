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


def find_closests_parallel(csv_path, dump_to_dir, batch_size, slice=(0, None)):
    lower, upper = slice
    data_index = read_csv(csv_path).dropna().post.to_numpy()
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
    slice = int(argv[3]), int(argv[4]) if len(argv) == 5 else None

    assert csv_path.exists()
    assert dump_to_dir.exists()

    slice_dir = dump_to_dir / f"{slice[0]}-{slice[1]}"
    slice_dir.mkdir(exist_ok=True)

    find_closests_parallel(csv_path, slice_dir, cpu_count, slice)
