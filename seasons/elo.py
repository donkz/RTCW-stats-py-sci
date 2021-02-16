# -*- coding: utf-8 -*-
"""
credit to https://github.com/PredatH0r/XonStat/blob/master/xonstat/elo.py

ELO algorithm to calculate player ranks

"""
import os
from datetime import datetime
import logging
import math
#import random
#import sys
import pandas as pd


log = logging.getLogger(__name__)

class PlayerElo(object):
    def __init__(self, player_id=None, game_type_cd=None, elo=None):
        self.create_dt = datetime.utcnow()
        self.player_id = player_id
        self.game_type_cd = game_type_cd
        self.elo = 100.0;
        self.g2_r = None
        self.g2_rd = None
        self.score = 0
        self.games = 0
        self.g2_games = 0
        self.g2_dt = None
        self.b_r = None
        self.b_rd = None
        self.b_games = 0
        self.b_dt = None
        
    def __repr__(self):
        return "<PlayerElo(pid=%s, gametype=%s, elo=%s, games=%s)>" % (self.player_id, self.game_type_cd, self.elo, self.games)

    def to_dict(self):
        return {
          'player_id':self.player_id, 'game_type_cd':self.game_type_cd, 'elo':self.elo, 'games':self.games,
          'g2_r':self.g2_r, 'g2_rd':self.g2_rd,  "g2_games":self.g2_games, "g2_dt":self.g2_dt,
          'b_r':self.b_r, 'b_rd':self.b_rd,  "b_games":self.b_games, "b_dt":self.b_dt
        }


class EloParms:
    def __init__(self, global_K = 15, initial = 100, floor = 100, logdistancefactor = math.log(10)/float(400), maxlogdistance = math.log(10)):
        self.global_K = global_K
        self.initial = initial
        self.floor = floor
        self.logdistancefactor = logdistancefactor
        self.maxlogdistance = maxlogdistance


class KReduction:
    #KREDUCTION = KReduction(900, 75, 0.5, 5, 15, 0.2)
    def __init__(self, fulltime, mintime, minratio, games_min, games_max, games_factor):
        self.fulltime = fulltime
        self.mintime = mintime
        self.minratio = minratio
        self.games_min = games_min
        self.games_max = games_max
        self.games_factor = games_factor

    def eval(self, mygames, mytime, matchtime):
        if mytime < self.mintime:
            return 0
        if mytime < self.minratio * matchtime:
            return 0
        if mytime < self.fulltime:
            k = mytime / float(self.fulltime)
        else:
            k = 1.0
        if mygames >= self.games_max:
            k *= self.games_factor
        elif mygames > self.games_min:
            k *= 1.0 - (1.0 - self.games_factor) * (mygames - self.games_min) / float(self.games_max - self.games_min)
        #print("Elo.KReduction.eval: " + str(k))
        return k


def process_games(stats): 
    df = stats[stats["round_num"]==2]
    df = df.reset_index()[["index", "Kills","round_time", "game_result", "round_guid", "Panzerfaust","Sniper", "Artillery", "Airstrike", "match_date"]]
    df ["Killpoints"] = df["Kills"] - df["Panzerfaust"]*.3 -df["Sniper"]*.3 - df["Artillery"]*.3 - df["Airstrike"]*.3
    df = df.sort_values("match_date")
    df["games"] = df.groupby('index').cumcount()+1
    
    elo_dict ={}
    lines = []
    matches = df["round_guid"].unique()
    gameno = 0
    for guid in matches:
        gameno +=1
        b = df[df["round_guid"]==guid].copy()
        b["rank"] = b["Killpoints"].rank(method="dense", ascending=True, na_option='bottom')
        b["rank2"] = b["rank"]
        b.loc[b[b["game_result"] == "LOST"].index,"rank2"] = b["rank"] - 1.5
        c = b.reset_index()
        
        #print(c.sort_values(by="rank2"))
        
        player_score_df = c[["index","rank2","round_time","games"]].copy()
        player_score_df.columns = ["player","rank2","duration", "games"]
        elos = process_elos(player_score_df, elo_dict)
        for p in elos:
            lines.append([gameno, elos[p].player_id, elos[p].elo, elos[p].games])

        for e in elos:
            elo_dict[e] = elos[e]

    elo_report = pd.DataFrame(lines)
    elo_report.columns = ["gameno", "player", "elo", "playergame"]
    elo_report.to_clipboard(sep=",", index=False)
    output_dest = r"..\data\elo\elo.csv"
    print("Writing elo.csv to: " + os.path.abspath(output_dest))
    elo_report.to_csv(output_dest, index=False)
    
    #print
    array = []
    for p in elo_dict:
        array.append([p, elo_dict[p].elo])
    df = pd.DataFrame(array)
    df.columns = ["player","elo"]
    #print(df.sort_values(by="elo", ascending = False))
    
    return df.sort_values(by="elo", ascending = False)
       
    
