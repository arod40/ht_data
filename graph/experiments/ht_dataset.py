from random import choice

import networkx as nx
from ht_heuristics import phone_number_heuristic, tracks_heuristics
from tqdm import tqdm

from leven import levenshtein

from pathlib import Path

from pandas import read_csv, DataFrame


def get_ht_connected_components(G, data_df, graph2index, places_df, save_to_dir=None):
    for i, component in tqdm(list(enumerate(nx.connected_components(G)))):
        subgraph = G.subgraph(component)
        if phone_number_heuristic(subgraph, data_df, graph2index) or tracks_heuristics(
            subgraph, data_df, graph2index, places_df
        ):
            if save_to_dir is not None:
                nx.write_edgelist(subgraph, f"{save_to_dir}/{i}.csv")
            yield i, component


def get_ht_edges_with_leven_threshold(G, data_df, graph2index, threshold=0.5):
    for node1, node2 in tqdm(list(G.edges)):
        body1 = data_df.loc[data_df["index"] == graph2index[int(node1)]].post.values[0]
        body2 = data_df.loc[data_df["index"] == graph2index[int(node2)]].post.values[0]
        if (
            isinstance(body1, str)
            and isinstance(body2, str)
            and levenshtein(body1, body2) / max(len(body1), len(body2)) > threshold
        ):
            yield node1, node2


def get_node2cc_map(G):
    node2cc = {}
    for i, component in tqdm(list(enumerate(nx.connected_components(G)))):
        for node in component:
            node2cc[node] = i
    return node2cc


# each pair is sampled uniformly at random, but we make sure that the two nodes are not in the same connected component
def get_negative_pairs(G, n):
    node2cc = get_node2cc_map(G)
    nodes = list(G.nodes)
    while n > 0:
        n1, n2 = choice(nodes), choice(nodes)
        if n1 == n2 or node2cc[n1] == node2cc[n2]:
            continue
        n -= 1
        yield n1, n2


# a pair is a positive example if it is in the same connected component and has a high levensthein distance
# i.e. the two posts have different text content
def create_ht_dataset_with_ht_edges(dataset_dir, graph_source_index_path, graph2index_path, save_to_dir):

    # Read graph data

    graph_data = read_csv(graph_source_index_path).to_numpy()
    G = nx.Graph()
    G.add_edges_from(graph_data)

    graph2index = read_csv(graph2index_path).to_dict()["index"]

    data_df = read_csv(dataset_dir)

 
    # Create positive pairs

    positive_pairs = [
        (graph2index[n1], graph2index[n2])
        for n1, n2 in get_ht_edges_with_leven_threshold(G, data_df, graph2index)
    ]
    positive_df = DataFrame(positive_pairs, columns=["index1", "index2"])
    positive_df.to_csv(save_to_dir / "ht_positive_pairs.csv")

    # Create negative pairs

    negative_pairs = [
        (graph2index[n1], graph2index[n2])
        for n1, n2 in get_negative_pairs(G, len(positive_pairs))
    ]
    negative_df = DataFrame(negative_pairs, columns=["index1", "index2"])
    negative_df.to_csv(save_to_dir / "ht_negative_pairs.csv")
