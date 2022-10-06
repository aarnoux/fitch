from bitstring import BitArray
from xml.dom import minidom
from queue import LifoQueue
import logging
import sys

logging.getLogger().setLevel(logging.INFO)


def create_node(xml, parent_node, node_name, label):
    """Create a node in an xml document and initiate attributes.

    Args:
        xml (xml.dom.minidom.Document): xml file
        parent_node (xml.dom.minidom.Element): parent node of the newly created node
        node_name (str): node name accessed with node.nodeName
        label (BitArray): node label

    Returns:
        xml.dom.minidom.Element: newly created node
    """
    node = xml.createElement(node_name)
    node.setAttribute("label", label)
    parent_node.appendChild(node)
    return node


def get_nodes(parent_node, node_queue):
    """Get a LIFO queue of all internal nodes.
    This function browses the tree from root to leafs in a recursive manner.
    Nodes found between the root-node and the leaf-nodes are stored in a LIFO (last in, first out) queue for ulterior use.

    Args:
        parent_node (xml.dom.minidom.Element): node with child nodes
        node_queue (queue): LIFO queue containing internal nodes

    Returns:
        queue: LIFO queue containing all internal nodes
    """
    for child in parent_node.childNodes:
        if child.childNodes:
            node_queue.put(child)
            get_nodes(child, node_queue)
    return node_queue


def test_consensus(node, pos, lenLabel):
    """Compare label of child nodes and add to parent node if equals.
    The comparison is made 2 bits by 2 bits on the labels with the bitwise XOR operator.
    If the bits are the same then the corresponding bits are added to the parent node label.
    If not, the position at which the comparison failed is returned.

    Args:
        node (xml.dom.minidom.Element): node to be labeled
        pos (int): position at which to begin the comparison
        lenLabel (int): max length of the labels

    Returns:
        int: length of the node label
    """
    nodeLabel = node.getAttribute("label")

    # (lenLabel * 2) because we are using bits and each letter is coded with 2 bits
    for i in range(pos, lenLabel * 2, 2):

        # compare child nodes labels to check if there is a consensus at the given position
        compare = (
            node.childNodes[0].getAttribute("label")[i : i + 2]
            ^ node.childNodes[1].getAttribute("label")[i : i + 2]
        )
        if bin(1) not in compare:  # if there is only '0' after XOR the bits are the same

            # we add the bits of the first child (doesn't matter because they are the same as the ones from the second child) to the node label
            nodeLabel.insert(node.childNodes[0].getAttribute("label")[i : i + 2], i)
        else:
            return len(nodeLabel)
    return len(nodeLabel)


def no_consensus(minNode, maxNode, pos):
    """Analyse bits when there is no consensus between the child nodes.
    To decide which bits to add to the node label, we take into account the label of the brother node.
    The query node being minNode and the brother node being maxNode.

    Args:
        minNode (xml.dom.minidom.Element): query node with the shortest label
        maxNode (xml.dom.minidom.Element): brother node with the longest label
        pos (int): position at which to start the analyse

    Returns:
        int: shortest length between brother nodes labels
    """
    # handling the special case of the root node with no brother node:
    # as such, since there is no consensus or else it would have been 
    # treated in the test_consensus() function, we arbitrarily take the bits 
    # corresponding to the first child
    if maxNode.nodeName == "root":
        maxNode.getAttribute("label").insert(
            maxNode.childNodes[0].getAttribute("label")[pos : pos + 2],
            pos
        )
        return len(maxNode.getAttribute("label"))

    for i in range(pos, pos + 2, 2):
        # initialize a bitstring to keep track of bits from the different labels
        concat = []
        # we put the childs labels first so that in case of no consensus between the tree nodes the label of the first child will be taken by default
        concat.append(minNode.childNodes[0].getAttribute("label")[i : i + 2])  # add the bit of the first child node label
        concat.append(minNode.childNodes[1].getAttribute("label")[i : i + 2])  # add the bit of the second child node label

        if len(maxNode.getAttribute("label")) == len(minNode.getAttribute("label")):
            concat.append(maxNode.childNodes[0].getAttribute("label")[i : i + 2])  # add the bit of the first child node label
            concat.append(maxNode.childNodes[1].getAttribute("label")[i : i + 2])  # add the bit of the second child node label
        else:
            concat.append(maxNode.getAttribute("label")[i : i + 2])  # add the bit of the brother node label

        maxIter = max(concat.count(format(0, '#04b')), concat.count(format(1, '#04b')), concat.count(format(2, '#04b')), concat.count(format(3, '#04b')))
        label = [value for value in concat if concat.count(value) == maxIter]
        minNode.getAttribute("label").insert(label[0], i)

    return min(len(minNode.getAttribute("label")), len(maxNode.getAttribute("label")))


def labeling(node_queue, lenLabel):
    """Find the label of internal nodes.
    Handle the labeling of nodes in pair (brother nodes).

    Args:
        node_queue (queue): LIFO queue containing all internal nodes
        lenLabel (int): max length of the labels
    """
    pos = 0
    # get the deepest not-leaf node from the tree
    intern_node = node_queue.get()
    if node_queue.empty():  # if the node is the root, bypass the brother node
        bro_node = intern_node
    else:
        # get the second deepest not-leaf node (= brother of previous node, as we work with binary trees)
        bro_node = node_queue.get()

    # iterate until the labels have reach their maximum length
    while pos < lenLabel * 2:
        # for the first node, search for a consensus within the child nodes labels
        intern_len = test_consensus(intern_node, pos, lenLabel)
        # if we are handling the root node, keep the brother node label length at 0
        if node_queue.empty():
            minNode = bro_node
            maxNode = intern_node
            pos = intern_len
        # else, put the node in the pair that has the shortest label as minNode, and the other one as maxNode.
        else:
            bro_len = test_consensus(bro_node, pos, lenLabel)
            if intern_len < bro_len:
                minNode = intern_node
                maxNode = bro_node
                pos = intern_len
            else:
                minNode = bro_node
                maxNode = intern_node
                pos = bro_len

        pos = no_consensus(minNode, maxNode, pos)

    # if we are at the root node, stop the iteration
    if node_queue.empty():
        return None

    labeling(node_queue, lenLabel)


