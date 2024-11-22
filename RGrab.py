import re
import sys

import praw
from PySide6 import QtCore, QtWidgets, QtGui

class Scraper(QtCore.QObject):
    
    scrape_progress = QtCore.Signal(int)
    scrape_error = QtCore.Signal(str)
    
    scrape_finished = QtCore.Signal(int, str)
    finished = QtCore.Signal()
    
    def __init__(self, r_url, outfile, reddit):
        super().__init__()
        self.r_url = r_url
        self.outfile = outfile
        self.reddit = reddit
        
    @QtCore.Slot() 
    def scrape(self):
        err_msg = ""
        if self.r_url == "":
            err_msg = "<font color='red'>Please input a link to a reddit thread!</font>"
        elif self.outfile == "":
            err_msg = "<font color='red'>Please select a file to save the comments in!</font>"
        if err_msg != "":
            self.scrape_error.emit(err_msg)
            self.finished.emit()
            return
        try:
            submission = self.reddit.submission(url=self.r_url)
            trees = []
            for tlc in submission.comments:
                trees.append(praw.models.comment_forest.CommentForest(submission, [tlc]))
            progress_counter = 0
            num_trees = len(trees)
            for t in trees:
                t.replace_more(limit=None)
                progress_counter+=1
                self.scrape_progress.emit(progress_counter * 100 // (num_trees * 2))
            comment_counter = 0
            with open(self.outfile, "w") as f:
                for t in trees:
                    for comment in t.list():
                        f.write("\n")
                        f.write(re.sub(r'\s+',' ',comment.body))
                        f.write("\n")
                        comment_counter+=1
                    progress_counter+=1
                    self.scrape_progress.emit(progress_counter * 100 // (num_trees * 2))
                f.write(f"Output {comment_counter} comments")
        except praw.exceptions.PRAWException as e:
            self.scrape_error.emit(f"<font color='red'>PRAWException: {str(e)}</font>")
        except OSError as e:
            self.scrape_error.emit(f"<font color='red'>OSError: {str(e)}</font>")
        except Exception as e:
            self.scrape_error.emit(f"<font color='red'>Exception: {str(e)}</font>")
        else:
            self.scrape_finished.emit(comment_counter, self.outfile)
        finally:
            self.finished.emit()
            


class RGrabWidget(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        
        # initialize Qt Widgets
        self.instructions_text = QtWidgets.QLabel("Paste a link to the reddit thread you wand to scrape comments from: ")
        self.instructions_text.setAlignment(QtCore.Qt.AlignCenter)
        
        self.r_link_text = QtWidgets.QLineEdit()
        self.r_link_text.setAlignment(QtCore.Qt.AlignCenter)
        
        self.row1 = QtWidgets.QHBoxLayout()
        self.row1.addWidget(self.instructions_text)
        self.row1.addWidget(self.r_link_text)
        
        self.test_text = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)
        
        self.button = QtWidgets.QPushButton("Select File")
        self.row2 = QtWidgets.QHBoxLayout()
        self.row2.addWidget(self.button)
        self.row2.addWidget(self.test_text)
        
        self.scrape_button = QtWidgets.QPushButton("Scrape Reddit Thread")
        self.row3 = QtWidgets.QHBoxLayout()
        self.row3.addWidget(self.scrape_button)
        
        self.result_text = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.row4 = QtWidgets.QHBoxLayout()
        self.row4.addWidget(self.result_text)
        self.row4.addWidget(self.progress_bar)
        
        self.col = QtWidgets.QVBoxLayout(self)
        self.col.addLayout(self.row1)
        self.col.addLayout(self.row2)
        self.col.addLayout(self.row3)
        self.col.addLayout(self.row4)
        
        self.button.clicked.connect(self.select_file)
        self.scrape_button.clicked.connect(self.begin_scrape)
        
        # Initialize PRAW objects
        c_secret=""
        c_id=""
        user_agent=""
        with open(".client_secret", "r") as f:
            c_secret = f.read().splitlines()[0]
        with open(".client_id", "r") as f:
            c_id = f.read().splitlines()[0]
        with open(".user_agent", "r") as f:
            user_agent = f.read().splitlines()[0]

        self.reddit = praw.Reddit(
            client_id=c_id,
            client_secret=c_secret,
            user_agent=user_agent
        )
        
        # references to thread and worker
        # otherwise scoping rules will delete them before they can work!
        self.scrape_thread = None
        self.scraper = None
        
    @QtCore.Slot()
    def select_file(self):
        filename, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, "Choose a file to save the scraped comments.")
        self.test_text.setText(filename)
        
    @QtCore.Slot()
    def begin_scrape(self):
        self.result_text.setText("Working ...")
        self.scrape_button.setEnabled(False)
        
        # Initialize Thread and Worker
        self.scrape_thread = QtCore.QThread()
        self.scraper = Scraper(self.r_link_text.text(), self.test_text.text(), self.reddit)
        self.scraper.moveToThread(self.scrape_thread)
        
        self.scrape_thread.started.connect(self.scraper.scrape)
        
        self.scraper.scrape_progress.connect(self.progress_bar.setValue) 
        self.scraper.scrape_error.connect(self.handle_scrape_error)
        
        self.scraper.finished.connect(self.progress_bar.reset)
        self.scraper.finished.connect(self.scrape_thread.quit)
        self.scraper.finished.connect(self.scraper.deleteLater)
        self.scraper.scrape_finished.connect(self.end_scrape)
        
        self.scrape_thread.finished.connect(self.scrape_thread.deleteLater)
        self.scrape_thread.start()
        
    @QtCore.Slot(int, str) 
    def end_scrape(self, counter, outfile):
        self.result_text.setText(f"Output {counter} comments to file {outfile}")
        self.test_text.setText("")
        self.scrape_button.setEnabled(True)
    
    @QtCore.Slot(str)
    def handle_scrape_error(self, error_msg):
        self.result_text.setText(error_msg)
        self.scrape_button.setEnabled(True)
        
        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = RGrabWidget()
    widget.show()

    sys.exit(app.exec())

