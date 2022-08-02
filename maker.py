# encoding:utf-8
# !/usr/bin/python3
from itertools import count
from re import T
from tkinter import W
from unittest import TestCase
import zipfile
import os.path
import  xml.dom.minidom

#生成META_INF/container.xml内容
container_template = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
      
   </rootfiles>
</container>
    '''
#生成content.opf内容            需要写目录获取什么的spine,manifest,guide
content_template = '''<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="2.0">
  <metadata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:calibre="http://calibre.kovidgoyal.net/2009/metadata" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:publisher>株式会社ＫＡＤＯＫＡＷＡ</dc:publisher>
    <meta name="calibre:title_sort" content="%(title)s"/>
    <dc:language>ja</dc:language>
    <dc:creator opf:file-as="%(w_n)s, %(w_m)s" opf:role="aut">%(w_m)s %(w_n)s</dc:creator>
    <meta name="calibre:timestamp" content="2022-03-13T01:38:04.636000+00:00"/>
    <dc:title>%(title)s</dc:title>
    <meta name="cover" content="cover"/>
    <dc:date>2022-03-09T16:00:00+00:00</dc:date>
    <dc:contributor opf:role="bkp">calibre (1.48.0) [http://calibre-ebook.com]</dc:contributor>
    <dc:identifier opf:scheme="MOBI-ASIN">B09T2MKPYM</dc:identifier>
    <dc:identifier id="uuid_id" opf:scheme="uuid">ef8fc1f4-b5ad-48b2-aa0a-86f2640611f6</dc:identifier>
    <dc:identifier opf:scheme="calibre">ef8fc1f4-b5ad-48b2-aa0a-86f2640611f6</dc:identifier>
  </metadata>
  <manifest>
    <item href="cover.jpeg" id="cover" media-type="image/jpeg"/>
    %(manifest)s
    <item href="Styles/page_styles.css" id="page_css" media-type="text/css"/>
    <item href="Styles/stylesheet.css" id="css" media-type="text/css"/>
    <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx" page-progression-direction="rtl">
    <itemref idref="cover" linear="no"/>
    <itemref idref="content"/>
    %(spine)s
  </spine>
  <guide>
    <reference href="text/part0000.html" title="本編" type="text"/>
    <reference href="titlepage.xhtml" title="Cover" type="cover"/>
    <reference href="contents.xhtml" title="Table of Contents" type="toc"/>
  </guide>
</package>
   '''
#生成toc.ncx中的nav
nav_template='''<navPoint id="navPoint-%(id)s" playOrder="%(id)s">
      <navLabel>
        <text>%(ep_title)s</text>
      </navLabel>
      <content src="Text/%(html_filname)s"/>
    </navPoint>'''
#生成toc.ncx内容
toc_template = '''<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="jpn">
  <head>
    <meta content="ef8fc1f4-b5ad-48b2-aa0a-86f2640611f6" name="dtb:uid"/>
    <meta content="2" name="dtb:depth"/>
    <meta content="calibre (1.48.0)" name="dtb:generator"/>
    <meta content="0" name="dtb:totalPageCount"/>
    <meta content="0" name="dtb:maxPageNumber"/>
  </head>
  <docTitle>
    <text>%(title)s</text>
  </docTitle>
  <navMap>
    %(navList)s
  </navMap>
</ncx>
'''
#生成
dir_temple = '''
<div class="sgc-toc-level-1">
  <a href=%(html_filname)s>%(ep_title)s</a>
</div>
'''
#生成小说内部目录contents章节名和章节序号
novelList ='<p class="calibre1"><a href="%(html_filname)s#toc-001" class="calibre2 pcalibre pcalibre4 pcalibre3 pcalibre2 pcalibre1">１　%(ep_title)s</a></p></div>'
#生成小说内部目录contents内容
content_html_template = '''<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="ja" class="vrtl">
  <head>
    <title>%(title)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  <link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css"/>
<link href="../Styles/page_styles.css" rel="stylesheet" type="text/css"/>
</head>
  <body class="p-text">
<div class="main2">

<p class="calibre1">　<span class="font-1em">CONTENTS</span></p>
<p class="calibre1"><br class="main"/></p>
<p class="calibre1"><br class="main"/></p>
<div class="font-1em1">

%(novelList)s

</div>
</body></html>
'''

class epub:
    def __init__(self, title, w_m, w_n):
        self.title = title
        self.w_m = w_m
        self.w_n = w_n
        # acreate zip file
        self.epubFile = zipfile.ZipFile('%s.epub' % title, 'w')
        self.manifest = ''
        self.spine = ''
        self.toc_navList = ''
        self.id = 0
        self.dirList = ''
        self.novelList = ''
        self.ep_title = ''
        #
        self.spine += '<itemref idref=".xhtml"/>'
        self.create_mimetype()
        self.create_container()
        self.create_stylesheet()
    def setAutho(self, autho):
        self.autho = autho
    def setType(self, type):
        self.type = type
    def addFile(self):
        # 总体思路：
        # 1.打开Text文件夹
        # 2.逐个读取html文件
        # 3.添加toc content标记
        # 4.循环
        count = 0
        #打开xml文档
        dom = xml.dom.minidom.parse('./Text/list.xml')
        #得到文档元素对象
        root = dom.documentElement
        idFind = root.getElementsByTagName('id')
        titleFind = root.getElementsByTagName('title')

        #x=xmlDoc.getElementsByTagName("title");
        #document.write(idFind[count].childNodes[0].nodeValue);
        #循环所有元素
        while count<idFind.length :
            self.id= idFind[count].childNodes[0].nodeValue
            print("self.id:", self.id)
            self.ep_title= titleFind[count].childNodes[0].nodeValue
            print("self.ep_title:", self.ep_title)
            html_filname = "Ep %s.html" % self.id
            #这里要改成自动获取目录
            #content.opf
            self.manifest += '<item href="Text/%s" id="%s" media-type="application/xhtml+xml"/>' % (html_filname, self.id)
            self.spine += '<itemref idref="id%s"/>' % (self.id)
            #toc.ncx
            self.toc_navList += nav_template % {"id": self.id, "ep_title": self.ep_title, "html_filname" : html_filname}
            #content.html
            self.novelList += novelList % {"html_filname": html_filname, "ep_title": self.ep_title}
            print("html_filname:", html_filname)
            #这个干什么的还不知道
            self.dirList += dir_temple % {"html_filname" : html_filname, "ep_title": self.ep_title}
            self.epubFile.write('./Text/' + html_filname, 'OEBPS/Text/' + html_filname, compress_type=zipfile.ZIP_DEFLATED)
            count= count+1
        

    def close(self):
        # save zip file
        self.create_toc()
        self.create_content_file()
        self.epubFile.close()
    def create_mimetype(self):
        self.epubFile.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
    def create_container(self):
        self.epubFile.writestr('META-INF/container.xml', container_template, compress_type=zipfile.ZIP_STORED)
    def create_toc(self):
        self.epubFile.writestr('OEBPS/toc.ncx', toc_template % {"title": self.title, "navList": self.toc_navList}, compress_type=zipfile.ZIP_STORED)
        self.epubFile.writestr('OEBPS/Text/Contents.xhtml', content_html_template % {"title": self.title, "novelList": self.novelList }, compress_type=zipfile.ZIP_STORED)
    def create_content_file(self):
        self.epubFile.writestr('OEBPS/content.opf', content_template % {
            'title': self.title,
            'w_m': self.w_m,
            'w_n': self.w_n,
            'manifest': self.manifest,
            'spine': self.spine, },
                      compress_type=zipfile.ZIP_STORED)
    def create_stylesheet(self):
        css1_info = '''.align-end {
    display: block;
    height: auto;
    text-align: right;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0
    }
.author {
    display: block;
    font-family: serif-ja, serif;
    font-size: 0.83333em;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0 0 0.4em;
    border-bottom: black solid 1px;
    margin: 0.6em 0 0.9em
    }
.book-title-main {
    display: block;
    font-family: serif-ja, serif;
    font-size: 1.29167em;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0
    }
.calibre {
    display: block;
    font-size: 2em;
    line-height: 1.2;
    padding: 0;
    margin: 0 5pt
    }
.calibre1 {
    display: block;
    height: auto;
    text-indent: inherit;
    width: auto;
    padding: 0;
    margin: 0
    }
.calibre2 {
    background: transparent;
    color: inherit;
    font-style: inherit;
    font-weight: inherit;
    text-decoration: overline
    }
.calibre3 {
    display: block;
    height: auto;
    line-height: 1.2;
    text-indent: inherit;
    width: auto;
    padding: 0;
    margin: 0
    }
.copyright {
    display: block;
    font-size: 0.75em;
    height: auto;
    line-height: 1.2;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0.6em 0 0
    }
.em-sesame {
    -webkit-text-emphasis-style: filled sesame
    }
.fit {
    background: transparent;
    display: inline-block;
    height: auto;
    page-break-inside: avoid;
    vertical-align: baseline;
    width: auto;
    padding: 0;
    border: currentColor none medium;
    margin: 0
    }
.font-0em {
    display: block;
    font-size: 0.83333em;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0
    }
.font-1em {
    font-size: 1.29167em
    }
.font-1em1 {
    display: block;
    font-size: 1.29167em;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0
    }
.font-1em2 {
    display: block;
    font-size: 1.29167em;
    height: auto;
    text-indent: inherit;
    width: auto;
    padding: 0;
    margin: 0
    }
.gaiji {
    background: transparent;
    display: inline-block;
    height: 1em;
    vertical-align: baseline;
    width: 1em;
    padding: 0;
    border: currentColor none medium;
    margin: 0
    }
.gaiji-wide {
    background: transparent;
    display: inline-block;
    height: 1em;
    vertical-align: baseline;
    width: auto;
    padding: 0;
    border: currentColor none medium;
    margin: 0
    }
.label {
    display: block;
    height: auto;
    line-height: 1.2;
    text-indent: 0;
    width: auto;
    padding: 0 0 0.3em;
    margin: 0
    }
.label-name {
    display: block;
    font-family: sans-serif-jp, sans-serif;
    font-size: 0.75em;
    height: auto;
    text-indent: inherit;
    width: auto;
    padding: 0;
    margin: 0
    }
.main {
    display: block
    }
.main1 {
    display: block;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0
    }
.main2 {
    display: block;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 2em 0 0
    }
.main3 {
    display: block;
    height: auto;
    line-height: 1.6;
    text-align: left;
    text-indent: 0;
    width: auto;
    padding: 2em 1em 1em;
    margin: 0 auto
    }
.original-books {
    display: block;
    font-size: 0.75em;
    height: auto;
    line-height: 1.2;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 1em 0 0
    }
.original-title {
    display: block;
    height: auto;
    line-height: 1.2;
    text-indent: inherit;
    width: auto;
    padding: 0;
    margin: 0.5em 0 0
    }
.p-caution {
    -epub-hyphens: auto;
    -epub-line-break: normal;
    -epub-text-underline-position: under left;
    -epub-word-break: normal;
    -webkit-hyphens: auto;
    -webkit-line-break: normal;
    -webkit-text-underline-position: under left;
    -webkit-word-break: normal;
    background: transparent;
    display: block;
    font-size: 0.83333em;
    letter-spacing: normal;
    line-height: 1.75;
    text-align: justify;
    text-indent: 0;
    vertical-align: baseline;
    white-space: normal;
    word-spacing: normal;
    word-wrap: break-word;
    padding: 0;
    margin: 0 5pt
    }
.p-text {
    -epub-hyphens: auto;
    -epub-line-break: normal;
    -epub-text-underline-position: under left;
    -epub-word-break: normal;
    -webkit-hyphens: auto;
    -webkit-line-break: normal;
    -webkit-text-underline-position: under left;
    -webkit-word-break: normal;
    background: transparent;
    display: block;
    font-size: 1em;
    letter-spacing: normal;
    line-height: 1.75;
    text-align: justify;
    text-indent: 0;
    vertical-align: baseline;
    white-space: normal;
    word-spacing: normal;
    word-wrap: break-word;
    padding: 0;
    margin: 0 5pt
    }
.release-date {
    display: block;
    font-size: 0.83333em;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 1em 0 0
    }
.release-version {
    display: block;
    font-size: 0.75em;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0
    }
.start-1em {
    display: block;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 1em 0 0
    }
.start-7em {
    display: block;
    height: auto;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 7em 0 0
    }
.support {
    display: block;
    font-size: 0.75em;
    height: auto;
    line-height: 1.2;
    text-indent: 0;
    width: auto;
    padding: 0;
    margin: 0.5em 0 0
    }
.tcy {
    -webkit-text-combine: horizontal;
    -webkit-text-combine-upright: all;
    text-combine-upright: all
    }
.pcalibre1:visited {
    color: #00f
    }
.pcalibre3:link {
    color: #00f
    }
.pcalibre4:focus {
    color: #00f
    }
.pcalibre2:hover {
    color: #00f
    }
.pcalibre:active {
    color: #00f
    }

        '''
        css2_info = '''@page {
    margin-bottom: 5pt;
    margin-top: 5pt
    }
'''
        self.epubFile.writestr('OEBPS/Styles/stylesheet.css', css1_info, compress_type=zipfile.ZIP_STORED)
        self.epubFile.writestr('OEBPS/Styles/page_styles.css', css2_info, compress_type=zipfile.ZIP_STORED)

if __name__ == '__main__':
    #path = 'E:\\python\\epub_test\\test1'
    #create_archive(path)
    title = input('input Title :\n')
    w_m = input("input Writer's 苗字 :\n")
    w_n = input("input Writer's 名前 :\n")
    epubObj = epub(title, w_m, w_n)
    epubObj.addFile()
    epubObj.close()


