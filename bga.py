import cairo
import math

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, Spacer, Table, TableStyle
from reportlab.lib.colors import darkgreen, tan, black, white
from reportlab.platypus.flowables import Flowable, Spacer
from reportlab.lib.units import cm



class PackObj:

    """
    abstract base class to derive package generation objects
    """ 
    
    def __init__(self,object_id):
        print("PackObj: created ",object_id)
        self.id = object_id
        
    def check(self):
#        print("PackObj: check",self.id)
        None


class PackObjList(PackObj):
    
    """abstract list class to derive iterateable package generation objects""" 

    def __init__(self,object_id):
        super().__init__(object_id)
        self.__dict = {}
        
    def add(self,item):
        print("PackObjList: create ",item.id)

        if item.id in self.__dict:
            print("PackObjList: found item ",item.id,"already in list")
        else:
            print("PackObjList: add item ",item.id,"to list")
            self.__dict[item.id]=item

        return(self.__dict[item.id])
            
    def get(self,item_id):
        if item_id in self.__dict:
            return(self.__dict[item_id])
        else:
            return(None)

    """"
    plot all objects of the list
    
    The methode requires a cairo handle to the drawing
    """
    def plot(self,ctx):
        for item in self.__dict:
            self.__dict[item].plot(ctx)
        
    def draw(self,canvas):
        for item in self.__dict:
            self.__dict[item].draw(canvas)
        
    def __iter__(self):
        self.iter_keys = list(self.__dict.keys())
        return(self)

    def __next__(self):
        try:
            return(self.__dict[self.iter_keys.pop()])
        except IndexError:
            raise StopIteration

    def check(self):
        for item in self.__dict:
            self.__dict[item].check()
    
    """
    Methode removes one or more items from the list
    """        
    def remove(self,*args):
        for item in args:
            if item in self.__dict:
                print("PackObjList: remove",item)
                del self.__dict[item]
            else:
                raise RuntimeError("item " + item + " not found")

class ChipListObj(PackObjList):
    """
    list of chips in a package
    """
    def __init__(self,package):
        super().__init__("chip_list")
        self.package = package

    def add(self,id,x,y):
        return(super().add(chip(self.package,id,x,y)))
    
class PadListObj(PackObjList):
    """
    pad list object is a list of pads
    """
    def __init__(self,package):
        super().__init__("pad_list")
        self.package = package

    def add(self,id,x,y):
        pad = PinObj(self.package,id,x,y)
        pad.r = 50
        super().add(pad)
    
        
class NetObj(PackObj):
    
    """
    Is an object that collects which pins are connected to a net and which pad cells are connected to this net
    """
    def __init__(self,object_id):
        super().__init__(object_id)
        self.pinlist = PackObjList("pinlist")
        self.padlist = PackObjList("padlist")
        self.color = None
        
