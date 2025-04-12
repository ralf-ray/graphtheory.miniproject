import pandas as pd
import networkx as nx
import itertools
import matplotlib.pyplot as plt
import matplotlib
import time

matplotlib.rcParams["font.family"] = "DejaVu Sans"

# Read Excel data
df = pd.read_excel("nba_champions_rosters.xlsx")
print("Data Preview:")
print(df.head())

# Count the number of championships each player has won (node weight)
player_championships = df['Player'].value_counts().to_dict()

# Construct an undirected graph
G = nx.Graph()

# Add nodes with championship count as the node attribute 'weight'
for player, count in player_championships.items():
    G.add_node(player, weight=count)

# Group data by Season and Team (each group corresponds to a championship team roster)
grouped = df.groupby(["Season", "Team"])

# Iterate through each group to retrieve the list of players for that season and team
for (season, team), group in grouped:
    players = group["Player"].tolist()
    # Iterate through all unique pairs of players (teammates)
    for player1, player2 in itertools.combinations(sorted(players), 2):
        if G.has_edge(player1, player2):
            G[player1][player2]['weight'] += 1
        else:
            G.add_edge(player1, player2, weight=1)

# Print basic graph information
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())

# Example: Print some nodes and their championship counts
for node, data in list(G.nodes(data=True))[:10]:
    print(f"Player: {node}, Championships: {data['weight']}")

# Example: Print some edges and their co-championship counts
for u, v, data in list(G.edges(data=True))[:10]:
    print(f"Teammates: {u} - {v}, Co-championship count: {data['weight']}")

# =======================
# 1. Precompute All Unique Simple Paths (of desired length)
# =======================

def precompute_unique_paths(G, desired_length=5):
    """
    Precompute all simple paths in graph G of length 'desired_length' (e.g., paths containing exactly 5 nodes)
    and ensure that the node combinations (ignoring order) are unique (i.e., if two paths contain the same set 
    of nodes, only one is kept).
    
    Parameters:
        G: A NetworkX graph object.
        desired_length: The desired path length (number of nodes), default is 5.
        
    Returns:
        A list of all unique paths, where each path is a list of nodes.
    """
    all_paths = []
    unique_paths = set()  # Stores encountered node combinations (sorted tuples) to avoid duplicates

    def dfs(current, path):
        if len(path) == desired_length:
            # Sort the current path (ignoring order) and convert it to a tuple
            sorted_path = tuple(sorted(path))
            if sorted_path not in unique_paths:
                unique_paths.add(sorted_path)
                all_paths.append(path.copy())
            return
        for neighbor in G.neighbors(current):
            if neighbor not in path:  # Ensure a simple path, no repeated nodes
                path.append(neighbor)
                dfs(neighbor, path)
                path.pop()  # Backtrack

    # Perform DFS starting from every node in the graph
    for node in G.nodes():
        dfs(node, [node])
    return all_paths

# =======================
# 2. Function to Query Paths by a Specific Node
# =======================

def query_paths_with_node(path_library, query_node):
    """
    From the precomputed path library, return all paths that include the specified query_node.
    
    Parameters:
        path_library: A list of precomputed paths, with each path as a list of nodes.
        query_node: The target node.
        
    Returns:
        A list of paths that include query_node.
    """
    return [path for path in path_library if query_node in path]

# =======================
# 3. Compute Group Score and Find the Maximum Scoring Group
# =======================

def compute_group_score(G, group):
    """
    Compute the total score for the given 5-node group (group):
      - The node score is the sum of the weights of all nodes (e.g., the number of championships for each player).
      - The edge score is the sum of the weights of the edges between every pair of nodes within the group 
        (if an edge exists, it represents the co-championship count).
    
    Returns:
        Total score = node score + edge score.
    """
    # Calculate the sum of node weights
    node_sum = sum(G.nodes[node].get('weight', 0) for node in group)
    
    # Calculate the sum of edge weights for every pair of nodes in the group
    edge_sum = 0
    for u, v in itertools.combinations(group, 2):
        if G.has_edge(u, v):
            edge_sum += G[u][v].get('weight', 0)
    return node_sum + edge_sum

def find_max_group(G, groups):
    """
    Among all given 5-node groups in 'groups', compute the total score for each group and
    return the group with the highest score along with that score.
    """
    best_score = None
    best_group = None
    for group in groups:
        score = compute_group_score(G, group)
        if best_score is None or score > best_score:
            best_score = score
            best_group = group
    return best_group, best_score

# =======================
# 4. Precompute all unique simple paths of length 5 (ensuring unique node combinations)
# =======================
print("Precomputing all unique simple paths of length 5...")
start_time = time.time()
path_library = precompute_unique_paths(G, desired_length=5)
elapsed = time.time() - start_time
print(f"Found {len(path_library)} unique 5-node paths in {elapsed:.2f} seconds.")

# Example: Query all paths that include the node 'Tim Duncan'
query_node ='Tim Duncan'
paths_with_C = query_paths_with_node(path_library, query_node)
print(f"Paths that include node '{query_node}':")
for path in paths_with_C:
    print(path)

# Compute the score for each path group that includes the query node and find the maximum scoring group
best_group, best_score = find_max_group(G, paths_with_C)
print("Maximum scoring 5-node group with:", query_node, best_group)
print("Maximum score with:", query_node, best_score)

# Also find the maximum scoring group among all groups in the path library
best_group, best_score = find_max_group(G, path_library)
print("Maximum scoring 5-node group:", best_group)
print("Maximum score:", best_score)
