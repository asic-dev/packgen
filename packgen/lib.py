import cairo
import math

from reportlab.lib.units import cm
from reportlab.lib.colors import darkgreen, tan, black, white


class PackObj:

    """
    abstract base class to derive package generation objects
    """ 
    
    def __init__(self,object_id):
#        print("PackObj: created ",object_id)
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

    def num_items(self):
        return(len(self.__dict))

    """
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

class ShapeObj(PackObj):
    """
    generic shape object that draws the boundary
    
    identifier: specifies the shape name
    boundary:   list of (x,y) tuple that specifies the boundary polygon;
                specify only one tuple for a rectangular boundary 
    """
    def __init__(self, identifier, boundary):
        super().__init__(identifier)
        self.boundary = boundary
        
        min_x = max_x = boundary[0][0]
        min_y = max_y = boundary[0][1]
        for point in boundary:
            if point[0]<min_x:
                min_x = point[0]
            if point[0]>max_x:
                max_x = point[0]
            if point[1]<min_y:
                min_y = point[1]
            if point[1]>max_y:
                max_y = point[1]
                
        print("min:",min_x,min_y)
        print("max:",max_x,max_y)
        
        self.width_x = max_x - min_x
        self.width_y = max_y - min_y
        
        print("width:",self.width_x,self.width_y)
            

    """
    draw shape boundary
    """ 
    def draw(self,canvas):
        canvas.setStrokeColor(black)
        canvas.setFillColor  (white)
        canvas.setLineWidth(1)

        p = canvas.beginPath()
        start_point = self.boundary[0]
        p.moveTo( start_point[0]*cm, start_point[1]*cm )
        for point in self.boundary:
            p.lineTo( point[0]*cm, point[1]*cm )
        p.lineTo( start_point[0]*cm, start_point[1]*cm )
        canvas.drawPath(p, fill=1, stroke=1)

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
        self.padlist = PadListObj(self)
        self.macrolist = MacroListObj(self)
        self.instlist = MacroInstListObj(self)

class MacroListObj(PackObjList):
    """
    list of macros
    """
    def __init__(self,parent):
        super().__init__("{}.macro_list".format(parent.id))
        self.parent = parent

    def add(self,id,boundary,spec = None):
        macro = MacroObj(self.parent,id,boundary)

        if spec is not None:
            for pin in spec["pin_spec"]:
                pos_x = spec["pin_spec"][pin]["xpos"]
                pos_y = spec["pin_spec"][pin]["ypos"]
                p = macro.add_pin(pin,(pos_x,pos_y))
                p.set_type(spec["pin_spec"][pin]["type"])
                p.set_related_ground(spec["pin_spec"][pin]["rel_gnd"])
                p.set_related_supply(spec["pin_spec"][pin]["rel_supply"])
                
            try:
                for macro_inst in spec["macro_spec"]:
                    pos_x = spec["macro_spec"][macro_inst]["xpos"]
                    pos_y = spec["macro_spec"][macro_inst]["ypos"]
                    macro.add_macro(macro_inst,spec["macro_spec"][macro_inst]["macro"],(pos_x,pos_y))
            except:
                None
                
        
        return(super().add(macro))
    
        
class MacroObj(ShapeObj):
    """
    object that collects the specification of a macro
    
    identifier: specifies the macro name
    boundary:   list of (x,y) tuple that specifies the boundary polygon;
                specify only one tuple for a rectangular boundary 
    """
    def __init__(self,parent,identifier, boundary):

        # if only one coordiate tuple is supplied as boundary create a rectangular boundary
        if len(boundary) == 1:
            max_x = boundary[0][0]
            max_y = boundary[0][1]
            boundary = [ (     0,     0) ,
                         ( max_x,     0) ,
                         ( max_x, max_y) ,
                         (     0, max_y)  ]

        super().__init__(identifier,boundary)
        self.parent = parent
            
        self.plist = PackObjList(self)
        self.mlist = MacroInstListObj(self)
        
        self.macrolist = parent.macrolist
        
    def add_pin(self,id,pos=None):
        print("MacroObj.add_pin:",id)
        if pos is None:
            return()
        return(self.plist.add(MacroPinObj(id,pos)))
        
    def add_macro(self,id,ref,pos):
        self.mlist.add(id,ref,pos)

    def draw(self,canvas):
        super().draw(canvas)
        for pin in self.plist:
            canvas.translate(pin.pos[0]*cm, pin.pos[1]*cm)
            pin.draw(canvas)
            canvas.translate(-pin.pos[0]*cm, -pin.pos[1]*cm)
        for macro in self.mlist:
            canvas.translate(macro.pos[0]*cm, macro.pos[1]*cm)
            macro.draw(canvas)
            canvas.translate(-macro.pos[0]*cm, -macro.pos[1]*cm)

class MacroInstObj(PackObj):
    """
    macro instance object
    
    identifier: specifies the instance name
    parent:     macro that instantiate this instance
    pos:        (x,y) tuple that specifies the macro positions in micrometer
    """
    def __init__(self,parent,identifier, macro, pos):
        super().__init__(identifier)
        self.parent = parent
        self.pos = pos
        self.macro = parent.macrolist.get(macro)
    """
    draw macro boundary
    """ 
    def draw(self,canvas):
        self.macro.draw(canvas)

class MacroInstListObj(PackObjList):
    """
    list of macros instances
    """
    def __init__(self,parent):
        super().__init__("{}.macro_instance_list".format(parent.id))
        self.parent = parent

    def add(self,id,ref,pos):
        return(super().add(MacroInstObj(self.parent,id,ref,pos)))
    
    def draw(self,canvas):
        for item in self:
            canvas.translate(item.pos[0]*cm, item.pos[1]*cm)
            item.draw(canvas)
            canvas.translate(-item.pos[0]*cm, -item.pos[1]*cm)
            
class PadListObj(PackObjList):
    """
    pad list object is a list of pads
    """
    def __init__(self,chip):
        super().__init__("pad_list")
        self.chip = chip

    def add(self,id,ref,x,y):
        pad = PadInstObj(id,self.chip.macrolist.get(ref),x,y)
        super().add(pad)
        return(pad)
    
        
class NetObj(PackObj):
    
    """
    Is an object that collects which pins are connected to a net and which pad cells are connected to this net
    """
    def __init__(self,object_id):
        super().__init__(object_id)
        self.pinlist = PackObjList("pinlist")
        self.padlist = PackObjList("padlist")
        self.color = None

class MacroPinObj(ShapeObj):
    
    def __init__(self,id,pos):
            boundary = [ ( -1, -1) ,
                         (  1, -1) ,
                         (  1,  1) ,
                         ( -1,  1)  ]
            super().__init__(id, boundary)
            self.pos = pos
            self._type = "tbd"
            self._type_str_dict = {
                    "tbd"     : "tbd.",
                    "clk_in"  : "clock input",
                    "sig_in"  : "signal input",
                    "sig_out" : "signal output",
                    "ana_in"  : "analog signal input",
                    "ana_out" : "analog signal output",
                    "supply"  : "supply",
                    "ground"  : "ground"
                } 
            self._related_ground = "tbd"
            self._related_supply = "tbd"
    """
    set type of the pin
    possible types are: "clk_in", "sig_in", "sig_out", ...
    """        
    def set_type(self,type):
        self._type = type
        
    def set_related_ground(self,ground_pin):
        self._related_ground = ground_pin
        
    def set_related_supply(self,supply_pin):
        self._related_supply = supply_pin
        
    def get_type_str(self):
        return(self._type_str_dict[self._type])
    
    def get_rel_gnd_str(self):
        return(self._related_ground)
    
    def get_rel_sup_str(self):
        return(self._related_supply)
    
    def is_pg_pin(self):
        if self._type == "supply" or self._type == "ground":
            return(True)
        else:
            return(False)
            
        
        
class PinObj(PackObj):
    
    """
    Is a object that collects all information of a package pin.
    
    A package pin has an identifier (0,1,2,... for QFN) or (A0,A1,...,B0,B1,... for BGA)
    A package pin also has a list of connected IC pads and connected package pins
    A package pin also has a geometry information of the x and y location
    """
    def __init__(self,package,object_id,x,y):
        super().__init__(object_id)
        self.type = "pin"
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

class PadInstObj(PackObj):
    """
    Pad instance object
    """
    def __init__(self,id,ref,x,y):
        super().__init__(id)
        self.type = "pad"
        self.ref = ref
        self.x = x
        self.y = y

    """
    draw macro boundary
    """ 
    def draw(self,canvas):
        canvas.translate(self.x*cm, self.y*cm)
        self.ref.draw(canvas)
        canvas.translate(-self.x*cm, -self.y*cm)

class ChipListObj(PackObjList):
    """
    list of chips in a package
    """
    def __init__(self,package):
        super().__init__("chip_list")
        self.package = package

    def add(self,id,x,y):
        return(super().add(chip(self.package,id,x,y)))
    

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

