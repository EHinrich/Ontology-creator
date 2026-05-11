"""Domain logic for ontology operations.

This module centralises the data model and related functions for tree-based
ontology construction. The GUI imports functions from here rather than
manipulating globals directly.
"""
from typing import Optional
from anytree import Node, RenderTree, find_by_attr

# shared state

# root node for the ontology; initially empty
tree = Node(id="", name="")
series = None
abstract = None
last_id = ""


def create_ontology_tree(fileName: str) -> Node:
    """Create a new ontology tree structure with empty branches for classes, elements, and relationships."""
    tree = Node(id="Null", name="<")
    Node(id="ontology_" + fileName, name=fileName, parent=tree)  # root node
    node1 = Node(id=" 1", name="•", parent=tree)
    node2 = Node(id=" 2", name="•", parent=node1)
    node3 = Node(id=" 3", name="•", parent=node1)
    node_c = Node(id="classes", name="Classes", parent=node2)
    null1 = Node(id="null1", name="•", parent=node2)

    node4 = Node(id=" 4", name="•", parent=node3)
    node5 = Node(id=" 5", name="•", parent=node3)
    node_rc = Node(id="rel_classes", name="Rel_classes", parent=node4)
    null2 = Node(id="null2", name="•", parent=node4)

    node6 = Node(id=" 6", name="•", parent=node5)
    node7 = Node(id=" 7", name="•", parent=node5)
    node_e = Node(id="elements", name="Elements", parent=node6)
    null3 = Node(id="null3", name="•", parent=node6)

    node8 = Node(id=" 8", name="•", parent=node7)
    node9 = Node(id=" 9", name="•", parent=node7)
    node_re = Node(id="rel_elem", name="Rel_elem", parent=node8)
    null4 = Node(id="null4", name="•", parent=node8)
    return tree



def add_elem_list1(tmp_tree: Node, elem_name: str) -> None:
    """Helper function to add element to list for displaying elements of a class."""
    parent_id = ""
    class_parent = Node(id="", name="")
    for pre, fill, node in RenderTree(tmp_tree):
        if "1" in node.id:
            parent_id = node.id
            class_parent = node
    Node(id=elem_name, name=elem_name, parent=class_parent)
    Node(id=parent_id + "1", name="•", parent=class_parent)


def add_elem_list2(tmp_tree: Node, elem_name: str) -> None:
    """Helper function to add element to list for displaying elements of a class."""
    parent_id = ""
    class_parent = Node(id="", name="")
    for pre, fill, node in RenderTree(tmp_tree):
        if "2" in node.id:
            parent_id = node.id
            class_parent = node
    Node(id=elem_name, name=elem_name, parent=class_parent)
    Node(id=parent_id + "2", name="•", parent=class_parent)


def add_class(tree: Node, class_name: str, type: str) -> None:
    """Add a new class to the ontology tree."""
    class_parent = Node(id="", name="")
    latest_index = 0
    for pre, fill, node in RenderTree(tree):
        if node.id == "null1":
            class_parent = node
        elif node.id.startswith("null1_"):
            suffix = node.id[len("null1_") :]
            if suffix.isdigit():
                index = int(suffix)
                if index >= latest_index:
                    latest_index = index
                    class_parent = node
    if class_parent.id:
        if find_by_attr(tree, class_name) is None:
            Node(id=class_name + type, name=class_name, parent=class_parent)
            next_index = latest_index + 1 if class_parent.id != "null1" else 1
            Node(id=f"null1_{next_index}", name="•", parent=class_parent)
    else:
        for pre, fill, node in RenderTree(tree):
            if " 1" == node.id:
                node1 = node
                break
        node2 = Node(id=" 2", name="•", parent=node1)
        node3 = Node(id=" 3", name="•", parent=node1)
        node_c = Node(id="classes", name="Classes", parent=node2)
        null1 = Node(id="null1", name="•", parent=node2)
        add_class(tree, class_name, type)


