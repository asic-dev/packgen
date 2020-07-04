def gen_liberty(macro):
    
    print("generate liberty file for macro",macro.id)
    
    f = open("{}.lib".format(macro.id),"w")
    
    f.write("library({}) ".format(macro.id))
    f.write("{\n\n")
    
    f.write("  cell({}) ".format(macro.id))
    f.write("{\n\n")
    
    for pin in macro.plist:
        if pin.is_pg_pin():
            f.write("    pg_pin({}) ".format(pin.id))
            f.write("{\n")
            f.write("    }\n\n")
        else:
            f.write("    pin({}) ".format(pin.id))
            f.write("{\n")
            if pin.is_input():
                f.write("        direction : input;\n")
            elif pin.is_output():
                f.write("        direction : output;\n")
                
            try:
                f.write("        related_ground_pin : {};\n".format(pin.get_related_ground()))
            except:
                f.write("        /* ERROR: related_ground_pin is not defined for pin {}*/\n".format(pin.id))
            
            try:
                f.write("        related_supply_pin : {};\n".format(pin.get_related_supply()))
            except:
                f.write("        /* ERROR: related_supply_pin is not defined for pin {}*/\n".format(pin.id))
            
            f.write("    }\n\n")
    
    f.write("  }\n\n")

    f.write("}")
    
    f.close()
    