from xlrd import open_workbook

def read_macros(spec_file):
    
    wb = open_workbook(spec_file)