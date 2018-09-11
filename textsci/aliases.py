name = "n!kon"
valid_names = ["donka","caffeine","nikon","source", "lunatic","reker","corpse"]


def decypher_name(name, valid_names):
    '''Try to guess the original alias of the provided player string'''
    n=2
    name = name.lower()
    name_chain = [name[i:i+n] for i in range(0, len(name)-(n-1), 1)] #break the name into n-char chains
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
            return valid_name
