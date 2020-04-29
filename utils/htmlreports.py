from bs4 import BeautifulSoup
from bs4 import Tag

from time import gmtime
from time import strftime

from textsci.awards import Awards 
from textsci.matchstats import MatchStats
from constants.logtext import Const 
from constants.awardtext import AwardText

from datetime import datetime
import hashlib

import time as _time

class HTMLReport:
    
    def __init__(self, result):
        
        time_start_html_init = _time.time()
        
        self.empty = False
        self.debug_time = False
        
        if result is None or len(result) == 0:
            print("[!] Result passed into HTMLReport is empty. HTMLReport did not load any data.")
            self.empty = True
            self.match_date = ""
            return
        
        self.award_info = AwardText()
        self.awards = Awards(result)
        matchstats = MatchStats()
        
        self.award_stats = self.awards.collect_awards()

        time_mid_html_init = _time.time()
        if self.debug_time: print ("Time to init and load awards is " + str(round((time_mid_html_init - time_start_html_init),2)) + " s")
           
        
        self.award_stats_html_table = self.awards_to_html(self.award_stats)
        self.award_megakills_html_table = self.megakills_to_html(self.award_stats[2])
        
        self.metrics = matchstats.match_metrics(result)
        
        self.match_time = self.match_date = match_datetime = self.metrics["match_time"]
        match_datetime_arr = match_datetime.split(" ")
        if len(match_datetime_arr) > 1:
            self.match_date = match_datetime_arr[0]
            self.match_time = match_datetime_arr[1]
        
        match_results = matchstats.table_match_results(result)
        self.match_results_html_table = self.match_results_to_html(match_results)
        
        basic_stats = matchstats.table_base_stats(result)
        self.basic_stats_html_table = self.all_stats_to_html(basic_stats)
        
        weapon_stats = matchstats.table_weapon_counts(result)
        self.weapon_stats_html_table = self.weapons_to_html(weapon_stats)
        
        
        
        self.award_summaries_html_table = self.award_summaries_to_html(self.award_stats)
        
        #kill_matrix_stats = matchstats.table_kill_matrix(result)
        #self.kill_matrix_stats_html_table = self.kill_matrix_to_html(kill_matrix_stats)
        
        top_feuds = matchstats.table_top_feuds(result)
        self.feuds_html_table = self.feuds_to_html(top_feuds)
        
        renames = matchstats.table_renames(result)
        if renames[0] is None:
            self.renames_html_table = None
        else:   
            self.renames_html_table = self.renames_to_html(renames)
        
        time_end_html_init = _time.time()
        if self.debug_time: print ("Time to build html tables " + str(round((time_end_html_init - time_mid_html_init),2)) + " s")
            

    
    def report_to_html(self,folder="", filenoext=""):
        r"""
        Write the awards into an HTML file
        
        Parameters
        ----------
        folder : str, default empty, resolves to current working directory
            Folder path where to place the report
        filenoext : str, default empty,  resolves to stats-date-hash.html
            Output file name without extension.
        
        Returns
        -------
        Tuple of (str,str) or (None,None) where:
            [0] is path to file
            [1] is filename
        
        Examples
        --------
        >>> html_report = HTMLReport(result)
           Initialization of html_report and all loaded information (awards, metrics, etc.)
        >>> html_report.report_to_html()
           Writes file stats-2020-04-02-58ab.html to current working directory
        >>> html_report.report_to_html(folder="/tmp/") #linux
           Writes file stats-2020-04-02-58ab.html to current working directory + /tmp/
        >>> html_report.report_to_html(folder="C:\\a\\") #Windows
        >>> html_report.report_to_html(folder="C:/a/")   #Windows
           Writes file stats-2020-04-02-58ab.html to C:\a\stats-2020-01-13-f04d.html
        >>> html_report.report_to_html(folder="/tmp/", filenoext = "file-kek")
           Writes file /tmp/file-kek.html  
        """
        outpath = ""
        nothing = (None, None)
        out_file_name = "stats-" + self.match_date + "-" + hashlib.md5(str(datetime.now()).encode()).hexdigest()[0:4] + ".html"
        if folder != "":
            outpath += folder
        if filenoext != "":
            out_file_name = filenoext + ".html"
            outpath += out_file_name
        else:
            outpath = outpath + out_file_name        
        
        time_start_html_write = _time.time()
        
        if self.empty:
            print("[!] Nothing to write.")
            return nothing

        soup = BeautifulSoup("","lxml")
        
        #<html>
        html = Tag(soup, name = "html")
        
        #<head>
        head = Tag(soup, name = "head")
        
        #css and libraries
        link = Tag(soup, name = "link")
        link["rel"] = "stylesheet"
        link["href"] = "https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css"
        script = Tag(soup, name = "script")
        script["src"] = "https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"
        script2 = Tag(soup, name = "script")
        script2["src"] = "https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"
        style = Tag(soup, name = "style")
        
        soup.append(html)
        soup.html.append(head)
        soup.head.append(link)
        soup.head.append(script)
        soup.head.append(script2)
        soup.head.append(style)
        soup.style.append(self.style_css)
        
        #<body>    
        body = Tag(soup, name = "body")
        soup.html.append(body)
        soup.body.append(self.insert_header("Log file for a match from " + self.match_date,2))
        soup.body.append(self.summary_text())
        soup.body.append(self.insert_header("Results",2))
        soup.body.append(self.insert_toggle("results"))
        soup.body.append(self.match_results_html_table)
        soup.body.append(self.insert_header("Awards",2))
        soup.body.append(self.insert_html(self.award_summaries_html_table))
        soup.body.append(self.insert_header("Award details",3))
        soup.body.append(self.insert_text("Minimum rounds to be ranked 20% - " + str(self.awards.minrounds) + " or 40"))
        soup.body.append(self.insert_toggle("awards"))
        soup.body.append(self.award_stats_html_table)
        soup.body.append(self.insert_header("Base stats",2))
        soup.body.append(self.insert_toggle("allstats"))
        soup.body.append(self.basic_stats_html_table)
        soup.body.append(self.insert_header("Weapon stats",2))
        soup.body.append(self.insert_toggle("weapons"))
        soup.body.append(self.weapon_stats_html_table)
        #soup.body.append(self.insert_header("Kill matrix",2))
        #soup.body.append(self.kill_matrix_stats_html_table)
        
        soup.body.append(self.insert_header("Top Feuds",2))
        soup.body.append(self.insert_text("The most numerous head-to-head encounters of the match"))
        soup.body.append(self.insert_toggle("feuds"))
        soup.body.append(self.feuds_html_table)
        soup.body.append(self.insert_header("MegaKills",2))
        soup.body.append(self.insert_toggle("megakills"))
        soup.body.append(self.insert_text("Kills that happened consequently, all at once"))
        soup.body.append(self.award_megakills_html_table)
        if self.renames_html_table is not None:
            soup.body.append(self.insert_header("Player rename history",2))
            soup.body.append(self.insert_toggle("renames"))
            soup.body.append(self.renames_html_table)
        
        #jquery scripts
        script_jq = Tag(soup, name = "script")
        script_jq["type"] = "text/javascript"
        script_jq.append(self.jquery_sort)
        soup.body.append(script_jq)
        #end of html report
        
        try:
            html_file = open(outpath,"w")
            html_file.write(soup.prettify())
            html_file.close() 
        
            time_end_html_write = _time.time()
            if self.debug_time: print ("Time to write html is " + str(round((time_end_html_write - time_start_html_write),2)) + " s")
            print("[ ] Wrote html report to " + html_file.name)
        except FileNotFoundError as err:
            print("[!] Could not write to " + outpath + " Error: ", err)
            return nothing
        except:
            print("[x] Could not write to " + outpath + " Unhandled error.")
            pass
        return (outpath, out_file_name)
            
        
    def insert_header(self,text, size):
        soup = BeautifulSoup("","lxml")
        header1 = Tag(soup, name = "h" + str(size))
        header1["class"] = "header"
        header1.append(text)
        soup.append(header1)
        return soup
    
    def insert_text(self, content):
        soup = BeautifulSoup("","lxml")
        text = Tag(soup, name = "p")
        text["class"]="text"
        
        text.append(content)
        soup.append(text)
        return soup
    
    def insert_html(self, content):
        soup = BeautifulSoup("","lxml")
        wrap = Tag(soup, name = "p")
        wrap["class"]="text"
        wrap.append(BeautifulSoup(content, 'html.parser'))
        soup.append(wrap)
        return soup
    
    def insert_toggle(self, toggle_div):
        soup = BeautifulSoup("","lxml")
        link = Tag(soup, name = "a")
        link["href"] = "#"
        link["id"] = toggle_div
        link.append("Hide/Show")
        soup.append(link)
        return soup
    
    def summary_text(self):
        content = "Match started at %s. Total of %s players played %s rounds on %s maps and murdered eachother %s times!" % (self.match_time, self.metrics["players_count"] , self.metrics["rounds_count"], self.metrics["maps_count"], self.metrics["kill_sum"])
        soup = self.insert_text(content)        
        return soup
        
    def award_summaries_to_html(self,award_stats):
        awardsdf = award_stats[0]
        content = ""
        
        rank_cols, ranked_cols, unranked_cols, inverse_ranked_cols = self.awards.ranked_column_types()
        #print(rank_cols, ranked_cols, unranked_cols, inverse_ranked_cols)
        for col in rank_cols:
            col_value  = col.replace("_rank","")
            if col in inverse_ranked_cols:
                if (awardsdf[col].max() == 0):
                    continue #do nothing if no one achieved anything
                result = awardsdf.loc[awardsdf[awardsdf[col] == awardsdf[col].max()].index, col_value]
            elif col in ranked_cols:
                if (awardsdf[col].min() == 5):
                    continue #do nothing if no one achieved anything
                result = awardsdf.loc[awardsdf[awardsdf[col] == awardsdf[col].min()].index, col_value]
            elif col in unranked_cols:
                result = awardsdf.loc[awardsdf[col_value] == awardsdf[col_value].max(), col_value]
            elif col == "RankPts_rank":
                "We'll give it a pass this time"
            else:
                print("[!] Warning: something left over in awards table: " + col)
                
            try:
                if col_value =="Rounds":
                    "Nothing"
                else:
                    content += self.award_info.awards[col_value].render(result.index.values, result.values[0])
            except:
                print("[!] Summary award failed!")
                print(col_value in self.award_info.awards.keys())
                import sys
                print(sys.exc_info())
                print("Columns being processed: " + col_value + " and " + col)
                print("Award dataframe:")
                print(awardsdf[[col_value,col]])
                
        return content
    
    #feuds table
    def feuds_to_html(self,top_feuds):
        feuds = top_feuds[0]
        columns = top_feuds[1]
        
        soup = BeautifulSoup("","lxml")        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        table["id"] = "divfeuds"
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        for col in columns:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
        for index, row in feuds.iterrows():
            tr = Tag(soup, name = "tr")
            td = Tag(soup, name = "td")
            for col in feuds.columns:
                td = Tag(soup, name = "td")
                td.insert(1, (str(row[col])))
                tr.append(td)
                table.append(tr)
        return soup

    
    def awards_to_html(self,award_stats):
        awardsdf = award_stats[0]
        columns = award_stats[1]
        
        soup = BeautifulSoup("","lxml")
        metrics = [name for name in columns if "rank" not in name]
        #ranks = [name for name in awardsdf.columns if "rank" in name]
        cols = ["Player"] + metrics
        
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        table["id"] = "divawards"
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        medals = {1 : "gold", 2 : "silver", 3: "bronze"}
        panzmedals = {5 : "red5", 4 : "red4", 3: "red3", 2 : "red2", 1 : "red1"}
        ltmedals = {3 : "red3", 2 : "red2", 1: "red1"}
        tapoutmedals = {3 : "red3", 2 : "red2", 1: "red1"}
        snipermedals = {2 : "red2", 1 : "red1"}
        
        for col in cols:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
            th["class"] = "awardheader"
            if(col in self.award_info.awards.keys()):
                th["title"] = self.award_info.awards[col].column_title
        for index, row in awardsdf.iterrows():
            tr = Tag(soup, name = "tr")
            td = Tag(soup, name = 'td')
            td.insert(1, index)
            tr.append(td)
            for col in metrics:
                td = Tag(soup, name = 'td')
                value = str(row[col]).replace("-","")
                td.insert(1, value)      
                td["title"] =  "Rank:" + str(row[col + "_rank"])
                if col == "Panzer":
                    td["class"] = panzmedals.get(row[col + "_rank"],"norank")
                elif col == "Smoker":
                    td["class"] = ltmedals.get(row[col + "_rank"],"norank")
                elif col == "Sniper":
                    td["class"] = snipermedals.get(row[col + "_rank"],"norank")
                elif col == "Tapout":
                    td["class"] = tapoutmedals.get(row[col + "_rank"],"norank")
                elif str(row[col])[0] == "-":
                    td["class"] = "nocount"
                else:
                    td["class"] = medals.get(row[col + "_rank"],"norank")
                tr.append(td)
                table.append(tr)
        return soup
        
    #Weapons stats <table>
    def weapons_to_html(self,weapon_stats):
        weapondf = weapon_stats[0]
        columns = weapon_stats[1]
        soup = BeautifulSoup("","lxml")
        metrics = [name for name in columns if "rank" not in name]
        #ranks = [name for name in awardsdf.columns if "rank" in name]
        cols = ["Player"] + metrics
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        table["id"] = "divweapons"
        soup.append(table)
        
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        medals = {1 : "gold", 2 : "silver", 3: "bronze"}
        
        for col in cols:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
        for index, row in weapondf.iterrows():
            tr = Tag(soup, name = "tr")
            td = Tag(soup, name = 'td')
            td.insert(1, index)
            tr.append(td)
            for col in metrics:
                td = Tag(soup, name = 'td')
                td.insert(1, str(row[col]).replace(".0",""))
                td["class"] = medals.get(row[col + "_rank"],"norank")
                tr.append(td)
                table.append(tr)    
        return soup
    
    #Kill matrix <table>
    def kill_matrix_to_html(self,kill_matrix_stats):
        kill_matrix = kill_matrix_stats[0]
        #columns = kill_matrix_stats[1]
        columns = kill_matrix.columns
        
        soup = BeautifulSoup("","lxml")
        metrics = [name for name in columns if "rank" not in name]
        #ranks = [name for name in awardsdf.columns if "rank" in name]
        cols = ["Killer"] + metrics
        
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        medals = {1 : "gold"}
        
        for col in cols:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
        for index, row in kill_matrix.iterrows():
            tr = Tag(soup, name = "tr")
            td = Tag(soup, name = 'td')
            td.insert(1, index)
            tr.append(td)
            for col in metrics:
                td = Tag(soup, name = 'td')
                td.insert(1, (str(row[col]) + " ").replace(".0 ",""))
                td["class"] = medals.get(row[col + "_rank"],"norank")
                tr.append(td)
                table.append(tr)
        return soup
    
    #Basic stats <table>
    def all_stats_to_html(self,basic_stats):
        stats = basic_stats[0]
        columns = stats.columns
        
        soup = BeautifulSoup("","lxml")
        metrics = [name for name in columns if "rank" not in name]
        cols = ["Player"] + metrics
        
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        table["id"] = "divallstats"
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        medals = {1 : "gold", 2 : "silver", 3: "bronze"}
        
        for col in cols:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
            
        for index, row in stats.iterrows():
            tr = Tag(soup, name = "tr")
            td = Tag(soup, name = 'td')
            td.insert(1, index)
            tr.append(td)
            for col in metrics:
                td = Tag(soup, name = 'td')
                td.insert(1, (str(row[col]) + " ").replace(".0 ",""))
                td["class"] = medals.get(row[col + "_rank"],"norank")
                tr.append(td)
                table.append(tr)
        return soup
    
    #megakill table
    def megakills_to_html(self,megakills):
        columns = megakills.columns
        
        soup = BeautifulSoup("","lxml")        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        table["id"] = "divmegakills"
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        for col in columns:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
        for index, row in megakills.iterrows():
            tr = Tag(soup, name = "tr")
            td = Tag(soup, name = 'td')
            for col in columns:
                td = Tag(soup, name = 'td')
                td.insert(1, (str(row[col])))
                tr.append(td)
                table.append(tr)
        return soup
    
    #Match results <table>
    def match_results_to_html(self, table_match_results):
        stats = table_match_results[0]
        soup = BeautifulSoup("","lxml")
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        table["id"] = "divresults"
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        team_1_score = 0
        team_2_score = 0
        r1fullhold = False
        
        cols = ["#","map","Round",". . . Round Time . . .", "Team 1", "Winner","Score", "Team 2", "Format", "Match Time"]
        
        for col in cols:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
        for index, row in stats.iterrows():
            tr = Tag(soup, name = "tr")
            
            #round order
            td = Tag(soup, name = 'td')
            td.string =  str(row["round_order"])
            tr.append(td)
            
            #map
            td = Tag(soup, name = 'td')
            td.string =  str(row["map"])
            tr.append(td)
            
            #round number (1/2)
            td = Tag(soup, name = 'td')
            td.string =  str(row["round_num"])
            tr.append(td)
            
            #time bars
            td = Tag(soup, name = 'td')
            td["class"]="bars"
            total_time = row["round_time"] + row["round_diff"]
            percentage = row["round_time"]/total_time*100
            time_label = Tag(soup, name = 'label')
            time_text = strftime("%M:%S", gmtime(row["round_time"]))
            time_label.string = time_text
            progress_bar = Tag(soup, name = 'progress')
            progress_bar["id"] = "round_time"
            progress_bar["max"] = "100"
            progress_bar["value"] = str(round(percentage,0))
            width = "width:" + str(int((row["round_time"] + row["round_diff"])/720*10+1)) + "em;"
            progress_bar["style"] = width
            td.append(time_label)
            td.append(progress_bar)
            tr.append(td)
            
            #Team_1
            players = row["players"]
            
            td = Tag(soup, name = 'td')
            if(players == None):
                players = [["??","??","??"],["??","??","??"]]
            td["title"] = players[0][0].replace(" ","_").replace(Const.TEXT_PLAYER_SEPARATOR,"\n")
            td.string = players[0][0][0:30].replace(Const.TEXT_PLAYER_SEPARATOR," ,")
            t1size = len(players[0][0].split(Const.TEXT_PLAYER_SEPARATOR))
            
            team_1 = players[0][1]
            team_2 = players[1][1]
            
            td["class"] = team_1 + " fullroster" 
            tr.append(td)
            
            #Winner sign ><
            td = Tag(soup, name = 'td')
            #here we go with round winner logic again...
            if row["round_num"] == 1:
                if row["round_diff"] == 0:
                    r1fullhold = True
                else:
                    r1fullhold = False
                if row["winner"] == team_1:
                    result = ">"
                    td["class"] = "versusgt1"
                else:
                    result = "<"
                    td["class"] = "versuslt1"
            elif row["round_num"] == 2:
                if row["winner"] == team_1:
                    team_1_score += 1
                    team_2_score += 1 if r1fullhold and row["round_diff"] == 0 else 0
                    result = ">"
                    td["class"] = "versusgt2"
                elif row["winner"] == team_2:
                    team_2_score += 1
                    team_1_score += 1 if r1fullhold and row["round_diff"] == 0 else 0
                    result = "<"
                    td["class"] = "versuslt2"
            else:
                print("What round is it?")
            td.string = result  
            tr.append(td)
            
            #Score (logic above)
            td = Tag(soup, name = 'td')
            td.string = str(team_1_score) + ":" + str(team_2_score) if row["round_num"] == 2 else ""
            tr.append(td)
            
            #Team 2
            td = Tag(soup, name = 'td')
            td["title"] = players[1][0].replace(" ","_").replace(Const.TEXT_PLAYER_SEPARATOR,"\n")
            td.string = players[1][0][0:30].replace(Const.TEXT_PLAYER_SEPARATOR," ,")
            td["class"] = team_2 + " fullroster" 
            t2size = len(players[1][0].split(Const.TEXT_PLAYER_SEPARATOR))
            tr.append(td)
            
            #Format
            td = Tag(soup, name = 'td')
            td.string = str(t1size) + "v" + str(t2size)
            tr.append(td)
            
            #Match Date            
            td = Tag(soup, name = 'td')
            #td.string = row["match_date"].split(" ")[1] if len(row["match_date"].split(" ")) >1 else row["match_date"]
            td.string = row["match_date"]
            tr.append(td)
            
            #Finish row
            table.append(tr)
    
        return soup
    
    #Player rename history <table>
    def renames_to_html(self, table_renames):
        renamesdf = table_renames[0]
        columns = renamesdf.columns
        soup = BeautifulSoup("","lxml")
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        table["id"] = "divrenames"
       
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        for col in columns:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
        for index, row in renamesdf.iterrows():
            tr = Tag(soup, name = "tr")
            for col in columns:
                td = Tag(soup, name = 'td')
                td.insert(1, row[col])
                tr.append(td)
            table.append(tr)    
        
        soup.append(table)
        return soup 
        
    
    style_css = """
    .text {
      font-family: "Courier New", Courier, monospace;
      font-size: 14px;
    }
    .versuslt1 {
      font-weight: bold;
    }
    .versusgt1 {
      font-weight: bold;
    }
    .versuslt2 {
      font-weight: bold;
      color: red;
      font-size: 14px !important;;
    }
    .versusgt2 {
      font-weight: bold;
      color: red;
      font-size: 14px !important;;
    }
    .gold {
      background-color: #D4AF37;
    }
    .silver {
      background-color: #C0C0C0;
    }
    .bronze {
      background-color: #cd7f32;
    }
    .red5 {
      background-color: #F50000;
    }
    .red4 {
      background-color: #ff704d;
    }
    .red3 {
      background-color: #ff9980;
    }
    .red2 {
      background-color: #ffc2b3;
    }
    .red1 {
      background-color: #ffebe6;
    }
    .Allies {
      background-color: #BFDAFF;
    }
    .Axis {
      background-color: #FFBFBF;
    }
    .nocount {
      color: darksalmon;
    }
        
    tr:nth-child(even) {background-color: #f2f2f2;}
        
    table.blueTable {
      font-family: "Courier New", Courier, monospace;
      border: 1px solid #14191B;
      background-color: #F3FFFB;
      text-align: center;
      border-collapse: collapse;
      white-space: nowrap;
    }
    .bars {
      width: 13em;
      text-align: left;
    }
    table.blueTable td, table.blueTable th {
      border: 1px solid #AAAAAA;
      padding: 0px 6px;
    }
    table.blueTable tbody td {
      font-size: 12px;
    }
    table.blueTable thead {
      background: #030D14;
      background: -moz-linear-gradient(top, #42494f 0%, #1c252b 66%, #030D14 100%);
      background: -webkit-linear-gradient(top, #42494f 0%, #1c252b 66%, #030D14 100%);
      background: linear-gradient(to bottom, #42494f 0%, #1c252b 66%, #030D14 100%);
      border-bottom: 0px solid #444444;
    }
    table.blueTable thead th {
      font-size: 14px;
      font-weight: bold;
      color: #EFEFEF;
      text-align: center;
      border-left: 4px solid #D0E4F5;
    }
    table.blueTable thead th:first-child {
      border-left: none;
    }
    
    table.blueTable tfoot .links {
      text-align: right;
    }
    table.blueTable tfoot .links a{
      display: inline-block;
      background: #1C6EA4;
      color: #FFFFFF;
      padding: 2px 8px;
      border-radius: 5px;
    }
        
    progress[value]::-webkit-progress-bar {
      background-color: #B1E59F;
      foreground-color: #FF5757;
      border-radius: 2px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25) inset;
    }
    .ui-tooltip {
        white-space: pre-line;
    	font-size:12;
    	background: #A0A0A0;
    	box-shadow: none;
    	border-style: solid;
    	border-width: 10px 10px 0;
    	z-index: 0;
    }
    """
    
    jquery_sort = """
    $('th').click(function(){
        var table = $(this).parents('table').eq(0)
        var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
        this.asc = !this.asc
        if (!this.asc){rows = rows.reverse()}
        for (var i = 0; i < rows.length; i++){table.append(rows[i])}
    })
        
    $('a').click(
        function(event) {
        $('#div' + event.target.id).slideToggle();
    });

    
    $(document).ready(function(){
       $(".awardheader").tooltip();
    });  
    
    $(document).ready(function(){
       $(".fullroster").tooltip();
    });  
    
    function comparer(index) {
        return function(a, b) {
            var valA = getCellValue(a, index), valB = getCellValue(b, index)
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
        }
    }
    function getCellValue(row, index){ return $(row).children('td').eq(index).text() }
    """


#debug execution
#h = HTMLReport(result[0])
#h.report_to_html("a.html")