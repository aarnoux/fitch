from xml.dom import minidom
import bitstring as bs

def create_node(upper_node, node_name, etiq, cost):
    node = xml.createElement(node_name)
    node.setAttribute('etiq', etiq)
    node.setAttribute('cost', cost)
    upper_node.appendChild(node)
    return node

def consensus(upper_node):
    for child in upper_node.childNodes:
        if child.getAttribute('etiq') == '':
            consensus(child)
        for i in range(lenEtiq):
            etiq1 = etiq1 + bin(int(upper_node.childNodes[0].getAttribute('etiq')[i]))
            etiq2 = etiq2 + bin(int(upper_node.childNodes[1].getAttribute('etiq')[i]))
        print(etiq1, etiq2)

        etiq = bin(int(upper_node.childNodes[0].getAttribute('etiq')) ^ int(upper_node.childNodes[1].getAttribute('etiq')))
        print(upper_node)
        print(etiq)
        if etiq == 0:
            upper_node.setAttribute('etiq', etiq)

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
    etiq = 0
    cost = ''
    if tree[i] == ')':
        if tree[i-1] in alphabet.keys():
            j = 1
            while j <= lenEtiq:
                etiq = BitArray(lenEtiq*2)
                print(etiq)
                etiq = etiq + alphabet[tree[i-j]]
                print(etiq, "=", bin(etiq))
                etiq >> 2
                print(bin(etiq))
                j += 1
        node = create_node(node, str(i), etiq, cost)

    if tree[i] == ',':
        node = node.parentNode
        if tree[i+1] == '(':
            node = node.parentNode
        if tree[i-1] in alphabet.keys():
            j = 1
            while j <= lenEtiq:
                etiq = str(alphabet[tree[i-j]]) + etiq
                j += 1
        node = create_node(node, str(i), etiq, cost)

consensus(xml)

xml_str = xml.toprettyxml(indent ="\t") 
  
save_path_file = "tree.xml"
  
with open(save_path_file, "w") as f:
    f.write(xml_str)
