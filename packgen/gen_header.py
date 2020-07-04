from datetime import datetime

def gen_header_str():
    
    comment_start = "/*"
    comment_end   = "*/"
    
    print("gen_header_str executed")
    print("  comment_start : {}".format(comment_start))
    
    now = datetime.now() # current date and time
    
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print("  date and time:",date_time)
    
