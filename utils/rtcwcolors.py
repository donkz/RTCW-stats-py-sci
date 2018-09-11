def stripColors(line, colors):
    '''Strip character combinations like ^7don^eN^7ka to doNka'''
    ret = line
    for color in colors:
        ret = ret.replace(color,"")
    return ret;  

def setup_colors():
    colors_arr = []
    for x in range(33,126):
        colors_arr.append("^"+chr(x))
    return colors_arr