import networkx as nx
from pandas import read_csv
import matplotlib.pyplot as plt
from tqdm import tqdm
from pathlib import Path

data = read_csv("query.csv").to_numpy()

G = nx.Graph()
G.add_edges_from(data)

for i, component in tqdm(list(enumerate(nx.connected_components(G)))):
    size_folder = Path(f'results/components/{len(component)}')
    if not size_folder.exists():
        size_folder.mkdir()

    # fig, ax = plt.subplots()

    nx.draw_networkx(G.subgraph(component), with_labels=False, node_size=10,alpha=0.1, width=0.3)
    plt.axis('off')
    plt.savefig(size_folder/f'{i}.png', dpi=400)
    Path(size_folder/f'{i}.nodes').write_text(" ".join([str(x) for x in component]))

    plt.clf()