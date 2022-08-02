import urllib.request as ur
import time

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

def find_chapter(html):
    chapterStart = html.find("chapter_title")
    chapterEnd = html.find("</p>", chapterStart, chapterStart + 255)
    chapter = html[chapterStart + 15 : chapterEnd]
    return chapter


def find_before(html):
    content = []
    start = html.find('<p id="Lp1', 0, -1)
    end = html.find("</div>", start, -1)
    

    Ls = html.find('">', start, end)
    while Ls < end:
        Le = html.find("</p>", Ls, -1)
        if Le < end:
            if '<br />'==html[Ls + 2: Le]:
                content.append('\n')
            else:
                content.append(html[Ls + 2: Le])        
        else:
            break
        Ls = html.find('">', Le + 3, -1)
    return content
#(Ls:line start Le:line end)



def find_content(html):
    content = []
    start = html.find('<p id="L1', 0, -1)
    end = html.find("</div>", start, -1)


    Ls = html.find('">', start, end)
    while Ls < end:
        Le = html.find("</p>", Ls, -1)
        if Le < end:
            if '<br />'==html[Ls + 2: Le]:
                content.append('\n')
            else:
                content.append(html[Ls + 2: Le])        
        else:
            break
        Ls = html.find('">', Le + 3, -1)
    return content



def find_after(html):
    content = []
    start = html.find('<p id="La1', 0, -1)
    end = html.find("</div>", start, -1)


    Ls = html.find('">', start, end)
    while Ls < end:
        Le = html.find("</p>", Ls, -1)
        if Le < end:
            if '<br />'==html[Ls + 2: Le]:
                content.append('\n')
            else:
                content.append(html[Ls + 2: Le])        
        else:
            break
        Ls = html.find('">', Le + 3, -1)
    return content



def save_file(file_name, title, content_list):
    f = open(file_name, "a+", encoding="UTF-8")
    f.write(title + '\n\n'+'========================'+'\n')
    for content in content_list:
        f.write(content+'\n')
    f.close()



url='https://ncode.syosetu.com/'+input('input the cord of url novel'+'\n')+'/'
url='https://ncode.syosetu.com/n3862be/'
print('Check url: '+url)
url_number=232
#url_number=input('input the start of url number (type "0" if from first)'+'\n')
url_number_end=input('input the end of url number'+'\n')
print('Start')
if __name__ == "__main__":
    # html = url_open("https://ncode.syosetu.com/n3862be/{}.html")
    while url_number != url_number_end :
        url_number = url_number +1
        html = url_open(url+"{}.html". format(url_number)). decode("utf-8")
        print('url numbre = ','{}'. format(url_number),'')
        the_chapter = find_chapter(html)
        print(the_chapter)
        the_title = find_title(html)
        print(the_title)
        the_contents = find_before(html)+find_content(html)+find_after(html)
        # save
        save_file("{}.txt". format(the_chapter+" "+the_title), the_title, the_contents)
        print("save")
        
