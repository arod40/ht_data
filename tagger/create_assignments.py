import json
from random import randint, shuffle

import matplotlib.pyplot as plt
import numpy as np
import requests
from pandas import read_csv
from scipy.stats import truncnorm

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


# def get_truncated_gaussian_sample(
#     low=0, up=1, mu=0.5, sigma=1, size=10000, plot=False, seed=None
# ):
#     mu, sigma = 0.5, 0.35
#     low, up = 0, 1

#     a, b = (low - mu) / sigma, (up - mu) / sigma
#     sample = truncnorm.rvs(a, b, loc=mu, scale=sigma, size=size, random_state=seed)

#     if plot:
#         x_range = np.linspace(low, up, 1000)
#         plt.plot(x_range, truncnorm.pdf(x_range, a, b, loc=mu, scale=sigma))
#         plt.hist(sample, bins=100, density=True)
#         plt.show()

#     return sample


# def create_samples_by_batch(
#     samples, batch_size=8
# ):
#     samples_by_batch = defaultdict(list)
#     for i, j in samples:
#         samples_by_batch[i // batch_size].append((i % batch_size, j))

#     return samples_by_batch


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
    annotators_csv_path, data_csv_path, overlap, host, bulk_annotation_post_endpoint
):
    annotators_data = read_csv(annotators_csv_path)
    commitment = {
        idx: annotator.commitment for idx, annotator in annotators_data.iterrows()
    }

    # for bulk populate
    annotators = [
        {
            "name": annotator.email,
            "password": "",
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
    posts_indices, sample = get_random_sample_from_triu(len(data), total_commitment)

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
    create_assignments("sample_annotators.csv", "../data/dataset.csv", 3, "http://localhost:8080", "/bulk_populate")
