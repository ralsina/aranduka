from feedparser import parse
from PyQt4 import QtGui, QtCore, QtWebKit, uic
import sys, os, urllib, urllib2
from elementtree.ElementTree import XML
from models import *
from pprint import pprint
from math import ceil
from pluginmgr import BookStore

# This gets the main catalog from feedbooks.

EBOOK_EXTENSIONS=['epub','mobi','pdf']

class Catalog(BookStore):

    title = "FeedBooks: Free and Public Domain Books"
    
    def __init__(self):
        print "INIT: feedbooks"
        self.widget = None
        self.w = None
        
    def setWidget (self, widget):
        self.widget = widget

    def treeItem(self):
        """Returns a QTreeWidgetItem representing this
        plugin"""
        return QtGui.QTreeWidgetItem(["FeedBooks"])

    def operate(self):
        "Show the store"
        if not self.widget:
            print "Call setWidget first"
            return
        self.widget.title.setText(self.title)
        if not self.w:
            uifile = os.path.join(
                os.path.abspath(
                    os.path.dirname(__file__)),'feedbooks_store.ui')
            self.w = uic.loadUi(uifile)
            self.pageNumber = self.widget.stack.addWidget(self.w)
            self.crumbs=[]
            self.openUrl(QtCore.QUrl('http://www.feedbooks.com/catalog.atom'))
            self.w.store_web.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateExternalLinks)
            self.w.store_web.page().linkClicked.connect(self.openUrl)
            self.w.crumbs.linkActivated.connect(self.openUrl)
            self.w.search_text.returnPressed.connect(self.doSearch)
            
        self.widget.stack.setCurrentIndex(self.pageNumber)
        

    @QtCore.pyqtSlot()
    def doSearch(self, *args):
        self.search(unicode(self.w.search_text.text()))
        
    def search (self, terms):
        url = "http://www.feedbooks.com/search.atom?"+urllib.urlencode(dict(query=terms))
        self.crumbs=[self.crumbs[0],["Search: %s"%terms, url]]
        self.openUrl(QtCore.QUrl(url))

    def openUrl(self, url):
        print "CRUMBS:", self.crumbs
        if isinstance(url, QtCore.QUrl):
            url = url.toString()
        url = unicode(url)
        extension = url.split('.')[-1]
        print "Opening:",url
        if url.split('/')[-1].isdigit():
            # A details page
            self.crumbs.append(["#%s"%url.split('/')[-1],url])
            self.showCrumbs()
            self.w.store_web.load(QtCore.QUrl(url))
        elif extension in EBOOK_EXTENSIONS:
            # It's a book, get metadata, file and download
            book_id = url.split('/')[-1].split('.')[0]
            bookdata = parse("http://www.feedbooks.com/book/%s.atom"%book_id).entries[0]
            title = bookdata.title
            book = Book.get_by(title = title)
            if not book:
                # Let's create a lot of data
                tags = []
                for tag in bookdata.tags:
                    t = Tag.get_by(name = tag.label)
                    if not t:
                        t = Tag(name = tag.label)
                    tags.append(t)
                ident = Identifier(key="FEEDBOOKS_ID", value=book_id)
                author = Author.get_by (name = bookdata.author)
                if not author:
                    author = Author(name = bookdata.author)
                book = Book (
                    title = title,
                    authors = [author],
                    tags = tags,
                    identifiers = [ident]
                )
            session.commit()
            
            # Get the file
            fname = os.path.abspath(os.path.join("ebooks", str(book.id) + '.' + extension))

            try:
                print "Fetching: ", url
                u=urllib2.urlopen(url)
                data = u.read()
                u.close()
                f = open(fname,'wb')
                f.write(data)
                f.close()
            except urllib2.HTTPError:
                pass
            f = File(file_name = fname)
            book.files.append(f)
            session.commit()
            book.fetch_cover("http://www.feedbooks.com/book/%s.jpg"%book_id)
            
        else:
            self.showBranch(url)

    def showCrumbs(self):
        ctext = []
        for c in self.crumbs:
            ctext.append('<a href="%s">%s</a>'%(c[1],c[0]))
        ctext = "&nbsp;>&nbsp;".join(ctext)
        self.w.crumbs.setText(ctext)

    def showBranch(self, url):
        print "Showing:", url
        data = parse(url)
        html = ["<h1>%s</h1>"%data.feed.title]
        crumb = [data.feed.title.split("|")[0].split("/")[-1].strip(), url]
        try:
            r=self.crumbs.index(crumb)
            self.crumbs=self.crumbs[:r+1]
        except ValueError:
            self.crumbs.append(crumb)
        self.showCrumbs()
        
        for entry in data.entries:
            iurl = entry.links[0].href

            # Find acquisition links
            acq_links = [l.href for l in entry.links if l.rel=='http://opds-spec.org/acquisition']
            acq_fragment = []
            for l in acq_links:
                acq_fragment.append('<a href="%s">%s</a>'%(l, l.split('.')[-1]))
            acq_fragment='&nbsp;|&nbsp;'.join(acq_fragment)
            
            if iurl.split('/')[-1].isdigit():
                # A book
                item = """
                <table><tr>
                    <td>
                    <img src=%s width="64px">
                    <td>
                        %s <a href="%s">[Details]</a></br>
                        Download: %s
                </table>
                """%(
                    iurl+".jpg",
                    entry.title,
                    iurl,
                    acq_fragment,
                    )
            elif len(entry.links) == 1:
                # A category without icon
                item = """
                <dd>
                    <a href="%s">%s</a>: %s
                </dd>--
                """%(
                    iurl,
                    entry.title,
                    entry.get('subtitle',''),
                    )
            else:
                # A book link, or a category with icons
                item = """
                <dd>
                    <img src="%s">
                    <a href="%s">%s</a>: %s
                </dd>
                """%(
                    entry.links[1].href,
                    iurl,
                    entry.title,
                    entry.get('subtitle',''),
                    )
            html.append(item)

        # Maybe it's paginated
        pCount = int(ceil(float(data.feed.get('opensearch_totalresults', 1))/int(data.feed.get('opensearch_itemsperpage', 1))))
        #from pudb import set_trace; set_trace()
        if pCount > 1:
            html.append("<div>")
            for pnum in range(1,pCount+1):
                html.append('<a href="%s&page=%s">%s</a>&nbsp;'%(url, pnum, pnum))
            html.append("</div>")
            
        html='\n'.join(html)
        self.w.store_web.setHtml(html)

    def on_catalog_itemExpanded(self, item):
        if item.childCount()==0:
            self.addBranch(item, item.url)

    def on_catalog_itemActivated(self, item, column):
        url=item.url
        if url.split('/')[-1].isdigit():
            # It's a book
            self.web.load(QtCore.QUrl(url))