def decode(parent_node, lenLabel, alphabet):
    """Get the letters from the label bitstring.

    Args:
        parent_node (xml.dom.minidom.Element): node with child nodes
        lenLabel (int): max length of the labels
        alphabet (dict): dictionnary with letter as key and int as value
    """
    for child in parent_node.childNodes:
        chaine = ""
        # for each pair of bit translated as an int, get the corresponding char from the dictionnary
        for i in range(0, lenLabel * 2, 2):
            chaine += "".join(
                [
                    num
                    for num, val in alphabet.items()
                    if val == child.getAttribute("label")[i : i + 2].uint
                ]
            )
        child.attributes["label"].value = chaine
        decode(child, lenLabel, alphabet)


def read_newick(xml, tree, node, lenLabel, alphabet):
    """Read a newick tree without internal node label, as xml.

    Args:
        xml (xml.dom.minidom.Document): xml document
        tree (str): phylogenic tree in newick format
        node (xml.dom.minidom.Element): root node
        lenLabel (int): max length of the labels
        alphabet (dict): dictionnary with letter as key and int as value
    """
    nodeId = 0
    treeLeaf = 0
    # read the string from right to left
    for i in range(len(tree) - 1, 0, -1):
        label = BitArray()
        # a closed parenthesis means a new node
        if tree[i] == ")":
            nodeId += 1
            # a serie of letter means the node is a leaf with a label
            if tree[i - 1] in alphabet.keys():
                treeLeaf += 1
                j = 1
                pos = 0
                while j <= lenLabel:  # read the label
                    # add the label as a bitstring based on translation of letter to integrer with the dictionnary
                    label.insert(format(alphabet[tree[i - j]], "#04b"), pos)
                    j += 1
                    pos -= 2
            node = create_node(xml, node, str(nodeId), label)
        # a coma means the creation of a brother node, we need to go up to the parent node in order to add it to the right place in the file
        elif tree[i] == ",":
            nodeId += 1
            node = node.parentNode
            # an open parenthesis means that the brother node is of event higher order, we need to go up again to the parent node
            if tree[i + 1] == "(":
                node = node.parentNode
            if tree[i - 1] in alphabet.keys():
                treeLeaf += 1
                j = 1
                pos = 0
                while j <= lenLabel:
                    label.insert(format(alphabet[tree[i - j]], "#04b"), pos)
                    j += 1
                    pos -= 2
            node = create_node(xml, node, str(nodeId), label)
    return treeLeaf


def export(xml):
    """Export the tree in a tree.xml file.

    Args:
        xml (xml.dom.minidom.Document): xml document
    """
    xml_str = xml.toprettyxml(indent="\t")
    save_path_file = "tree.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)


def visualization(depth, parent_node, treeLeaf, numLeaf):
    """_summary_

    Args:
        depth (int): depth of the current position in the tree
        parent_node (_type_): _description_
        treeLeaf (_type_): _description_
        numLeaf (int): number of leaf visited 

    Returns:
        _type_: _description_
    """
    PIPE_PREFIX = "│   "
    SPACE_PREFIX = "    "
    if len(parent_node.childNodes) == 1:
        print(f"{parent_node.childNodes[0].getAttribute('label')}")
        parent_node = parent_node.childNodes[0]
    for child in parent_node.childNodes:
        if numLeaf == treeLeaf - 2:
            PIPE_PREFIX = SPACE_PREFIX
        if child == parent_node.childNodes[0]:
            depth += 1
            marker = "├──"
        else:
            marker = "└──"
            if child.childNodes:
                depth -= 1
        if child.childNodes:
            print(f"{SPACE_PREFIX*depth}{marker}{child.getAttribute('label')}")
        else:
            print(f"{SPACE_PREFIX*int(depth-1)}{PIPE_PREFIX}{marker}{child.getAttribute('label')}")
            numLeaf += 1
        depth, numLeaf = visualization(depth, child, treeLeaf, numLeaf)
    return depth, numLeaf


def help():
    print("")


def main():
    # Taille des étiquettes données en argument par l'utilisateur.
    lenLabel = int(sys.argv[1])
    # Arbre Newick donné par l'utilisateur
    tree = sys.argv[2]
    # Associer des chiffres aux lettres pour utiliser moins d'espace en ne stockant chaque caractères que sur 2 bits au lieux de 8.
    alphabet = {"A": 0, "C": 1, "G": 2, "T": 3}
    xml = minidom.Document()
    label = BitArray()

    # Création de la racine
    node = create_node(xml, xml, "root", label)
    logging.info("=> reading newick file")

    # Reading newick
    treeLeaf = read_newick(xml, tree, node, lenLabel, alphabet)
    logging.info("=> tree created")
    node_queue = LifoQueue()
    node_queue = get_nodes(xml, node_queue)
    
    logging.info("=> labeling internal nodes")
    labeling(node_queue, lenLabel)
    decode(xml, lenLabel, alphabet)
    logging.info("=> exporting tree to xml")
    export(xml)

    print("\n**** labeled tree ****")
    depth = -1
    numLeaf = 0
    visualization(depth, xml, treeLeaf, numLeaf)


if __name__ == "__main__":
    main()
