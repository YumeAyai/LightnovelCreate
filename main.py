import spider

from maker import epub
title = input('input Title :\n')
w_m = input("input Writer's 苗字 :\n")
w_n = input("input Writer's 名前 :\n")
epubObj = epub(title, w_m, w_n)
epubObj.addFile()
epubObj.close()

