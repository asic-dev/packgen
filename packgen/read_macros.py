from xlrd import open_workbook

def extract_pin_table_header(sheet):
    print("extract pin tbale header")
    
    header_dict = {}
    
    return(header_dict)

def extract_macro_spec_sheet(sheet):
    print("extract macro specification for ",sheet.name)
    
    print("pin table header:",extract_pin_table_header(sheet))

def read_macros(spec_file):
    
    with open_workbook(spec_file) as wb:
        print("Read macro specification from ",spec_file)
        
        for sheet in wb.sheets():
            extract_macro_spec_sheet(sheet)
