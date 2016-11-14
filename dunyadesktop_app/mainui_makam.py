import sys
import os
import Queue

from PyQt4 import QtGui

from cultures import apiconfig
from cultures.makam import utilities
from cultures.makam.query import QueryThread
from mainui_design_makam import MainWindowMakamDesign
from widgets.playerdialog import PlayerDialog
from utilities import database

apiconfig.set_token()
# apiconfig.set_hostname()

DOCS_PATH = os.path.join(os.path.dirname(__file__), '..', 'cultures',
                         'documents')


class MainWindowMakam(MainWindowMakamDesign):
    """The main window of makam"""
    def __init__(self):
        MainWindowMakamDesign.__init__(self)

        # fetches the attributes and sets the comboboxes
        (self.makams, self.forms, self.usuls, self.composers,
         self.performers, self.instruments) = utilities.get_attributes()
        self._set_combobox_attributes()

        self.frame_query.frame_attributes.comboBox_instrument.setDisabled(True)
        self.recordings = []
        self.work_count = 0
        self.progress_number = 0
        self.thread_query = QueryThread(self)
        #self.thread_feature_downloader = utilities.DocThread()
        self.threads = []
        self.queue = Queue.Queue()

        # creating db
        self._set_collections()

        self.download_queue = []
        # signals
        self.frame_query.frame_attributes.toolButton_query.clicked.connect(self.query)
        self.thread_query.combobox_results.connect(
            self.change_combobox_backgrounds)
        self.thread_query.progress_number.connect(self.set_progress_number)
        self.thread_query.query_completed.connect(self.query_finished)
        self.thread_query.fetching_completed.connect(self.work_received)

        self.frame_query.recording_model.rec_fetched.connect(self.append_recording)

        self.frame_query.lineEdit_filter.textChanged.connect(
            lambda: self.frame_query.proxy_model.filter_table(
                self.frame_query.lineEdit_filter.text()))
        self.frame_query.tableView_results.add_maincoll.triggered.connect(
            lambda: self.download_related_features(
                self.frame_query.tableView_results.index))

        self.dwc_left.listView_collections.index_changed.connect(
            self.update_coll_list)
        self.dwc_left.tableView_downloaded.added_new_doc.connect(
            self.check_new_doc)

    def _set_combobox_attributes(self):
        self.frame_query.frame_attributes.comboBox_melodic.add_items(self.makams)
        self.frame_query.frame_attributes.comboBox_form.add_items(self.forms)
        self.frame_query.frame_attributes.comboBox_rhythm.add_items(self.usuls)
        self.frame_query.frame_attributes.comboBox_composer.add_items(self.composers)
        self.frame_query.frame_attributes.comboBox_performer.add_items(self.performers)
        self.frame_query.frame_attributes.comboBox_instrument.add_items(self.instruments)

    def _set_collections(self):
        conn, c = database.connect(add_main=True)
        database._add_docs_to_maincoll(conn, c)

        colls = database.get_collections(c)
        self.dwc_left.listView_collections.add_collections(
            [coll[0] for coll in colls])
        conn.close()

    def query(self):
        self.recordings = []
        self.work_count = 0
        self.frame_query.recording_model.clear_items()
        self.frame_query.frame_attributes.toolButton_query.setEnabled(False)
        self.frame_query.lineEdit_filter.setEnabled(True)
        self.frame_query.tableView_results.setEnabled(True)
        self.frame_query.tableView_results.horizontal_header.show()

        mid = self.frame_query.frame_attributes.comboBox_melodic.get_attribute_id()
        fid = self.frame_query.frame_attributes.comboBox_form.get_attribute_id()
        uid = self.frame_query.frame_attributes.comboBox_rhythm.get_attribute_id()
        cmbid = self.frame_query.frame_attributes.comboBox_composer.get_attribute_id()
        ambid = self.frame_query.frame_attributes.comboBox_performer.get_attribute_id()

        self.thread_query.mid = mid
        self.thread_query.fid = fid
        self.thread_query.uid = uid
        self.thread_query.cmbid = cmbid
        self.thread_query.ambid = ambid

        self.progress_bar.setVisible(True)
        self.thread_query.start()

    def set_progress_number(self, progress_number):
        self.progress_number = progress_number

    def append_recording(self, rec_mbid):
        self.recordings.append(str(rec_mbid.toUtf8()))
        self.dwc_left.tableView_downloaded.recordings = self.recordings

    def work_received(self, work):
        self.work_count += 1
        self.progress_bar.update_progress_bar(self.work_count,
                                              self.progress_number)
        self.frame_query.recording_model.add_recording(work)
        self.frame_query.tableView_results.resizeColumnToContents(1)
        self.frame_query.tableView_results.setColumnWidth(0, 28)

    def change_combobox_backgrounds(self, combobox_status):
        color_palette = {0: '', 1: '#D9F4DD', 2: '#F4D1D0'}
        self.frame_query.frame_attributes.comboBox_melodic.change_background(
            color=color_palette[combobox_status[0]])
        self.frame_query.frame_attributes.comboBox_form.change_background(
            color=color_palette[combobox_status[1]])
        self.frame_query.frame_attributes.comboBox_rhythm.change_background(
            color=color_palette[combobox_status[2]])
        self.frame_query.frame_attributes.comboBox_composer.change_background(
            color=color_palette[combobox_status[3]])
        self.frame_query.frame_attributes.comboBox_performer.change_background(
            color=color_palette[combobox_status[4]])

    def query_finished(self):
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")
        self.frame_query.frame_attributes.toolButton_query.setEnabled(True)

    def download_related_features(self, index):
        source_index = self.frame_query.tableView_results.model().mapToSource(index)
        self.recid = self.recordings[source_index.row()]
        #self.thread_feature_downloader.docid = self.recid
        #self.thread_feature_downloader.start()

    def open_player(self, pitch_data, pd):
        player = PlayerDialog(self.recid, pitch_data, pd)
        player.exec_()

    def update_coll_list(self, coll):
        conn, c = database.connect()
        raw = database.fetch_collection(c, coll)
        self.dwc_left.tableView_downloaded.coll = coll
        self.dwc_left.tableView_downloaded.create_table([item[0] for item in raw])
        self.dwc_left.change_downloaded_text(coll)

    def check_new_doc(self, docs):
        print(docs, 'is sent')
        downlaod = []
        for docid in docs:
            if not os.path.isdir(os.path.join(DOCS_PATH, str(docid))):
                downlaod.append(str(docid))
        print(downlaod, 'will be downloaded')
        d_thread = utilities.DocThread(self.queue)
        self.threads.append(d_thread)
        d_thread.start()

        for doc in downlaod:
            self.queue.put(doc)
        self.queue.put(None)  # tells the workers to shut down



app = QtGui.QApplication(sys.argv)
mainwindow_makam = MainWindowMakam()
mainwindow_makam.show()
app.exec_()
