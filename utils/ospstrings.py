import re
import hashlib
#Disassemble the following lines into a tuple of (player,statline)
#                                Kll Dth Sui TK Eff Gib DG    DR      TD  Score
#line = "Allies /mute doNka      19   3   0  0  86   5  2367  1435    0     48"
#line = "Allies /mute sem        19  10   2  2  65   4  3588  2085  226     46"
def process_OSP_line(line):
    tokens = re.split("\s+", line)
    if len(tokens) < 10:
        return (None, None)
    player = " ".join(tokens[1:len(tokens)-10])
    return (player, [player, tokens[0],tokens[-10],tokens[-9],tokens[-8],tokens[-7],tokens[-6],tokens[-5],tokens[-4],tokens[-3],tokens[-2],tokens[-1]])

#re.search("^Accuracy info for: (.*)","Accuracy info for: -doNka- (2 Rounds)")
#text = '-doNka- (2 Rounds)'
def osp_token_accuracy_playername_round(text):
    tokens = text.split("(")
    name = ""
    round_num = 1
    if len(tokens) > 1:
        name = "(".join(tokens[:-1]).strip()
        round_num = tokens[-1][0]
    else:
        print(f"[!] Could not extract name from {text}")
    return (name, round_num)

def osp_token_accuracy_round_num(text):
    tokens = text.split(" ")
    round_num = 1
    if len(tokens) > 1:
        round_num = int(tokens[-2][-1])
    else:
        print(f"[!] Could not extract round_num from {text}")
    return round_num

def osp_token_one_slash_two(text):
    tokens = text.strip().split("/")
    one = ''
    two = ''
    if len(tokens) > 1:
        one = tokens[0]
        two = tokens[1]
    return (one,two)

def get_round_guid_osp(osp_lines):
    string = ''.join(osp_lines)
    osp_guid = hashlib.md5(string.encode()).hexdigest()
    return osp_guid

import collections
def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_accuracy_cols(players_all):
    all_items = {}
    for k,v in players_all.items():
        if len(v.keys()) > 0:
            all_items.update(flatten(v[list(v.keys())[0]]))
    
    for v in all_items:
        all_items[v] = '0'
    return all_items