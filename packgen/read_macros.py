from xlrd import open_workbook

def extract_table_header(sheet,label_dict):
    """
    extract a table header by searching for a row or
    a column in the Excel sheet that
    contains the words of the label dictionary
    """
    header_dict = None

    max_cell_index = 100
    max_idx    = None
    max_weight = 0
    
    for idx0 in range(0,max_cell_index):
        
        # reset weight computation for each row/column scan
        row_weight = 0
        row_header_dict = {}
        col_weight = 0
        col_header_dict = {}
        
        for idx1 in range(0,max_cell_index):
           
            try:
                val = sheet.cell_value(idx0,idx1)
                if val in label_dict:
                    row_weight = row_weight + 1
                    row_header_dict.update({label_dict[val] : idx1})
            except:
                None
        
            try:
                val = sheet.cell_value(idx1,idx0)
                if val in label_dict:
                    col_weight = col_weight + 1
                    col_header_dict.update({label_dict[val] : idx1})
            except:
                None
        
        # update max values when new row was found that matches the label_dict better         
        if row_weight > max_weight:
            max_weight = row_weight
            header_dict = row_header_dict
            header_dict.update({"header_row":idx0})

        # update max values when new column was found that matches the label_dict better         
        if col_weight > max_weight:
            max_weight = col_weight
            header_dict = col_header_dict
            header_dict.update({"header_col":idx0})
    
#    print("header_dict:",header_dict)
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
    
    # extract header dictionary with row/column index (_rcidx) for the macro parameters
    label_dict = {"width"      : "width_rcidx",
                  "height"     : "height_rcidx",
                  "macro type" : "mtype_rcidx",
                  "LEF"        : "lef_rcidx",
                  "LIB"        : "lib_rcidx"}
    param_header_dict = extract_table_header(sheet,label_dict)
    
    print("parameter header:",param_header_dict)

    label_dict = {"pin"            : "pin_col",
                  "type"           : "type_col",
                  "related ground" : "rel_gnd_col",
                  "related supply" : "rel_supply_col",
                  "x"              : "xpos_col",
                  "y"              : "ypos_col"}
    pin_header_dict = extract_table_header(sheet,label_dict)
    
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
