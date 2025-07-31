import os
import pandas as pd
import diaglog_box
from tableau_xml_extractor import TableauWorkbook

filepath = diaglog_box.filepath()
# at this point, the variable filepath will either be one explicit file, or a directory.
# If a directory was chosen, the last character will be a '/', and a full list of files
# within that directory needs to be selected

def selected_files(fp):
    files = []
    last_char = fp[-1]
    if last_char != "/":
        files.append(fp)
        return files
    else:
        dir_files = os.listdir(fp)
        for file in dir_files:
            files.append(file)
        return files

sel_files = selected_files(filepath)

print(sel_files)
# above is good

def parse_workbook(filepaths):
    calculations = pd.DataFrame()
    for file in filepaths:
        append_df = TableauWorkbook(filePath=file).calculations
        # calculations.append(append_df, ignore_index=True)
        calculations = pd.concat([calculations, append_df])
    return calculations

results = parse_workbook(sel_files)

print(results)