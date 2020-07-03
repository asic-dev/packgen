def gen_vlog(macro):
    
    print("generate verilog module file for the macro",macro.id)
    
    f = open("{}.v".format(macro.id),"w")
    
    f.write("module {} (\n".format(macro.id))

    seperator = ""
    for pin in macro.plist:
        if pin.is_pg_pin():
            None
        else:
            f.write("{}    {}".format(seperator,pin.id))
            seperator = ",\n"

    f.write("\n);")

    f.write("\n\n")
    f.write("  // input declarations\n")
    f.write("  //-------------------\n\n")
    for pin in macro.plist:
        if pin.is_input():
            f.write("  input {};\n".format(pin.id))

    f.write("\n\n")
    f.write("  // output declarations\n")
    f.write("  //--------------------\n\n")
    for pin in macro.plist:
        if pin.is_output():
            f.write("  output {};\n".format(pin.id))

            
    
    f.write("\n\n")
    
    f.write("endmodule\n\n")

    f.close()
    