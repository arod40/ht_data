import networkx as nx
from pandas import read_csv
import matplotlib.pyplot as plt
from tqdm import tqdm
from pathlib import Path

exp_dir = Path("350kdata-cc")

data = read_csv(exp_dir / "query.csv").to_numpy()

G = nx.Graph()
G.add_edges_from(data)

for i, component in tqdm(list(enumerate(nx.connected_components(G)))):
    size_folder = exp_dir / f'results/components/{len(component)}'
    if not size_folder.exists():
        size_folder.mkdir()

    # fig, ax = plt.subplots()

    nx.draw_networkx(G.subgraph(component), with_labels=False, node_size=10,alpha=0.1, width=0.3)
    plt.axis('off')
    plt.savefig(size_folder/f'{i}.png', dpi=400)
    Path(size_folder/f'{i}.nodes').write_text(" ".join([str(x) for x in component]))

    plt.clf()