import json
from random import randint, shuffle

import matplotlib.pyplot as plt
import numpy as np
import requests
from pandas import read_csv
from scipy.stats import truncnorm
from sortedcollections import SortedList
from tqdm import tqdm
from pathlib import Path
from shuffle import lazy_shuffle

FAKE = "FAKE_ANOTATOR"


def assign_annotators(commitment, overlap):
    total_commitment = sum(commitment.values())
    if total_commitment % overlap != 0:
        fake_effort = overlap - total_commitment % overlap
        commitment[FAKE] = fake_effort
        total_commitment += fake_effort

    data_indices = list(range(total_commitment // overlap))
    annotators = list(commitment.keys())

    shuffle(data_indices)
    shuffle(annotators)

    replicated_annotators = [
        annotator for annotator in annotators for _ in range(commitment[annotator])
    ]
    replicated_data_indices = data_indices * overlap

    assignment = {annotator: [] for annotator in annotators}
    for annotator, data_idx in zip(replicated_annotators, replicated_data_indices):
        assignment[annotator].append(data_idx)

    return assignment, total_commitment


def aggregate(distances_dir):
    samples = range(len(list(Path(distances_dir).iterdir())))

    # assume the first row of the first batch is of the length of the matrix
    triu_max = len(
        np.load(f"{distances_dir}/closest-{samples[0]}.npy").astype(np.float32)[0]-1
    )

    # calculate size of triu matrix non-zero elems
    total_size = triu_max * (triu_max + 1) // 2
    distances = np.zeros((total_size,))

    current = 0
    i = 1
    for idx in tqdm(samples):
        batch = np.load(f"{distances_dir}/closest-{idx}.npy").astype(np.float32)
        for row in batch:
            dist_triu_row = 1 - row[i:]
            distances[current : current + len(dist_triu_row)] = dist_triu_row
            current += len(dist_triu_row)
            i += 1
    return distances

def triu_index_gen(n):
    k = 1
    for i in range(n):
        for j in range(k,n):
            yield i,j
        k += 1

def lazy_shuffle_gen(l):
    return (l[idx] for idx in lazy_shuffle(len(l)))


def get_truncated_gaussian_sample(
    low=0, up=1, mu=0.5, sigma=0.35, size=10000, plot=False, seed=None
):
    a, b = (low - mu) / sigma, (up - mu) / sigma
    sample = truncnorm.rvs(a, b, loc=mu, scale=sigma, size=size, random_state=seed)

    if plot:
        x_range = np.linspace(low, up, 1000)
        plt.plot(x_range, truncnorm.pdf(x_range, a, b, loc=mu, scale=sigma))
        plt.hist(sample, bins=100, density=True)
        plt.show()

    return sample


def find_closest(sample: SortedList, x, tol):
    i = sample.bisect_left(x)
    if i > 0 and (i == len(sample) or sample[i] - x >= x - sample[i - 1]):
        i -= 1
    if abs(sample[i] - x) < tol:
        return i
    else:
        return -1


def subsample_with_distribution(data_points, sample, tol=0.1):
    sample = SortedList(sample)
    values = []
    ret_sample = []
    for x, (i, j) in data_points:
        if len(sample) == 0:
            break
        k = find_closest(sample, x, tol)
        if k >= 0:
            a = sample[k]
            values.append(x)
            ret_sample.append((i, j))
            sample.remove(a)
    return values, ret_sample


def get_random_sample_from_triu(n, no_samples, diag=False):
    sample_control = set()
    sample = []
    posts_control = {}
    posts = []
    for _ in range(no_samples):
        idx = randint(0, n**2 - 1)
        i, j = idx // n, idx % n
        i, j = sorted((i, j))
        if (not diag and i == j) or (i, j) in sample_control:
            continue
        sample_control.add((i, j))

        if i not in posts_control:
            posts_control[i] = len(posts)
            posts.append(i)
        if j not in posts_control:
            posts_control[j] = len(posts)
            posts.append(j)

        sample.append((posts_control[i], posts_control[j]))

    return posts, sample


def get_random_sample_from_distribution(data_points, no_samples):
    dist = get_truncated_gaussian_sample(size=no_samples, plot=False)
    _, indices = subsample_with_distribution(data_points, dist)

    sample = []
    posts_control = {}
    posts = []
    for (i, j) in tqdm(indices):
        if i not in posts_control:
            posts_control[i] = len(posts)
            posts.append(i)
        if j not in posts_control:
            posts_control[j] = len(posts)
            posts.append(j)

        sample.append((posts_control[i], posts_control[j]))

    return posts, sample


def request_bulk_populate(
    host, bulk_annotation_post_endpoint, annotators, posts, annotations
):
    url = f"{host}{bulk_annotation_post_endpoint}"

    payload = json.dumps(
        {"annotators": annotators, "posts": posts, "annotations": annotations}
    )
    headers = {"Content-Type": "application/json"}

    return requests.request("POST", url, headers=headers, data=payload)


def create_assignments(
    annotators_csv_path,
    data_csv_path,
    distances_dir,
    overlap,
    host,
    bulk_annotation_post_endpoint,
):
    annotators_data = read_csv(annotators_csv_path)
    commitment = {
        idx: annotator.commitment for idx, annotator in annotators_data.iterrows()
    }

    # for bulk populate
    annotators = [
        {
            "access_code": annotator.access_code
        }
        for _, annotator in annotators_data.iterrows()
    ]

    # create assignments
    assignments, total_commitment = assign_annotators(commitment, overlap)

    # load posts data
    data = read_csv(data_csv_path).dropna()
    titles = data.title.to_numpy()
    bodies = data.post.to_numpy()

    # get random sample
    # posts_indices, sample = get_random_sample_from_triu(len(data), total_commitment)

    # get sample from distribution of the sim values
    # data_points = aggregate(distances_dir)
    # data_points = zip(lazy_shuffle_gen(data_points), triu_index_gen(len(data)))

    from itertools import product
    from numpy.random import permutation
    data_points = permutation(
        list(
            zip(
                get_truncated_gaussian_sample(
                    low=0, up=1, mu=0.1, sigma=0.5, size=10**6, plot=True
                ),
                product(range(10**3), range(10**3)),
            )
        )
    )
    posts_indices, sample = get_random_sample_from_distribution(
        data_points, total_commitment
    )

    # for bulk populate
    posts = [{"title": titles[idx], "body": bodies[idx]} for idx in posts_indices]

    # for bulk populate
    annotations = [
        {
            "left_post_index": sample[sample_idx][0],
            "right_post_index": sample[sample_idx][1],
            "annotator_index": annotator_idx,
        }
        for annotator_idx, assignment in assignments.items()
        for sample_idx in assignment
    ]

    print(
        request_bulk_populate(
            host, bulk_annotation_post_endpoint, annotators, posts, annotations
        )
    )


if __name__ == "__main__":
    create_assignments(
        "sample_annotators.csv",
        "../data/dataset.csv",
        "../closests",
        3,
        "http://localhost:8080",
        "/bulk_populate",
    )
