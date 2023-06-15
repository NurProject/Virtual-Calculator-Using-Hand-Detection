import cv2
import mediapipe as mp
import math

# Function to calculate the Euclidean distance between two points
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to detect button press based on hand landmarks
def detect_button_press(lm_list, button_positions):
    for i, button_pos in enumerate(button_positions):
        button_x, button_y = button_pos
        dist = calculate_distance(lm_list[8][0], lm_list[8][1], button_x, button_y)
        if dist < 40:  # Adjust this threshold based on your hand size and camera resolution
            return i
    return None

# Load the hand detection module
mp_hands = mp.solutions.hands

# Open the laptop's webcam
video_capture = cv2.VideoCapture(0)

# Create a hand detection object
with mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7) as hands:
    # Calculator button positions
    button_positions = [(80, 200), (180, 200), (280, 200), (380, 200),  # Number buttons: 1, 2, 3, +
                        (80, 300), (180, 300), (280, 300), (380, 300),  # Number buttons: 4, 5, 6, -
                        (80, 400), (180, 400), (280, 400), (380, 400),  # Number buttons: 7, 8, 9, *
                        (80, 500), (180, 500), (280, 500), (380, 500),  # Number buttons: 0, Clear, =, /
                        (380, 100)]  # Display button

    current_number = ""  # Variable to store the current number being input
    result = None  # Variable to store the result of calculations

    while True:
        # Read each frame from the webcam
        ret, frame = video_capture.read()

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to detect hands
        results = hands.process(frame_rgb)

        # Check if hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm_list = []
                for lm in hand_landmarks.landmark:
                    # Convert normalized landmark coordinates to pixel coordinates
                    h, w, c = frame.shape
                    x, y = int(lm.x * w), int(lm.y * h)
                    lm_list.append((x, y))

                button_index = detect_button_press(lm_list, button_positions)

                if button_index is not None:
                    if button_index <= 9:  # Number buttons: 0-9
                        current_number += str(button_index)
                    elif button_index == 10:  # Clear button
                        current_number = ""
                        result = None
                    elif button_index == 11:  # Equal button (=)
                        try:
                            result = eval(current_number)
                        except:
                            result = "Error"
                    elif button_index == 12:  # Display button
                        pass  # Do nothing for the display button
                    break

        # Draw calculator buttons on the frame
        for i, button_pos in enumerate(button_positions):
            button_x, button_y = button_pos
            cv2.circle(frame, (button_x, button_y), 30, (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, str(i), (button_x - 10, button_y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Draw the current number and result on the frame
        cv2.putText(frame, "Input: " + current_number, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if result is not None:
            cv2.putText(frame, "Result: " + str(result), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow('Virtual Calculator', frame)

        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the video capture object and close the window
video_capture.release()
cv2.destroyAllWindows()