class PinObj(PackObj):
    
    """
    Is a object that collects all information of a package pin.
    
    A package pin has an identifier (0,1,2,... for QFN) or (A0,A1,...,B0,B1,... for BGA)
    A package pin also has a list of connected IC pads and connected package pins
    A package pin also has a geometry information of the x and y location
    """
    def __init__(self,package,object_id,x,y):
        super().__init__(object_id)
        self.package = package
        self.connected_net = None
        self.x = x
        self.y = y
        self.r = 0.25    # default radius
        
    def check(self):
        super().check()
        if self.connected_net is None:
            print("WARNING: PinObj {} : no net is connected".format(self.id))

    """
    connect the pin to a net
    
    the function returns the connected net so that it could be used for further operations
    """        
    def connect(self,net_id):
        print("PinObj: connect",self.id,"to",net_id)
        if self.connected_net is None:                   # if pin is not yet connected ...
            net = self.package.netlist.get(net_id)       # ... get the net
            if net is None:                              # if the net does not exist ...
                print(net_id,"does not exist")        
                net = NetObj(net_id)                     # ... create it
                net.pinlist.add(self)
                self.connected_net = net
                self.package.netlist.add(net)
            else:
                net.pinlist.add(self)
                self.connected_net = net
                
            return(net)
        
        else:
            raise RuntimeError (self.id,"is already connected to",self.connected_net.id)

    def plot(self,ctx):
        RADIUS = 0.2

        # if the ball is connected and a color is assigned draw an octagon around it
        if self.connected_net is not None:
            if self.connected_net.color is not None:
                ctx.set_source_rgb(self.connected_net.color[0],
                                   self.connected_net.color[1],
                                   self.connected_net.color[2])
                ctx.set_line_width(0.01)
                ctx.move_to(self.x-0.25, self.y-0.50)
                ctx.line_to(self.x+0.50, self.y-0.50)
                ctx.line_to(self.x+0.50, self.y+0.50)
                ctx.line_to(self.x-0.50, self.y+0.50)
                ctx.line_to(self.x-0.50, self.y-0.25)
                if self.id == "A0":
                    ctx.line_to(self.x-0.25, self.y-0.50)
                else:
                    ctx.line_to(self.x-0.50, self.y-0.50)
                    ctx.line_to(self.x-0.25, self.y-0.50)
                ctx.fill()

        # draw black circle for the ball
        ctx.set_line_width(0.1)
        ctx.set_source_rgb(1, 1, 1)  # white fill
        ctx.move_to(self.x+RADIUS, self.y)
        ctx.arc(self.x, self.y, RADIUS, 0, 2*math.pi)
        ctx.fill()
        ctx.set_source_rgb(0, 0, 0)  # black border
        ctx.arc(self.x, self.y, RADIUS, 0, 2*math.pi)
        ctx.stroke()

        # print the net id in the circle
        ctx.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(0.05)
        if self.connected_net is None:
            s = "n.c."
        else:
            s = self.connected_net.id
        xbearing, ybearing, width, height, dx, dy = ctx.text_extents(s)
        ctx.move_to(self.x - width/2, self.y + height/2)
        ctx.show_text(s)

    """
    draw the balls and surrounding rectangular in the pinout drawing of the PDF specification
    """        
    def draw(self,canvas):
        # if the ball is connected and a color is assigned draw an rectangle around it
        if self.connected_net is not None:
            if self.connected_net.color is not None:
                canvas.setStrokeColorRGB(self.connected_net.color[0],
                                         self.connected_net.color[1],
                                         self.connected_net.color[2])
                canvas.setFillColorRGB  (self.connected_net.color[0],
                                         self.connected_net.color[1],
                                         self.connected_net.color[2])
                canvas.setLineWidth(0.1)
                p = canvas.beginPath()
                p.moveTo( (self.x-self.r)*cm, (self.y-2*self.r)*cm )
                p.lineTo( (self.x+2*self.r)*cm, (self.y-2*self.r)*cm )
                p.lineTo( (self.x+2*self.r)*cm, (self.y+2*self.r)*cm )
                p.lineTo( (self.x-2*self.r)*cm, (self.y+2*self.r)*cm )
                p.lineTo( (self.x-2*self.r)*cm, (self.y-self.r)*cm )
                if self.id == "A0":
                    p.lineTo( (self.x-self.r)*cm, (self.y-2*self.r)*cm )
                else:
                    p.lineTo( (self.x-2*self.r)*cm, (self.y-2*self.r)*cm )
                    p.lineTo( (self.x-  self.r)*cm, (self.y-2*self.r)*cm )
                p.close()
                canvas.drawPath(p, fill=1, stroke=0)
                
        # draw circle for the ball
        canvas.setStrokeColor(black)
        canvas.setFillColor  (white)
        canvas.setLineWidth(1)
        p = canvas.beginPath()
        p.moveTo( (self.x-self.r)*cm, (self.y-2*self.r)*cm )
        p.circle( self.x*cm, self.y*cm, (self.r-0.05)*cm)
        canvas.drawPath(p, fill=1, stroke=1)

        # print the net id in the circle
        canvas.setFillColor (black)
        canvas.setFont("Helvetica", 2)
        if self.connected_net is None:
            s = "n.c."
        else:
            s = self.connected_net.id
        canvas.drawCentredString(self.x*cm, self.y*cm-4*self.r, s)

class BGA(PackObj):
    
    """
    create a BGA package object
    
    nb_x and nb_y parameters specify the number of balls in each direction
    """
    def __init__(self,nb_x,nb_y):
        print("\nPackage: created\n")
        self.nb_x   = nb_x
        self.nb_y   = nb_y
        self.marker = 0.3
        
        # create a pin list and add the ball array
        self.pinlist = PackObjList("pinlist")
        for x in range(0,nb_x):
            for y in range (0,nb_y):
                pin_id = chr(65+y)+str(x)
                self.pinlist.add(PinObj(self,pin_id,x,y))
        
        # create the netlist for the package        
        self.netlist = PackObjList("netlist")
        
        self.chiplist =ChipListObj(self)
                
    def check(self):
        print("BGA: check")
        self.pinlist.check()
        
    """
    create a plot of the package
    
    the methode requires a width and height parameter of the drawing to generate
    """    
    def plot(self,width,height):
        
        MARKER = self.marker
        
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.scale(width/(self.nb_x+2), height/(self.nb_y+2))  # Normalizing the canvas
        
        ctx.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(0.5)
        for x in range(0,self.nb_x):
            ctx.move_to(1.3+x,0.5)
            ctx.show_text(str(x))

        for y in range(0,self.nb_y):
            ctx.move_to(0.5,1.7+y)
            ctx.show_text(chr(65+y))
        
        # draw the package boundary
        ctx.translate(1,1) # move the coordinate origin 
        ctx.set_source_rgb(1, 1, 1)  # white fill

        ctx.move_to(MARKER,0)
        ctx.line_to(self.nb_x,        0) 
        ctx.line_to(self.nb_x,self.nb_y) 
        ctx.line_to(        0,self.nb_y) 
        ctx.line_to(        0,   MARKER)
        ctx.line_to(   MARKER,        0) 
        ctx.fill()

        # draw the balls
        ctx.translate(0.5,0.5) # move the coordinate origin before drawing the balls 
        self.pinlist.plot(ctx)
        
        ctx.translate(-0.5,-0.5) # move the coordinate origin back before drawing the border 
        ctx.set_source_rgb(0, 0, 0)  # black border
        ctx.set_line_width(0.1)
        ctx.move_to(MARKER,0)
        ctx.line_to(self.nb_x,        0) 
        ctx.line_to(self.nb_x,self.nb_y) 
        ctx.line_to(        0,self.nb_y) 
        ctx.line_to(        0,   MARKER)
        ctx.line_to(   MARKER,        0) 
        ctx.line_to(self.nb_x,        0) 
        ctx.stroke()
        
        surface.write_to_png("example.png")  # Output to PNG

