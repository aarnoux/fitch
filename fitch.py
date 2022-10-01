from bitstring import BitArray
from xml.dom import minidom
from queue import LifoQueue

def create_node(upper_node, node_name, etiq, cost):
    node = xml.createElement(node_name)
    node.setAttribute('etiq', etiq)
    node.setAttribute('cost', cost)
    upper_node.appendChild(node)
    return node

def get_nodes(upper_node, node_queue):
    for child in upper_node.childNodes:
        if child.childNodes:
            node_queue.put(child)
            get_nodes(child, node_queue)
    return node_queue

def consensus(node_queue):
    intern_node = node_queue.get()
    etiq_intern = intern_node.getAttribute('etiq')
    pos = []
    n = 0
    comp = intern_node.childNodes[0].getAttribute('etiq') ^ intern_node.childNodes[1].getAttribute('etiq')
    for i in range(0, len(comp), 2):
        if bin(1) not in comp[i:i+2]:
            etiq_intern.insert(intern_node.childNodes[0].getAttribute('etiq')[i:i+2], i+n)
        else:
            pos.append(i+n)
            etiq_intern.insert(intern_node.childNodes[0].getAttribute('etiq')[i:i+2], i+n)
            n += 2
            etiq_intern.insert(intern_node.childNodes[1].getAttribute('etiq')[i:i+2], i+n)
            print("consensus = ", etiq_intern)
            print(pos)
        #upper_node.setAttribute('etiq', etiq_intern)
        print(intern_node.nodeName)
        print(intern_node.getAttribute("etiq"))
    consensus(node_queue)

        # if etiq_intern == BitStream(lenEtiq * 2):
        #     upper_node.setAttribute('etiq', upper_node.childNodes[0].getAttribute('etiq'))
        # print(etiq_intern, child)

        #    print(upper_node)
        #    print(upper_node.getAttribute('etiq'))

tree = "(((ACT,ACT),(AGA,AGT)),(TGA,TCG));"

# Taille des étiquettes données en argument par l'utilisateur.
#lenEtiq = sys.argv[2]
lenEtiq = 3

# Associer des chiffres aux lettres pour utiliser moins d'espace en ne stockant chaque caractères que sur 2 bits au lieux de 8.
alphabet = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

xml = minidom.Document()

# Création de la racine
node = create_node(xml, 'root', '', 'null')

for i in range(len(tree)-1, 0, -1):
    etiq = BitArray()
    cost = ''
    if tree[i] == ')':
        if tree[i-1] in alphabet.keys():
            j = 1
            pos = 0
            while j <= lenEtiq:
                etiq.insert(format(alphabet[tree[i-j]], '#04b'), pos)
                j += 1
                pos -= 2
        node = create_node(node, str(i), etiq, cost)

    if tree[i] == ',':
        node = node.parentNode
        if tree[i+1] == '(':
            node = node.parentNode
        if tree[i-1] in alphabet.keys():
            j = 1
            pos = 0
            while j <= lenEtiq:
                etiq.insert(format(alphabet[tree[i-j]], '#04b'), pos)
                j += 1
                pos -= 2
        node = create_node(node, str(i), etiq, cost)

node_queue = LifoQueue()
node_queue = get_nodes(xml.childNodes[0], node_queue)
consensus(node_queue)

# xml_str = xml.toprettyxml(indent ="\t") 
  
# save_path_file = "tree.xml"
  
# with open(save_path_file, "w") as f:
#     f.write(xml_str)
