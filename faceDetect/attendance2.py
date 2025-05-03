import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import pyttsx3
import smtplib
from twilio.rest import Client

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Maximum volume

# List available voices and select the first one (default system voice)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Use the first available voice

# Twilio configuration
twilio_sid = 'AC72b08c0d9048b5285501a1fb50287561'
twilio_auth_token = '7972e03223513e7ef8365e243a41c987'
twilio_phone_number = "+12517327309"

client = Client(twilio_sid, twilio_auth_token)

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_address = 'vanisridurai2004@gmail.com'
email_password = 'nuwgzsmiluktetcp'  # Use App Password if using Gmail with 2-step verification
notification_email = 'vanisridurai2004@gmail.com'
notification_phone_number = "+91 8946010002"

# Path where student images are stored
path = 'images'
images = []
classNames = []
mylist = os.listdir(path)

# Load and encode images
for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(img)[0]
        encodeList.append(encoded_face)
    return encodeList


encoded_face_train = findEncodings(images)
print("Encoding Complete")


def send_email(name):
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        subject = "Attendance Notification"
        body = f"Attendance marked for {name} on {datetime.now().strftime('%d-%B-%Y %I:%M:%S %p')}."
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(email_address, notification_email, message)
        print(f"Email sent for {name}")

def send_sms(name):
    message = client.messages.create(
        body=f"Attendance marked for {name} on {datetime.now().strftime('%d-%B-%Y %I:%M:%S %p')}.",
        from_= '+12517327309',
        to='+918946010002'
    )
    print(f"SMS sent for {name}: {message.sid}")


def markAttendance(name):
    today = datetime.now().strftime('%d-%B-%Y')
    filename = './attendance.csv'

    with open(filename, 'r+') as f:
        myDataList = f.readlines()
        nameList = [line.split(',')[0] for line in myDataList]

        if name not in nameList:
            now = datetime.now()
            time_str = now.strftime('%I:%M:%S %p')
            date_str = now.strftime('%d-%B-%Y')
            f.writelines(f'\n{name},{time_str},{date_str}')
            print(f"Attendance marked for {name} at {time_str} on {date_str}")

            # Voice notification
            engine.say(f"Attendance marked for {name}")
            engine.runAndWait()

            # Send email and SMS notifications
            send_email(name)
            send_sms(name)


# Confidence threshold for face recognition
confidence_threshold = 0.6

# Capture from the webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Resize to 1/4 size for faster processing
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces in the current frame
    faces_in_frame = face_recognition.face_locations(imgS)
    encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)

    for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
        # Check for matches with the known faces
        matches = face_recognition.compare_faces(encoded_face_train, encode_face)
        faceDist = face_recognition.face_distance(encoded_face_train, encode_face)
        matchIndex = np.argmin(faceDist)

        if matches[matchIndex] and faceDist[matchIndex] < confidence_threshold:
            name = classNames[matchIndex]
            print(f"Detected {name} with confidence {1 - faceDist[matchIndex]:.2f}")

            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            markAttendance(name)

    # Show the webcam feed
    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()
