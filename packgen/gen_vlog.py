def gen_vlog(macro):
    
    print("generate verilog module file for the macro",macro.id)
    
    f = open("{}.v".format(macro.id),"w")
    
    f.write("module {} () ".format(macro.id))
    f.write("\n\n")
    
    f.write("endmodule\n\n")

    f.close()
    