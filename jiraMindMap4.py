import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from tkinter import Tk
from tkinter.filedialog import askopenfilename


# Fonction pour ouvrir une boîte de dialogue et sélectionner un fichier CSV
def open_csv_file():
    Tk().withdraw()  # Cacher la fenêtre principale de Tkinter
    file_path = askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Sélectionnez le fichier CSV contenant les issues Jira"
    )
    return file_path


# Charger le fichier CSV à partir de la boîte de dialogue
file_path = open_csv_file()

# Vérifier que le fichier est sélectionné
if not file_path:
    print("Aucun fichier sélectionné. Veuillez réessayer.")
else:
    # Charger les données
    data = pd.read_csv(file_path)

    # Filtrer les colonnes pertinentes
    relevant_columns = [
        "Issue key",
        "Summary",
        "Inward issue link (Blocks)",
        "Outward issue link (Blocks)",
        "Inward issue link (Cloners)",
        "Outward issue link (Cloners)",
        "Inward issue link (Duplicate)",
        "Outward issue link (Duplicate)",
        "Inward issue link (Relates)",
        "Outward issue link (Relates)"
    ]
    filtered_data = data[relevant_columns]

    # Construire la structure du mindmap
    mindmap_structure = {}


    def add_link(issue_key, linked_issue, link_type):
        if issue_key not in mindmap_structure:
            mindmap_structure[issue_key] = {"summary": "", "links": []}
        mindmap_structure[issue_key]["links"].append((linked_issue, link_type))


    # Itérer sur les lignes du CSV
    for _, row in filtered_data.iterrows():
        issue_key = row["Issue key"]
        summary = row["Summary"]

        # Initialiser l'issue dans la structure
        if issue_key not in mindmap_structure:
            mindmap_structure[issue_key] = {"summary": summary, "links": []}

        link_fields = [
            ("Inward issue link (Blocks)", "blocks"),
            ("Outward issue link (Blocks)", "is blocked by"),
            ("Inward issue link (Cloners)", "is cloned by"),
            ("Outward issue link (Cloners)", "clones"),
            ("Inward issue link (Duplicate)", "is duplicated by"),
            ("Outward issue link (Duplicate)", "duplicates"),
            ("Inward issue link (Relates)", "relates to"),
            ("Outward issue link (Relates)", "relates to")
        ]

        # Ajouter les liens
        for field, link_type in link_fields:
            if pd.notna(row[field]):
                linked_issues = row[field].split(",")  # Plusieurs liens possibles
                for linked_issue in linked_issues:
                    linked_issue = linked_issue.strip()
                    add_link(issue_key, linked_issue, link_type)

    # Filtrer les issues sans lien
    filtered_mindmap = {k: v for k, v in mindmap_structure.items() if v["links"]}

    # Générer le graphe NetworkX
    G = nx.DiGraph()

    for issue, details in filtered_mindmap.items():
        node_label = f"{issue}: {details['summary']}"
        G.add_node(node_label)  # Ajouter un nœud avec Issue Key + Summary

        for link in details['links']:
            linked_issue, link_type = link
            if linked_issue in mindmap_structure:
                linked_issue_label = f"{linked_issue}: {mindmap_structure[linked_issue]['summary']}"
                G.add_edge(node_label, linked_issue_label, label=link_type)

    # Positionner les nœuds
    pos = nx.spring_layout(G)

    # Extraire les positions des nœuds
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)  # Separate edges
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Créer la trace des nœuds
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # Affichage de la figure avec Plotly
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title="Mindmap des Issues Jira (Déplaçable)",
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=50),
                        annotations=[dict(
                            showarrow=False,
                            text="Mindmap Interactive",
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False))
                    )

    fig.show()
