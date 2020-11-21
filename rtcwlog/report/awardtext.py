import random

class AwardStruct:
      
    def __init__(self, award_name, column_title, award_verbiage, max_items_num):
         self.award_name = award_name
         self.column_title = column_title      #kills by panzer
         self.award_verbiage = award_verbiage    #["%s need %s to xyz %s times!","%s idioma xyz %s times!"]
         self.max_items_num = max_items_num  #how many players to display in an award line

    def render(self, people, statistic):
        """ 
        The function chooses a random award description and plugs in people names and statistic number
  
        Parameters: 
            people (list): People to be plugged into award text
            statistic (number): Number to be plugged into award text
            
        Returns: 
            string: Award string like "Kek killed pek 50 times."
        """
        multiplier = "" if len(people) > 1 else "s"
        peoplestring = "<b>" + ", ".join(people[0:self.max_items_num]) + "</b>"
            
        
        values = {
                "people" : peoplestring,
                "multiplier" : multiplier,
                "statistic" : "<b>" + str(statistic) + "</b>"
                }
        return random.choice(self.award_verbiage).format(**values) + "<br/>"
    
    def get_award_row(self, people, statistic):
        """ 
        The function chooses a random award description and plugs in people names and statistic number
  
        Parameters: 
            people (list): People to be plugged into award text
            statistic (number): Number to be plugged into award text
            
        Returns: 
            touple to plug into award table row
        """
        multiplier = "" if len(people) > 1 else "s"
        peoplestring = ", ".join(people[0:self.max_items_num])

            
        
        values = {
                "multiplier" : multiplier,
                "statistic" : str(statistic)
                }
        return (self.award_name, peoplestring, random.choice(self.award_verbiage).format(**values))