def del_class(tree: Node, class_name: str) -> None:
    """Delete a class from the ontology tree."""
    k = 0
    current_class = Node(id="", name="")
    current_elem = ""
    for pre, fill, node_tmp in RenderTree(tree):
        if node_tmp.parent is not None:
            if class_name + "null33" in node_tmp.parent.id:
                current_elem = node_tmp.name
                for pre, fill, node in RenderTree(tree):
                    if current_elem + class_name == node.id:
                        node.parent = None

    for pre, fill, node in RenderTree(tree):
        if class_name + "object" == node.id or class_name + "abstract" == node.id:
            node.parent = None
            node = None


def add_elem(tree: Node, class_name: str, elem_name: str) -> None:
    """Add an element to a class in the ontology tree."""
    parent_id = ""
    class_parent = Node(id="", name="")
    for pre, fill, node in RenderTree(tree):
        if (class_name + " in elements" in node.id and "null3" in node.parent.id):
            for pre, fill, node in RenderTree(tree):
                if class_name + "null33" in node.id:
                    parent_id = node.id
                    class_parent = node
            if find_by_attr(tree, elem_name + class_name) is None:
                Node(name=elem_name, id=elem_name + class_name, parent=class_parent)
                Node(name="•", id=parent_id + "3", parent=class_parent)
    k = 0
    for pre, fill, node in RenderTree(tree):
        if (class_name + " in elements" in node.id and "null3" in node.parent.id):
            k = k + 1
    if k == 0:
        for pre, fill, node in RenderTree(tree):
            if node.id.find("null3") == 0:
                parent_id = node.id
                class_parent = node
        Node(name="•", id=parent_id + "3", parent=class_parent)
        node1 = Node(name="•", id=class_name + "null3", parent=class_parent)
        Node(name=class_name, id=class_name + " in elements", parent=node1)
        node2 = Node(name="•", id=class_name + "null3" + "3", parent=node1)
        Node(name=elem_name, id=elem_name + class_name, parent=node2)
        Node(name="•", id=class_name + "null3" + "33", parent=node2)


def del_elem(tree: Node, elem_name: str) -> None:
    """Delete an element from the ontology tree."""
    curr_class = ""
    for pre, fill, node in RenderTree(tree):
        if node.parent is not None:
            if "null1" in node.parent.id:
                curr_class = node.name
                for pre, fill, node_tmp in RenderTree(tree):
                    if (elem_name + curr_class == node_tmp.id and "null3" in node_tmp.parent.id):
                        node_tmp.parent = None


def add_classes_rel(tree: Node, class_name1: str, rel: str, class_name2: str) -> None:
    """Add a relationship between two classes in the ontology."""
    parent_id1 = ""
    parent_class = Node(id="", name="")
    for pre, fill, node in RenderTree(tree):
        if (rel + " in classes_rel" in node.id and "null2" in node.parent.id):
            for pre, fill, node in RenderTree(tree):
                if rel + " null22" in node.id:
                    parent_id1 = node.id
                    parent_class = node
            if find_by_attr(tree, class_name1 + rel + class_name2 + "classes") is None:
                node1 = Node(name="•", id=class_name1 + rel + class_name2 + "classes", parent=parent_class)
                Node(name="•", id=parent_id1 + "2", parent=parent_class)
                Node(name=class_name1, id=class_name1 + "in" + class_name1 + rel + class_name2 + "classes" + "1", parent=node1)
                Node(name=class_name2, id=class_name2 + "in" + class_name1 + rel + class_name2 + "classes" + "2", parent=node1)
    k = 0
    for pre, fill, node in RenderTree(tree):
        if (rel + " in classes_rel" in node.id and "null2" in node.parent.id):
            k = k + 1
    if k == 0:
        for pre, fill, node in RenderTree(tree):
            if node.id.find("null2") == 0:
                parent_id = node.id
                parent_class = node
        Node(name="•", id=parent_id + "2", parent=parent_class)
        node1 = Node(name="•", id=rel + " in classes_rel", parent=parent_class)
        Node(name=rel, id=rel + " in classes", parent=node1)
        node2 = Node(name="•", id=rel + " null2", parent=node1)
        Node(name="•", id=rel + " null2" + "2", parent=node2)
        node3 = Node(name="•", id=class_name1 + rel + class_name2 + "classes", parent=node2)
        Node(name=class_name1, id=class_name1 + "in" + class_name1 + rel + class_name2 + "classes" + "1", parent=node3)
        Node(name=class_name2, id=class_name2 + "in" + class_name1 + rel + class_name2 + "classes" + "2", parent=node3)


