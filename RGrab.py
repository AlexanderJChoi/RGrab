import sys

import praw
from PySide6 import QtCore, QtWidgets, QtGui

class RGrabWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # initialize Qt Widgets
        self.instructions_text = QtWidgets.QLabel("Paste a link to the reddit thread you wand to scrape comments from: ")
        self.instructions_text.setAlignment(QtCore.Qt.AlignCenter)
        
        self.r_link_text = QtWidgets.QLineEdit(self)
        self.r_link_text.setAlignment(QtCore.Qt.AlignCenter)
        
        self.row1 = QtWidgets.QHBoxLayout()
        self.row1.addWidget(self.instructions_text)
        self.row1.addWidget(self.r_link_text)
        
        self.test_text = QtWidgets.QLabel("0", alignment=QtCore.Qt.AlignCenter)
        
        self.button = QtWidgets.QPushButton("Select File")
        self.row2 = QtWidgets.QHBoxLayout()
        self.row2.addWidget(self.button)
        self.row2.addWidget(self.test_text)
        
        self.scrape_button = QtWidgets.QPushButton("Scrape Reddit Thread")
        self.row3 = QtWidgets.QHBoxLayout()
        self.row3.addWidget(self.scrape_button)
        
        self.result_text = QtWidgets.QLabel("", alignment=QtCore.Qt.AlignCenter)
        self.row4 = QtWidgets.QHBoxLayout()
        self.row4.addWidget(self.result_text)
        
        self.col = QtWidgets.QVBoxLayout(self)
        self.col.addLayout(self.row1)
        self.col.addLayout(self.row2)
        self.col.addLayout(self.row3)
        self.col.addLayout(self.row4)
        
        self.button.clicked.connect(self.select_file)
        self.scrape_button.clicked.connect(self.scrape)
        
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
        
    @QtCore.Slot()
    def select_file(self):
        filename, file_filter = QtWidgets.QFileDialog.getSaveFileName(self, "Choose a file to save the scraped comments.")
        self.test_text.setText(filename)
        
    @QtCore.Slot()
    def scrape(self):
        r_url = self.r_link_text.text()
        outfile = self.test_text.text()
        #self.result_text.setText("Working ...") # NOT WORKING
        #self.scrape_button.setEnabled(False)
        
        submission = self.reddit.submission(url=r_url)
        submission.comments.replace_more(limit=None)
        counter = 0
        with open(outfile, "w") as f:
            for comment in submission.comments.list():
                f.write(" == BEGIN COMMENT == \n")
                f.write(comment.body)
                f.write("\n == END COMMENT == \n")
                counter+=1
            f.write(f"Output {counter} comments")
        
        #self.scrape_button.setEnabled(True)
        self.result_text.setText(f"Output {counter} comments to file {outfile}")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = RGrabWidget()
    widget.show()

    sys.exit(app.exec())

