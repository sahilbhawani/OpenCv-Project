import cv2
import numpy as np
import av
import mediapipe as mp
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import time
from cvzone.HandTrackingModule import HandDetector
import cvzone
import math
import HandTrackingModule as htm


print(cv2.__version__)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def process(image):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    return cv2.flip(image, 1)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


class VideoProcessor:

    detector2 = HandDetector(detectionCon=0.8, maxHands=2)
    detector = htm.handDetector(detectionCon=0.8,maxHands=2)
    devices = AudioUtilities.GetSpeakers()

    x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
    y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C
    pTime = 0
    cTime = 0

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        img = process(img)
        
    # FPS
    
        self.cTime = time.time()
        fps = 1 / (self.cTime - self.pTime)
        self.pTime = self.cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    # Hand Distance

        hands = self.detector2.findHands(img, draw=False)
        image = self.detector.findHands(img)

        closehand = []
        if hands:
            for i in range(len(hands)):

                lmList = hands[i]['lmList']
                x, y, w, h = hands[i]['bbox']
                x1, y1 , z1 = lmList[5]
                x2, y2 , z2 = lmList[17]

                distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
                A, B, C = self.coff
                distanceCM = A * distance ** 2 + B * distance + C
                closehand.append(distanceCM)

        numOfHands = len(closehand)
        if(numOfHands==0):
            position = self.detector.findPosition(image, draw=False)
            print("No hands detected")
        elif(numOfHands==1):
            position = self.detector.findPosition(image, draw=False)
            cvzone.putTextRect(img, f'{int(distanceCM)} cm', (50,100))
        else:
            if(closehand[0]>closehand[1]):
                position = self.detector.findPosition(img, 1,draw=False)
                cvzone.putTextRect(img, f'{int(closehand[1])} cm', (50,100))
            else:
                position = self.detector.findPosition(img, draw=False)
                cvzone.putTextRect(img, f'{int(closehand[0])} cm', (50,100))
    
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    # Face Analysis Application #
    st.title("Gesture Volume Control using Hand Detection")
    activiteis = ["Home", "Webcam Face Detection"]
    choice = st.sidebar.selectbox("Select Activity", activiteis)
    st.sidebar.markdown(
        """ Developed by 

            Group Members:
            Saurabh_Keskar
            Sahil Bhawani
            Ajay Mahajan
            Sushant Gawade
        """)
    if choice == "Home":
        html_temp_home1 = """<div style="background-color:#6D7B8D;padding:10px">
                                            <h4 style="color:white;text-align:center;">
                                            The hand detected from video stream is used to control volume of device in real time using OpenCV , MediaPipe and PyCaw Libraries</h4>
                                            </div>
                                            </br>"""
        st.markdown(html_temp_home1, unsafe_allow_html=True)
        st.write("""
                 The application has two functionalities.

                 1. Real time Hand Detection using web cam feed

                 2. Measure hand distance and control volume using nearest hand

                 """)
    elif choice == "Webcam Face Detection":
        st.header("Webcam Live Feed")
        st.write("Click on start to use webcam and detect your face emotion")
        webrtc_streamer(
    key="WYH",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_processor_factory=VideoProcessor,
    async_processing=True,
)

    else:
        pass


if __name__ == "__main__":
    main()