def add_elements_rel(tree: Node, el_name1: str, rel: str, el_name2: str) -> None:
    """Add a relationship between two elements in the ontology."""
    parent_id = ""
    class_parent = Node(id="", name="")
    for pre, fill, node in RenderTree(tree):
        if (rel + " in elements_rel" in node.id and "null4" in node.parent.id):
            for pre, fill, node in RenderTree(tree):
                if rel + " null44" in node.id:
                    parent_id = node.id
                    class_parent = node
            if find_by_attr(tree, el_name1 + rel + el_name2 + "elements") is None:
                node1 = Node(name="•", id=el_name1 + rel + el_name2 + "elements", parent=class_parent)
                Node(name="•", id=parent_id + "4", parent=class_parent)
                Node(name=el_name1, id=el_name1 + "in" + el_name1 + rel + el_name2 + "elements" + "1", parent=node1)
                Node(name=el_name2, id=el_name2 + "in" + el_name1 + rel + el_name2 + "elements" + "2", parent=node1)
    k = 0
    for pre, fill, node in RenderTree(tree):
        if (rel + " in elements_rel" in node.id and "null4" in node.parent.id):
            k = k + 1
    if k == 0:
        for pre, fill, node in RenderTree(tree):
            if node.id.find("null4") == 0:
                parent_id = node.id
                parent_class = node
        Node(name="•", id=parent_id + "4", parent=parent_class)
        node1 = Node(name="•", id=rel + " in elements_rel", parent=parent_class)
        Node(name=rel, id=rel + " in elements", parent=node1)
        node2 = Node(name="•", id=rel + " null4", parent=node1)
        Node(name="•", id=rel + " null4" + "4", parent=node2)
        node3 = Node(name="•", id=el_name1 + rel + el_name2 + "elements", parent=node2)
        Node(name=el_name1, id=el_name1 + "in" + el_name1 + rel + el_name2 + "elements" + "1", parent=node3)
        Node(name=el_name2, id=el_name2 + "in" + el_name1 + rel + el_name2 + "elements" + "2", parent=node3)


def create_series(tree: Node, depth: str, element: str, rel: str, rel_2: str) -> Node:
    """Create a new series structure from ontology data."""
    if depth == "1":
        series = Node(id="root_relation_series", name=rel)
        Node(id="root_" + element, name=element, parent=series)  # root node
        node1 = Node(id=element+"null5", name="•••", parent=series)
        parent_id = ""
        class_parent = Node(id="", name="")
        for pre, fill, node1 in RenderTree(tree):
            for pre, fill, node2 in RenderTree(tree):
                if (element + rel + node2.name + "elements" == node1.id):
                    for pre, fill, node3 in RenderTree(series):
                        if element + "null5" in node3.id:
                            parent_id = node3.id
                            class_parent = node3
                    if find_by_attr(series, node2.name) is None:
                        Node(name="•••", id=parent_id + "5", parent=class_parent)
                        Node(name=node2.name, id=node2.name, parent=class_parent)
    return series

