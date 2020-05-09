
from reportlab.lib.colors import darkgreen, tan, black, white
from reportlab.lib.units import cm

from datasheet.pdf_gen import datasheet
from packgen.lib import BGA

from packgen.read_ballout import read_ballout
from packgen.gen_pad_vlog import gen_pad_vlog
        

#=============
# main program
#=============

print("\nBGA ball array generation script\n")

#=================
# package creation
#=================
my_package = BGA(8,8)

# refine package by removing some balls
#my_package.pinlist.remove("J6","I7","G4")    

# create a ball out dictionary from an Excel table
ball_out = read_ballout("spec/ball_out.xlsx")
print(ball_out)
for ball in ball_out:
    print("ball:",ball)
    my_package.pinlist.get(ball).connect(ball_out[ball])


#=========================================
# package to chip connectivity description
#=========================================
# connect VDDD_0P8V supply net
#for item_id in ["A0","A3","C0","C3"]:
#    my_package.pinlist.get(item_id).connect("VDDD_0P8V")

# change VDDD_0P8V color to red    
my_package.netlist.get("VDDA").color = [1,0,0]

# connect GNDD supply net
#for item_id in ["C1","C2"]:
#    my_package.pinlist.get(item_id).connect("GNDD")
# change VDDD_0P8V color to black
my_package.netlist.get("GNDD").color = [0,0,0]

    
#my_package.pinlist.remove("J6")    

darkgreen = [0,0.5,0]
#my_package.pinlist.get("B0").connect("MISO").color = darkgreen
#my_package.pinlist.get("B1").connect("MOSI").color = darkgreen
#my_package.pinlist.get("B2").connect( "SCK").color = darkgreen

#=========================
# chip description of mars
#=========================
CHIP_TOP = "mars"
CHIP_XDIM = 2500
CHIP_YDIM = 3000
mars = my_package.chiplist.add( CHIP_TOP,
                                CHIP_XDIM,
                                CHIP_YDIM )

lshape = mars.macrolist.add("L_SHAPE",[ (  0,  0) ,
                                        (200,  0) ,
                                        (200,150) ,
                                        (150,150) ,
                                        (150,100) ,
                                        (  0,100)  ])

mars.macrolist.add("BOX_SHAPE", [ (200,100) ] )

mars.macrolist.add("GPIO_PAD_H", [( 50,150)] )
mars.macrolist.add("GPIO_PAD_V", [(150,50 )] )

mars.instlist.add("L_SHAPE_I1","L_SHAPE",( 500,700))
mars.instlist.add("L_SHAPE_I2","L_SHAPE",( 700,700))
mars.instlist.add("L_SHAPE_I3","L_SHAPE",( 900,700))
mars.instlist.add("L_SHAPE_I4","L_SHAPE",(1100,700))

mars.instlist.add("B_SHAPE_I1","BOX_SHAPE",(200,1000))

mars.padlist.add("MISO_inst","GPIO_PAD_H",1000,1000)
mars.padlist.add("MOSI_inst","GPIO_PAD_H",2000,2000)

print("LSHAPE:",lshape)
lshape.add_pin("input_ena",(10,10))
lshape.add_pin("output_ena",(20,10))

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

from packgen.spec import SpecObj
test_spec = SpecObj()

gen_pad_vlog("test.v",mars.padlist)