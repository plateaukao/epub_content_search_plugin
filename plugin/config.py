#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2020, Daniel Kao<daniel.kao@gmail.com>'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QIntValidator

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/epub_content_search) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/epub_content_search')

# Set defaults
prefs.defaults['rga_path'] = '/usr/local/bin/rga'
prefs.defaults['tags'] = 'searchable'
prefs.defaults['search_result_count'] = ''


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.l = QHBoxLayout()
        self.layout.addLayout(self.l)

        self.l = QHBoxLayout()
        self.layout.addLayout(self.l)
        self.label = QLabel('epub tag')
        self.l.addWidget(self.label)

        self.tags = QLineEdit(self)
        self.tags.setText(prefs['tags'])
        self.l.addWidget(self.tags)
        self.label.setBuddy(self.tags)

        self.l = QHBoxLayout()
        self.layout.addLayout(self.l)
        self.label = QLabel('search result limit:')
        self.l.addWidget(self.label)

        self.search_result_count = QLineEdit(self)
        self.search_result_count.setValidator(QIntValidator(self.search_result_count))
        self.search_result_count.setText(prefs['search_result_count'])
        self.l.addWidget(self.search_result_count)
        self.label.setBuddy(self.search_result_count)

    def save_settings(self):
        prefs['tags'] = self.tags.text()
        prefs['search_result_count'] = self.search_result_count.text()
