
from reportlab.lib.colors import darkgreen, tan, black, white
from reportlab.lib.units import cm

from datasheet.pdf_gen import datasheet
from packgen.lib import BGA

        
        
#=============
# main program
#=============

print("\nBGA ball array generation script\n")

#=================
# package creation
#=================
my_package = BGA(10,10)

# refine package by removing some balls
my_package.pinlist.remove("J6","I7","G4")    

#=========================================
# package to chip connectivity description
#=========================================
# connect VDDD_0P8V supply net
for item_id in ["A0","A3","C0","C3"]:
    my_package.pinlist.get(item_id).connect("VDDD_0P8V")
# change VDDD_0P8V color to red    
my_package.netlist.get("VDDD_0P8V").color = [1,0,0]

# connect GNDD supply net
for item_id in ["C1","C2"]:
    my_package.pinlist.get(item_id).connect("GNDD")
# change VDDD_0P8V color to black
my_package.netlist.get("GNDD").color = [0,0,0]

    
#my_package.pinlist.remove("J6")    

darkgreen = [0,0.5,0]
my_package.pinlist.get("B0").connect("MISO").color = darkgreen
my_package.pinlist.get("B1").connect("MOSI").color = darkgreen
my_package.pinlist.get("B2").connect( "SCK").color = darkgreen

#=========================
# chip description of mars
#=========================
CHIP_TOP = "mars"
CHIP_XDIM = 2500
CHIP_YDIM = 3000
mars = my_package.chiplist.add( CHIP_TOP,
                                CHIP_XDIM,
                                CHIP_YDIM )

mars.padlist.add("MISO",1000,1000)
mars.padlist.add("MOSI",2000,2000)

mars.macrolist.add("L_SHAPE", (500,700) ,
                            [ (  0,  0) ,
                              (200,  0) ,
                              (200,150) ,
                              (150,150) ,
                              (150,100) ,
                              (  0,100)  ])

mars.macrolist.add("BOX_SHAPE", (700,700) , [ (200,100) ] )

mars.instlist.add("L_SHAPE_I1","L_SHAPE",( 500,700))
mars.instlist.add("L_SHAPE_I2","L_SHAPE",( 700,700))
mars.instlist.add("L_SHAPE_I3","L_SHAPE",( 900,700))
mars.instlist.add("L_SHAPE_I4","L_SHAPE",(1100,700))

#=================
# chip2 description
#=================
#CHIP_TOP = "mercury"
#CHIP_XDIM = 3500
#CHIP_YDIM = 3000
#my_package.chiplist.add( chip(CHIP_TOP,
#                              CHIP_XDIM,
#                              CHIP_YDIM) )    

#===================
# datasheet creation
#===================
my_package.plot(600,600)

my_package.check()

my_datasheet = datasheet("ABC123",my_package)
my_datasheet.write_pdf("datasheet.pdf")

