
"""
a spec opbject is a dictionary that collects the spec information

e.g.
Ball ID -> Ball name
A0 -> VDDA 

a spec can be extracted from a fileassociated/
e.g. ball_out.xlsx

file -> FileSpecObj(specialized versions for git, DesSync,...) -> Extractor -> PackgenSpecObj (e.g. ball_out, pad_out, ...) -> Generator (ipxact, verilog RTL, verilog netlist) -> FileSpecObj

this chain is basically a graph

The graph itself (interconnection of different Object Types) costruct a design flow

PackgenSpecObj can be compared and reduce the stack trace to the overlapping part.
The non overlapping part can be set to validated in case the match is successful.


the stack trace is collected during creation of the data structurs for the spec information
to automatically trace the extraction from source files and detect extraction code overlaps
"""
import traceback

class SpecObj:
    
    def __init__(self):
        print(traceback.extract_stack(limit=10))
        None