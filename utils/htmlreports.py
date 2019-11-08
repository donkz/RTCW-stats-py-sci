from bs4 import BeautifulSoup
from bs4 import Tag

from time import gmtime
from time import strftime

from textsci.awards import Awards 
from textsci.matchstats import MatchStats
import os

class HTMLReport:
    
    def __init__(self, single_result):
        result = single_result
    
        awards = Awards()
        award_stats = awards.collect_awards(result)
        
        matchstats = MatchStats()
        weapon_stats = matchstats.table_weapon_counts(result)
        kill_matrix_stats = matchstats.table_kill_matrix(result)
        basic_stats = matchstats.table_base_stats(result)
        match_results = matchstats.table_match_results(result)
        #match_info_datetime = matchstats.match_info_datetime(result)
        #table_map_list = matchstats.table_map_list(result)
        renames = matchstats.table_renames(result)
        
        self.match_results_html_table = self.match_results_to_html(match_results)
        self.basic_stats_html_table = self.all_stats_to_html(basic_stats)
        self.weapon_stats_html_table = self.weapons_to_html(weapon_stats)
        self.award_stats_html_table = self.awards_to_html(award_stats)
        self.kill_matrix_stats_html_table = self.kill_matrix_to_html(kill_matrix_stats)
        if renames[0] is None:
            self.renames_html_table = None
        else:   
            self.renames_html_table = self.renames_to_html(renames)
       
             
    award_explanations = {
            "FirstInDoor" : "First killer or victim of the round",
            "Blownup"     : "Exploded by grenade, AS, dynamite",
            "Panzed"      : "Died to panzer",
            "KillStreak"  : "Kills without dying",
            "Deathroll"   : "Consecutive deaths without a kill",
            "Kills"       : "Kills in the entire match",
            "KDR"         : "Kills to enemy deaths ratio",
            "Caps"        : "Captured objective on offense",
            "Holds"       : "Held the time on defense",
            "AdjScore"    : "Objective Score (Total minus kills, TKs, and deaths)",
            "Pack5"       : "5 kills without dying",
            "RankPts"    : "Total rank for the match",
            }
    
    
    def report_to_html(self,*argv):
        
        if len(argv) == 0:
            outfile ="html_report.html"
        else:
            outfile = argv[0]
            
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
        soup.body.append(self.insert_header("Results",2))
        soup.body.append(self.match_results_html_table)
        soup.body.append(self.insert_header("Base stats",2))
        soup.body.append(self.basic_stats_html_table)
        soup.body.append(self.insert_header("Weapon stats",2))
        soup.body.append(self.weapon_stats_html_table)
        soup.body.append(self.insert_header("Awards",2))
        soup.body.append(self.award_stats_html_table)
        soup.body.append(self.insert_header("Kill matrix",2))
        soup.body.append(self.kill_matrix_stats_html_table)
        if self.renames_html_table is not None:
            soup.body.append(self.insert_header("Player rename history",2))
            soup.body.append(self.renames_html_table)
        
        #jquery scripts
        script_jq = Tag(soup, name = "script")
        script_jq["type"] = "text/javascript"
        script_jq.append(self.jquery_sort)
        soup.body.append(script_jq)
        #end of html report
        
        html_file = open(outfile,"w")
        html_file.write(soup.prettify())
        html_file.close() 
        print("Wrote html report to " + html_file.name)
        
    def insert_header(self,text, size):
        soup = BeautifulSoup("","lxml")
        header1 = Tag(soup, name = "h" + str(size))
        header1["class"] = "header"
        header1.append(text)
        soup.append(header1)
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
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        medals = {1 : "gold", 2 : "silver", 3: "bronze"}
        
        for col in cols:
            th = Tag(soup, name = "th")
            tr.append(th)
            th.append(col)
            th["class"] = "awardheader"
            if(col in self.award_explanations):
                th["title"] = self.award_explanations[col]
        for index, row in awardsdf.iterrows():
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
        #columns = kill_matrix_stats[1]
        columns = stats.columns
        
        soup = BeautifulSoup("","lxml")
        metrics = [name for name in columns if "rank" not in name]
        #ranks = [name for name in awardsdf.columns if "rank" in name]
        cols = ["Player"] + metrics
        
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
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
    
    #Match results <table>
    def match_results_to_html(self, table_match_results):
        stats = table_match_results[0]
        soup = BeautifulSoup("","lxml")
        
        table = Tag(soup, name = "table")
        table["class"] = "blueTable"
        soup.append(table)
        tr = Tag(soup, name = "tr")
        table.append(tr)
        
        team_1_score = 0
        team_2_score = 0
        r1fullhold = False
        
        cols = ["#","map","Round",". . . Round Time . . .", "Team 1", "Winner","Score", "Team 2", "Format"]
        
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
            td["title"] = players[0][0].replace(" ","_").replace("#","\n")
            td.string = players[0][0][0:30].replace("#"," ,")
            t1size = len(players[0][0].split("#"))
            
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
            td["title"] = players[1][0].replace(" ","_").replace("#","\n")
            td.string = players[1][0][0:30].replace("#"," ,")
            td["class"] = team_2 + " fullroster" 
            t2size = len(players[1][0].split("#"))
            tr.append(td)
            
            #Format
            td = Tag(soup, name = 'td')
            td.string = str(t1size) + "v" + str(t2size)
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
    .Allies {
      background-color: #BFDAFF;
    }
    .Axis {
      background-color: #FFBFBF;
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
#h = HTMLReport(results)
#h.report_to_html("a.html")