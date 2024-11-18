#!/usr/bin/env python3

import contextlib
from qt.core import Qt, QProgressDialog, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QMessageBox, QWidget, QTimer, QGroupBox, QCheckBox # type: ignore

from calibre_plugins.grauthornotes.config import prefs # type: ignore
from calibre_plugins.grauthornotes.unzip import install_libs # type: ignore
install_libs()
from calibre_plugins.grauthornotes.authornotes import link, notes, clear # type: ignore
from calibre.library import db # type: ignore

with contextlib.suppress(NameError):
    load_translations() # type: ignore

class AuthorProgressDialog(QProgressDialog):
    def __init__(self, gui, authors, db, authorstotal, skippedtotal, linkstotal, clear, status_msg_type=_('authors'), action_type=_('Getting bio for')):
        """Initialize the progress dialog."""
        self.total_count = len(authors)
        super().__init__('', _('Cancel'), 0, self.total_count, gui)
        self.setMinimumWidth(400)
        self.setMinimumHeight(150)
        
        # Set colors from preferences
        self.bgcolor = '#%02x%02x%02x' % tuple(prefs['bg_color'])
        self.bordercolor = '#%02x%02x%02x' % tuple(prefs['border_color'])
        self.textcolor = '#%02x%02x%02x' % tuple(prefs['text_color'])
        
        self.authors = authors
        self.db = db
        self.authorstotal = authorstotal
        self.skippedtotal = skippedtotal
        self.linkstotal = linkstotal
        self.clear = clear
        self.action_type = action_type
        self.status_msg_type = status_msg_type
        
        if self.clear:
            self.action_type = _('Clearing notes from')
        
        self.gui = gui
        self.setWindowTitle(f'{self.action_type} {self.total_count} {self.status_msg_type}...')
        
        self.i = 0
        self.t = 0
        
        QTimer.singleShot(0, self.do_timer_start)
        self.exec_()

    def do_timer_start(self):
        """Start the timer for processing authors."""
        self.author = self.authors[self.i]
        self.setWindowTitle(f'{self.action_type} {self.total_count} {self.status_msg_type} ...')
        self.setLabelText(f'{self.action_type}: {self.author[1].get("name")}')
        self.setValue(self.i)
        QTimer.singleShot(0, self.do_author_action)

    def do_author_action(self):

      #window management
      if self.wasCanceled():
          return self.do_close()
      if self.i >= self.total_count:
          return self.do_close()
      self.author = self.authors[self.i]
      self.i += 1
      if self.author[1].get('name') == 'Unknown':
          QTimer.singleShot(0, self.do_author_action)
          return
      # code for processing a single author ...
      author_link = self.author[1].get('link')
      if author_link == '' and prefs['update_links'] == True and not self.clear:
        textLabel = (_('Getting author link and  ') + self.action_type.lower() +
                     ': ' + self.author[1].get("name"))
        self.setLabelText(textLabel)
        #self.setLabelText(_(f'Getting author link and {self.action_type.lower()}: {self.author[1].get("name")}'))
        author_link = link(self.author, self.db)
        if author_link:
            self.linkstotal += 1
      else:
        self.setLabelText(f'{self.action_type}: {self.author[1].get("name")}')
      self.setWindowTitle(f'{self.action_type} {self.total_count} {self.status_msg_type} ...')
      self.setValue(self.i - 1)
      if self.clear:
          status = clear(self.author, self.db)
      else:
          status = notes(self.author, self.db, self.bgcolor, self.bordercolor, self.textcolor, author_link)
      if status:
          self.authorstotal += 1
      else:
          self.skippedtotal += 1

      #next author
      QTimer.singleShot(0, self.do_author_action)

    def do_close(self):
        self.hide()
        self.gui.do_field_item_value_changed()
        self.gui = None

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QGroupBox, QRadioButton, QHBoxLayout

