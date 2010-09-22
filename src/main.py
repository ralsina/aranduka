"""The user interface for our app"""

import os,sys
import models, importer

# Import Qt modules
from PyQt4 import QtCore, QtGui, uic
from progress import progress
from book_editor import BookEditor
import rc_icons

from pluginmgr import manager

class SearchWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uifile = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),'searchwidget.ui')
        uic.loadUi(uifile, self)
        self.ui = self

class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        uifile = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),'main.ui')
        uic.loadUi(uifile, self)
        self.ui = self
        
        self.currentBook = None

        # View types toggles
        self.viewGroup = QtGui.QButtonGroup(self)
        self.viewGroup.setExclusive(True)
        self.viewGroup.addButton(self.gridMode)
        self.viewGroup.addButton(self.listMode)
        self.gridMode.setChecked(True)

        # Search Bar
        self.searchBar = QtGui.QToolBar()
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.searchBar)
        self.searchWidget = SearchWidget()
        self.searchBar.addWidget(self.searchWidget)
        self.searchBar.hide()
        self.searchWidget.closeBar.clicked.connect(self.searchBar.hide)

        # Plugins
        manager.locatePlugins()
        manager.loadPlugins()

        for plugin in manager.getPluginsOfCategory("ShelveView"):
            # Ways to fill the shelves
            item = plugin.plugin_object.treeItem()
            item.handler = plugin.plugin_object
            item.title = plugin.plugin_object.title
            plugin.plugin_object.setWidget(self)
            self.treeWidget.addTopLevelItem(item)

        for plugin in manager.getPluginsOfCategory("BookStore"):
            # Ways to fill the shelves
            item = plugin.plugin_object.treeItem()
            item.handler = plugin.plugin_object
            item.title = plugin.plugin_object.title
            plugin.plugin_object.setWidget(self)
            self.treeWidget.addTopLevelItem(item)

        self._layout = QtGui.QVBoxLayout()
        self.details.setLayout(self._layout)
        self.book_editor = BookEditor(None)
        self._layout.addWidget(self.book_editor)
        print "Finished initializing main window"

    def on_treeWidget_itemClicked(self, item):
        try:
            self.searchWidget.doSearch.clicked.disconnect()
        except TypeError: # Happens when there's no connections
            pass
        self.searchWidget.doSearch.clicked.connect(item.handler.doSearch)
        if self.gridMode.isChecked():
            item.handler.showGrid()
        else:
            item.handler.showList()

    def on_actionFind_triggered(self):
        self.searchBar.show()
        self.searchWidget.text.setFocus(True)

    def bookContextMenuRequested(self, book, point):
        """Given a book, and a place in the screen,
        shows a proper context menu for it"""

        self.currentBook = book
        menu = QtGui.QMenu()
        menu.addAction(self.actionEdit_Book)
        menu.addAction(self.actionOpen_Book)
        menu.addAction(self.actionDelete_Book)

        # Check what converters apply
        converters = []
        for plugin in manager.getPluginsOfCategory("Converter"):
            r = plugin.plugin_object.can_convert(book)
            if r:
                converters.append([plugin.plugin_object, r])

        if converters:
            # So, we can convert
            convert_menu = QtGui.QMenu("Convert")
            for plugin, formats in converters:
                for f in formats:
                    convert_menu.addAction("%s via %s"%(f, plugin.name),
                        lambda f = f : plugin.convert(book, f))

            menu.addMenu(convert_menu)
            
        menu.exec_(point)

    @QtCore.pyqtSlot()
    def on_actionOpen_Book_triggered(self):
        if not self.currentBook:
            return
        if self.currentBook.files:
            url = QtCore.QUrl.fromLocalFile(self.currentBook.files[0].file_name)
            print "Opening:", url
            QtGui.QDesktopServices.openUrl(url)

    def on_books_itemActivated(self, item):
        self.book_editor.load_data(item.book.id)
        self.title.setText('Editing properties of "%s"'%item.book.title)
        self.stack.setCurrentIndex(1)

    def show_shelves(self):
        if self.store_handler:
            del(self.store_handler)
            self.store_handler = None
        self.updateItem(self.books.currentItem())
        self.stack.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_actionImport_Files_triggered(self):
        fname = unicode(QtGui.QFileDialog.getExistingDirectory(self, "Import Folder"))
        if not fname: return
        # Get a list of all files to be imported
        flist = []
        for data in os.walk(fname, followlinks = True):
            for f in data[2]:
                flist.append(os.path.join(data[0],f))
        for f in progress(flist, "Importing Files","Stop"):
            status = importer.import_file(f)
            print status
        # Reload books
        self.shelves_handler.loadBooks()

    @QtCore.pyqtSlot()
    def on_actionImport_File_triggered(self):
        fname = unicode(QtGui.QFileDialog.getOpenFileName(self, "Import File"))
        if not fname: return
        status = importer.import_file(fname)
        self.shelves_handler.loadBooks()
            
    def updateItem(self, item):
        """Updates one item with the data for its book"""

        # Make sure we are updated from the DB
        if not item:
            return
            item.book = models.Book.get_by(id = item.book.id)
            cname = os.path.join("covers",str(item.book.id)+".jpg")
            item.setText(item.book.title)
            if os.path.isfile(cname):
                try:
                    icon =  QtGui.QIcon(QPixmap(cname).scaledToHeight(128))
                    item.setIcon(icon)
                except:
                    pass
        

def main():
    # Init the database before doing anything else
    models.initDB()

    # Again, this is boilerplate, it's going to be the same on
    # almost every app you write
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
