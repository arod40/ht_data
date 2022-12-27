from itertools import product

from geopy.distance import geodesic


def phone_number_heuristic(subgraph, data_df, graph2index, threshold=1):
    cc_nodes = subgraph.nodes
    cc_phone_numbers = set()
    for node_id in cc_nodes:
        for pn in data_df.loc[
            data_df["index"] == graph2index[node_id]
        ].phone_numbers.dropna():
            cc_phone_numbers.add(pn)
    return len(cc_phone_numbers) > threshold


def tracks_heuristics(
    subgraph, data_df, graph2index, places_df, distance_threshold_mi=200
):
    cc_nodes = subgraph.nodes
    for node_id1, node_id2 in product(cc_nodes, cc_nodes):
        if node_id1 == node_id2:
            continue
        region1 = data_df.loc[data_df["index"] == graph2index[node_id1]].region
        region2 = data_df.loc[data_df["index"] == graph2index[node_id2]].region
        if region1 is None or region2 is None:
            continue

        geo1 = places_df.loc[places_df["place"] == region1].geolocation
        geo2 = places_df.loc[places_df["place"] == region2].geolocation

        if geodesic(geo1, geo2).miles < distance_threshold_mi:
            return True
    return False
