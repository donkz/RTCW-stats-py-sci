from textsci.aliases import decypher_name
import time
from textsci.teams import team_name_chars, team_name_front, get_team_name

name = "n!kon"
valid_names = ["donka","caffeine","nikon","source", "lunatic","reker","corpse"]

def test_decypher_name():            
    print(decypher_name("/mute donkz", valid_names))
    print(decypher_name("donkanator", valid_names))
    print(decypher_name("sourcerer", valid_names))    
    print(decypher_name("rekenator", valid_names))    
    print(decypher_name("caff", valid_names))  
    print(decypher_name("<333 caffe1ne", valid_names))  
    print(decypher_name("Lunatic ????", valid_names))  
    print(decypher_name("----E corpserrr", valid_names))  

test_teams = ['----E Spuddy', '----E caffeine', '----E copserr', '----E jaytee', '----E oreo', '----E v1k!ng', '/mute ABomB', '/mute Op!o', '/mute doNka', '/mute eternal', '/mute nigel', '/mute sem']

def test_clan_tags():
    start_time = time.time()
    print(team_name_chars(["parcher-X-","cky-X-","ra!ser-X-","-a-brian-X-","-a-holliwood-X-","fx-gook-X-","fx-dook-X-"]))
    print(team_name_chars(["parcher","cky","ra!ser","-a-brian","-a-holliwood","fx-gook","fx-dook"]))
    print(team_name_chars(test_teams [0:6]))
    print(team_name_chars(test_teams [7:]))
    print("--- %s seconds ---" % (time.time() - start_time))
    
    start_time = time.time()
    print(team_name_front(["parcher-X-","cky-X-","ra!ser-X-","-a-brian-X-","-a-holliwood-X-","fx-gook-X-","fx-dook-X-"]))
    print(team_name_front(["parcher","cky","ra!ser","-a-brian","-a-holliwood","fx-gook","fx-dook"]))
    print(team_name_front(test_teams[0:6]))
    print(team_name_front(test_teams[7:]))
    print("--- %s seconds ---" % (time.time() - start_time))
    
#standard front chars clan tag
players = ["exe-donkz",
           "exe-wiza4d",
           "exe-flog",
           "exe-blog",
           "exe-bizz",
           "exe-pschonic",
           "ex-tard"]

#similar chars, but not too many
players2 = ["colgate",
           "wiza4d",
           "flog",
           "blog",
           "bolg",
           "mogul",
           ]

#one letter somewhat repeats
players3 = ["donkz",
           "kittens",
           "caffeine",
           "blan",
           "clan",
           "brazilian flan"]

#suffix clan tag
players4 = ["luigi-x-",
           "eternal-x-",
           "slaya-x-",
           "ringer-x-",
           "elutard",
           "cky-x-",
           "mario-x-"
           ]

test_strings = [players, players2, players3, players4]

def test_all(test_strings):
    for team in test_strings:
        print("Team: " + ",".join(team))
        print("Front chars method: " + team_name_front(team))
        print("Segments method: " + team_name_chars(team))
        print("Final result: " + get_team_name(team))
        
test_all(test_strings)