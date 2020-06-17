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
        pin_col        = None
        type_col       = None
        rel_gnd_col    = None
        rel_supply_col = None
        xpos_col       = None
        ypos_col       = None
        
        for mt_col in range(0,max_cell_index):
            
            try:
                
                val = sheet.cell_value(mt_row,mt_col)
                
                if val == "pin":
                    pin_col = mt_col
                elif val == "type":
                    type_col = mt_col
                elif val == "related ground":
                    rel_gnd_col = mt_col
                elif val == "related supply":
                    rel_supply_col = mt_col
                elif val == "x":
                    xpos_col = mt_col
                elif val == "y":
                    ypos_col = mt_col
                    
            except:
                break
            
        if (pin_col is not None) and (type_col is not None):
            
            if header_dict is None:
                header_dict = { "header_row"     : mt_row,
                                "pin_col"        : pin_col,
                                "type_col"       : type_col,
                                "rel_gnd_col"    : rel_gnd_col,
                                "rel_supply_col" : rel_supply_col, 
                                "xpos_col"       : xpos_col,
                                "ypos_col"       : ypos_col
                              }
             
    return(header_dict)

def extract_macro_table_header(sheet):
    """
    extract the macro table header by searching for a line in the Excel sheet that
    contains the words "macro", "instance", "x", "y"
    """
    print("extract macro table header")
    
    max_cell_index = 100
    
    header_dict = None

    for mt_row in range(0,max_cell_index):
        macro_col = None
        inst_col  = None
        xpos_col  = None
        ypos_col  = None
        
        for mt_col in range(0,max_cell_index):
            
            try:
                
                val = sheet.cell_value(mt_row,mt_col)
                
                if val == "macro":
                    macro_col = mt_col
                elif val == "instance":
                    inst_col = mt_col
                elif val == "x":
                    xpos_col = mt_col
                elif val == "y":
                    ypos_col = mt_col
                    
            except:
                break
            
        if (macro_col is not None) and (inst_col is not None):
            
            if header_dict is None:
                header_dict = { "header_row"     : mt_row,
                                "macro_col"      : macro_col,
                                "inst_col"       : inst_col,
                                "xpos_col"       : xpos_col,
                                "ypos_col"       : ypos_col
                              }
             
    return(header_dict)

def extract_pin_spec(sheet,header_dict,num_pin_rows):

    max_cell_index = 100
    
    pin_dict = {}
    
    for mt_row in range(header_dict["header_row"]+1,header_dict["header_row"]+num_pin_rows):
        
        try:
            pin_name       = sheet.cell_value(mt_row,header_dict["pin_col"])
            pin_type       = sheet.cell_value(mt_row,header_dict["type_col"])
            pin_rel_gnd    = sheet.cell_value(mt_row,header_dict["rel_gnd_col"])
            pin_rel_supply = sheet.cell_value(mt_row,header_dict["rel_supply_col"])
            pin_xpos       = sheet.cell_value(mt_row,header_dict["xpos_col"])
            pin_ypos       = sheet.cell_value(mt_row,header_dict["ypos_col"])
            
            # if cell is not empty add pin to pin dictionary
            if len(pin_name)>0:
                pin_dict[pin_name] = {"type"       : pin_type,
                                      "rel_gnd"    : pin_rel_gnd,
                                      "rel_supply" : pin_rel_supply,
                                      "xpos"       : pin_xpos,
                                      "ypos"       : pin_ypos}
                
        except:
            None
            
    return(pin_dict)

def extract_macro_spec(sheet,header_dict,num_macro_rows):

    macro_dict = {}
    
    for mt_row in range(header_dict["header_row"]+1,header_dict["header_row"]+num_macro_rows):
        
        try:
            macro_name   = sheet.cell_value(mt_row,header_dict["macro_col"])
            macro_inst   = sheet.cell_value(mt_row,header_dict["inst_col"])
            macro_xpos   = sheet.cell_value(mt_row,header_dict["xpos_col"])
            macro_ypos   = sheet.cell_value(mt_row,header_dict["ypos_col"])
            
            # if cell is not empty add instance to macro dictionary
            if len(macro_inst)>0:
                macro_dict[macro_inst] = { "macro"    : macro_name,
                                           "xpos"     : macro_xpos,
                                           "ypos"     : macro_ypos}
                
        except:
            None
            
    return(macro_dict)



def extract_macro_spec_sheet(sheet):
    
    max_cell_index = 100
    
    pin_dict = None
    macro_dict = None
    
    print("extract macro specification for ",sheet.name)
    
    pin_header_dict   = extract_pin_table_header(sheet)
    
    try:
        macro_header_dict = extract_macro_table_header(sheet)
    
        if macro_header_dict["header_row"] > pin_header_dict["header_row"]:
            num_pin_rows = macro_header_dict["header_row"] - pin_header_dict["header_row"]
            num_macro_rows = max_cell_index
        else:
            num_pin_rows = max_cell_index
            num_macro_rows = pin_header_dict["header_row"] - macro_header_dict["header_row"]
            
        macro_dict = extract_macro_spec(sheet,macro_header_dict,num_macro_rows)
        
        print("macro table header:",macro_header_dict)
        print("num macro rows:",num_macro_rows)
        print("macro table:",macro_dict)
        
#        macro_spec[sheet.name]["macro_spec"] = macro_dict
    except:
        num_pin_rows = max_cell_index
        
    pin_dict = extract_pin_spec(sheet,pin_header_dict,num_pin_rows)
    
    print("pin table header:",pin_header_dict)
    print("num pin rows:",num_pin_rows)
    print("pin table:",pin_dict)
    
    macro_spec = { sheet.name : {"pin_spec"   : pin_dict,
                                 "macro_spec" : macro_dict} }
    return(macro_spec)

def read_macros(spec_file):
    
    macros = {}
    
    with open_workbook(spec_file) as wb:
        print("Read macro specification from ",spec_file)
        
        for sheet in wb.sheets():
            macros.update(extract_macro_spec_sheet(sheet))
            
    print("Macros:",macros)
    return(macros)
