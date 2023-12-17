#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai


__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

from qt.core import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QColorDialog, QColor, QPushButton, Qt

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/grauthornotes')

# Set defaults
prefs.defaults['bg_color'] = [
    36,
    36,
    36,
    255
  ]
prefs.defaults['border_color'] = [
    255,
    252,
    240,
    255
  ]
prefs.defaults['text_color'] = [
    255,
    255,
    255,
    255
  ]


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QGridLayout()
        self.setLayout(self.l)
        print(prefs['bg_color'])

        bgc = prefs['bg_color']
        bc = prefs['border_color']
        tc = prefs['text_color']
        bgcolor = QColor()
        bordercolor = QColor()
        textcolor = QColor()
        bgcolor.setRgb(bgc[0], bgc[1], bgc[2], bgc[3])
        bordercolor.setRgb(bc[0], bc[1], bc[2], bc[3])
        textcolor.setRgb(tc[0], tc[1], tc[2], tc[3])
        colorstr = " background-color : "
        bgcolorstr = colorstr + bgcolor.name()
        bordercolorstr = colorstr + bordercolor.name()
        textcolorstr = colorstr + textcolor.name()

        # Background Color
        self.bglabel = QLabel('Background Color:')
        self.l.addWidget(self.bglabel,0,0,Qt.AlignRight)
        self.bg_color_button = QPushButton(
            'Select', self)
        self.bg_color_button.clicked.connect(self.select_bg_color)
        self.l.addWidget(self.bg_color_button,0,2,Qt.AlignCenter)
        self.bg_color = QLabel()
        self.bg_color.setStyleSheet(bgcolorstr)
        self.bg_color.setFixedHeight(20)
        self.bg_color.setFixedWidth(20)
        self.l.addWidget(self.bg_color,0,4,Qt.AlignLeft)
        
        # Border Color
        self.borderlabel = QLabel('Border Color:')
        self.l.addWidget(self.borderlabel,1,0,Qt.AlignRight)
        self.border_color_button = QPushButton(
            'Select', self)
        self.border_color_button.clicked.connect(self.select_border_color)
        self.l.addWidget(self.border_color_button,1,2,Qt.AlignCenter)
        self.border_color = QLabel()
        self.border_color.setStyleSheet(bordercolorstr)
        self.border_color.setFixedHeight(20)
        self.border_color.setFixedWidth(20)
        self.l.addWidget(self.border_color,1,4,Qt.AlignLeft)
        
        # Text Color
        self.textlabel = QLabel('Text Color:')
        self.l.addWidget(self.textlabel,2,0,Qt.AlignRight)
        self.text_color_button = QPushButton(
            'Select', self)
        self.text_color_button.clicked.connect(self.select_text_color)
        self.l.addWidget(self.text_color_button,2,2,Qt.AlignCenter)
        self.text_color = QLabel()
        self.text_color.setStyleSheet(textcolorstr)
        self.text_color.setFixedHeight(20)
        self.text_color.setFixedWidth(20)
        self.l.addWidget(self.text_color,2,4,Qt.AlignLeft)
        

    def save_settings(self):
        prefs['bg_color'] = self.bg_color.palette().base().color().getRgb()
        prefs['border_color'] = self.border_color.palette().base().color().getRgb()
        prefs['text_color'] = self.text_color.palette().base().color().getRgb()
    
    def select_bg_color(self):
        color = QColorDialog.getColor()
        colorstr = " background-color : "
        colorstr = colorstr + color.name()
        self.bg_color.setStyleSheet(colorstr)
    
    def select_border_color(self):
        color = QColorDialog.getColor()
        colorstr = " background-color : "
        colorstr = colorstr + color.name()
        self.border_color.setStyleSheet(colorstr)
    
    def select_text_color(self):
        color = QColorDialog.getColor()
        colorstr = " background-color : "
        colorstr = colorstr + color.name()
        self.text_color.setStyleSheet(colorstr)