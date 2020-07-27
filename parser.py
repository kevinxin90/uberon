from collections import defaultdict
import networkx as nx
import obonet
import os

def load_data(data_folder):
    path = os.path.join(data_folder, "uberon.obo")
    graph = obonet.read_obo(path)
    for item in graph.nodes():
        if item.startswith("UBERON:"):
            rec = graph.nodes[item]
            rec["_id"] = item
            if rec.get("is_a"):
                rec["parents"] = [parent for parent in rec.pop("is_a") if parent.startswith("UBERON:")]
            if rec.get("xref"):
                xrefs = defaultdict(set)
                for val in rec.get("xref"):
                    if ":" in val:
                        prefix, id = val.split(':', 1)
                        if prefix in ["http", "https"]:
                            continue
                        if prefix in ['UMLS', 'MESH']:
                            xrefs[prefix.lower()].add(id)
                        else:
                            xrefs[prefix.lower()].add(val)
                for k, v in xrefs.items():
                    xrefs[k] = list(v)
                rec.pop("xref")
                rec["xrefs"] = dict(xrefs)
            rec["children"] = [child for child in graph.predecessors(item) if child.startswith("UBERON:")]
            rec["ancestors"] = [ancestor for ancestor in nx.descendants(graph, item) if ancestor.startswith("UBERON:")]
            rec["descendants"] = [descendant for descendant in nx.ancestors(graph,item) if descendant.startswith("UBERON:")]
            if rec.get("created_by"):
                rec.pop("created_by")
            if rec.get("creation_date"):
                rec.pop("creation_date")
            if rec.get("property_value"):
                rec.pop("property_value")
            if rec.get("relationship"):
                rels = {}
                for rel in rec.get("relationship"):
                    predicate, val = rel.split(' ')
                    prefix = val.split(':')[0]
                    if predicate not in rels:
                        rels[predicate] = defaultdict(set)
                    if prefix.lower() not in rels[predicate]:
                        rels[predicate][prefix.lower()].add(val)
                for m, n in rels.items():
                    for p, q in n.items():
                        n[p] = list(q)
                    rels[m] = dict(n)
                rec.update(rels)
                rec.pop("relationship")
            yield rec
