from bs4 import BeautifulSoup
from bs4 import Tag

def stripColors(line, colors):
    '''Strip character combinations like ^7don^eN^7ka to doNka'''
    ret = line
    for color in colors:
        ret = ret.replace(color,"")
    return ret;  

def setup_colors():
    colors_arr = ["^^"]
    for x in range(33,126):
        colors_arr.append("^"+chr(x))
    return colors_arr

def rtcw_to_html_colors(name):
    '''Convert rtcw chars like ^7don^eN^7ka to html like 
    <span style="color: #681EA7">do</span><span style="color: #00B906">N</span>'''
    # name = "^>don^^N^7ka"  # debug
    soup = BeautifulSoup("", "html.parser")
    
    name = name.replace("^^","^~")  # going split by carot
    name_tokens = name.split("^")
    if len(name_tokens) > 1:
        for i, token in enumerate(name_tokens):
            #print("Current token: ", token)
            if len(token.strip()) < 2:
                continue
            token_html_span = Tag(soup, name = "span")
            if i == 0:
                token_html_span.append(token)
            else:
                token_html_span.append(token[1:])

                color_code = token[0:1]
                if color_code == "~":
                    color_code="cr"
                elif color_code == "/":
                    color_code="sl"
                elif color_code == "*":
                    color_code="st"       
                elif color_code == "-":
                    color_code="mi"  
                elif color_code == "+":
                    color_code="pl"  
                elif color_code == "?":
                    color_code="qu"  
                elif color_code == "@":
                    color_code="at"  
                elif color_code == ">":
                    color_code="mt"  
                elif color_code == "<":
                    color_code="lt"  
                token_html_span["class"] = "c" + color_code
            soup.append(token_html_span)
    else:
        span = Tag(soup, name = "span")
        span.append(name)
        soup.append(span)
    #print("Current result: ", soup)
    return soup  