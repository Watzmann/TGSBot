
import sys
import time

lap = 10.0

if len(sys.argv) > 1:
    #print sys.argv
    lap = float(sys.argv[1])
    
time.sleep(lap)