class chip(PackObj):
    """
    object that collects the chip specification
    
    identifier specifies the toplevel chip hierarchy name
    x and y specifies the chip dimension in micrometer 
    """
    def __init__(self,package,identifier,x,y):
        super().__init__(identifier)
        print("chip: create chip object",identifier)
        self.size_x = x
        self.size_y = y
        self.padlist = PadListObj(package)

"""
draw the pinout
"""
class pinout_drawing(Flowable):
    def __init__(self, package, xoffset=0, size=None, fillcolor=white, strokecolor=black):
        if size is None: size=package.nb_y*cm
        self.fillcolor, self.strokecolor = fillcolor, strokecolor
        self.xoffset = xoffset
        self.size = size + 1*cm
        self.scale = size/(package.nb_y*cm)
        self.package = package
    def wrap(self, *args):
        return (self.xoffset, self.size)
    def draw(self):
        canvas = self.canv
        canvas.setStrokeColor(self.strokecolor)
        canvas.setFillColor(self.fillcolor)
        canvas.translate(self.xoffset+self.size,0)
        canvas.scale(self.scale, self.scale)
        
        canvas.translate(0.5*cm,0.5*cm)
        self.package.pinlist.draw(canvas)
        
        #draw package border
        canvas.translate(-0.5*cm,-0.5*cm)
        canvas.setLineWidth(2)
        p = canvas.beginPath()
        marker = self.package.marker
        nb_x   = self.package.nb_x
        nb_y   = self.package.nb_y
        p.moveTo(         0, marker*cm)
        p.lineTo(         0,   nb_y*cm)
        p.lineTo(   nb_x*cm,   nb_y*cm)
        p.lineTo(   nb_x*cm,         0)
        p.lineTo( marker*cm,         0)
        p.close()
        canvas.drawPath(p, fill=0)
        
        canvas.setFillColor (black)
        canvas.setFont("Helvetica", 8)
        for x in range(self.package.nb_x):
            canvas.drawCentredString( (0.5+x)*cm, -0.5*cm, str(x))
        for y in range(self.package.nb_y):
            canvas.drawCentredString( -0.5*cm, (y+0.5)*cm-4, chr(65+y))

        print("pinout drawing scale:",self.scale)

"""
draw the floorplan
"""
class floorplan_drawing(Flowable):
    def __init__(self, chip, xoffset=0, size=None, fillcolor=white, strokecolor=black):
        if size is None: size=chip.size_x*cm
        self.fillcolor, self.strokecolor = fillcolor, strokecolor
        self.xoffset = xoffset
        self.size = size + 1*cm
        self.scale = (14*cm)/size
        self.chip = chip
    def wrap(self, *args):
        return (self.xoffset, self.chip.size_y*cm*self.scale)
    def draw(self):
        canvas = self.canv
        canvas.setStrokeColor(self.strokecolor)
        canvas.setFillColor(self.fillcolor)
        canvas.scale(self.scale, self.scale)
#        canvas.translate(0,-0.3*cm)
        
        #draw package border
        canvas.setLineWidth(2/self.scale)
        p = canvas.beginPath()
#        size_x   = self.chip.size_x/10000*cm
#        size_y   = self.chip.size_y/10000*cm
        size_x   = self.chip.size_x*cm
        size_y   = self.chip.size_y*cm
        p.moveTo(         0,      0)
        p.lineTo(         0, size_y)
        p.lineTo(    size_x, size_y)
        p.lineTo(    size_x,      0)
        p.close()
        canvas.drawPath(p, fill=1)

        self.chip.padlist.draw(canvas)

        print("floorplan drawing scale:",self.scale)

