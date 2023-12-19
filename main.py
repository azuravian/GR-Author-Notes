#!/usr/bin/env python3

from qt.core import Qt, QProgressDialog, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QMessageBox, QWidget, QTimer, QGroupBox, QCheckBox

from calibre_plugins.grauthornotes.config import prefs
from calibre_plugins.grauthornotes.unzip import install_libs
install_libs()
from calibre_plugins.grauthornotes.authornotes import notes, clear
from calibre.library import db

try:
  load_translations()
except NameError:
  pass # load_translations() added in calibre 1.9

class AuthorProgressDialog(QProgressDialog):

    def __init__(self, gui, authors, db, authorstotal, skippedtotal, clear, status_msg_type='authors', action_type=_('Getting bio for')):
        
        self.total_count = len(authors)
        QProgressDialog.__init__(self, '', _(
            'Cancel'), 0, self.total_count, gui)
        self.setMinimumWidth(400)
        self.setMinimumHeight(150)
        self.bgcolor = prefs['bg_color']
        self.bordercolor = prefs['border_color']
        self.textcolor = prefs['text_color']
        self.bgcolor = '#%02x%02x%02x' % (self.bgcolor[0], self.bgcolor[1], self.bgcolor[2])
        self.bordercolor = '#%02x%02x%02x' % (self.bordercolor[0], self.bordercolor[1], self.bordercolor[2])
        self.textcolor = '#%02x%02x%02x' % (self.textcolor[0], self.textcolor[1], self.textcolor[2])
        
        self.authors, self.db, self.authorstotal, self.skippedtotal = authors, db, authorstotal, skippedtotal
        self.clear, self.action_type, self.status_msg_type = clear, action_type, status_msg_type
        self.gui = gui
        self.setWindowTitle('%s %d %s...' % (
            self.action_type, self.total_count, self.status_msg_type))
        # ... ...
        self.i, self.t, = 0, 0
        # ... ...
        QTimer.singleShot(0, self.do_timer_start)
        self.exec_()

    def do_timer_start(self):
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

        # code for processing a single author ...
        self.setWindowTitle(f'{self.action_type} {self.total_count} {self.status_msg_type} ...')
        self.setLabelText(f'{self.action_type}: {self.author[1].get("name")}')

        self.setValue(self.i - 1)
        if self.clear:
            status = clear(self.author, self.db)
        else:
            status = notes(self.author, self.db, self.bgcolor, self.bordercolor, self.textcolor)
        if status == "complete":
            self.authorstotal += 1
        elif status == "skipped":
            self.skippedtotal += 1

        #next author
        QTimer.singleShot(0, self.do_author_action)

    def do_close(self):
        self.hide()
        self.gui.do_field_item_value_changed()
        self.gui = None

class Dialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase from db/legacy.py
        # This class has many, many methods that allow you to do a lot of
        # things. For most purposes you should use db.new_api, which has
        # a much nicer interface from db/cache.py
        self.db = gui.current_db

        self.master = QVBoxLayout()
        self.master.setContentsMargins(0,0,0,0)
        self.setLayout(self.master)
        
        self.main = QWidget()
        self.mainLayout = QVBoxLayout(self.main)
        
        self.setWindowTitle(_('GR Author Notes'))
        self.setWindowIcon(icon)

        self.rbgroupmain = QGroupBox(_('Function'))
        self.rbvbox = QVBoxLayout(self.rbgroupmain)
        self.addnotes_rb = QRadioButton(_(
            'Write Author bio to author notes'))
        self.rbvbox.addWidget(self.addnotes_rb)
        self.addnotes_rb.setChecked(True)

        self.subrbs = QGroupBox(_('Author Selection'))
        self.subrbsLayout = QHBoxLayout(self.subrbs)
        self.srcAuthors_rb = QRadioButton(_('All Authors'))
        self.srcBooks_rb = QRadioButton(_('Selected Books'))
        self.srcBooks_rb.setChecked(True)
        self.subrbsLayout.addWidget(self.srcAuthors_rb)
        self.subrbsLayout.addWidget(self.srcBooks_rb)
        
        self.clearnotes_rb = QRadioButton(_('Clear notes from authors'))
        self.rbvbox.addWidget(self.clearnotes_rb)
        self.rbvbox.addWidget(self.subrbs)
        self.mainLayout.addWidget(self.rbgroupmain)

        self.overwrite_cb = QCheckBox(_('Update existing notes'))
        self.mainLayout.addWidget(self.overwrite_cb)
        
        self.update_notes_button = QPushButton(_('Process Authors'))
        self.update_notes_button.clicked.connect(self.update_notes)
        self.mainLayout.addWidget(self.update_notes_button)

        self.extrabuttons = QWidget()
        self.extrabuttonsLayout = QHBoxLayout(self.extrabuttons)
        
        self.conf_button = QPushButton(_('Configure this plugin'))
        self.conf_button.clicked.connect(self.config)
        self.extrabuttonsLayout.addWidget(self.conf_button)

        self.extrabuttonsLayout.setSpacing(0)
        self.extrabuttonsLayout.addStretch()
        self.extrabuttonsLayout.addSpacing(15)

        self.about_button = QPushButton(_('About'))
        self.about_button.clicked.connect(self.about)
        self.extrabuttonsLayout.addWidget(self.about_button)

        self.master.addWidget(self.main)
        self.master.addStretch()
        self.master.addSpacing(15)
        self.master.addWidget(self.extrabuttons)

        self.resize(self.sizeHint())

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

        text = get_resources('about.txt')
        QMessageBox.about(self, _('About GR Author Notes'), text.decode('utf-8'))

    def update_notes(self):
        
        from calibre.gui2 import error_dialog, info_dialog

        authorids = []
        authors = []
        authorstotal = 0
        skippedtotal = 0
        overwrite = self.overwrite_cb.isChecked()
        db = self.gui.current_db.new_api
        if self.srcAuthors_rb.isChecked():
            authors = list(db.author_data().items())
        elif self.srcBooks_rb.isChecked():
            # Get currently selected books
            rows = self.gui.library_view.selectionModel().selectedRows()
            if not rows or len(rows) == 0:
                return error_dialog(self.gui, _('Cannot process books'),
                                _('No books selected'), show=True)
            # Map the rows to book ids
            ids = list(map(self.gui.library_view.model().id, rows))
            for bid in ids:
                mi = db.get_metadata(bid)
                for author in mi.authors:
                    aid = db.get_item_id('authors', author)
                    note = db.export_note('authors', aid)
                    if _('Generated using the GR Author Notes plugin') in note and not overwrite:
                        continue
                    else:
                        authorids.append(aid)
            authors = list(db.author_data(author_ids=authorids).items())
        else:
            info_dialog(self, _('Error'), _('No authors selected. Make sure you have chosen the correct Author Selection and/or that you have books selected.'), show=True)
            return
        
        if not authors and not overwrite:
            info_dialog(self, _('Info'), _('All selected authors already have their note set by GR Author Notes.'), show=True)
            return

        clear = self.clearnotes_rb.isChecked()
        event = _('Cleared') if clear else _('Added')
        dlg = AuthorProgressDialog(self.gui, authors, db, authorstotal, skippedtotal, clear)
        if dlg.wasCanceled():
            # do whatever should be done if user cancelled
            canceledtext = _(f'Process was canceled after updating {dlg.authorstotal} author(s) \n\n{event} a total of {dlg.authorstotal} author bios to notes.\n\n')
            canceledtext = self.get_skipped(dlg, canceledtext)
            info_dialog(self, _('Canceled'), canceledtext, show=True)
        else:
            processedtext = _(f'Processed {len(authors)} author(s) \n\n{event} a total of {dlg.authorstotal} author bios to notes. \n\n')
            processedtext = self.get_skipped(dlg, processedtext)
            info_dialog(self, _('Updated files'), processedtext, show=True)
            self.close()

    def get_skipped(self, dlg, text):
        if dlg.skippedtotal > 0:
            return _(f'{text}A total of {dlg.skippedtotal} author(s) were skipped based on html content.')
        else:
            return text

    def config(self):
        self.do_user_config(parent=self)