import random

class AwardStruct:
      
    def __init__(self, column_title, award_verbiage, max_items_num):
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


class AwardText:
        
    awards = {}
    awards["FirstInDoor"] = AwardStruct("First killer or victim of the round (per round)",
                                        ["{people}! Good job leading your team with getting in the door first {statistic} times per round!",
                                         "{people} wait{multiplier} for no-one with {statistic} of first kills/deaths per round played.",
                                         "{people} drew the first blood {statistic} of the rounds!"],
                                         3)
    awards["Blownup"]     = AwardStruct("Exploded by grenade, AS, dynamite",
                                        ["{people} ... watch your step and try not to walk into explosives {statistic} times again!",
                                         "{people}, see that smoke? Don't go there! Exploded {statistic} times!"],
                                         3)
    awards["Panzed"]      = AwardStruct("Died to panzer",
                                        ["{people} attract{multiplier} panzer like a magnet ({statistic} times)!",
                                         "{people} take{multiplier} one-too-many for the team dying {statistic} times to panzer :(",
                                         "{people} get{multiplier} something to complain about. Died to panzer {statistic} times!"],
                                         2)
    awards["KillStreak"]  = AwardStruct("Kills without dying",
                                         ["{people} need{multiplier} to chill with the {statistic} killsreak...",
                                         "{people} manage{multiplier} to get {statistic} kills without dying!",
                                         "{people} went on a rampage with {statistic} kills without dying!"],
                                         3)
    awards["Deathroll"]   = AwardStruct("Consecutive deaths without a kill",
                                         ["{people} need{multiplier} to take a breather and try not to die {statistic} times in a row!",
                                         "Tell {people} to regain their composure. {statistic} deathstreak isn't helping anyone."],
                                         3)
    awards["Kills"]       = AwardStruct("Kills in the entire match",
                                         ["{people} killed the most people in this event - {statistic}!",
                                         "{people} enjoy{multiplier} a fragtastic time with {statistic} kills!",
                                         "{people} got the KrisOfWin Slaughterhouse Award with {statistic} frags!"],
                                         3)
    awards["KDR"]         = AwardStruct("Kills to enemy deaths ratio",
                                         ["{people} dance with the devil with the highest KDR ratios",
                                         "{people} get{multiplier} the good old terminator award for the match with highest KDR"],
                                         4) #chaces are it's always one
    awards["Caps"]        = AwardStruct("Captured objective on offense",
                                         ["not used at the moment",
                                         "not used at the moment"],
                                         8)
    awards["Holds"]       = AwardStruct("Held the time on defense",
                                         ["not used at the moment",
                                         "not used at the moment"],
                                         8)
    awards["AdjScore"]    = AwardStruct("Objective Score Per Round (Total minus kills, TKs, and deaths)",
                                         ["{people} like{multiplier} to work for the team and bring{multiplier} impressive {statistic} points per round!"],
                                         3)
    awards["Pack5"]       = AwardStruct("5 kills without dying",
                                         ["not used at the moment",
                                         "not used at the moment"],
                                         3)
    awards["RankPts"]     = AwardStruct("Total rank for the match",
                                         ["<br/><b>MVP</b> of the night goes to {people}! You did it all with best rank sum of {statistic}!!!"],
                                         4)
    awards["Wins"]        = AwardStruct("Wins in a single AB match",
                                         ["{people} know{multiplier} how to win and got {statistic} wins to show for it!",
                                         "{people} take{multiplier} the cake with {statistic} wins!",
                                         "{people} keep{multiplier} eyes on the prize with {statistic} wins!"],
                                         8)
    awards["Win%"]        = AwardStruct("Winning ratio",
                                         ["{people} show{multiplier} up to win {statistic} of his games!",
                                          "Who's the conductor of the pain train? Ask {people} with their {statistic} winning percentage."],
                                         8)
    awards["MegaKill"]    = AwardStruct("Number of kills player done at once",
                                         ["Watch out for {people} mowing others down in batches of {statistic}",
                                         "The impressive megakill{multiplier} by {people}. {statistic} kills at once!",
                                         "{people} got to be one-man army with {statistic} kills at once!"],
                                         3)
    awards["Panzer"]      = AwardStruct("Number of kills using panzerfaust (5 pts penalty)",
                                         ["{people} get{multiplier} the classic Panzer-Lama Award with {statistic} panzer kills!"],
                                         2)
    awards["Smoker"]      = AwardStruct("Artillery and Airstrike kills (3 pts penalty)",
                                         ["{people} get{multiplier} the award for The Best Indian Smoke-Messenger with {statistic} artillery and airstrike kills!"],
                                         4)
    awards["Sniper"]      = AwardStruct("Sniper kills (2 pts penalty)",
                                         ["{people} like{multiplier} to do it from afar with {statistic} sniper kills.",
                                         "{people} raked {statistic} sniper kills while everyone else was frontlining."],
                                         2)
    awards["KPM"]         = AwardStruct("Kills per minute",
                                         ["{people} showing how to kill with {statistic} kills per minute played!",
                                         "{people} - top killer{multiplier} per pound (minute) with {statistic} kills per minute."],
                                         2)
    awards["Minutes"]     = AwardStruct("Minutes played",
                                         ["{people} thanks for sticking around the longest - {statistic} minutes!",
                                         "{people} - hold{multiplier} down the house with {statistic} minutes in action!"],
                                         20)
    awards["Rounds"]    = AwardStruct("Rounds played",
                                     [],
                                     20)
    