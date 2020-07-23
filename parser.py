import networkx as nx
import obonet
import os

def load_data(data_folder):
    path = os.path.join(data_folder, "ext.obo")
    graph = obonet.read_obo(path)
    for item in graph.nodes():
        if item.startswith("UBERON:"):
            rec = graph.nodes[item]
            rec["_id"] = item
            if rec.get("is_a"):
                rec["parents"] = rec.pop("is_a")
            if rec.get("xrefs"):
                rec["xrefs"] = rec.pop('xref')
            rec["children"] = list(graph.predecessors(item))
            rec["ancestors"] = list(nx.descendants(graph, item))
            rec["descendants"] = list(nx.ancestors(graph,item))
            if rec.get("created_by"):
                rec.pop("created_by")
            if rec.get("creation_date"):
                rec.pop("creation_date")
            if rec.get("property_value"):
                rec.pop("property_value")
            yield rec