#!/usr/bin/env python
# -*- coding: latin -*-

import sys, urllib2
from PyQt4 import QtCore, QtGui, uic
from gdata.books.service import BookService
servicio = BookService()

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType('interface.ui')

class GBooks(QtGui.QMainWindow, form_class):
    def __init__(self, *args):
        super(GBooks, self).__init__(*args)
        self.setupUi(self)

    def validaISBN(self,isbn):
        """
        Validar codigo ISBN. Devuelve el ISBN ó 0 si no es válido.
        """
        #TODO: deberia validar el ISBN con la cuenta

        #isbn.replace("-","") #Por ahora, lo mas sencillo

        isbn = ''.join(c for c in isbn if c.isdigit())

        #Intento de validación de ISBN según artículo de Paenza en Pag.12
        #ref: http://www.pagina12.com.ar/diario/contratapa/13-113285-2008-10-14.html
        #Aparentemente se podría corregir el error pero me dio fiaca..:)
        total = 0
        for i,n in enumerate(isbn):
            total = total + (i+1) * int(n)

        if total % 11 == 0:
            return isbn
        else:
            return 0


    def buscarLibro(self):
        """
        Busca un libro por ISBN en GoogleBooks y devuelve un dict con todos los datos.
        """
        isbn = self.validaISBN(str(self.isbnEdit.text()))
        if isbn:
            resultado = servicio.search('ISBN' + isbn)
            if resultado.entry:
                return resultado.entry[0].to_dict()

    def on_actionBuscarLibro_triggered(self, checked = None):
        if checked == None: return

        datos = self.buscarLibro()

        if not datos:
            QtGui.QMessageBox.critical(self,
                                       self.trUtf8("Error"),
                                       self.trUtf8("Por favor revise el ISBN, parece ser erróneo."),
                                       QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Ok)
                                       )
            return

        identifiers = dict(datos['identifiers'])
        print datos['identifiers']
        print identifiers
        if datos:
            self.tituloLibro.setText(datos['title'])
            self.fechaLibro.setText(datos['date'])
            self.generosLibro.setText(', '.join(datos['subjects']))
            self.autoresLibro.setText(', '.join(datos['authors']))
            self.descripcionLibro.setText(datos['description'])
            
            #Merengue para bajar la thumbnail porque QPixmap
            #no levanta desde una url :(

            thumbdata = urllib2.urlopen('http://covers.openlibrary.org/b/isbn/%s-M.jpg'%identifiers['ISBN']).read()
            thumb = QtGui.QPixmap()
            # FIXME: en realidad habría que guardarlo
            thumb.loadFromData(thumbdata)
            self.tapaLibro.setPixmap(thumb)
            
        else:
            print 'No encontre ese ISBN :('


if __name__ == '__main__':
    ventana = GBooks()
    ventana.show()
    sys.exit(app.exec_())
