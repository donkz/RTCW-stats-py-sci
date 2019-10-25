from bs4 import BeautifulSoup
from bs4 import Tag

from time import gmtime
from time import strftime

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


def report_to_html(*argv):
    if len(argv) == 0:
        outfile ="html_report.html"
    else:
        outfile = argv[0]
        
    soup = BeautifulSoup("","lxml")
    html = Tag(soup, name = "html")
    head = Tag(soup, name = "head")
    link = Tag(soup, name = "link")
    link["rel"] = "stylesheet"
    link["href"] = "https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css"
    script = Tag(soup, name = "script")
    script["src"] = "https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"
    script2 = Tag(soup, name = "script")
    script2["src"] = "https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"
    style = Tag(soup, name = "style")
    body = Tag(soup, name = "body")
    soup.append(html)
    soup.html.append(head)
    soup.head.append(link)
    soup.head.append(script)
    soup.head.append(script2)
    soup.head.append(style)
    soup.style.append(style_css)
    soup.html.append(body)
    soup.body.append(insert_header("Results"))
    soup.body.append(match_results_to_html(table_match_results))
    soup.body.append(insert_header("Base stats"))
    soup.body.append(all_stats_to_html(basic_stats))
    soup.body.append(insert_header("Weapon stats"))
    soup.body.append(weapons_to_html(weapon_stats))
    soup.body.append(insert_header("Awards"))
    soup.body.append(awards_to_html(award_stats))
    soup.body.append(insert_header("Kill matrix"))
    soup.body.append(kill_matrix_to_html(kill_matrix_stats))
    
    script_jq = Tag(soup, name = "script")
    script_jq["type"] = "text/javascript"
    script_jq.append(jquery_sort)
    soup.body.append(script_jq)
    
    
    html_file = open(outfile,"w")
    html_file.write(soup.prettify())
    html_file.close() 
    
def insert_header(text):
    soup = BeautifulSoup("","lxml")
    h1 = Tag(soup, name = "h1")
    h1["class"] = "header"
    soup.append(h1)
    soup.h1.append(text)
    return soup
    

def awards_to_html(award_stats):
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
        if(col in award_explanations):
            th["title"] = award_explanations[col]
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
    

def weapons_to_html(weapon_stats):
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

def kill_matrix_to_html(kill_matrix_stats):
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

def all_stats_to_html(basic_stats):
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


def match_results_to_html(table_match_results):
    stats = table_match_results[0]
    soup = BeautifulSoup("","lxml")
    
    table = Tag(soup, name = "table")
    table["class"] = "blueTable"
    soup.append(table)
    tr = Tag(soup, name = "tr")
    table.append(tr)
    
    cols = ["#","map","Round","Round Time", "Team 1", "winner","Team 2"]
    
    for col in cols:
        th = Tag(soup, name = "th")
        tr.append(th)
        th.append(col)
    for index, row in stats.iterrows():
        tr = Tag(soup, name = "tr")

        td = Tag(soup, name = 'td')
        td.string =  str(row["round_order"])
        tr.append(td)
        
        td = Tag(soup, name = 'td')
        td.string =  str(row["map"])
        tr.append(td)
        
        td = Tag(soup, name = 'td')
        td.string =  str(row["round_num"])
        tr.append(td)
        
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
        
        players = row["players"]
        
        td = Tag(soup, name = 'td')
        td["title"] = players[0][0].replace(" ","_").replace("#","\n")
        td.string = players[0][0][0:30].replace("#"," ,")
        team_1 = players[0][1]
        team_2 = players[1][1]
        
        td["class"] = team_1 + " fullroster" 
        tr.append(td)
        
        td = Tag(soup, name = 'td')
        if(row["winner"] == team_1):
            result = ">"
            td["class"] = "versusgt"
        else:
            result = "<"
            td["class"] = "versuslt"
        
        td.string = result
        
        tr.append(td)
        
        td = Tag(soup, name = 'td')
        td["title"] = players[1][0].replace(" ","_").replace("#","\n")
        td.string = players[1][0][0:30].replace("#"," ,")
        td["class"] = team_2 + " fullroster" 
        tr.append(td)
        
        table.append(tr)
    #print(soup)
    return soup

style_css = """
.versusgt {
  font-weight: bold;
  color: blue;
}
.versusgt {
  font-weight: bold;
  color: red;
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
.norank {
  background-color: #F5F5F5;
}
    
table.blueTable {
  font-family: "Courier New", Courier, monospace;
  border: 1px solid #14191B;
  background-color: #F3FFFB;
  text-align: center;
  border-collapse: collapse;
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
  font-size: 14px;
  color: #292929;
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