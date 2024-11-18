#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
import contextlib
__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'
from pathlib import Path
from qt.core import QWidget, QGridLayout, QLabel, QColorDialog, QColor, QPushButton, QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, QLineEdit, Qt # type: ignore

from calibre.utils.config import JSONConfig # type: ignore
from calibre.utils.localization import get_udc as _ # type: ignore

with contextlib.suppress(NameError):
    load_translations()
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
prefs.defaults['update_links'] = True
prefs.defaults['only_confirmed'] = False
prefs.defaults['overwrite_links'] = False
prefs.defaults['translate'] = False
prefs.defaults['language'] = ''

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QGridLayout()
        self.setLayout(self.l)
        bgc = prefs['bg_color']
        bc = prefs['border_color']
        tc = prefs['text_color']
        update_links = prefs['update_links']
        only_confirmed = prefs['only_confirmed']
        overwrite_links = prefs['overwrite_links']
        language = prefs['language']
        translate = prefs['translate']
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

        self.colors = QGroupBox(_('Table Colors'))
        self.colorsLayout = QGridLayout(self.colors)

        # Background Color
        self.bglabel = QLabel(_('Background Color:'))
        self.colorsLayout.addWidget(self.bglabel,0,0,Qt.AlignRight)
        self.bg_color_button = QPushButton(_('Select'), self)
        self.bg_color_button.clicked.connect(self.select_bg_color)
        self.colorsLayout.addWidget(self.bg_color_button,0,2,Qt.AlignLeft)
        self.bg_color = QLabel()
        self.bg_color.setStyleSheet(bgcolorstr)
        self.bg_color.setFixedHeight(20)
        self.bg_color.setFixedWidth(20)
        self.colorsLayout.addWidget(self.bg_color,0,1,Qt.AlignCenter)
        
        # Border Color
        self.borderlabel = QLabel(_('Border Color:'))
        self.colorsLayout.addWidget(self.borderlabel,1,0,Qt.AlignRight)
        self.border_color_button = QPushButton(_('Select'), self)
        self.border_color_button.clicked.connect(self.select_border_color)
        self.colorsLayout.addWidget(self.border_color_button,1,2,Qt.AlignLeft)
        self.border_color = QLabel()
        self.border_color.setStyleSheet(bordercolorstr)
        self.border_color.setFixedHeight(20)
        self.border_color.setFixedWidth(20)
        self.colorsLayout.addWidget(self.border_color,1,1,Qt.AlignCenter)
        
        # Text Color
        self.textlabel = QLabel(_('Text Color:'))
        self.colorsLayout.addWidget(self.textlabel,2,0,Qt.AlignRight)
        self.text_color_button = QPushButton(_('Select'), self)
        self.text_color_button.clicked.connect(self.select_text_color)
        self.colorsLayout.addWidget(self.text_color_button,2,2,Qt.AlignLeft)
        self.text_color = QLabel()
        self.text_color.setStyleSheet(textcolorstr)
        self.text_color.setFixedHeight(20)
        self.text_color.setFixedWidth(20)
        self.colorsLayout.addWidget(self.text_color,2,1,Qt.AlignCenter)

        # Update Links
        self.author_links = QGroupBox(_('Author Links'))
        self.alvbox = QVBoxLayout(self.author_links)
        self.update_links_cb = QCheckBox(_('Set author links for authors who do not have them'))
        self.update_links_cb.setChecked(update_links)
        self.alvbox.addWidget(self.update_links_cb)

        # Overwrite Links
        self.overwrite_links_cb = QCheckBox(_('Overwrite existing author links'))
        self.overwrite_links_cb.setChecked(overwrite_links)
        self.overwrite_links_cb.setEnabled(self.update_links_cb.isChecked())
        self.alvbox.addWidget(self.overwrite_links_cb)

        # Only Confirmed
        self.only_confirmed_cb = QCheckBox(_('Only process for authors with confirmed links'))
        self.only_confirmed_cb.setChecked(only_confirmed)
        self.alvbox.addWidget(self.only_confirmed_cb)
        self.update_links_cb.clicked.connect(self.update_links)

        # Translation
        self.translation = QGroupBox(_('Translation'))
        self.transbox = QVBoxLayout(self.translation)
        self.translate_cb = QCheckBox(_('Translate author bio'))
        self.translate_cb.setChecked(translate)
        self.transbox.addWidget(self.translate_cb)

        # Language
        self.langwidget = QWidget()
        self.lang_layout = QHBoxLayout(self.langwidget)
        self.lang_layout.setContentsMargins(0,0,0,0)
        self.lang_label = QLabel(_('Language Code'))
        self.lang_label_ico = QLabel('<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAADAFBMVEVHcEwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAABAAAAAAACAQAAAAAEAQABAAAAAAACAQACAAABAAABAAAAAAAAAAAEAQABAAAAAAAAAAABAAAAAAAAAAAAAAABAAADAQACAQACAQAAAAAAAAABAAADAQAEAQACAAABAAAHAwACAQAEAgAAAAADAQABAAACAQCdQAoDAQACAQBZKQapRwsBAADDUg82GgR6MgcnEAKRQwp+NAg+GQTBTw3hXA9qMQc3FwNdJga/TwzHWw4pEQOiTQs8GwSsRgzXWA5XJQXTVg7aWQ6LOQmxSQyHOQjoXw9JHQWuTQx0MQjYXA7dbQ8eDAJuLgdEHARFHQTochDaWQ7JUg27UBD1bxHPZQ8WCQE3GgQ7GQT3fBFcJQZXIwXrYhDxcxCbQwv2dxH8fhLvYhDrYQ/pYA/wYxDoXw/nXw/sYQ/mXw/uYhD3ZhDxYxDvYhDkXg/qYA/zZBDlXg/1ZRD5ZhDiXQ/4ZhDtYRDx8fHyYxDgXA/2ZRD0ZBD6bxHhXQ/jXQ/n5+fo6Ojp6ent7e7m5ub5axHs7Ozq6urr6+vu7u/w8PD6ZxDy8/PbWg75chH5bBH5aRDeWw76eRH7cRH5dBHZWQ37dRH5bhHWWA76cBHtYg/0ZRD7cxHyZBDjXg/fXA/TVw3QVQ35dxHqYQ/6ehHLUw3ESgL5dhH2ZhD/aRDGUAru9Pju8fTy9vjgWgrw9/vz+v3hXA7SUAP1aRH8ZxDdVAPLTAL0/P/XUQP/fhG6RgPNUAb3axH/bRH/gRLbVwj/dRHWVQjq8PTarZPxZxD/eRHo6+3sYxDoxrPUhVfs6OXozb7uZQ/o4dzWZyXVlG3MbDTu5N3ko37n1crfg07HWBbq7vHhyrzjrY7gv6zn2dHacDLXe0Xhl2zCYCbhtJnYpYfYnXrfuaLoYQ/TjGLpvqXKd0fTXRfv6+nNXx7nXg/gfD/nWATmXQwAAAAAAAAdzE9GAAABAHRSTlMABBEMBQoDAQgCDhoXFB0gIyo1KERMQTIVUX1IXjgsPi9phFZZbmE7ZXOKJSaWwXmudqSS0anJj7vntZ9v1Zz+WcaxoObB6fh8q8/dx92zY/H7jPj12um2+9q/kuTik6yRdurt9Pv62dtRgfe5ou/xw/n7/f///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////wwR4wM96QAAGnNJREFUeNq8mPlP03kax6X3xa1S4yySzA8zG/0T2AwbkpUEAwnZROMRr4xGNzvu7vS+D0ppgVbpAlKsWgQ5SlsUQbAdKgwg5T7sOqKDB+wq4+i64uyOu7/s8/l+vz0peM/zgzH88nre7+f9eT6fb9ete5+io1r3ixdAmUxaQgIlWAkJCTTmL9UKwIHMCBbxXyqVyqBgXXxkOC2BgmBUMid1y7HC7Oy8vLzs7MKc9VnJJDKZjLr4iE0g6UgsO/NY9p4dh440tE1NBaagKpqOfLUjNy8nLYVEhS4oCcyPQ0fSSRnZuTsOXQ34A1NtbW0XWlpamioqKs5VjENVoS42skks6IHG/NDeI+2k9JzcE35/IHDxYkPDWVQtTVDnzp0bGzsPNdAzPu7YnZ3GARsYH9IGOpPCIFOTc3L3XfEH6q9ebSDwGB/Dj43JZLISVAM9A18VZGdwSSxogf7h8OSUvKP+iUD95csIT8gHPsC/hXKg0mq1Zd3d3bK6np69uWmJWAsfgk9hsFjp2Tsm/ECP5WP4mzdvCgQCudxgUDvKUSfl2rrxvXu2cBM/QAv0BAaZxSncN+G/cjmGH8TfvXvr1i0eTyxulSoEcoMar5Kew3tSuYkQx/eaA5NCZXHXF/zFf6U+pP9sJP/mzbu3lpeXJRKRSMjvEOuhBbkTyiCXl/XsKEzhkt7HBDoN5Cfn/mHiCs6Pko/zEV7Z1zs4ONjb55KI+Dy9FE0DCqZSUrL7Vxwu+Z1NgOmTSMdg+JH8hsjxI76yd9L9ZHFx8YltsFenEal4rVKUCIFAoZAK6vIPJnMhCfR345NJ7Dwk/0r9ivFD/HF+3+D84wfWM2dKf1542Dxs10mQCQoFxpfq9WXanRmcROq7jIFJIbMyC5B8jH81fPyDxw/xeyefPrjxzRlU31y/8+Ow3aQRdoihA5wPyRzYvZn9LmNggv05R1eR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" width="20" height="20">')
        self.lang_label_ico.setToolTip(_('Input the 2 character ISO 639-1 language code. This can be found at the following URL: <a href="https://www.loc.gov/standards/iso639-2/php/code_list.php">https://www.loc.gov/standards/iso639-2/php/code_list.php</a>'))
        self.language = QLineEdit(language)
        self.language.setInputMask('AA')
        self.lang_layout.addWidget(self.lang_label)
        self.lang_layout.addWidget(self.language)
        self.lang_layout.addWidget(self.lang_label_ico)
        self.transbox.addWidget(self.langwidget)
        
        
        self.l.addWidget(self.colors,0,0,1,3,Qt.AlignLeft)
        self.l.addWidget(self.translation,0,3,1,1,Qt.AlignRight)
        self.l.addWidget(self.author_links,1,0,1,5,Qt.AlignCenter)
        

    def save_settings(self):
        prefs['bg_color'] = self.bg_color.palette().base().color().getRgb()
        prefs['border_color'] = self.border_color.palette().base().color().getRgb()
        prefs['text_color'] = self.text_color.palette().base().color().getRgb()
        prefs['update_links'] = self.update_links_cb.isChecked()
        prefs['overwrite_links'] = self.overwrite_links_cb.isChecked()
        prefs['only_confirmed'] = self.only_confirmed_cb.isChecked()
        prefs['language'] = self.language.text()
        prefs['translate'] = self.translate_cb.isChecked()
    
    def update_links(self):
        self.overwrite_links_cb.setEnabled(self.update_links_cb.isChecked())

    def select_bg_color(self):
        color = QColorDialog.getColor()
        colorstr = " background-color : "
        colorstr += color.name()
        self.bg_color.setStyleSheet(colorstr)
    
    def select_border_color(self):
        color = QColorDialog.getColor()
        colorstr = " background-color : "
        colorstr += color.name()
        self.border_color.setStyleSheet(colorstr)
    
    def select_text_color(self):
        color = QColorDialog.getColor()
        colorstr = " background-color : "
        colorstr += color.name()
        self.text_color.setStyleSheet(colorstr)