class Dialog(QDialog):
    def __init__(self, gui, icon, do_user_config):
        super().__init__(gui)
        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase from db/legacy.py
        # This class has many, many methods that allow you to do a lot of
        # things. For most purposes you should use db.new_api, which has
        # a much nicer interface from db/cache.py
        self.db = gui.current_db

        self.init_ui(icon)

    def init_ui(self, icon):
        """Initialize the user interface."""
        self.master = QVBoxLayout()
        self.master.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.master)

        self.main = QWidget()
        self.mainLayout = QVBoxLayout(self.main)

        self.setWindowTitle('GR Author Notes')
        self.setWindowIcon(icon)

        self.rbgroupmain = QGroupBox(_('Function'))
        self.rbvbox = QVBoxLayout(self.rbgroupmain)
        self.addnotes_rb = QRadioButton(_('Write Author bio to author notes'))
        self.rbvbox.addWidget(self.addnotes_rb)
        self.addnotes_rb.setChecked(True)

        self.subrbs = QGroupBox(_('Author Selection'))
        self.subrbsLayout = QHBoxLayout(self.subrbs)
        self.srcAuthors_rb = QRadioButton(_('All Authors'))
        self.srcBooks_rb = QRadioButton(_('Selected Books'))

        self.subrbsLayout.addWidget(self.srcAuthors_rb)
        self.subrbsLayout.addWidget(self.srcBooks_rb)

        self.master.addWidget(self.rbgroupmain)
        self.master.addWidget(self.subrbs)

    def do_close(self):
        """Close the dialog and perform necessary cleanup."""
        self.hide()
        self.gui.do_field_item_value_changed()
        self.gui = None

    def about(self):
        # Get the about text from a file inside the plugin zip file
        # The get_resources function is a builtin function defined for all your
        # plugin code. It loads files from the plugin zip file. It returns
        # the bytes from the specified file.
        #
        # Note that if you are loading more than one file, for performance, you
        # should pass a list of names to get_resources. In this case,
        # get_resources will return a dictionary mapping names to bytes. Names that
        # are not found in the zip file will not be in the returned dictionary.

        text = get_resources('about.txt') # type: ignore
        QMessageBox.about(self, _('About GR Author Notes'), text.decode('utf-8'))

    def update_notes(self):
        
        from calibre.gui2 import error_dialog, info_dialog # type: ignore

        authorids = []
        authors = []
        authorstotal = 0
        skippedtotal = 0
        linkstotal = 0
        clear = self.clearnotes_rb.isChecked()
        event = _('Cleared') if clear else _('Added')
        prep = _('from') if clear else _('to')
        overwrite = self.overwrite_cb.isChecked()
        db = self.gui.current_db.new_api
        if self.srcAuthors_rb.isChecked():
            authors = list(db.author_data().items())
        elif self.srcBooks_rb.isChecked():
            # Get currently selected books
            print ("Get currently selected books") # Terisa
            rows = self.gui.library_view.selectionModel().selectedRows()
            if not rows or len(rows) == 0:
                return error_dialog(self.gui, _('Cannot process books'),
                                _('No books selected'), show=True)
            # Map the rows to book ids
            ids = list(map(self.gui.library_view.model().id, rows))
            for bid in ids:
                mi = db.get_metadata(bid)

            for author in mi.authors:
                print ('Author: ', author) # Terisa
                aid = db.get_item_id('authors', author)
                note = db.export_note('authors', aid)
                print ("Note: ", note) # Terisa
                if (clear and note
                    or 'Generated using the GR Author Notes plugin' not in note
                    or overwrite):
                    authorids.append(aid)
                else:
                    continue
            authors = list(db.author_data(author_ids=authorids).items())
        else:
            info_dialog(self, _('Error'), _('No authors selected. Make sure you have chosen the correct Author Selection and/or that you have books selected.'), show=True)
            return

        if not authors and not overwrite:
            info_dialog(self, _('Info'), _('All selected authors already have their note set by GR Author Notes.'), show=True)
            return


        dlg = AuthorProgressDialog(self.gui, authors, db, authorstotal, skippedtotal, linkstotal, clear)
        if dlg.wasCanceled():
            # do whatever should be done if user cancelled
            canceledtext = (
                (_('Process was canceled after updating ') + dlg.authorstotal +
                _(f' author(s) \n\n') + event + _(' a total of ') + dlg.authorstotal +
                _(' author bios ')) + prep) + _(f' notes.\n\n')
            #canceledtext = _(f'Process was canceled after updating {dlg.authorstotal} author(s) \n\n{event} a total of {dlg.authorstotal} author bios {prep} notes.\n\n')
            self.build_dialog(dlg, canceledtext, info_dialog, _('Canceled'))
        else:
            processedtext = (
                (_('Processed ') + str(len(authors)) + _(f' author(s) \n\n') + event +
                _(' a total of ') + str(dlg.authorstotal) + _(' author bios ')) +
                prep) + _(f' notes. \n\n')
            #processedtext = _(f'Processed {len(authors)} author(s) \n\n{event} a total of {dlg.authorstotal} author bios {prep} notes. \n\n')
            self.build_dialog(dlg, processedtext, info_dialog, _('Updated files'))
            self.close()

    def build_dialog(self, dlg, text, info_dialog, title):
        text = self.get_linked(dlg, text)
        text = self.get_skipped(dlg, text)
        info_dialog(self, title, text, show=True)

    def get_skipped(self, dlg, text) -> str:
        """Append skipped authors information to the text."""
        if dlg.skippedtotal > 0:
            return (text + _('A total of ') + str(dlg.skippedtotal) +
                    _(' author(s) were skipped based on html content.'))
        else:
            return text
        
    def get_linked(self, dlg, text):
        if dlg.linkstotal <= 0:
            return text
        textEnd = (text + _('Added links to a total of ') + str(dlg.linkstotal) +
                    _(' authors.'))
        #return _(f'{text}Added links to a total of {dlg.linkstotal} authors.')
        return _(textEnd)

    def config(self):
        """Open the user configuration dialog."""
        self.do_user_config(parent=self)