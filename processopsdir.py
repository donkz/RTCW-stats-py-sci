import os
from zipfile import ZipFile, is_zipfile
from datetime import datetime

test_zip = "test_samples\playername.zip"
test_dir = "test_samples\stats"

def list_osp_files(path):
    print("scanning files in " + path)
    
    osp_files = [] # will contain elements like [filepath,date]
    for subdir, dirs, files in os.walk(path):
            for file in files:
                #print os.path.join(subdir, file)
                filepath = subdir + os.sep + file

                if filepath.endswith(".txt"):
                    print (filepath)
                    file_date_str = filepath.replace(path,"")
                    file_date_dt = datetime.strptime(file_date_str, "\\%Y.%m.%d\\%H%M%S.txt" )
                    osp_files.append([filepath,file_date_dt])
    #print(osp_files)
    sorted_osp_files = sorted(osp_files,  key=lambda x: x[1])
    return sorted_osp_files

def get_osp_files(path):
    print(path)
    filename, file_extension = os.path.splitext(path)
    
    if(file_extension == ""):
        return os.path.abspath(path)
    
    #get tbw file from the tbwx
    if(file_extension == ".zip"):
        if(is_zipfile(path) == False):
            print("Not recognized zipfile")
            exit()
        with ZipFile(os.path.abspath(path), 'r') as zipObj:
            # Extract all the contents of zip file into a temp directory
            zipObj.extractall('temp')
    return os.path.abspath('temp')

path = get_osp_files(test_zip)
list_osp_files(path)

print("")

path = get_osp_files(test_dir)
sorted_osp_files = list_osp_files(path)
# =============================================================================
# print("")
# print("")
# print("")
# print("")
# print(sorted_osp_files)
# =============================================================================

osp_stats_begun = False
lines = []
for osp_file in sorted_osp_files:
    with open(osp_file[0],"r") as file:
            for line in file:
                if line[0:26] == "TEAM   Player          Kll":
                    osp_stats_begun = True
                if osp_stats_begun and (line[0:7] == 'Axis   ' or line[0:7] ==  'Allies '):
                    if line[7:13] != 'Totals':
                        lines.append(line.strip())
                if line[0:24] == 'Allies Totals           ':
                    osp_stats_begun = False
print(*lines, sep = "\n")