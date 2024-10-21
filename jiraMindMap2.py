import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
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

    # Générer et visualiser le mindmap
    G = nx.DiGraph()

    print ("Adding nodes and edges")
    # Ajouter les nœuds et les arêtes dans le graph
    for issue, details in filtered_mindmap.items():
        print("Adding item")
        node_label = f"{issue}: {details['summary']}"  # Concaténer Issue Key et Summary
        G.add_node(node_label)  # Ajouter un nœud avec la concaténation

        for link in details['links']:
            print("Adding link")
            linked_issue, link_type = link
            if linked_issue in mindmap_structure:  # Vérifier si le lien existe dans les données
                linked_issue_label = f"{linked_issue}: {mindmap_structure[linked_issue]['summary']}"
                G.add_edge(node_label, linked_issue_label, label=link_type)  # Ajouter l'arête

    # Plot le mindmap
    plt.figure(figsize=(16, 16))

    # Utiliser le spring layout pour le positionnement des nœuds
    pos = nx.spring_layout(G, k=0.5)

    # Dessiner les nœuds avec les étiquettes
    nx.draw(G, pos, with_labels=True, node_size=4000, node_color="lightblue", font_size=8, font_weight="bold",
            arrows=True)

    # Ajouter des étiquettes pour les types de liens (les arêtes)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # Afficher le mindmap
    plt.title("Mindmap des Issues Jira avec Liens")
    plt.show()
