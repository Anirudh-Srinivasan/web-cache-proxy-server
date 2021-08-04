from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow
from ClientUI_V2 import Ui_MainWindow
import socket
import sys
import requests
import pickle
import time

class ClientUiWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)        
        self.ui.searchButton.clicked.connect(self.actionClicked)
        self.ui.actionAbout.triggered.connect(self.actionAboutClicked)
        self.ui.actionClose.triggered.connect(self.actionCloseClicked)
    
    def getDetails(self):
        self.serverAddress = self.ui.serverAddress.toPlainText()
        self.serverPort = self.ui.serverPort.toPlainText()
        self.urlText = self.ui.urlText.toPlainText()
        self.timeText = self.ui.timeText.toPlainText()
    
    def actionCloseClicked(self):
        self.close()
        
    def actionAboutClicked(self):
        QtWidgets.QMessageBox.information(self, "About", "Done By: Anirudh S\nRegistration Number: 122003029\nYear: III\nCourse: B.Tech\nDegree: Computer Science and Engineering")        
        
    
    def actionClicked(self):
        try:
            self.getDetails()
            conditionPort = False
            conditionAddress = False
            conditionUrl = False
            if(self.serverAddress == ''):
                QtWidgets.QMessageBox.critical(self, "Error", "Server Address is empty")        
            elif((self.serverAddress.strip() == '127.0.0.1' or self.serverAddress.strip() == 'localhost') is False):       
                QtWidgets.QMessageBox.critical(self, "Error", "Server IP not '127.0.0.1' warning")
                self.ui.serverAddress.clear()
            else:
                conditionAddress = True
            
            if(self.serverPort == ''):
                QtWidgets.QMessageBox.critical(self, "Error", "Server Port is empty")
            elif(self.serverPort != '8085'):
                QtWidgets.QMessageBox.critical(self, "Error", "Server Port not '8085' warning")
                self.ui.serverPort.clear()
            else:
                conditionPort = True
            
            if(self.urlText==''):
                QtWidgets.QMessageBox.critical(self, "Error", "Enter a non Empty URL")        
            elif(self.urlText.startswith("https://") is False):
                QtWidgets.QMessageBox.critical(self, "Error", "URL not entered Correctly")
                self.ui.urlText.clear()
            else:
                conditionUrl = True    
            
            if conditionPort and conditionAddress and conditionUrl:
                self.ui.searchButton.setEnabled(False)
                self.ui.serverAddress.setReadOnly(True)
                self.ui.serverPort.setReadOnly(True)
                self.ui.urlText.setReadOnly(True)

                try:                    
                    client = socket.socket()                    
                    print("Client Socket created successfully")
                except socket.error as e:
                    print("Socket Creation failed with ", e)
                    
                time_start = time.process_time_ns()
                client.connect((self.serverAddress, int(self.serverPort)))
                #URL Send
                client.send(self.urlText.encode())
                #Request Status in cache
                cacheStatusPickled = client.recv(2048)
                cacheStatus = pickle.loads(cacheStatusPickled)
                # Changing the Hit and Miss Count
                self.ui.hitCount.setFont(QFont("MS Shell Dlg 2",16))
                self.ui.missCount.setFont(QFont("MS Shell Dlg 2",16))
                self.ui.hitCount.setText(str(cacheStatus[1]))
                self.ui.hitCount.adjustSize()
                self.ui.missCount.setText(str(cacheStatus[2]))
                self.ui.missCount.adjustSize()
                
                QtWidgets.QMessageBox.information(self, "Caching Info", "The Request to url\n" + self.urlText + "\n is a " + cacheStatus[0])                
                
                #print("Request Status: ", cacheStatus)
                #Acknowledgement Sending
                client.send("OK".encode())
                received = b''
                while True:                    
                    recv = client.recv(4096)
                    received += recv
                    if(len(recv)<4096):  
                        break
                
                response = pickle.loads(received)
                
                #Elapsed time
                elapsed_time = time.process_time_ns() - time_start
                self.ui.webPage.setReadOnly(False)
                self.ui.timeText.setPlainText(str(elapsed_time))
                self.ui.webPage.setPlainText(response.text)
                #requestStatus = client.recv(1024).decode()
                file_name = self.urlText[8:38]
                file_name = file_name.replace('/', '_')
                with open(file_name+'.html','wb') as fin:
                    fin.write(response.text.encode())               
                client.close()
                QtWidgets.QMessageBox.information(self, "", "This Client is disconnected! \nKindly Close the Client UI")        
        except Exception as e:
            print(str(e))
               
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ClientUiWindow()
    win.show()
    app.exec_()
        
    