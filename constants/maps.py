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
    OBJ_NM = "Steal Object"
    maps = {}

    #announcement values come from maps/map_name.script look for wm_announce
    #objective names come from BSP files - look for team_CTF_redflag team_CTF_blueflag or trigger_objective_info
    map_announce = {
            "mp_ice" : [
                      [O_WIN,"Axis transmitted the documents!"],
                      [D_FLAG, "Allies reclaim the Shipping Halls!"],
                      [O_FLAG,"Axis captures the Shipping Halls!"],
                      [O_OBJ,"Service Door breached!"],
                      [O_OBJ,"Fortress Wall breached!"],
                      [OBJ_NM,"Allied Documents"]
                    ],
            "te_ufo" : [
                      [O_WIN,"Allies Transmitted the UFO Documents!"],
                      [D_FLAG,"Axis Regain Control of The Reinforcement Point!"],
                      [O_FLAG,"Allies Capture The Reinforcement Point!"],
                      [O_OBJ,"The Main Gate has been breached!"],
                      [O_OBJ,"The South Gate has been breached!"],
                      [OBJ_NM,"The UFO Documents"]
                    ],
            "template" : [
                      [O_WIN,""],
                      [D_FLAG,""],
                      [O_FLAG,""],
                      [O_OBJ,""],
                      [O_OBJ,""],
                      [OBJ_NM,""]
                    ],
            "te_frostbite" : [
                      [O_WIN,"Allies transmitted the documents!"],
                      [D_FLAG,"Axis reclaims the Upper Complex!"],
                      [O_FLAG,"Allies capture the Upper Complex!"],
                      [O_OBJ,"The Service Door has been breached!"],
                      [O_OBJ,"The Storage Wall has been breached!"],
                      [O_OBJ,"The Main Door has been breached!"],
                      [OBJ_NM,"the War Documents"]
                    ],
            "mp_village" : [
                      [O_WIN,"The Allies have escaped with the Gold!"],
                      [D_FLAG,"Axis reclaims the Northwest Courtyard!"],
                      [O_FLAG,"Allies capture the Northwest Courtyard!"],
                      [O_OBJ,"The Allies have broken into the Crypt!"],
                      [OBJ_NM,"the Gold"]
                    ],
            "mp_beach" : [
                      [O_WIN,"Allies transmitted the documents!"],#same as frostbite
                      [D_FLAG,"Axis reclaims the Forward Bunker!"],
                      [O_FLAG,"Allies capture the Forward Bunker!"],
                      [O_OBJ,"The Sea Wall has been breached!"],
                      [O_OBJ,"you would thing there would be something about door here but no"],
                      [OBJ_NM,"the War Documents"] #same as frostbite
                    ],
            "mp_sub" : [
                      [O_WIN,"Allied team has destoryed the Axis Submarine!"],
                      [D_FLAG,"Axis reclaims the Central Access Room!"],
                      [O_FLAG,"Allies capture the Central Access Room!"],
                      [O_OBJ,"Allies have breached the Sub Area!"],
                      [O_OBJ,"you would thing there would be something about filt here but no"],
                      [OBJ_NM,"the Axis Submarine"]
                    ],
            "mp_base" : [
                      [O_WIN,"Allied team has disabled the North Radar!"], #one or the other... whatever
                      [O_OBJ,"Allied team has disabled the South Radar!"]
                    ],
            "tundra_rush_beta" : [
                      [O_WIN,"Allies transmitted the beatdown list!"],
                      [D_FLAG,"Axis control the Tunnel!"],
                      [O_FLAG,"Allies control the Tunnel!"],
                      [O_OBJ,"The Compound Gate has been breached!"],
                      [OBJ_NM,"The Docs"]
                    ],
            "mp_assault" : [
                      [O_WIN,"Axis team destroyed the Communications Tower!"],
                      [D_FLAG,"Allies reclaim the Gate Area!"],
                      [O_FLAG,"Axis captures the Gate Area!"],
                      [O_OBJ,"Axis team breached the Gate Hatch!"],
                      [O_OBJ,"Axis team breached the Warehouse Door!"]
                    ]
            #todo castle, password, church
            }
  
    def load_maps(self):
        maps = {}
        #                        code,      name,  announcements,                defense,         offense, timelimit
        maps["mp_ice"] = RTCWMap("mp_ice", "Ice", self.map_announce["mp_ice"], self.G_ALLIES, self.G_AXIS, 10)
        maps["te_ufo"] = RTCWMap("te_ufo", "UFO", self.map_announce["te_ufo"], self.G_AXIS, self.G_ALLIES, 10)
        maps["te_frostbite"] = RTCWMap("te_frostbite", "Frostbite", self.map_announce["te_frostbite"], self.G_AXIS, self.G_ALLIES, 10)
        maps["mp_village"] = RTCWMap("mp_village", "Village", self.map_announce["mp_village"], self.G_AXIS, self.G_ALLIES, 10)
        maps["mp_beach"] = RTCWMap("mp_beach", "Beach", self.map_announce["mp_beach"], self.G_AXIS, self.G_ALLIES, 8)
        maps["mp_sub"] = RTCWMap("mp_sub", "Sub", self.map_announce["mp_sub"], self.G_AXIS, self.G_ALLIES, 12)
        maps["mp_base"] = RTCWMap("mp_base", "Base", self.map_announce["mp_base"], self.G_AXIS, self.G_ALLIES, 15)
        maps["tundra_rush_beta"] = RTCWMap("tundra_rush_beta", "Tundra", self.map_announce["tundra_rush_beta"], self.G_AXIS, self.G_ALLIES, 12)
        maps["mp_assault"] = RTCWMap("mp_assault", "Assault", self.map_announce["mp_assault"], self.G_ALLIES, self.G_AXIS, 10)
        self.maps = maps
    
    def transpose_by_obj(self):
        objectives = {}
        for m in self.maps:
            for o in self.maps[m].announcements:
                objectives[o[1]] = [o[0],m]
        return objectives