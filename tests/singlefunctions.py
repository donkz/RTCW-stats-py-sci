from textsci.aliases import decypher_name
import time
from textsci.teams import team_name_chars, team_name_front

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