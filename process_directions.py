import re
import glob
import numpy as np

arrow_dict = {'turn left':'&#8592',
             'continue':'&#8593',
             'turn right':'&#8594',
             'slight right':'&#8599',
             'slight left':'&#8598'
             }

HEADER = \
'''
<head>
<title> Day {:d} Queue sheet </title>
<link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=inconsolata">
<link rel="stylesheet" type="text/css" href="qstyle.css" />
</head>
'''

#height and width of pages
h_page = 17*72/4
w_page = 11*72/3
print(h_page,w_page)

#layout margins
h_marg = 9
w_marg = 7

#line height
h_text = 12

#box dims
h_box = h_page - 2*h_marg
w_box = w_page - 2*w_marg


#image dims
h_img = h_box - h_text
w_img = w_box

CHARS_PER_ROW = 41
ROWS_PER_PAGE = 24
DISTANCE_REGEX = re.compile('\d+[.,]?\d*\s+(mi|ft)',re.I)

for day_no,file_in in enumerate(sorted(glob.glob('*.txt'))):
    file_in='directions.txt'
    box_index=0
    pg_ct = 0
    pg_lnct = 0
    day_lnct = 0

    fin = open(file_in)

    line = fin.readline()
    start_page = '<div class=page>'
    end_page = '</div>'

    pages = list()

    pages_str = ''
    pages_str += start_page
    while not line=='':


        #figure out if next line is distance
        nline = fin.readline()
        if DISTANCE_REGEX.match(nline):
            line = line[:-1] +' '+ nline[:-1]
            nline = fin.readline()

        prefix=''
        for k,v in arrow_dict.items():
            if re.match(k,line,re.I):
                prefix = v
                line = re.sub(k+'\s+(onto|to)\s+','',line,flags=re.I)

        prefix = '{:d}) {}'.format(day_lnct,prefix)
        scraps = line
        step_lines = list()
        day_lnct += 1

        while not scraps=='':
            if len(scraps)<CHARS_PER_ROW:
                line=scraps
                scraps=''
            else:
                tks = np.array(scraps.split())
                lengths = np.cumsum([len(t) for t in tks])+np.arange(0,len(tks))
                line = ' '.join(tks[lengths<CHARS_PER_ROW])
                scraps = ' '.join(tks[lengths>=CHARS_PER_ROW])

            step_lines.append(r'<div class=box{}>'.format(box_index)
                              + ' '.join((prefix,line))
                              + r'</div>')
            prefix=' '

        if len(step_lines)+pg_lnct>=ROWS_PER_PAGE:
            pages_str += '<div class=box0></div>'*(ROWS_PER_PAGE - pg_lnct - 1)
            pages_str += r'<div class=pageno>'
            pages_str += '{:d}'.format(pg_ct)
            pages_str += r'</div>'
            pages_str += end_page
            pages.append(pages_str)
            pg_ct += 1

            pages_str = ''
            pages_str += start_page
            pages_str += '<img src=map_day{0:02}_pg{1:02}.png width={2:d} height={3:d} alt="map_day{0:02}_pg{1:02}.png">'.format(day_no,pg_ct, w_img, h_img)
            pages_str += r'<div class=pageno>'
            pages_str += '{:d}'.format(pg_ct)
            pages_str += r'</div>'
            pages_str += end_page
            pages.append(pages_str)
            pg_ct += 1

            pages_str = start_page
            pg_lnct = 0

        for l in step_lines:
            pages_str += l

        pg_lnct += len(step_lines)

        box_index = (box_index+1)%2
        line = nline

    pages_str += '<div class=box0></div>'*(ROWS_PER_PAGE - pg_lnct - 1)
    pages_str += r'<div class=pageno>'
    pages_str += '{:d}'.format(pg_ct)
    pages_str += r'</div>'
    pages_str += end_page
    pages.append(pages_str)
    pg_ct += 1

    pages_str = ''
    pages_str += start_page
    pages_str += '<img src=map_day{0:02}_pg{1:02}.png width={2:d} height={3:d} alt="map_day{0:02}_pg{1:02}.png">'.format(day_no,pg_ct, w_img, h_img)
    pages_str += r'<div class=pageno>'
    pages_str += '{:d}'.format(pg_ct)
    pages_str += r'</div>'
    pages_str += end_page
    pages.append(pages_str)
    pg_ct += 1

    for i in range(len(pages)//6):
        fout = open('day{:02d}_pg{:02d}.html'.format(day_no,i),'w')
        fout.write('<html>\n'+HEADER.format(day_no))
        for j,p in enumerate(pages[i*6:(i+1)*6]):
            s ='style="position: absolute; top: {}px; left: {}px;"'.format(h_page*(j//3),w_page*(j%3))
            fout.write('<div {}>{}</div>'.format(s,p))

        fout.write('</html>')
        fout.close()

    fin.close()