def process_elos(player_score_df, elo_dict):
    
    duration = player_score_df["duration"].max()
    
    scores = {}
    alivetimes = {}
    games = {}
    
    #for (p,s,a) in session.query(PlayerGameStat.player_id,PlayerGameStat.score, PlayerGameStat.alivetime).filter(PlayerGameStat.game_id==game.game_id).filter(PlayerGameStat.alivetime > timedelta(seconds=0)).filter(PlayerGameStat.player_id > 2).all()
    for p in player_score_df.itertuples():
                # scores are per second
                    scores[p.player] = p.rank2/float(p.duration)
                    alivetimes[p.player] = p.duration
                    games[p.player] = p.games
                    
                    
    player_ids = scores.keys()

    elos = {}
    #test
#    player_elo_df = player_score_df[["player","kills"]]
#    player_elo_df["elo"] = player_score_df[["kills"]]*50 + 1200
#    player_elo_df.drop(["kills"], axis = 1, inplace=True)
    #end of test
    
    #for e in session.query(PlayerElo).filter(PlayerElo.player_id.in_(player_ids)).filter(PlayerElo.game_type_cd==game_type_cd).all()
    #for e in player_elo_df.itertuples(index=False):
    #            elos[e.player] = PlayerElo(e.player, game_type_cd=None, elo=e.elo)
    
    for p in player_ids:
        if p in elo_dict:
            elos[p] = elo_dict[p]
        

    # ensure that all player_ids have an elo record
    for pid in player_ids:
        if pid not in elos.keys():
            elos[pid] = PlayerElo(pid, None, ELOPARMS.initial)

    for pid in list(player_ids):
        elos[pid].k = KREDUCTION.eval(games[pid], alivetimes[pid], duration)
        if elos[pid].k == 0:
            del(elos[pid])
            del(scores[pid])
            del(alivetimes[pid])
    
    #print(elos)
    elos = update_elos(elos, scores, ELOPARMS)
    
    #print("\nScores\n")
    #print(player_score_df.sort_values(by="kills", ascending=False))
    #print("\nElos\n")
    #print(pd.DataFrame(elos.items()))
    
    #print(elos)

    # add the elos to the session for committing
    #for e in elos:
        #session.add(elos[e])
        
    return elos


def update_elos(elos, scores, ep):
    if len(elos) < 2:
        return elos

    pids = list(elos.keys())

    eloadjust = {}
    for pid in pids:
        eloadjust[pid] = 0.0

    for i in range(0, len(pids)):
        ei = elos[pids[i]]
        for j in range(i+1, len(pids)):
            ej = elos[pids[j]]
            si = scores[ei.player_id]
            sj = scores[ej.player_id]

            # normalize scores
            ofs = min(0, si, sj)
            si -= ofs
            sj -= ofs
            if si + sj == 0:
                si, sj = 1, 1 # a draw

            # real score factor
            scorefactor_real = si / float(si + sj)

            # duels are done traditionally - a win nets
            # full points, not the score factor
            
            #if game.game_type_cd == 'duel':
            if False:
                # player i won
                if scorefactor_real > 0.5:
                    scorefactor_real = 1.0
                # player j won
                elif scorefactor_real < 0.5:
                    scorefactor_real = 0.0
                # nothing to do here for draws

            # expected score factor by elo
            elodiff = min(ep.maxlogdistance, max(-ep.maxlogdistance,
                (float(ei.elo) - float(ej.elo)) * ep.logdistancefactor))
            scorefactor_elo = 1 / (1 + math.exp(-elodiff))

            # initial adjustment values, which we may modify with additional rules
            adjustmenti = scorefactor_real - scorefactor_elo
            adjustmentj = scorefactor_elo - scorefactor_real

