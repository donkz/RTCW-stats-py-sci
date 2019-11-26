import pandas as pd

name = "n!kon"
valid_names = [
 'abomb',
 'Boo7y',
 'caffe',
 'corpse',
 'cypher'
 'donka',
 'Fister Miagi',
 'illkilla',
 'jaytee',
 'krazykaze',
 'lunatic',
 'John_Mullins',
 'murkey',
 'Luna',
 'nigel',
 'nikon',
 'op!o',
 'parcher',
 'reker',
 'sem',
 'sonic',
 'source',
 'spuddy',
 'tragic',
 'VirUs047',
 'Wang of Pain'
]


def decypher_name(name, valid_names):
    '''Try to guess the original alias of the provided player string'''
    n=2
    name = name.lower()
    name_chain = [name[i:i+n] for i in range(0, len(name)-(n-1), 1)] #break the name into n-char chains
    matched_name = "??"
    #print(name_chain)
    for valid_name in valid_names:
        valid_name = valid_name.lower()
        valid_name_chain = [valid_name[i:i+n] for i in range(0, len(valid_name)-(n-1), 1)]  #break the name into n-char chains
        commonalities = set(name_chain).intersection(set(valid_name_chain)) #find common elements between name and valid_name
        #print("Name " + name +  " and template " + valid_name +" produced " + str(len(commonalities))+ " commonalities")
        #print(valid_name_chain)
        #print(commonalities)
        base_length = len(name)-(n-1) if len(name) < len(valid_name) else len(valid_name)-(n-1) #determine which name is longer to judge matching score
        if len(commonalities) >= base_length*.75:
            matched_name = valid_name
    return matched_name

all_names = pd.Series()
for result in results:
    temp1 = result["logs"]
    temp2  = temp1[temp1["event"] == "kill"]
    all_names = all_names.append(temp2["killer"]).append(temp2["victim"])
    
names = all_names.unique()

for name in names:
    print(name.ljust(20) + " to " + decypher_name(name.lower(), valid_names))