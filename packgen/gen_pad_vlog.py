def gen_pad_vlog(output_file,padlist):
    
    print("generate pad verilog netlist:",output_file)
    
    for pad in padlist:
        print("  pad:",pad.id,pad.ref.id)