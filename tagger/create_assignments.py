import json
from pathlib import Path
from random import randint, shuffle

import matplotlib.pyplot as plt
import numpy as np
import requests
from pandas import read_csv
from scipy.stats import truncnorm
from shuffle import lazy_shuffle
from sortedcollections import SortedList
from tqdm import tqdm
from tri import TriL

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
    tril_max = len(
        np.load(f"{distances_dir}/closest-{samples[0]}.npy").astype(np.float32)[0] - 1
    )

    # calculate size of triu matrix non-zero elems
    total_size = tril_max * (tril_max + 1) // 2
    distances = np.zeros((total_size,))

    current = 0
    i = 0
    for idx in tqdm(samples):
        batch = np.load(f"{distances_dir}/closest-{idx}.npy").astype(np.float32)
        for row in batch:
            dist_triu_row = 1 - row[:i]
            distances[current : current + len(dist_triu_row)] = dist_triu_row
            current += len(dist_triu_row)
            i += 1
    assert current == len(distances)
    return distances


def lazy_shuffle_two_sequences(l1, l2):
    return ((l1[idx], l2[idx]) for idx in lazy_shuffle(len(l1)))


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


def get_random_sample_from_distribution(data_points, dist="trunc_gaussian", **kwargs):
    distributions = {"trunc_gaussian": get_truncated_gaussian_sample}

    dist = distributions[dist](**kwargs)
    values, indices = subsample_with_distribution(data_points, dist)

    sample = []
    posts_control = {}
    posts = []
    for sim, (i, j) in tqdm(list(zip(values, indices))):
        if i not in posts_control:
            posts_control[i] = len(posts)
            posts.append(i)
        if j not in posts_control:
            posts_control[j] = len(posts)
            posts.append(j)

        sample.append((posts_control[i], posts_control[j], sim))

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
    host,
    bulk_annotation_post_endpoint,
    annotators_csv_path=None,
    data_csv_path=None,
    distances_dir=None,
    overlap=3,
    dist="random",
    save_to=None,
    load_from=None,
):
    assert load_from is not None or None not in [
        annotators_csv_path,
        data_csv_path,
        distances_dir,
    ], "Arguments missing"

    if load_from is None:
        annotators_data = read_csv(annotators_csv_path)
        commitment = {
            idx: annotator.commitment for idx, annotator in annotators_data.iterrows()
        }

        # for bulk populate
        annotators = [
            {"access_code": annotator.access_code}
            for _, annotator in annotators_data.iterrows()
        ]

        # create assignments
        assignments, total_commitment = assign_annotators(commitment, overlap)

        assert total_commitment % overlap == 0

        # load posts data
        data = read_csv(data_csv_path).dropna()
        titles = data.title.to_numpy()
        bodies = data.post.to_numpy()

        if dist == "random":
            # get random sample
            print("Generating random sample.")
            posts_indices, sample = get_random_sample_from_triu(
                len(data), total_commitment // overlap
            )
        else:
            # get sample from distribution of the sim values
            print(f"Generating sample from distribution: '{dist}'.")
            data_points = aggregate(distances_dir)
            data_points = lazy_shuffle_two_sequences(data_points, TriL(diag=False))
            posts_indices, sample = get_random_sample_from_distribution(
                data_points,
                "trunc_gaussian",
                size=total_commitment // overlap,
                plot=True,
            )
        print(sorted([x for _, _, x in sample]))

        # for bulk populate
        posts = [
            {"title": titles[idx], "body": bodies[idx], "external_reference": idx}
            for idx in posts_indices
        ]

        # for bulk populate
        annotations = [
            {
                "left_post_index": sample[sample_idx][0],
                "right_post_index": sample[sample_idx][1],
                "annotator_index": annotator_idx,
                "leven_sim": sample[sample_idx][2],
            }
            for annotator_idx, assignment in assignments.items()
            for sample_idx in assignment
        ]

        if save_to is not None:
            save_to = Path(save_to)
            (save_to / "annotations.json").write_text(json.dumps(annotations))
            (save_to / "annotators.json").write_text(json.dumps(annotators))
            (save_to / "posts.json").write_text(json.dumps(posts))

    else:
        annotations = json.loads((Path(load_from) / "annotations.json").read_text())
        annotators = json.loads((Path(load_from) / "annotators.json").read_text())
        posts = json.loads((Path(load_from) / "posts.json").read_text())

    print(
        request_bulk_populate(
            host, bulk_annotation_post_endpoint, annotators, posts, annotations
        )
    )


if __name__ == "__main__":
    create_assignments(
        host="http://3.138.226.155:8080",
        bulk_annotation_post_endpoint="/bulk_populate",
        annotators_csv_path="as_is_phase.csv",
        data_csv_path="../data/150k/dataset.csv",
        distances_dir="../closests",
        overlap=3,
        dist="trunc_gaussian",
        save_to="./assignments/as_is",
    )
