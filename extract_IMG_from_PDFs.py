# # Extract jpg's from pdf's. Quick and dirty.
# import sys

# pdf = open('tabela.pdf', "rb").read()

# startmark = "\xff\xd8"
# startfix = 0
# endmark = "\xff\xd9"
# endfix = 2
# i = 0

# njpg = 0
# while True:
#     istream = pdf.find("stream", i)
#     print("istream: ", istream)
#     if istream < 0:
#         break
#     istart = pdf.find(startmark, istream, istream+20)
#     print("istart: ", istart)
#     if istart < 0:
#         i = istream+20
#         continue
#     iend = pdf.find("endstream", istart)
#     print("iend 1 : ", iend)
#     if iend < 0:
#         raise Exception("Didn't find end of stream!")
#     iend = pdf.find(endmark, iend-20)
#     print("iend 2 : ", iend)
#     if iend < 0:
#         raise Exception("Didn't find end of JPG!")
    
#     istart += startfix
#     iend += endfix
#     print (njpg, istart, iend)
#     jpg = pdf[istart:iend]
#     jpgfile = file("imagens/jpg%d.jpg" % njpg, "wb")
#     jpgfile.write(jpg)
#     jpgfile.close()
    
#     input(">> ")
#     njpg += 1
#     i = iend


########################################################################3
#!/usr/bin/env python
chunk = 1048576 * 4
# http://www.obrador.com/essentialjpeg/headerinfo.htm
start_of_image = soi = '\xff\xd8\xff\xe0'
jfif_id = 'JFIF\x00'
diffie_quant_marker = '\xff\xdb'
diffie_huffman_marker = '\xff\xc4'
frame_marker = '\xff\xc0'
scan_marker = '\xff\xda'
comment_marker = '\xff\xee'
end_of_image = eoi = '\xff\xd9'

def extra_check(string):
    """An extra check to make sure we're looking at a jpeg file..."""
    return jfif_id in string[:11]

def slice_image(img):
    """Find the EOI marker assuming we are at the beginning of a jpeg file."""
    dqm_loc = img.find(diffie_quant_marker)
    dhm_loc = img.find(diffie_huffman_marker, dqm_loc)
    frm_loc = img.find(frame_marker, dhm_loc)
    smk_loc = img.find(scan_marker, frm_loc)
    com_loc = img.find(comment_marker, smk_loc)
    eoi_loc = img.find(end_of_image, com_loc)
    return img[:eoi_loc+2]

def generate_jpeg_files(f):
    """A generator that spits out strings that match jpeg files.  `f` is a
    file opened in binary mode."""
    eof = False
    s = ''
    while not eof:
        while soi not in s:
            s = f.read(chunk)
            if not s:
                eof = True
                break
        img_loc = s.find(soi)
        img = s[img_loc:]
        if len(img) < 11:
            extra = f.read(chunk)
            img += extra
            s += extra
        if not extra_check(img):
            # hmm.. it wasn't a jpeg after all, continue
            s = s[img_loc+1:]
            continue
        image = slice_image(img)
        s = s[img_loc + len(image):]
        yield image

def find_all_images(filename, threshold=None):
    f = open(filename, 'rb')
    image_generator = generate_jpeg_files(f)
    print(image_generator)
    for num,img in enumerate(image_generator):
        ifile = open('potential_image_%04d.jpg' % num, 'wb')
        ifile.write(img)
        ifile.close()
        if threshold and num > threshold:
            break
    f.close()

if __name__ == '__main__':
    # import optparse
    # parser = optparse.OptionParser(usage='%prog [opts] filename', version='1.0')
    # parser.add_option('-t', '--threshold', help='maximum number of image files to extract')
    # opts, args = parser.parse_args()
    # threshold = int(opts.threshold) if opts.threshold else None
    print("indo")
    find_all_images('Prova.pdf')
    print("foi")