
import os

cmd=os.path.join('C:\Programme\RealVNC\VNC4','winvnc4.exe')
os.spawnl(os.P_NOWAIT,cmd, '-noconsole','RemoveWallpaper=1','QueryConnect=1','DisableOptions=1','PortNumber=5902')

