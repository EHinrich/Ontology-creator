"""Visualization functions for ontology trees and graphs."""

from typing import Any, Dict, List, Tuple
from anytree import Node, RenderTree
import networkx as nx
from ontology_app import models

def draw_tree(tmp_tree: Node, ax) -> None:
    global tree2graph
    tree2graph = nx.DiGraph()
    
    for pre, fill, node in RenderTree(tmp_tree):
        if (node.id!="Null"):
            if ("null1" in node.parent.id and node.name!="•"):
                tree2graph.add_node(node.name)

    for pre, fill, node in RenderTree(tmp_tree):
        if (node.id!="Null"):
            if (node.name + " in classes" + "null2" == node.id):
                rel = node.name
                for node1 in tree2graph.nodes():
                    for node2 in tree2graph.nodes():
                        for pre, fill, node_node in RenderTree(tmp_tree):
                            if (node_node.id.find(node1+rel+node2+"classes")==0):
                                tree2graph.add_edge(node1, node2, title=rel)
        
    pos = nx.nx_pydot.pydot_layout(tree2graph, prog='neato')

    nx.draw(tree2graph, ax=ax, pos=pos, with_labels=True, bbox=dict(facecolor='skyblue', edgecolor='black', boxstyle='circle, pad=0.3'))
    nx.draw_networkx_edge_labels(tree2graph, ax=ax, pos=pos, edge_labels=nx.get_edge_attributes(tree2graph,'title'))

def draw_class(tmp_tree: Node, current_class_1: str, current_class_2: str, ax) -> None:

    tree2graph = nx.DiGraph()
    labels_of_another_class = {}
    node_class = None
    for pre, fill, node in RenderTree(tmp_tree):
        if (node.id == current_class_1 + " in elements" + "null3"):
            node_class = node.parent
    if (node_class is not None):
        for pre, fill, node in RenderTree(tmp_tree):
            if (node.name!="•" and node.name!=current_class_1 and node.name+current_class_1 == node.id):
                tree2graph.add_node(node.name)
                labels_of_another_class.update({node.name:node.name})

    node_class = None
    for pre, fill, node in RenderTree(tmp_tree):
        if (node.id == current_class_2 + " in elements" + "null3"):
            node_class = node.parent
    if (node_class is not None):
        for pre, fill, node in RenderTree(tmp_tree):
            if (node.name!="•" and node.name!=current_class_2 and node.name+current_class_2 == node.id):
                tree2graph.add_node(node.name)

    for pre, fill, node in RenderTree(tmp_tree):
        if node.id == node.name + " in elements" + "null4":
            rel = node.name
            for node1 in tree2graph.nodes():
                for node2 in tree2graph.nodes():
                    for pre, fill, node_node in RenderTree(tmp_tree):
                        if node_node.id.find(node1 + rel + node2 + "elements") == 0:
                            tree2graph.add_edge(node1, node2, title=rel)

    pos = nx.nx_pydot.pydot_layout(tree2graph, prog='neato')
    nx.draw(tree2graph, ax=ax, pos=pos, with_labels=True,
            bbox=dict(facecolor='pink', edgecolor='black', boxstyle='round, pad=0.3'))
    nx.draw_networkx_labels(tree2graph, ax=ax, pos=pos, labels = labels_of_another_class, bbox=dict(facecolor='yellow', edgecolor='black', boxstyle='round, pad=0.3'))
    nx.draw_networkx_edge_labels(tree2graph, ax=ax, pos=pos, edge_labels=nx.get_edge_attributes(tree2graph, 'title'))

