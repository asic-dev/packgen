from xlrd import open_workbook

def get_weight(table,x,y,type):
    if type == "xup":
        x_inc = 1
        y_inc = 0
    elif type == "xdown":
        x_inc = -1
        y_inc = 0
    elif type == "yup":
        x_inc = 0
        y_inc = 1
    elif type == "ydown":
        x_inc = 0
        y_inc = -1
        
#    print("get_weight: {},{},{}".format(x,y,type))
    
    match = True
    weight = 0
    x_index = x
    y_index = y
    while match:
        next_x = x_index + x_inc
        next_y = y_index + y_inc
        match = False
        if not ( (next_x < 0) or (next_y < 0) ) :
#            print("compare: {} - {}".format(sheet.cell_value(next_y,next_x),sheet.cell_value(y,x)))
            try:
#                if (float(sheet.cell_value(next_y,next_x))-float(sheet.cell_value(y_index,x_index)) == 1):
                if (table[next_y][next_x]-table[y_index][x_index] == 1):
                    weight = weight + 1
                    match = True
            except:
#                print("no match : {},{} {}".format(x,y,sheet.cell_value(y,x)))
                None
            x_index = next_x
            y_index = next_y
            
    next_x = x - x_inc
    next_y = y - y_inc
    if not ( (next_x < 0) or (next_y < 0) ) :
        try:
#            if ((float(sheet.cell_value(y,x))-float(sheet.cell_value(next_y,next_x))) == 1):
            if ((table[y][x]-table[next_y][next_x]) == 1):
                weight = 0
        except:
            None
            
    return (weight)         

def scan_table(table,scope,direction):

    max_cell_index = 20
    
    if scope is not None:
        xmin = scope[0]
        ymin = scope[1]
        xmax = scope[2]
        ymax = scope[3]
    else:
        xmin = 0
        ymin = 0
        xmax = max_cell_index
        ymax = max_cell_index
    
    max_weight = -1
    pos_list = []
        
    for x in range(xmin,xmax):
        for y in range(ymin,ymax):
            current_weight = get_weight(table,x,y,direction)
#            print("{},{}: {}".format(x,y,current_weight))
            if max_weight < current_weight:
                max_weight = current_weight
                pos_list = [(x,y)]
            elif max_weight == current_weight:
                pos_list.append((x,y))
    
    result = {            
        "max_weight" : max_weight,
        "pos_list"   : pos_list
    }
    
    return(result)

def convert_sheet(sheet,scope,type):

    max_cell_index = 20
    
    if scope is not None:
        xmin = scope[0]
        ymin = scope[1]
        xmax = scope[2]
        ymax = scope[3]
    else:
        xmin = 0
        ymin = 0
        xmax = max_cell_index
        ymax = max_cell_index

    table = []
    for x in range(xmin,xmax):
        line = []
        for y in range(ymin,ymax):
            item = -2
            try:
                if type == "num":
                    item = int(float(sheet.cell_value(x,y)))
                elif type == "alpha":
                    if (len(sheet.cell_value(x,y))==1):
                        item = ord(sheet.cell_value(x,y))-64
                    #item = int(float(sheet.cell_value(x,y)))
            except:
                None
            line.append (item)
        table.append(line)
    
    return(table)

def find_label(sheet,scope,type):
    
    directions = ["xdown","xup","ydown","yup"]
    
    max_weight = -1
    pos_list = []
    max_dir = ""
    
    table  = convert_sheet(sheet,scope,type)
    
    for dir in directions:
        current_scan = scan_table(table,scope,dir)
        if max_weight < current_scan["max_weight"]:
            max_weight = current_scan["max_weight"]
            pos_list   = current_scan["pos_list"]
            max_dir    = dir
            
    result = {            
        "max_weight" : max_weight,
        "positions"  : pos_list,
        "direction"  : max_dir
    }
     
    print ("direction : {} -> {} -> {}".format(result["direction"],result["max_weight"],result["positions"]))
    
    label_list=[]
    pos_dir={}
    for i in range(0,max_weight+1):
        cell_y = pos_list[0][1]
        cell_x = pos_list[0][0]
        
        if max_dir == "xdown":
            cell_x = cell_x-i
            pos = cell_x
        elif max_dir == "xup":
            cell_x = cell_x+i
            pos = cell_x
        elif max_dir == "ydown":
            cell_y = cell_y-i
            pos = cell_y
        elif max_dir == "yup":
            cell_y = cell_y+i
            pos = cell_y

        cell_value = sheet.cell_value(cell_y,cell_x)
        print("cell:",cell_value,cell_y,cell_x)
        if type == "num":
            cell_value = int(float(cell_value))

        label_list.append(cell_value)
        pos_dir[cell_value] = pos

#        print("cell:",cell_value,pos)
        
        label = {
            "label_list" : label_list,
            "pos_dir"    : pos_dir,
            "type"       : max_dir
        }

#    print ("label:",label)
    
    return(label)

def read_ballout (spec_file,sheet_name=None,scope=None):

    wb = open_workbook(spec_file)
#    print ("number of sheets: {}".format(len(wb.sheet_names())))
    
    sheet = None
    
    # try to access the spec sheet by the specified name
    if sheet_name is not None:
        sheet = wb.sheet_by_name(sheet_name)
    elif len(wb.sheet_names()) == 1:
        sheet = wb.sheets()[0]
    
    assert sheet is not None, "could not extract specification sheet: sheet_name argument was not provided and more than one sheet was found in the workbook"
 
    num_label = find_label(sheet,scope,"num")
    alpha_label = find_label(sheet,scope,"alpha")
    
    ball_out={}
    for num_id in num_label["label_list"]:
        for alpha_id in alpha_label["label_list"]:
            if ( (num_label["type"] == "xdown") or
                 (num_label["type"] == "xup") ):
                id = "{}{}".format(alpha_id,num_id)
                cell_value = sheet.cell_value(alpha_label["pos_dir"][alpha_id],num_label["pos_dir"][num_id])
#                print("read out:",id,cell_value)
                if len(cell_value)>0:
                    ball_out[id] = cell_value

#    print("ballout:",ball_out)

    assert num_label is not None, "could not extract num label specification"
    
#    print("num_label:",num_label)
#    print("alpha_label:",alpha_label)
    
    return(ball_out)

