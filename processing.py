import requests
import numpy as np
import cv2

# URL of the MJPEG stream
url = 'http://172.26.229.47:7123/stream.mjpg'

lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

def main():
    # Initialize variables to smooth direction over time
    last_direction = None
    last_majority_direction = None
    direction_counts = {"left": 0, "right": 0}
    direction_history = []  # Store direction history for smoothing
    angle_history = []  # Store angles for smoothing
    frame_count = 0

    # Open the stream
    stream = requests.get(url, stream=True)

    # Iterate over the stream and process each frame
    bytes_data = b''
    for chunk in stream.iter_content(chunk_size=1024):
        bytes_data += chunk
        a = bytes_data.find(b'\xff\xd8')  # JPEG start
        b = bytes_data.find(b'\xff\xd9')  # JPEG end

        if a != -1 and b != -1:
            jpg = bytes_data[a:b + 2]
            bytes_data = bytes_data[b + 2:]

            # Convert to image
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_blue, upper_blue)

            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # Perform morphological operations to remove noise
            kernel = np.ones((5, 5), np.uint8)  # A 5x5 kernel
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Close small holes
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # Remove small objects

            # Find contours in the thresholded image
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop through the contours to find the arrow
            for contour in contours:
                # Calculate the bounding box of the contour
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h)
                if aspect_ratio > 1.5 and w > 50 and h > 50:  # Adjust this threshold as necessary
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Fit a rotated rectangle to the contour to get the direction of the arrow
                    rect = cv2.minAreaRect(contour)

                    # Get the angle of rotation of the bounding box
                    angle = rect[2]
                    angle_history.append(angle)

                    # Smooth the angle using a moving average
                    if len(angle_history) > 5:  # Limit history size
                        angle_history.pop(0)  # Remove the oldest entry
                    avg_angle = np.mean(angle_history)

                    # Check if the direction has changed too rapidly
                    if last_direction is not None:
                        # Calculate the difference in angle (absolute value)
                        angle_diff = abs(avg_angle - last_direction)

                        if angle_diff < 5:
                            direction = last_direction  # Keep the last direction if change is too small
                        else:
                            # Classify direction based on average angle
                            if -45 < avg_angle < 45:
                                direction = "right"
                            else:
                                direction = "left"
                    else:
                        # If there's no previous direction, assign based on the angle
                        if -45 < avg_angle < 45:
                            direction = "right"
                        else:
                            direction = "left"

                    # Store the current direction
                    last_direction = 1 if direction == "right" else -1
                    direction_history.append(direction)

                    # Limit history size to avoid memory overflow
                    if len(direction_history) > 5:
                        direction_history.pop(0)

                    # Update the direction counts
                    if direction == "right":
                        direction_counts["right"] += 1
                    elif direction == "left":
                        direction_counts["left"] += 1

                    # Get the majority direction based on counts
                    majority_direction = "right" if direction_counts["right"] > direction_counts["left"] else "left"

                    # Output the detected direction (instead of drawing a line)
                    if last_majority_direction is None or majority_direction != last_majority_direction:
                        print(f"Majority Direction: {majority_direction}")

                    last_majority_direction = majority_direction

            # Do something with the frame (e.g., display it)
            cv2.imshow('Video Feed', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()