"""
draw cover sheet pinout
"""
class cover_sheet(Flowable):
    def __init__(self, project, xoffset=0, size=None, fillcolor=white, strokecolor=black):
        if size is None: size=20*cm
        self.fillcolor, self.strokecolor = fillcolor, strokecolor
        self.xoffset = xoffset
        self.size = size
        self.scale = size/(20*cm)
        self.project = project
    def wrap(self, *args):
        return (self.xoffset, self.size)
    def draw(self):
        from datetime import date
        canvas = self.canv
        canvas.setStrokeColor(self.strokecolor)
        canvas.setFillColor(self.fillcolor)
        canvas.translate(self.xoffset+self.size,0)
        canvas.scale(self.scale, self.scale)

        canvas.setFillColor (black)
        canvas.setFont("Helvetica", 30)
        canvas.drawString( 0*cm, 10*cm, self.project)

        canvas.setFont("Helvetica", 20)
        canvas.drawString( 0*cm, 0*cm, "physical implementation specification")

        canvas.setFont("Helvetica", 10)
        canvas.drawString( 0*cm, -10*cm, "Date : " + str(date.today()))
        
        
            

class datasheet:
    
    def __init__(self,project,package):
        self.project = project
        self.package = package
        self.style = getSampleStyleSheet()
        self.cover_sheet = cover_sheet(project,-16*cm,16*cm)
        
    def pin_table(self):
        doc_data = []
        doc_data.append(Paragraph('Pin Table',self.style['Heading2']))
        doc_data.append(Paragraph('''The pin table list the pins of the package and the connected nets''',self.style['BodyText']))
        doc_data.append(Spacer(20*cm,1*cm))

        table_data = [("Net Name","Pin(s)")]
        for net in self.package.netlist:
            pins = None
            for pin in net.pinlist:
                if pins is None:
                    pins = pin.id
                else:
                    pins = pins + "," +pin.id
            table_data.append((net.id,pins))
        
        table = Table(table_data)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),
                                   ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                                   ('INNERGRID',(0,0),(-1,-1),0.25,colors.black),
                                   ('BOX',(0,0),(-1,0),1,colors.black),
                                   ('BOX',(0,0),(-1,-1),1,colors.black)]))
        doc_data.append(table)
        doc_data.append(PageBreak())
        return(doc_data)

    def pad_table(self,chip):
        doc_data = []

        doc_data.append(Paragraph('Pad Table',self.style['Heading3']))
        doc_data.append(Paragraph('''The pad table list the pads''',self.style['BodyText']))
        
        table_data = [("Net Name","Type","X","Y")]
        for pad in chip.padlist:
#            doc_data.append(Paragraph(pad.id,self.style['BodyText']))
            table_data.append((pad.id,"signal",pad.x,pad.y))

        table = Table(table_data)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),
                                   ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                                   ('INNERGRID',(0,0),(-1,-1),0.25,colors.black),
                                   ('BOX',(0,0),(-1,0),1,colors.black),
                                   ('BOX',(0,0),(-1,-1),1,colors.black)]))
        doc_data.append(table)

        return(doc_data)
        
    def chip_doc(self):
        doc_data = []

        for chip in self.package.chiplist:
            doc_data.append(Paragraph(chip.id,self.style['Heading2']))
    
            doc_data.extend(self.pad_table(chip))

            doc_data.append(Paragraph('Floorplan',self.style['Heading3']))
            doc_data.append(floorplan_drawing(chip))
            
        return(doc_data)

    def write_pdf(self,filename):
        #create list that will contain the content
        doc_data = []

        doc_data.append(self.cover_sheet)
        doc_data.append(PageBreak())

        doc_data.append(Paragraph('Package',self.style['Heading1']))

        #add pinout drawing
        doc_data.append(Paragraph('Pinout',self.style['Heading2']))
        doc_data.append(Paragraph('''The pinout drawing show the balls and the connected nets''',self.style['BodyText']))
        doc_data.append(pinout_drawing(self.package,-16*cm,16*cm))

        doc_data.append(PageBreak())

        #add pinout table
        doc_data.extend(self.pin_table())

        doc_data.extend(self.chip_doc())

        #create PDF
        pdf = SimpleDocTemplate(filename,pagesize=A4)
        pdf.build(doc_data)

        

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
CHIP_XDIM = 3000
CHIP_YDIM = 3000
mars = my_package.chiplist.add( CHIP_TOP,
                                 CHIP_XDIM,
                                 CHIP_YDIM )

mars.padlist.add("MISO",1000,1000)
mars.padlist.add("MOSI",2000,2000)

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

