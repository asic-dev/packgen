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
        pin_col     = None
        type_col    = None
        rel_gnd_col = None
        
        for mt_col in range(0,max_cell_index):
            
            try:
                
                val = sheet.cell_value(mt_row,mt_col)
                
                if val == "pin":
                    pin_col = mt_col
                elif val == "type":
                    type_col = mt_col
                elif val == "related ground":
                    rel_gnd_col = mt_col
                    
            except:
                break
            
        if (pin_col is not None) and (type_col is not None):
            
            if header_dict is None:
                header_dict = { "header_row"  : mt_row,
                                "pin_col"     : pin_col,
                                "type_col"    : type_col,
                                "rel_gnd_col" : rel_gnd_col
                              }
             
    return(header_dict)

def extract_pin_spec(sheet,header_dict):

    max_cell_index = 100
    
    pin_dict = {}
    
    for mt_row in range(header_dict["header_row"]+1,max_cell_index):
        
        try:
            pin_name    = sheet.cell_value(mt_row,header_dict["pin_col"])
            pin_type    = sheet.cell_value(mt_row,header_dict["type_col"])
            pin_rel_gnd = sheet.cell_value(mt_row,header_dict["rel_gnd_col"])
            
            # if cell is not empty add pin to pin dictionary
            if len(pin_name)>0:
                pin_dict[pin_name] = {"type"    : pin_type,
                                      "rel_gnd" : pin_rel_gnd}
                
        except:
            None
            
    return(pin_dict)

def extract_macro_spec_sheet(sheet):
    print("extract macro specification for ",sheet.name)
    
    header_dict = extract_pin_table_header(sheet)
    
    pin_dict = extract_pin_spec(sheet,header_dict)
    
#    print("pin table header:",header_dict)
#    print("pin table:",pin_dict)
    
    macro_spec = { sheet.name : {"pin_spec" : pin_dict} }
    return(macro_spec)

def read_macros(spec_file):
    
    macros = {}
    
    with open_workbook(spec_file) as wb:
        print("Read macro specification from ",spec_file)
        
        for sheet in wb.sheets():
            macros.update(extract_macro_spec_sheet(sheet))
            
    print("Macros:",macros)
