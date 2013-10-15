from reportlab.lib.colors import HexColor 

pdf_chart_colors = [ HexColor("#0000e5"), HexColor("#1f1feb"), HexColor("#5757f0"), HexColor("#8f8ff5"), HexColor("#c7c7fa"), HexColor("#f5c2c2"), HexColor("#eb8585"), HexColor("#e04747"), HexColor("#d60a0a"), HexColor("#cc0000"), HexColor("#ff0000"), ] 

def setItems(n, obj, attr, values): 
    m = len(values) 
    i = m // n 
    for j in xrange(n): 
        setattr(obj[j],attr,values[j*i % m])