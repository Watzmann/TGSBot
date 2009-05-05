import Image, os
import StringIO
import pdb

def recode(imgfile):
    tmp_in,tmp_out = ('img.tif','unc.tif')
    tmp_in = os.path.join('/tmp',tmp_in)
    tmp_out = os.path.join('/tmp',tmp_out)
    imgtmp = file(tmp_in,'wb')
    imgtmp.write(imgfile.read())
    imgtmp.close()
    os.system('tiffcp -c none %s %s' % (tmp_in,tmp_out))
    img = file(tmp_out,'rb')
    os.remove(tmp_in)
    return img,tmp_out

def bild(img):
    satz = StringIO.StringIO()
    img.save(satz,format='TIFF')
    satz.seek(0)
    return satz.read()

def zerleg(img):
    try:
        img.seek(0)
        img.seek(1)
        img.seek(0)
    except:
        return []
    lst = []
    idx = 0
    while 1:
        try:
            print '->',idx
            img.seek(idx)
            lst.append(bild(img))
            idx += 1
        except:
            break
    return lst

def mpage(imgfile,imgtitle):
    #pdb.set_trace()
    if not imgtitle:
        imgtitle = imgfile.filename
    imgfile.seek(0)
    imgfile,uncompressed = recode(imgfile)
    img = imgfile.read()
    single = [(img,imgtitle)]
    orig = StringIO.StringIO(img)
    img = Image.open(orig)
    imglst = zerleg(img)
    if not imglst:
        return single
    titlst = ['Seite %d' % (int(i)+1,) for i in range(len(imglst))]
    return zip(imglst,titlst)

if __name__ == '__main__':
    try:
        iName = sys.argv[1]
    except:
        iName = '_0309113009_001.tif'
    img = file(iName,'rb')
    lst = mpage(img,iName)
    print 'len',len(lst)
