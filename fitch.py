from xml.dom import minidom

def create_node(upper_node, node_id):
    node_id.setAttribute('id', node_id.tagName)
    node_id.setAttribute('Etiq', 'NA')
    upper_node.appendChild(node_id)

newick = "(((ACT,AGA)W,(TGA,AGT)V)X,(ACT,TCG)Y)Z;"
newick_cons = "((C,(H,I)),(F,G));"  # TODO

# demander sys.argv pour avoir la taille des étiquettes

tree = newick[::-1]
print(tree)

xml = minidom.Document()
node_id = xml.createElement(tree[1])
create_node(xml, node_id)
xml.appendChild(node_id)

for i in range(2,len(tree)):
    if tree[i] == ')':
        upper_node = node_id
        node_id = xml.createElement(tree[i+1])
        create_node(upper_node, node_id)
    if tree[i] == ',':
        upper_node = node_id.parentNode
        if tree[i-1] == '(':
            upper_node = upper_node.parentNode
        node_id = xml.createElement(tree[i+1])
        create_node(upper_node, node_id)


for nodes in xml.childNodes:
    print(nodes)

A = 0
C = 1
G = 2
T = 3


xml_str = xml.toprettyxml(indent ="\t") 
  
save_path_file = "tree.xml"
  
with open(save_path_file, "w") as f:
    f.write(xml_str)
