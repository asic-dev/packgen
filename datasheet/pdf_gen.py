
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, Spacer, Table, TableStyle
from reportlab.lib.colors import darkgreen, tan, black, white
from reportlab.platypus.flowables import Flowable, Spacer
from reportlab.lib.units import cm

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
        
        #draw package border
        canvas.setLineWidth(2/self.scale)
        p = canvas.beginPath()
        size_x   = self.chip.size_x*cm
        size_y   = self.chip.size_y*cm
        p.moveTo(         0,      0)
        p.lineTo(         0, size_y)
        p.lineTo(    size_x, size_y)
        p.lineTo(    size_x,      0)
        p.close()
        canvas.drawPath(p, fill=1)

        self.chip.padlist.draw(canvas)
        self.chip.instlist.draw(canvas)

"""
draw the macro
"""
class macro_drawing(Flowable):
    def __init__(self, macro, fillcolor=white, strokecolor=black):
        self.fillcolor, self.strokecolor = fillcolor, strokecolor
        self.macro = macro
        self.macro.width = 200
        self.macro.height = 200
    def wrap(self, *args):
        return (self.macro.width, self.macro.height)
    def draw(self):
        canvas = self.canv
        canvas.setStrokeColor(self.strokecolor)
        canvas.setFillColor(self.fillcolor)
 #       canvas.scale(self.scale, self.scale)
        
        #draw package border
#        canvas.setLineWidth(2/self.scale)
        p = canvas.beginPath()
#        size_x   = self.chip.size_x*cm
#        size_y   = self.chip.size_y*cm
        p.moveTo(         0,      0)
        for point in self.macro.boundary:
            p.lineTo(point[0],point[1])
        p.close()
        canvas.drawPath(p, fill=1)


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
                if pin.type == "pin":
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

        doc_data.append(Paragraph('Pad List',self.style['Heading3']))
        doc_data.append(Paragraph('''The pad table list the pads''',self.style['BodyText']))
        
        table_data = [("Instance","Type","Net","X","Y")]
        for pad in chip.padlist:
            try:
                net = pad.connected_net.id
            except:
                net = ""
            table_data.append((pad.id,"signal",net,pad.x,pad.y))

        table = Table(table_data)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),
                                   ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                                   ('INNERGRID',(0,0),(-1,-1),0.25,colors.black),
                                   ('BOX',(0,0),(-1,0),1,colors.black),
                                   ('BOX',(0,0),(-1,-1),1,colors.black)]))
        doc_data.append(table)

        return(doc_data)
        
    def macro_table(self,chip):
        doc_data = []

        doc_data.append(PageBreak())
        doc_data.append(Paragraph('Macro List',self.style['Heading3']))
        
        table_data = [("Instance","Macro","Position")]
        for instance in chip.instlist:
            table_data.append((instance.id,instance.macro.id,"{},{}".format(instance.pos[0],instance.pos[1])))

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
            doc_data.append(Paragraph("Chip: {}".format(chip.id),self.style['Heading2']))
    
            doc_data.append(Paragraph('Floorplan',self.style['Heading3']))
            doc_data.append(floorplan_drawing(chip))
            
            doc_data.extend(self.pad_table(chip))
            doc_data.extend(self.macro_table(chip))
            doc_data.extend(self.macro_doc(chip.macrolist))

        return(doc_data)

    def macro_doc(self,macrolist):
        doc_data = []

        for macro in macrolist:
            doc_data.append(Paragraph("Macro: {}".format(macro.id),self.style['Heading3']))
            doc_data.append(Paragraph("Floorplan",self.style['Heading4']))
            doc_data.append(macro_drawing(macro))
        
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