def create_abstract_class(abstract: Node, mode: str, element: str, first_elem: str, second_elem: str, rel: str, one_elem: str, current_node_id: str) -> Node:
    if mode == "load":
        abstract = None
        abstract = Node(id="root_relation", name="root of structure")
        Node(id="root_" + element, name=element, parent=abstract)
        Node(id=element+"null6", name="•••", parent=abstract)
        #"""Create a new abstract class structure from ontology data."""
        #if find_by_attr(abstract, "root of structure") is None:
            #abstract = Node(id="root_relation", name="root of structure")
            #Node(id="root_" + element, name=element, parent=abstract)
            #Node(id=element+"null6", name="•••", parent=abstract)

    if mode == "add RDF triple":
        parent_id = element + "null6"
        next_node = None
        current_node_data = None
        for pre, fill, node in RenderTree(abstract):
            if node.id == current_node_id:
                current_node = node
        for pre, fill, node in RenderTree(abstract):
            if node.id != "root_relation":
                if node.parent.id == current_node_id and "null6" in node.id:
                    next_node = node
                if node.parent.id == current_node_id and "null6" not in node.id:
                    current_node_data = node
        next_index = 1
        for pre, fill, node in RenderTree(abstract):
            if node.id.startswith(parent_id + "_"):
                suffix = node.id[len(parent_id) + 1 :]
                if suffix.isdigit():
                    next_index = max(next_index, int(suffix) + 1)
        if current_node_data is not None:
            current_node_data.parent = None
        new_node = Node(name="•••", id=f"{parent_id}_{next_index}", parent=current_node)
        if next_node is not None:
            next_node.parent = new_node
            new_rel_node = Node(name=rel, id=first_elem + rel + second_elem, parent=new_node)
            current_node_data.parent = current_node
        else:
            new_rel_node = Node(name=rel, id=first_elem + rel + second_elem, parent=current_node)
        Node(name=first_elem, id=first_elem + " in " + first_elem + rel + second_elem + " elements" + "1", parent=new_rel_node)
        Node(name=second_elem, id=second_elem + " in " + first_elem + rel + second_elem + " elements" + "2", parent=new_rel_node)

    if mode == "add element":
        parent_id = element + "null6"
        next_node = None
        current_node_data = None
        for pre, fill, node in RenderTree(abstract):
            if node.id == current_node_id:
                current_node = node
        for pre, fill, node in RenderTree(abstract):
            if node.id != "root_relation":
                if node.parent.id == current_node_id and "null6" in node.id:
                    next_node = node
                if node.parent.id == current_node_id and "null6" not in node.id:
                    current_node_data = node
        next_index = 1
        for pre, fill, node in RenderTree(abstract):
            if node.id.startswith(parent_id + "_"):
                suffix = node.id[len(parent_id) + 1 :]
                if suffix.isdigit():
                    next_index = max(next_index, int(suffix) + 1)
                    #latest_node = node
        if current_node_data is not None:
            current_node_data.parent = None
        new_node = Node(name="•••", id=f"{parent_id}_{next_index}", parent=current_node)
        if next_node is not None:
            next_node.parent = new_node
            Node(name=one_elem, id=one_elem + " elements", parent=new_node)
            current_node_data.parent = current_node
        else:
            Node(name=one_elem, id=one_elem + " elements", parent=current_node)

    if mode == "edit RDF triple":
        node_triple = None
        for pre, fill, node in RenderTree(abstract):
            if node.id != "root_relation":
                if node.parent.id == current_node_id:
                    node_triple = node
        node_triple.children = ()
        node_triple.id = first_elem + rel + second_elem
        node_triple.name = rel
        Node(name=first_elem, id=first_elem + " in " + first_elem + rel + second_elem + " elements" + "1", parent=node_triple)
        Node(name=second_elem, id=second_elem + " in " + first_elem + rel + second_elem + " elements" + "2", parent=node_triple)

    if mode == "edit one element":
        node_one = None
        for pre, fill, node in RenderTree(abstract):
            if node.id != "root_relation":
                if node.parent.id == current_node_id:
                    node_one = node
        node_one.id = one_elem + " elements"
        node_one.name = one_elem
    
    if mode == "delete":
        node_to_delete = None
        prev_node = None
        next_node = None
        for pre, fill, node in RenderTree(abstract):
            if node.id == current_node_id:
                node_to_delete = node
                prev_node = node.parent
                next_node = node.children[0]
        node_to_delete.parent = None
        prev_node.children = (next_node,) + prev_node.children

    return abstract

__all__ = [
    "tree",
    "series",
    "abstract",
    "last_id",
    "create_ontology_tree",
    "add_elem_list1",
    "add_elem_list2",
    "add_class",
    "del_class",
    "add_elem",
    "del_elem",
    "add_classes_rel",
    "add_elements_rel",
    "create_series",
    "create_abstract_class"
]
