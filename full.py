from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy, QFileDialog
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
import cv2 
import mediapipe as mp
import pyautogui
import time
import threading 
import logging
def fingers():
    def count_fingers(lst):
        cnt = 0

        thresh = (lst.landmark[0].y*100 - lst.landmark[9].y*100)/2

        if (lst.landmark[5].y*100 - lst.landmark[8].y*100) > thresh:
            cnt += 1

        if (lst.landmark[9].y*100 - lst.landmark[12].y*100) > thresh:
            cnt += 1

        if (lst.landmark[13].y*100 - lst.landmark[16].y*100) > thresh:
            cnt += 1

        if (lst.landmark[17].y*100 - lst.landmark[20].y*100) > thresh:
            cnt += 1

        if (lst.landmark[5].x*100 - lst.landmark[4].x*100) > 6:
            cnt += 1


        return cnt 

    cap = cv2.VideoCapture(0)

    drawing = mp.solutions.drawing_utils
    hands = mp.solutions.hands
    hand_obj = hands.Hands(max_num_hands=1)


    start_init = False 

    prev = -1

    while True:
        end_time = time.time()
        _, frm = cap.read()
        frm = cv2.flip(frm, 1)

        res = hand_obj.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

        if res.multi_hand_landmarks:

            hand_keyPoints = res.multi_hand_landmarks[0]

            cnt = count_fingers(hand_keyPoints)

            if not(prev==cnt):
                if not(start_init):
                    start_time = time.time()
                    start_init = True

                elif (end_time-start_time) > 0.2:
                    if (cnt == 1):
                        pyautogui.press("right")
                
                    elif (cnt == 2):
                        pyautogui.press("left")

                    elif (cnt == 3):
                        pyautogui.press("up")

                    elif (cnt == 4):
                        pyautogui.press("down")

                    elif (cnt == 5):
                        pyautogui.press("space")

                    prev = cnt
                    start_init = False


        


            drawing.draw_landmarks(frm, hand_keyPoints, hands.HAND_CONNECTIONS)
        
        cv2.imshow("window", frm)

        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            cap.release()
            break 
        time.sleep(0.01) 
def gui():
    class Window(QWidget):
        def _init_(self):
            super()._init_()

            self.setWindowTitle("PyQt5 Media Player")
            self.setGeometry(350, 100, 700, 500)
            self.setWindowIcon(QIcon('player.png'))

            p =self.palette()
            p.setColor(QPalette.Window, Qt.black)
            self.setPalette(p)

            self.init_ui()


            self.show()


        def init_ui(self):

            
            self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)


            

            videowidget = QVideoWidget()


            
            openBtn = QPushButton('Open Video')
            openBtn.clicked.connect(self.open_file)



            
            self.playBtn = QPushButton()
            self.playBtn.setEnabled(False)
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playBtn.clicked.connect(self.play_video)



        
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setRange(0,0)
            self.slider.sliderMoved.connect(self.set_position)



            
            self.label = QLabel()
            self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


            
            hboxLayout = QHBoxLayout()
            hboxLayout.setContentsMargins(0,0,0,0)

            
            hboxLayout.addWidget(openBtn)
            hboxLayout.addWidget(self.playBtn)
            hboxLayout.addWidget(self.slider)



            
            vboxLayout = QVBoxLayout()
            vboxLayout.addWidget(videowidget)
            vboxLayout.addLayout(hboxLayout)
            vboxLayout.addWidget(self.label)


            self.setLayout(vboxLayout)

            self.mediaPlayer.setVideoOutput(videowidget)


            

            self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
            self.mediaPlayer.positionChanged.connect(self.position_changed)
            self.mediaPlayer.durationChanged.connect(self.duration_changed)


        def open_file(self):
            filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

            if filename != '':
                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
                self.playBtn.setEnabled(True)


        def play_video(self):
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()

            else:
                self.mediaPlayer.play()


        def mediastate_changed(self, state):
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.playBtn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause)

                )

            else:
                self.playBtn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay)

                )

        def position_changed(self, position):
            self.slider.setValue(position)


        def duration_changed(self, duration):
            self.slider.setRange(0, duration)


        def set_position(self, position):
            self.mediaPlayer.setPosition(position)


        def handle_errors(self):
            self.playBtn.setEnabled(False)
            self.label.setText("Error: " + self.mediaPlayer.errorString())
    time.sleep(0.01)




    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
start=time.time()
finger_thread=threading.Thread(target=fingers,args=())
gui_thread=threading.Thread(target=gui,args=())

finger_thread.start()
gui_thread.start()

finger_thread.join()
gui_thread.join()
end = time.time()