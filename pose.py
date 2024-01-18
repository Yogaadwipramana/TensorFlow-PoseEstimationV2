import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Fungsi ini mengambil tiga titik (a, b, c) sebagai input dan menghitung sudut antara mereka menggunakan arctan2.
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Video capture
# Membuka objek perekaman video (cap) untuk mengambil bingkai dari kamera default (0).
cap = cv2.VideoCapture(0)

# Curl counter variables
# Menginisialisasi variabel untuk menghitung curl (counter) dan melacak tahap curl (stage).
counter = 0
stage = None

# Set up mediapipe instance
# Membuat instance MediaPipe Pose dengan ambang kepercayaan tertentu untuk deteksi dan pelacakan pose.
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    # Memulai loop untuk membaca bingkai dari objek perekaman video.
    while cap.isOpened():
        ret, frame = cap.read()

        # Mengubah bingkai BGR menjadi RGB untuk deteksi pose, memproses bingkai menggunakan instance MediaPipe Pose (pose), dan mengembalikannya ke BGR untuk rendering.
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        # Make detection
        results = pose.process(image)
        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        # Mengambil landmark pose untuk bahu kiri, siku, dan pergelangan tangan. Menghitung sudut menggunakan fungsi yang telah ditentukan sebelumnya.
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Visualize angle
            cv2.putText(image, str(angle),
                        tuple(np.multiply(elbow, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Curl counter logic
            # Melacak tahap curl berdasarkan sudut. Jika sudut di atas 160, tahap adalah "down." Jika sudut turun di bawah 30 setelah berada dalam tahap "down," tingkatkan penghitung.
            if angle > 160:
                stage = "down"
            if angle < 30 and stage == 'down':
                stage = "up"
                counter += 1
                print(counter)

        except:
            pass

        # Render curl counter
        # Setup status box
        # Merender informasi tentang jumlah repetisi (counter) dan tahap curl saat ini (stage) pada bingkai.
        cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

        # Rep data
        cv2.putText(image, 'REPS', (15, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter),
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Stage data
        cv2.putText(image, 'STAGE', (65, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage,
                    (60, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Render detections
        # Menggambar landmark pose pada bingkai.
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                )

        # Menampilkan bingkai dengan informasi dan landmark yang telah dirender.
        cv2.imshow('Mediapipe Feed', image)

        # Keluar dari loop dan lepaskan sumber daya jika tombol 'q' ditekan.
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    # Melepaskan objek perekaman video dan menutup semua jendela OpenCV.
    cap.release()
    cv2.destroyAllWindows()