class AwardText:
        
    awards = {}
    awards["FirstInDoor"] = AwardStruct("First in door",
                                        "First killer or victim of the round (per round)",
                                        ["Good job leading your team with getting in the door first {statistic} times per round!",
                                         "Wait{multiplier} for no-one with {statistic} of first kills/deaths per round played.",
                                         "Drew the first blood {statistic} of the rounds!"],
                                         3)
    awards["Blownup"]     = AwardStruct("Cannon fodder",
                                        "Exploded by grenade, AS, dynamite",
                                        [" ... watch your step and try not to walk into explosives {statistic} times again!",
                                         "See that smoke? Don't go there! Exploded {statistic} times!"],
                                         3)
    awards["Panzed"]      = AwardStruct("Panzer magnet",
                                        "Died to panzer",
                                        ["Attract{multiplier} panzer like a magnet ({statistic} times)!",
                                         "Take{multiplier} one-too-many for the team dying {statistic} times to panzer :(",
                                         "Get{multiplier} something to complain about. Died to panzer {statistic} times!"],
                                         2)
    awards["KillStreak"]  = AwardStruct("Undying",
                                        "Kills without dying",
                                         ["Need{multiplier} to chill with the {statistic} killsreak...",
                                         "Manage{multiplier} to get {statistic} kills without dying!",
                                         "Went on a rampage with {statistic} kills without dying!"],
                                         3)
    awards["Deathroll"]   = AwardStruct("Deathroll",
                                        "Consecutive deaths without a kill",
                                         ["Need{multiplier} to take a breather and try not to die {statistic} times in a row!",
                                         "Regain your composure. {statistic} deathstreak isn't helping anyone."],
                                         3)
    awards["Kills"]       = AwardStruct("Most kills",
                                        "Kills in the entire match",
                                         ["Killed the most people in this event - {statistic}!",
                                         "Enjoy{multiplier} a fragtastic time with {statistic} kills!",
                                         "Got the KrisOfWin Slaughterhouse Award with {statistic} frags!"],
                                         3)
    awards["KDR"]         = AwardStruct("Terminator",
                                        "Kills to enemy deaths ratio",
                                         ["Dance with the devil with the highest KDR ratios",
                                         "Get{multiplier} the good old terminator award for the match with highest KDR{multiplier}"],
                                         4) #chaces are it's always one
    awards["Caps"]        = AwardStruct("Delivery",
                                        "Captured objective on offense",
                                         ["not used at the moment",
                                         "not used at the moment"],
                                         8)
    awards["Holds"]       = AwardStruct("Brick Wall",
                                        "Held the time on defense",
                                         ["not used at the moment",
                                         "not used at the moment"],
                                         8)
    awards["AdjScore"]    = AwardStruct("Team player",
                                        "Objective Score Per Round (Total minus kills, TKs, and deaths)",
                                         ["Like{multiplier} to work for the team and bring{multiplier} impressive {statistic} points per round!"],
                                         3)
    awards["Pack5"]       = AwardStruct("Pack5",
                                        "5 kills without dying",
                                         ["not used at the moment",
                                         "not used at the moment"],
                                         3)
    awards["RankPts"]     = AwardStruct("MVP",
                                        "Total rank for the match",
                                         ["You did it all with best rank sum of {statistic}!!!"],
                                         4)
    awards["Wins"]        = AwardStruct("Winner",
                                        "Wins in a single AB match",
                                         ["Know{multiplier} how to win and got {statistic} wins to show for it!",
                                         "Take{multiplier} the cake with {statistic} wins!",
                                         "Keep{multiplier} eyes on the prize with {statistic} wins!"],
                                         8)
    awards["Win%"]        = AwardStruct("Winner%",
                                        "Winning ratio",
                                         ["Show{multiplier} up to win {statistic} of his games!",
                                          "Conductor of the pain train with {statistic} winning percentage."],
                                         8)
    awards["MegaKill"]    = AwardStruct("Mega Kill",
                                        "Number of kills player done at once",
                                         ["Mowing others down in batches of {statistic}",
                                         "The impressive megakill{multiplier}. {statistic} kills at once!",
                                         "One-man army with {statistic} kills at once!"],
                                         3)
    awards["Panzer"]      = AwardStruct("Boomstick",
                                        "Number of kills using panzerfaust (3 pts penalty)",
                                         ["Get{multiplier} the classic Panzer-Lama Award with {statistic} panzer kills!"],
                                         2)
    awards["Smoker"]      = AwardStruct("Puff and stuff",
                                        "Artillery and Airstrike kills (2 pts penalty)",
                                         ["Get{multiplier} the award for The Best Indian Smoke-Messenger with {statistic} artillery and airstrike kills!"],
                                         4)
    awards["Sniper"]      = AwardStruct("Marksman",
                                        "Sniper kills (2 pts penalty)",
                                         ["Like{multiplier} to do it from afar with over {statistic} sniper kills.",
                                         "Raked over {statistic} sniper kills while everyone else was frontlining."],
                                         2)
    awards["Tapout"]      = AwardStruct("Tapout",
                                        "High suicide/deaths ratio (3 pts penalty)",
                                         ["Come{multiplier} back fresh. {statistic} of all deaths are suicides.",
                                         "Tap{multiplier} out at the slightest sign of danger."],
                                         2)
    awards["KPM"]         = AwardStruct("Destroyer",
                                        "Kills per minute",
                                         ["Showing how to kill with {statistic} kills per minute played!",
                                         "Top killer{multiplier} per pound (minute) with over {statistic} kills per minute."],
                                         2)
    awards["Minutes"]     = AwardStruct("Veteran",
                                        "Minutes played",
                                         ["Thanks for sticking around the longest - {statistic} minutes!",
                                         "Hold{multiplier} down the house with {statistic} minutes in action!"],
                                         20)
    awards["Rounds"]      = AwardStruct("",
                                        "Rounds played",
                                        [],
                                        20)
    awards["elo"]         = AwardStruct("",
                                        "ELO Score for the year",
                                        [],
                                        20)
    