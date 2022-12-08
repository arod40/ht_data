def phone_number_heuristic(subgraph, data_df, graph2index, threshold=1):
    cc_nodes = subgraph.nodes
    cc_phone_numbers = set()
    for node_id in cc_nodes:
        for pn in data_df.loc[data_df['index'] == graph2index[node_id]].phone_numbers.dropna():
            cc_phone_numbers.add(pn)
    return len(cc_phone_numbers) > threshold

def tracks_heuristics(subgraph, data_df, graph2index):
    # how to find distances between regions
    # connect to google maps api maybe
    pass