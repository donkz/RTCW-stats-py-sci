class RTCWMap:
      
    def __init__(self, code, name, announcements, defense, offense, timelimit, objname):
         self.code = code
         self.name = name
         self.announcements = announcements
         self.defense = defense
         self.offense = offense
         self.timelimit = timelimit
         self.objname = objname


class ConstMap:
    
    G_AXIS = "Axis"
    G_ALLIES = "Allies"
    O_WIN = "Offense win"
    D_WIN = "Defense win"
    O_FLAG = "Offense flag"
    D_FLAG = "Defense flag"
    O_OBJ = "Mid objective"
    OBJ_NM = "Steal Object"
    O_STEAL = "Stole objective"
    D_RETURN = "Returned objective"
    B_DISARM = "Defense disarmed" #Allies
    R_DISARM = "Defense disarmed" #Axis
    O_PLANT = "Offense plant"
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
                      [O_PLANT, "Dynamite planted near the Fortress Wall!"], # Dynamite planted near %s! https://github.com/id-Software/RTCW-MP/blob/937b209a3c14857bea09a692545c59ac1a241275/src/game/g_weapon.c
                      [O_PLANT, "Dynamite planted near the Service Door!"]
                    ],
            "te_ufo" : [
                      [O_WIN,"Allies Transmitted the UFO Documents!"],
                      [D_FLAG,"Axis Regain Control of The Reinforcement Point!"],
                      [O_FLAG,"Allies Capture The Reinforcement Point!"],
                      [O_OBJ,"The Main Gate has been breached!"],
                      [O_OBJ,"The South Gate has been breached!"],
                      [O_PLANT, "Dynamite planted near The South Gate!"],
                      [O_PLANT, "Dynamite planted near The Main Gate!"]
                    ],
            "template" : [
                      [O_WIN,""],
                      [D_FLAG,""],
                      [O_FLAG,""],
                      [O_OBJ,""],
                      [O_OBJ,""]
                    ],
            "anymap" : [
                      [R_DISARM,"Axis engineer disarmed the Dynamite!"], #https://github.com/id-Software/RTCW-MP/blob/937b209a3c14857bea09a692545c59ac1a241275/src/game/g_weapon.c
                      [B_DISARM,"Allied engineer disarmed the Dynamite!"]
                    ],
            "te_frostbite" : [
                      [O_WIN,"Allies transmitted the documents!"],
                      [D_FLAG,"Axis reclaims the Upper Complex!"],
                      [O_FLAG,"Allies capture the Upper Complex!"],
                      [O_OBJ,"The Service Door has been breached!"],
                      [O_OBJ,"The Storage Wall has been breached!"],
                      [O_OBJ,"The Main Door has been breached!"],
                      [O_PLANT, "Dynamite planted near the service door!"],
                      [O_PLANT, "Dynamite planted near the main door!"],
                      [O_PLANT, "Dynamite planted near the storage wall!"]
                    ],
            "mp_beach" : [
                      [O_WIN,"Allies transmitted the documents!"],#same as frostbite
                      [D_FLAG,"Axis reclaims the Forward Bunker!"],
                      [O_FLAG,"Allies capture the Forward Bunker!"],
                      [O_OBJ,"The Sea Wall has been breached!"],
                      [O_OBJ,"you would thing there would be something about door here but no"],
                      [O_PLANT, "Dynamite planted near the Sea Wall breach!"],
                      [O_PLANT, "Dynamite planted near the Sea Wall door!"]
                    ],
            "axis_complex" : [
                      [O_WIN,"Allies have transmitted the decoder manual!"],
                      [D_FLAG,"Axis reclaim the Forward Deployment area!"], 
                      [O_FLAG,"Allies capture the Forward Deployment area!"],
                      [O_OBJ,"The service door has been breached!"],
                      [O_OBJ,"The Eastern Tower has been breached!"],
                      [O_OBJ,"The main complex has been breached!"],
                      [O_PLANT, "Dynamite planted near the Eastern Tower Entrance!"],
                      [O_PLANT, "Dynamite planted near the Main Entrance!"],
                      [O_PLANT, "Nothing about planting the service door"]
                    ],
            "te_escape2" : [
                      [O_WIN,"The Allied team escaped with the Unholy Grail!"],
                      [D_FLAG,"The Axis team reclaimed the Flag!"],
                      [O_FLAG,"The Allied team captured the Flag!"],
                      [O_OBJ,"The Tunnel Door was obliterated!"],
                      [O_OBJ,"The Main Gate has been destroyed!"],
                      [O_PLANT, "Dynamite planted near the Tunnel Door!"],
                      [O_PLANT, "Dynamite planted near the Main Gate!!"]
                    ],
            "mp_keep" : [
                      [O_WIN,"Allied team captured the Sacred Obelisk!"],
                      [O_OBJ,"Allies have breached the roof!"],
                      [O_PLANT, "Dynamite planted near the Southwest Gate!"],
                      [O_PLANT, "Dynamite planted near the Southeast Gate!"]
                    ],
            "mp_castle" : [
                      [O_WIN,"The Allies have escaped with the Obelisk!"],
                      [O_OBJ,"Allies have breached West Gate!"],
                      [O_OBJ,"Allies have breached the Hallway Gate!"],
                      [O_OBJ,"The Coffin has been destroyed!"],
                      [O_PLANT, "Dynamite planted near the West Gate!"],
                      [O_PLANT, "Dynamite planted near the Hallway Gate!"],
                      [O_PLANT, "Dynamite planted near the Coffin!"]
                    ],
            "mp_village" : [
                      [O_WIN,"The Allies have escaped with the Gold!"],
                      [D_FLAG,"Axis reclaims the Northwest Courtyard!"],
                      [O_FLAG,"Allies capture the Northwest Courtyard!"],
                      [O_OBJ,"The Allies have broken into the Crypt!"],
                      [O_PLANT, "Dynamite planted near Gold Storage Crypt!"]
                    ],
            "mp_sub" : [
                      [O_WIN,"Allied team has destoryed the Axis Submarine!"],
                      [D_FLAG,"Axis reclaims the Central Access Room!"],
                      [O_FLAG,"Allies capture the Central Access Room!"],
                      [O_OBJ,"Allies have breached the Sub Area!"],
                      [O_OBJ,"you would thing there would be something about filt here but no"],
                      [O_PLANT, "Dynamite planted near Filtration Door!"],
                      [O_PLANT, "Dynamite planted near Storage Door!"],
                      [O_PLANT, "Dynamite planted near the Axis Submarine!"],
                      [OBJ_NM,"the Axis Submarine"]
                    ],
            "mp_base" : [
                      [O_WIN,"Allied team has disabled the North Radar!"], #one or the other... whatever
                      [O_OBJ,"Allied team has disabled the South Radar!"],
                      [O_PLANT, "Dynamite planted near the South Radar [02]!"],
                      [O_PLANT, "Dynamite planted near the North Radar [01]!"]
                    ],
            "tundra_rush_beta" : [
                      [O_WIN,"Allies transmitted the beatdown list!"],
                      [D_FLAG,"Axis control the Tunnel!"],
                      [O_FLAG,"Allies control the Tunnel!"],
                      [O_OBJ,"The Compound Gate has been breached!"],
                      [O_PLANT, "Dynamite planted near The Radio!"]
                    ],
            "mp_assault" : [
                      [O_WIN,"Axis team destroyed the Communications Tower!"],
                      [D_FLAG,"Allies reclaim the Gate Area!"],
                      [O_FLAG,"Axis captures the Gate Area!"],
                      [O_OBJ,"Axis team breached the Gate Hatch!"],
                      [O_OBJ,"Axis team breached the Warehouse Door!"],
                      [O_PLANT, "Dynamite planted near the Gate Hatch!"],
                      [O_PLANT, "Dynamite planted near the Warehouse Entrance!"],
                      [O_PLANT, "Dynamite planted near The Communications Tower!"]
                    ],
            "te_pacific2" : [
                      [O_WIN,"Allied team has disabled the Radar Array!"],
                      [O_OBJ,"Allied team has destroyed the Barricade"],
                      [O_PLANT, "Dynamite planted near the Radar Array!"],
                      [O_PLANT, "Dynamite planted near the Security Wall!"]
                    ],
            "mp_password2" : [
                      [O_WIN,"Allies escaped with the Endoarm!"],
                      [D_FLAG,"Axis reclaims the Service Halls!"],
                      [O_FLAG,"Allies capture the Service Halls!"],
                      [D_FLAG,"Process aborted..."],
                      [D_FLAG,"Password has been changed..."],
                      [O_OBJ,"Allies breach the Service Door!"],
                      [O_PLANT, "Dynamite planted near Service Door!"],
                      [O_PLANT, "Process started with valid password!"],
                      [O_OBJ,"Process finished!"]
                    ],
            "mp_chateau" : [
                      [O_WIN,"Allies have transmitted the Top Secret Documents!"],
                      [D_FLAG, "Axis reclaims the Grand Staircase!"],
                      [O_FLAG,"Allies capture the Grand Staircase!"],
                      [O_OBJ,"Allies have gained entry into the Chateau."],
                      [O_PLANT, "Dynamite planted near the Main Door!"], 
                      [O_PLANT, "Dynamite planted near the Cellar Door!"]
                    ],
            "te_nordic_b2" : [
                      [O_WIN,"Allies have transmitted the generator plans!"],
                      [D_FLAG, "Axis reclaim the tunnel checkpoint flag!"],
                      [O_FLAG,"Allies capture the tunnel checkpoint flag!"],
                      [O_OBJ,"The main gate has been breached!"],
                      [O_OBJ,"The NOT SO main gate has been breached!"],  # TODO: whats the little door called
                      [O_PLANT, "Dynamite planted near the Main Gate!"], 
                      [O_PLANT, "Dynamite planted near The Radio!"]
                      ],
            "mp_depot" : [
                      [O_WIN,"Axis team destroyed the Allied Field Operations!"],
                      [O_WIN,"Allied team destoyed the Anti-Aircraft gun!"],
                      [D_FLAG, "Axis captures the Forward Deployment Area!"],
                      [O_FLAG, "Allies capture the Forward Deployment Area!"],
                      [O_OBJ,"Allies have breached the East Gate!"], 
                      [O_OBJ,"Dynamite planted near the Allied Field Operations!"],  
                      [O_OBJ,"Dynamite planted near the Anti-Aircraft Gun!"],
                      [O_PLANT, "Dynamite planted near the East Gate!"]
                      ],
            "mp_marketgarden" : [
                      [O_WIN,"Axis team destroyed the Allied Command Center!"],
                      [D_FLAG, "Allied team defused the Bridge Detonator!"],
                      [D_FLAG, "Allies have stolen (null)!"],
                      [O_FLAG, "Axis capture the Forward Deployment Area!"],
                      [O_PLANT, "Dynamite planted near the Allied Command Center!"],
                      [O_PLANT, "Dynamite planted near the Water Tower Door!"]
                      ],
            "te_delivery_b1" : [
                      [O_WIN,"Allies have escaped with the Gold!"],
                      [D_FLAG, "Axis reclaims the Forward Bunker!"],
                      [O_FLAG, "Allies capture the Forward Bunker!"],
                      [D_FLAG, "The Loading Door is Closing!"],
                      [O_FLAG, "The Vault Door is now Open!"],
                      [O_FLAG, "The Loading Door is Opening!"],
                      [O_PLANT,"Dynamite planted near the East Wall!"],
                      [O_PLANT,"Dynamite planted near the West Wall!"],
                      [O_OBJ, "The West Wall has been breached!"],
                      [O_PLANT,"Dynamite planted near the Control Room Door!"],
                      [O_OBJ, "The Control Room Door has been breached!"],
                      [O_OBJ, "The East Wall has been breached!"]
                      ],
            "mp_rocket" : [
                      [O_WIN,"Override console been used, rocket launch aborted!"],
                      [D_FLAG,"Axis reclaims the First Cave!"],
                      [O_FLAG,"Allies capture the First Cave!"],
                      [O_OBJ,"Allies have broken through train tunnel cave in!"],
                      [O_OBJ,"Allies have destroyed the Rocket Bay Emergency Exit!"], 
                      [O_PLANT, "Dynamite planted near The Upper Rocket Bay Door!"],
                      [O_PLANT, "Dynamite planted near Tunnel Rubble!"],
                      [O_PLANT, "Dynamite planted near The Rocket Bay Emergency Exit!"]
                    ],
            "mml_church_v1" : [
                      [O_WIN,"Axis have escaped with the Relic"],
                      [O_FLAG,"The Allied Alarm is off"],
                      [D_FLAG,"The Allied Alarm is on"],
                      [O_OBJ,"Axis have blown open the Side Door"],
                      [O_PLANT, "Dynamite planted near the Side Door!"]
                    ],
            "te_cipher_b3" : [
                      [O_WIN,"Allies have transmitted the codebook!"],
                      [D_FLAG, "Axis reclaim the East deployment area!"],
                      [O_FLAG,"Allies capture the East deployment area!"],
                      [O_OBJ,"The warehouse door has been breached!"],
                      [O_OBJ,"The main entrance has been breached!"],
                      [O_OBJ,"The East Tower entrance has been breached!"],  
                      [O_PLANT, "Dynamite planted near the Eastern Tower Entrance!"],
                      [O_PLANT, "Dynamite planted near the East Tower Entrance!"],
                      [O_PLANT, "Dynamite planted near the Warehouse Door!"],
                      [O_PLANT, "Dynamite planted near the Main Entrance!"]
                    ],
             "mp_breakout" : [
                      [O_WIN,"Allies have disabled the German 88!"],
                      [D_FLAG, "Axis take the Eastern Courtyard!"],
                      [O_FLAG, "Allies take the Eastern Courtyard!"],
                      [O_FLAG, "Allies take the Western Courtyard!"],
                      [O_FLAG, "Allies take the Western Control Point!"],
                      [D_FLAG, "Axis take the Eastern Control Point!"],
                      [O_FLAG, "Allies take the Eastern Control Point!"],
                      [D_FLAG, "Axis take the Western Courtyard!"],
                      [O_FLAG, "Allies take the Southern Control Point!"],
                      [D_FLAG, "Axis take the Northern Control Point!"],
                      [O_FLAG, "Allies take the Northern Control Point!"],
                      [O_FLAG, "Allies take the Town Market!"],
                      [D_FLAG, "Axis take the South Gate Area!"],
                      [D_FLAG, "Axis take the Artillery Gun!"],
                      [O_FLAG, "Allies take the Sewers!"],
                      [O_FLAG, "Dynamite planted near The Back Alley Wall!"],
                      [O_OBJ, "Dynamite planted near The German 88!"],
                      [D_FLAG, "Axis have Destroyed the Back Alley Wall!"],
                      [O_PLANT, "Dynamite planted near The Allied Field Communications!"],
                      [O_PLANT, "Dynamite planted near The Church Alley Gate!"],
                      [O_OBJ, "Allies have destroyed the Church Gate!"]
                    ],
             "mp_tram" : [
                      [O_WIN,"Allies transmitted the radio signal!"],
                      [D_FLAG,"Axis gains control of the Village Tram Tower!"],
                      [O_FLAG,"Allies gain control of the Village Tram Tower!"],
                      [O_OBJ,"Allies breached the Castle Basement!"],
                      [O_OBJ,"Allies breached the Outpost Lower Access Door!"],
                      [O_PLANT, "Dynamite planted near the Castle Basement Door!"],
                      [O_PLANT, "Dynamite planted near the Lower Access Door!"],
                      [O_OBJ,"Allies breached the Outpost Supply Room!"],
                      [O_PLANT, "Dynamite planted near the Supply Room Door!"]
                    ],
            "adlernest_b5" : [
                      [O_WIN,"Allies transmitted Hitler's Documents!"],
                      [D_FLAG,"Axis reclaim the Warehouse Flag!"],
                      [O_FLAG,"Allies capture the Warehouse Flag!"],
                      [O_PLANT, "Dynamite planted near the Door Controls!"],
                      [O_OBJ,"The Doors are opening!"],
                      [O_PLANT, "Dynamite planted near the Pipe Side Door!"],
                      [O_OBJ,"Pipe Side Door breached!"],
                      [O_FLAG, "Main Blast Doors closing!"],
                      [O_OBJ,"Main Blast Doors opening!"]
                    ],        
            "braundorf_b5" : [
                      [O_WIN,"Allies have destroyed the Bunker Controls!"],
                      [D_FLAG, "Axis capture the Factory Flag!"],
                      [O_FLAG,"Allies capture the Factory Flag!"],
                      [O_OBJ,"Allied team breached the Main Door!"],
                      [O_OBJ,"Allied team breached the Side door!"],  
                      [O_PLANT, "Dynamite planted near the Bunker Controls!"],
                      [O_PLANT, "Dynamite planted near the Main Gate!"], #frequent obj across several maps
                      [O_PLANT, "Dynamite planted near the Side Door!"] #same as church
                    ],
            "braundorf_b7" : [
                      [O_WIN,"Allies capture the Factory District!"],
                      [O_FLAG, "Allies capture the Side Entrance!"],
                      [D_FLAG,"Axis reclaim the Side Entrance!"],
                      [O_FLAG, "The Side Gate is opening!"],
                      [D_FLAG,"The Side Gate is closing!"],
                      [O_OBJ,"Allies have breached the Main Gate!"],
                      [O_OBJ,"Allies have breached the Side Door!"],  
                      [O_PLANT, "Dynamite planted near the Bunker Controls!"],
                      [O_PLANT, "Dynamite planted near the Main Gate!"], #frequent obj across several maps
                      [O_PLANT, "Dynamite planted near the Side Door!"] #same as church abd broun5
                    ],
            "bd_bunker_b2" : [
                      [O_WIN,"Allies have transmitted the Quiz Answers!"],
                      #[D_FLAG, "Axis capture the Factory Flag!"],
                      [O_FLAG,"Allies have captured the Inner Compound"],
                      [O_OBJ,"Allies have breached the Bunker Door!"],
                      [O_OBJ,"Allies have breached the Storage Wall!"],  
                      [O_PLANT, "Dynamite planted near the Storage Wall!"],
                      [O_PLANT, "Dynamite planted near the Bunker Door!"]
                    ],
            "radar_b4" : [
                      [O_WIN,"Axis have escaped with the West Radar Parts!"],
                      [D_FLAG, "Allies reclaim the Forward Bunker!"],
                      [O_FLAG,"Axis capture the Forward Bunker!"],
                      [O_OBJ,"Axis have breached the Main Entrance!"],
                      [O_OBJ,"Axis have breached the Side Entrance!"],  
                      [O_PLANT, "Dynamite planted near the Side Entrance!"],
                      #[O_PLANT, "Dynamite planted near the Bunker Door!"]
                    ],
            "kungfugrip" : [
                      [O_WIN,"Axis have transmitted the CD-Key!"],
                      [D_FLAG, "Allies reclaim the Forward Bunker!"],
                      [O_FLAG,"Allies reclaim the Playboy!"],
                      [O_OBJ,"Axis have breached the East heat duct!"],
                      [O_OBJ,"Axis have breached the North heat duct!"],  
                      [O_PLANT, "Dynamite planted near the East Vent!"],
                      [O_PLANT, "Dynamite planted near the North Vent!"]
                    ],
            "te_industrial" : [
                      [O_WIN,"Allies transmitted the documents!"],
                      [O_OBJ,"The Main Gate has been breached!"],
                      [O_OBJ,"The Transmitter Door has been breached!"],  
                      [O_PLANT, "Dynamite planted near the Transmitter Door!"],
                      [O_PLANT, "Dynamite planted near the Main Gate!"]
                    ]
            }
    
    '''
    Load all map data into a map dictionary {mapcode : mapclass}
    '''
    def load_maps(self):
        maps = {}
        #                                  code,                name,         announcements from above               defense,       offense,    timelimit  Objective name without exclamation mark
        maps["mp_ice"] =           RTCWMap("mp_ice",           "Ice",         self.map_announce["mp_ice"],           self.G_ALLIES, self.G_AXIS,   10,   "Allied Documents")
        maps["axis_complex"] =     RTCWMap("axis_complex",     "Axis Complex",self.map_announce["axis_complex"],     self.G_AXIS,   self.G_ALLIES, 10,   "The Decoder Manual")
        maps["te_escape2"] =       RTCWMap("te_escape2",       "Escape",      self.map_announce["te_escape2"],       self.G_AXIS,   self.G_ALLIES, 10,   "the Unholy Grail")       
        maps["te_ufo"] =           RTCWMap("te_ufo",           "UFO",         self.map_announce["te_ufo"],           self.G_AXIS,   self.G_ALLIES, 12,   "The UFO Documents")
        maps["te_frostbite"] =     RTCWMap("te_frostbite",     "Frostbite",   self.map_announce["te_frostbite"],     self.G_AXIS,   self.G_ALLIES, 10,   "the War Documents")
        maps["mp_village"] =       RTCWMap("mp_village",       "Village",     self.map_announce["mp_village"],       self.G_AXIS,   self.G_ALLIES, 10,   "the Gold")
        maps["mp_beach"] =         RTCWMap("mp_beach",         "Beach",       self.map_announce["mp_beach"],         self.G_AXIS,   self.G_ALLIES, 8,    "the War Documents")       # objective name same as frostbite
        maps["mp_sub"] =           RTCWMap("mp_sub",           "Sub",         self.map_announce["mp_sub"],           self.G_AXIS,   self.G_ALLIES, 12,    "")
        maps["mp_base"] =          RTCWMap("mp_base",          "Base",        self.map_announce["mp_base"],          self.G_AXIS,   self.G_ALLIES, 15,    "")
        maps["tundra_rush_beta"] = RTCWMap("tundra_rush_beta", "Tundra",      self.map_announce["tundra_rush_beta"], self.G_AXIS,   self.G_ALLIES, 12,    "The Docs")
        maps["mp_assault"] =       RTCWMap("mp_assault",       "Assault",     self.map_announce["mp_assault"],       self.G_ALLIES, self.G_AXIS,   10,    "")
        maps["mp_password2"] =     RTCWMap("mp_password2",     "Password",    self.map_announce["mp_password2"],     self.G_AXIS,   self.G_ALLIES, 12,    "the Endoarm")
        maps["mp_chateau"] =       RTCWMap("mp_chateau",       "Chateau",     self.map_announce["mp_chateau"],       self.G_AXIS,   self.G_ALLIES, 10,    "the Top Secret Documents!") #"the War Documents" also shows up mid-game on chateau although it shouldn't!
        maps["te_nordic_b2"] =     RTCWMap("te_nordic_b2",     "Tunordic",    self.map_announce["te_nordic_b2"],     self.G_AXIS,   self.G_ALLIES, 10,    "the Generator Plans")
        maps["mp_rocket"] =        RTCWMap("mp_rocket",        "Rocket",      self.map_announce["mp_rocket"],        self.G_AXIS,   self.G_ALLIES, 12,    "Override Key")         
        maps["mml_church_v1"] =    RTCWMap("mml_church_v1",    "Church",      self.map_announce["mml_church_v1"],    self.G_ALLIES, self.G_AXIS,   10,    "the Holy Relic")      
        maps["te_pacific2"] =      RTCWMap("te_pacific2",      "Pacific",     self.map_announce["te_pacific2"],      self.G_AXIS,   self.G_ALLIES,  8,    "")      
        maps["mp_castle"] =        RTCWMap("mp_castle",        "Castle",      self.map_announce["mp_castle"],        self.G_AXIS,   self.G_ALLIES, 10,    "the Obelisk")
        maps["mp_keep"] =          RTCWMap("mp_keep",          "Keep",        self.map_announce["mp_keep"],          self.G_AXIS,   self.G_ALLIES, 10,    "the Sacred Obelisk")
        maps["te_delivery_b1"] =   RTCWMap("te_delivery_b1",   "Delivery",    self.map_announce["te_delivery_b1"],   self.G_AXIS,   self.G_ALLIES, 10,    "the Axis Gold")
        maps["mp_depot"] =         RTCWMap("mp_depot",         "Depot",       self.map_announce["mp_depot"],         self.G_AXIS,   self.G_ALLIES, 10,    "")
        maps["te_cipher_b3"] =     RTCWMap("te_cipher_b3",     "Cipher",      self.map_announce["te_cipher_b3"],     self.G_AXIS,   self.G_ALLIES, 10,    "the Enigma codebook")
        maps["mp_marketgarden"] =  RTCWMap("mp_marketgarden",  "Market garden",self.map_announce["mp_marketgarden"], self.G_ALLIES, self.G_AXIS,   20,    "(null)")
        maps["mp_breakout"] =      RTCWMap("mp_breakout",      "Breakout",    self.map_announce["mp_breakout"],      self.G_AXIS,   self.G_ALLIES, 16,    "")
        maps["mp_tram"] =          RTCWMap("mp_tram",          "Tram",        self.map_announce["mp_tram"],          self.G_AXIS,   self.G_ALLIES, 20,    "the Radio Codes Booklet") 
        maps["adlernest_b5"] =     RTCWMap("adlernest_b5",     "Adlernest",   self.map_announce["adlernest_b5"],     self.G_AXIS,   self.G_ALLIES, 10,    "Hitler's Documents")
        maps["adlernest_b5_rtcwpro"] =     RTCWMap("adlernest_b5",     "Adlernest",   self.map_announce["adlernest_b5"],     self.G_AXIS,   self.G_ALLIES, 10,    "Hitler's Documents")
        maps["braundorf_b5"] =     RTCWMap("braundorf_b5",     "Braundorf",   self.map_announce["braundorf_b5"],     self.G_AXIS,   self.G_ALLIES, 8,     "")
        maps["braundorf_b7"] =     RTCWMap("braundorf_b7",     "Braundorf",   self.map_announce["braundorf_b7"],     self.G_AXIS,   self.G_ALLIES, 8,     "")
        maps["bd_bunker_b2"] =     RTCWMap("bd_bunker_b2",     "Brewdog",     self.map_announce["bd_bunker_b2"],     self.G_AXIS,   self.G_ALLIES, 10,    "the Secret Documents")
        maps["radar_b4"] =         RTCWMap("radar_b4",         "Radar",       self.map_announce["radar_b4"],         self.G_ALLIES, self.G_AXIS,   10,    "the West Radar Parts")
        maps["kungfugrip"] =       RTCWMap("kungfugrip",       "Kungfugrip",  self.map_announce["kungfugrip"],       self.G_ALLIES, self.G_AXIS,   9,     "the CD-Key")
        maps["te_industrial"] =    RTCWMap("te_industrial",    "Industrial",  self.map_announce["te_industrial"],    self.G_AXIS,   self.G_ALLIES, 8,     "the Supply Documents")
        maps["anymap"] =           RTCWMap("anymap",           "anymap",      self.map_announce["anymap"],           self.G_ALLIES, self.G_AXIS,   10,    "")
        
        
        #each map will have additional objective likes related to stoled and returned objectives
        for mapname, map_ in maps.items():
            if(map_.objname == "the War Documents"):
                continue #throw away lines with "the War Documents" because they are shared between several maps (beach, frost, chateau)
            map_.announcements.append([self.D_RETURN, map_.defense + " have returned " + map_.objname + "!"])
            map_.announcements.append([self.O_STEAL,  map_.offense + " have stolen "   + map_.objname + "!"])
            map_.announcements.append([self.O_STEAL,  map_.offense + " have lost "   + map_.objname + "!"])
        self.maps = maps
    
    def transpose_by_obj(self):
        objectives = {}
        for m in self.maps:
            for o in self.maps[m].announcements:
                objectives[o[1]] = [o[0],m]
        return objectives