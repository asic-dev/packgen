from xlrd import open_workbook

def extract_pin_table_header(sheet):
    """
    extract the pin table header by searching for a line in the Excel sheet that
    contains the words "pin", "type, "related ground", "related supply"
    """
    print("extract pin table header")
    
    max_cell_index = 100
    
    header_dict = None

    for mt_row in range(0,max_cell_index):
        pin_col  = None
        type_col = None
        
        for mt_col in range(0,max_cell_index):
            
            try:
                val = sheet.cell_value(mt_row,mt_col)
                if val == "pin":
                    pin_col = mt_col
                elif val == "type":
                    type_col = mt_col
            except:
                break
            
        if (pin_col is not None) and (type_col is not None):
            
            if header_dict is None:
                header_dict = { "header_row" : mt_row,
                                "pin_col"    : pin_col,
                                "type_col"   : type_col
                              }
             
    return(header_dict)

def extract_macro_spec_sheet(sheet):
    print("extract macro specification for ",sheet.name)
    
    print("pin table header:",extract_pin_table_header(sheet))

def read_macros(spec_file):
    
    with open_workbook(spec_file) as wb:
        print("Read macro specification from ",spec_file)
        
        for sheet in wb.sheets():
            extract_macro_spec_sheet(sheet)
