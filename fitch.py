from bitstring import BitArray
from xml.dom import minidom
from queue import LifoQueue

# Taille des étiquettes données en argument par l'utilisateur.
#lenEtiq = sys.argv[2]
lenEtiq = 3

tree = "(((ACT,ACT),(AGA,AGT)),(TGA,TCG));"

# Associer des chiffres aux lettres pour utiliser moins d'espace en ne stockant chaque caractères que sur 2 bits au lieux de 8.
alphabet = {'A': 0, 'C': 1, 'G': 2, 'T': 3}

xml = minidom.Document()

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

def cons(node, len_min):
    etiq_intern = node.getAttribute('etiq')
    for i in range(len_min, lenEtiq * 2, 2):
        comp = node.childNodes[0].getAttribute('etiq')[i:i+2] ^ node.childNodes[1].getAttribute('etiq')[i:i+2]
        if bin(1) not in comp:
            etiq_intern.insert(node.childNodes[0].getAttribute('etiq')[i:i+2], i)
        else:
            return len(etiq_intern)
    return len(etiq_intern)

def not_cons(min_node, max_node, cons_min):
    if max_node.nodeName == 'root':
        max_node.getAttribute('etiq').insert(max_node.childNodes[0].getAttribute('etiq')[cons_min:cons_min+2], cons_min)
        
        return len(max_node.getAttribute('etiq'))

    for i in range(cons_min, cons_min + 2, 1):
        concat = BitArray()
        concat.append(max_node.getAttribute('etiq')[i:i+1])
        concat.append(min_node.childNodes[0].getAttribute('etiq')[i:i+1])
        concat.append((min_node.childNodes[1].getAttribute('etiq')[i:i+1]))
        if concat.count(1) < concat.count(0):
            min_node.getAttribute('etiq').insert(bin(0), i)
        elif concat.count(1) > concat.count(0):
            min_node.getAttribute('etiq').insert(bin(1), i)
        else:
            min_node.getAttribute('etiq').insert(min_node.childNodes[0].getAttribute('etiq')[i:i+2], i)

            return min(len(min_node.getAttribute('etiq')), len(max_node.getAttribute('etiq')))

    return min(len(min_node.getAttribute('etiq')), len(max_node.getAttribute('etiq')))

def consensus(node_queue):
    len_min = 0
    intern_node = node_queue.get()
    if node_queue.empty():
        bro_node = intern_node
    else:
        bro_node = node_queue.get()

    while len_min < lenEtiq * 2:

        intern_len = cons(intern_node, len_min)
        bro_len = cons(bro_node, len_min)

        if intern_len < bro_len:
            min_node = intern_node
            max_node = bro_node
            cons_min = intern_len
        else:
            min_node = bro_node
            max_node = intern_node
            cons_min = bro_len

        len_min = not_cons(min_node, max_node, cons_min)
    
    if node_queue.empty():
        return None

    consensus(node_queue)

def decodage(upper_node):
    for child in upper_node.childNodes:
        chaine = ''
        for i in range(0, lenEtiq * 2, 2):
            chaine += ''.join([num for num, val in alphabet.items() if val == child.getAttribute('etiq')[i:i+2].uint])
        child.attributes['etiq'].value = chaine
        decodage(child)

# Création de la racine
etiq = BitArray()
node = create_node(xml, 'root', etiq, 'NA')

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
node_queue = get_nodes(xml, node_queue)
consensus(node_queue)
decodage(xml)

xml_str = xml.toprettyxml(indent ="\t") 
  
save_path_file = "tree.xml"
  
with open(save_path_file, "w") as f:
    f.write(xml_str)