#            print("Player i: {0}".format(ei.player_id))
#            print("Player i's K: {0}".format(ei.k))
#            print("Player j: {0}".format(ej.player_id))
#            print("Player j's K: {0}".format(ej.k))
#            print("Scorefactor real: {0}".format(scorefactor_real))
#            print("Scorefactor elo: {0}".format(scorefactor_elo))
#            print("adjustment i: {0}".format(adjustmenti))
#            print("adjustment j: {0}".format(adjustmentj))

            if scorefactor_elo > 0.5:
            # player i is expected to win
                if scorefactor_real > 0.5:
                # he DID win, so he should never lose points.
                    adjustmenti = max(0, adjustmenti)
                else:
                # he lost, but let's make it continuous (making him lose less points in the result)
                    adjustmenti = (2 * scorefactor_real - 1) * scorefactor_elo
            else:
            # player j is expected to win
                if scorefactor_real > 0.5:
                # he lost, but let's make it continuous (making him lose less points in the result)
                    adjustmentj = (1 - 2 * scorefactor_real) * (1 - scorefactor_elo)
                else:
                # he DID win, so he should never lose points.
                    adjustmentj = max(0, adjustmentj)

            eloadjust[ei.player_id] += adjustmenti
            eloadjust[ej.player_id] += adjustmentj

    elo_deltas = {}
    for pid in pids:
        old_elo = float(elos[pid].elo)
        new_elo = max(float(elos[pid].elo) + eloadjust[pid] * elos[pid].k * ep.global_K / float(len(elos) - 1), ep.floor)
        elo_deltas[pid] = new_elo - old_elo
        
        debug_player = "kek"
        if debug_player in elo_deltas:
            print(debug_player + " elo delta: " + str(elo_deltas[debug_player]))

        elos[pid].elo = new_elo
        elos[pid].games += 1
        elos[pid].update_dt = datetime.utcnow()

        #log.debug("Setting Player {0}'s Elo delta to {1}. Elo is now {2} (was {3}).".format(pid, elo_deltas[pid], new_elo, old_elo))
        #print("Setting Player {0}'s Elo delta to {1}. Elo is now {2} (was {3}).".format(pid, elo_deltas[pid], new_elo, old_elo))

    #save_elo_deltas(game, session, elo_deltas)

    return elos


def save_elo_deltas(game, session, elo_deltas):
    """
    Saves the amount by which each player's Elo goes up or down
    in a given game in the PlayerGameStat row, allowing for scoreboard display.
    elo_deltas is a dictionary such that elo_deltas[player_id] is the elo_delta
    for that player_id.
    """
    pgstats = {}
    #for pgstat in session.query(PlayerGameStat).filter(PlayerGameStat.game_id == game.game_id).all():
    for pgstat in session.query(PlayerGameStat).\
            filter(PlayerGameStat.game_id == game.game_id).\
            all():
                pgstats[pgstat.player_id] = pgstat

    for pid in elo_deltas.keys():
        try:
            pgstats[pid].elo_delta = elo_deltas[pid]
            session.add(pgstats[pid])
        except:
            log.debug("Unable to save Elo delta value for player_id {0}".format(pid))


# parameters for K reduction
# this may be touched even if the DB already exists
#KREDUCTION = KReduction(600, 120, 0.5, 0, 32, 0.2)
KREDUCTION = KReduction(900, 75, 0.5, 5, 15, 0.2)

# parameters for chess elo
# only global_K may be touched even if the DB already exists
# we start at K=200, and fall to K=40 over the first 20 games
ELOPARMS = EloParms(global_K = 200)