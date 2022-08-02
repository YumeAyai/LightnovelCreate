import urllib.request as ur
import time
import os

def url_open(url):
    time.sleep(0.1)
    req = ur.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/80.0.3987.116 Safari/537.36")

    response = ur.urlopen(req)
    html = response.read()

    return html


def find_title(html):
    titleStart = html.find("novel_subtitle")
    titleEnd = html.find("</p>", titleStart, titleStart + 255)
    title = html[titleStart + 16 : titleEnd]
    return title

def find_novel_title(html):
    titleStart = html.find('class="margin_r20">')
    titleEnd = html.find("</a>", titleStart, titleStart + 255)
    novel_title = html[titleStart + 19: titleEnd]
    return novel_title

def find_chapter(html):
    chapterStart = html.find("chapter_title")
    chapterEnd = html.find("</p>", chapterStart, chapterStart + 255)
    chapter = html[chapterStart + 15 : chapterEnd]
    return chapter


#def xml(html):
  #  xml_head=
    #return xml

def find_before(html):
    content = []
    start = html.find('<p id="Lp1', 0, -1)
    end = html.find("</div>", start, -1)
    content.append(html[start : end])
    return content



def find_content(html):
    content = []
    start = html.find('<p id="L1', 0, -1)
    end = html.find("</div>", start, -1)
    content.append(html[start : end])
    return content




def find_after(html):
    content = []
    start = html.find('<p id="La1', 0, -1)
    end = html.find("</div>", start, -1)
    content.append(html[start : end])
    return content



def save_file(file_name, title, content_list):
    f = open('./Text/{}'. format(file_name), "a+", encoding="UTF-8")

    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="ja" class="vrtl"><head>
<meta charset="UTF-8"/>
<title>"""+'{}'. format(novel_title)+"""</title>
<link rel="stylesheet" type="text/css" href="../Styles/style0010.css"/>
</head>
<body class="p-text">
<div class="main">"""+'\n')
    f.write("""<div class="start-3em">
<p class="mfont font-1em40" id="toc-006">"""+title+"""</p>
</div>"""+'\n')
    for content in content_list:
        f.write(content)
    f.close()

def save_list(url_number, the_chapter, the_title):
    f = open('./Text/{}'. format("list.xml"), "a+", encoding="UTF-8")
    f.write('\t<id>{}</id>'. format(url_number))
    f.write('<chapter>{}</chapter>'. format(the_chapter))
    f.write('<title>{}</title>'. format(the_title)+'\n')
    f.close()





url='https://ncode.syosetu.com/'+input('input the cord of novel'+'\n')+'/'
print('Check url: '+url)
url_number=0
url_number=int(input('url number from: '))-1
url_number_end=int(input('url number to: '))
print('Start')
if not os.path.exists('Text'):
    os.mkdir('Text')
    # html = url_open("https://ncode.syosetu.com/n3862be/{}.html")
list = open("./Text/list.xml", "a+", encoding="UTF-8")
list.write("""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="testxsl.xsl"?>
<body>\n""")
list.close()
while url_number != url_number_end :
    url_number = url_number + 1
    html = url_open(url+"{}.html". format(url_number)). decode("utf-8")
    print('url number : ','{}'. format(url_number),'')
    novel_title=find_novel_title(html)
    the_chapter = find_chapter(html)
    print(the_chapter)
    the_title = find_title(html)
    print(the_title)
    the_contents = ['\n']+find_before(html)+find_content(html)+find_after(html)+['</div>'+'\n'+'</body></html>']
    # save
    save_file("Ep {}.html". format(url_number), the_title, the_contents)
    save_list(url_number, the_chapter, the_title)
    print("save")
list = open("./Text/list.xml", "a+", encoding="UTF-8")
list.write("""</body>\n""")
list.close()
        
        
