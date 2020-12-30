#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2020, Daniel Kao<daniel.kao@gmail.com>'
__docformat__ = 'restructuredtext en'

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QWidget, QLayout, QScrollBar, QAbstractItemView
from PyQt5.QtCore import Qt

from calibre_plugins.epub_content_search.config import prefs

import subprocess

from functools import partial

class DemoDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config
        largerFont = self.font()
        largerFont.setPointSize(24)
        self.setFont(largerFont)

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase from db/legacy.py
        # This class has many, many methods that allow you to do a lot of
        # things. For most purposes you should use db.new_api, which has
        # a much nicer interface from db/cache.py
        self.db = gui.current_db

        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.setWindowTitle('Epub Text Search')
        self.setWindowIcon(icon)

        # add search line 
        self.search_layout = QHBoxLayout()
        self.l.addLayout(self.search_layout)

        self.search_input = QLineEdit(self)
        self.search_layout.addWidget(self.search_input)
        self.search_button = QPushButton('search', self)
        self.search_button.clicked.connect(self.search_epub_content)
        self.search_layout.addWidget(self.search_button)

        # add search results
        self.scroll_bar = QScrollBar(self) 
        self.search_results = QListWidget()
        self.search_results.setVerticalScrollBar(self.scroll_bar)
        self.search_results.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel) 
        self.l.addWidget(self.search_results)

        self.about_button = QPushButton('About', self)
        self.about_button.clicked.connect(self.about)
        self.l.addWidget(self.about_button)

        self.conf_button = QPushButton('Configure this plugin', self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.resize(self.sizeHint())

    def about(self):
        text = get_resources('about.txt')
        QMessageBox.about(self, 'About the Epub Text Search Plugin', text.decode('utf-8'))

    def search_epub_content(self):
        ''' Search epub content '''
        # reset results layout
        self.search_results.clear()

        # get search input
        keyword = self.search_input.text()
        print('search input: '+ keyword)

        # search in each book
        db = self.db.new_api
        matched_ids = {book_id for book_id in db.all_book_ids() if 'EPUB' in db.formats(book_id)}
        for book_id in matched_ids:
            mi = db.get_metadata(book_id, get_cover=False, cover_as_data=False)
            if prefs['tags'] in mi.tags:
                title = mi.title
                filepath = fmt_path = self.gui.current_db.format_abspath(book_id, 'EPUB', index_is_id=True)
                result = subprocess.run([prefs['rga_path'], keyword, filepath, '-C', '2', '-g', '*.epub'], stdout=subprocess.PIPE)
                if len(result.stdout) != 0:
                  widgetLayout = QVBoxLayout()
                  book_button = QPushButton(title, self)
                  book_button.clicked.connect(partial(self.view, book_id))
                  widgetLayout.addWidget(book_button)
                  widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
                  widget = QWidget()
                  widget.setLayout(widgetLayout)
                  widgetItem = QListWidgetItem()
                  widgetItem.setSizeHint(widget.sizeHint())
                  self.search_results.addItem(widgetItem)
                  self.search_results.setItemWidget(widgetItem, widget)

                  matched = result.stdout.decode('utf-8')
                  for lines in matched.split('--\n'):
                    widgetLayout = QVBoxLayout()
                    qLabel = QLabel(lines.replace(keyword, '<font color=yellow>' + keyword + '</font>').replace('\n\n', '\n').replace('\n','<br/>') + '<br/>')
                    qLabel.setTextFormat(Qt.RichText)
                    qLabel.setStyleSheet(''' font-size: 24px; ''')
                    widgetLayout.addWidget(qLabel)

                    widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
                    widget = QWidget()
                    widget.setLayout(widgetLayout)
                    widgetItem = QListWidgetItem()
                    widgetItem.setSizeHint(widget.sizeHint())
                    self.search_results.addItem(widgetItem)
                    self.search_results.setItemWidget(widgetItem, widget)


    def marked(self):
        ''' Show books with only one format '''
        db = self.db.new_api
        matched_ids = {book_id for book_id in db.all_book_ids() if len(db.formats(book_id)) == 1}
        # Mark the records with the matching ids
        # new_api does not know anything about marked books, so we use the full
        # db object
        self.db.set_marked_ids(matched_ids)

        # Tell the GUI to search for all marked records
        self.gui.search.setEditText('marked:true')
        self.gui.search.do_search()

    def view(self, book_id):
        ''' View book '''
        view_plugin = self.gui.iactions['View']
        # Ask the view plugin to launch the viewer for row_number
        keyword = self.search_input.text()
        view_plugin.view_format_by_id(book_id, 'EPUB', search=keyword)


    def config(self):
        self.do_user_config(parent=self)
