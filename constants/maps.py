class RTCWMap:
      
    def __init__(self, code, name, announcements, defense, offense, timelimit):
         self.code = code
         self.name = name
         self.announcements = announcements
         self.defense = defense
         self.offense = offense
         self.timelimit = timelimit


class ConstMap:
    
    G_AXIS = "Axis"
    G_ALLIES = "Allies"
    O_WIN = "Offense win"
    D_WIN = "Defense win"
    O_FLAG = "Offense flag"
    D_FLAG = "Defense flag"
    O_OBJ = "Mid objective"

    map_announce = {
            "mp_ice" : [
                      [O_WIN,"Offense win", "Axis transmitted the documents!"],
                      [D_FLAG,"Defense flag", "Allies reclaim the Shipping Halls!"],
                      [O_FLAG,"Offense flag","Axis captures the Shipping Halls!"],
                      [O_OBJ,"Service Door breached!"],
                      [O_OBJ,"Fortress Wall breached!"]
                    ]
            }

    maps = {}  
    maps["mp_ice"] = RTCWMap("mp_ice", "Ice", map_announce["mp_ice"], G_ALLIES, G_AXIS, 10)