def draw_series_depth_2(tmp_series: Node, rel: str, ax) -> None:
    tree2graph = nx.DiGraph()
    parsed_series = []
    id_to_str = {}
    for pre, fill, node in RenderTree(tmp_series):
        if (node.id!="root_relation_series " + rel):
            if ((node.parent.id,node.id) in parsed_series):
                if (node.name=="•••"):
                    id_to_str.update({node.id:""})
                else:
                    id_to_str.update({node.id:node.name})
            else:
                parsed_series.append((node.parent.id,node.id))
                if (node.name=="•••"):
                    id_to_str.update({node.id:""})
                else:
                    id_to_str.update({node.id:node.name})
        else:
            id_to_str.update({node.id:node.name})
    tree2graph.add_edges_from(parsed_series, color='black')
    for node in tree2graph.nodes():
        tree2graph.nodes[node]['label'] = id_to_str[node]
    edges = tree2graph.edges()
    colors = [tree2graph[u][v]['color'] for u,v in edges]
    color_map = []
    node_sizes = []
    for node in tree2graph:
        if id_to_str.get(node)=="":
            color_map.append('black')
            node_sizes.append(0)
        else: 
            color_map.append('skyblue')
            node_sizes.append(100)
    pos = nx.nx_pydot.pydot_layout(tree2graph, prog='dot')
    nx.draw_networkx(tree2graph, ax=ax, node_color=color_map, node_size = node_sizes, pos=pos, edge_color=colors, arrows= True, with_labels=True, labels=id_to_str, bbox=dict(facecolor='yellow', edgecolor='black', boxstyle='round, pad=0.3'))

def draw_series_depth_1(tmp_series: Node, rel: str, element: str, ax) -> None:
    tree2graph = nx.DiGraph()
    parsed_series = []
    id_to_str = {}
    for pre, fill, node in RenderTree(tmp_series):
        if (node.id!="root_relation_series " + element + " " + rel):
            if ((node.parent.id,node.id) in parsed_series):
                if (node.name=="•••"):
                    id_to_str.update({node.id:""})
                else:
                    id_to_str.update({node.id:node.name})
            else:
                parsed_series.append((node.parent.id,node.id))
                if (node.name=="•••"):
                    id_to_str.update({node.id:""})
                else:
                    id_to_str.update({node.id:node.name})
        else:
            id_to_str.update({node.id:node.name})
    tree2graph.add_edges_from(parsed_series, color='black')
    for node in tree2graph.nodes():
        tree2graph.nodes[node]['label'] = id_to_str[node]
    edges = tree2graph.edges()
    colors = [tree2graph[u][v]['color'] for u,v in edges]
    color_map = []
    node_sizes = []
    for node in tree2graph:
        if id_to_str.get(node)=="":
            color_map.append('black')
            node_sizes.append(0)
        else: 
            color_map.append('skyblue')
            node_sizes.append(100)
    pos = nx.nx_pydot.pydot_layout(tree2graph, prog='dot')
    nx.draw_networkx(tree2graph, ax=ax, node_color=color_map, node_size = node_sizes, pos=pos, edge_color=colors, arrows= True, with_labels=True, labels=id_to_str, bbox=dict(facecolor='yellow', edgecolor='black', boxstyle='round, pad=0.3'))


def draw_abstract_class(tmp_abstract: Node, current_node: str, ax) -> None:
    tree2graph = nx.DiGraph()
    parsed_series = []
    id_to_str = {}
    for pre, fill, node in RenderTree(tmp_abstract):
        if (node.id!="root_relation"):
            if ((node.parent.id,node.id) in parsed_series):
                id_to_str.update({node.id:node.name})
            else:
                parsed_series.append((node.parent.id,node.id))
                id_to_str.update({node.id:node.name})
        else:
            id_to_str.update({node.id:node.name})
    tree2graph.add_edges_from(parsed_series, color='black')
    edges = tree2graph.edges()
    colors = [tree2graph[u][v]['color'] for u,v in edges]
    node_sizes = []
    for node in tree2graph:
        node_sizes.append(0)
    pos = nx.nx_pydot.pydot_layout(tree2graph, prog='dot')
    nx.draw_networkx(tree2graph, ax=ax, node_size = node_sizes, pos=pos, edge_color=colors, arrows= True, with_labels=True, labels=id_to_str, bbox=dict(facecolor='yellow', edgecolor='black', boxstyle='round, pad=0.3'))
    nx.draw_networkx_labels(tree2graph, ax=ax, pos=pos, labels = {current_node: "•••"}, bbox=dict(facecolor='skyblue', edgecolor='black', boxstyle='round, pad=0.3'))


__all__ = ["draw_tree", "draw_class", "draw_series", "draw_abstract_class"]
