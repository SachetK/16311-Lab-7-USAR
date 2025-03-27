import pygame
import socket
import json

def compute_wheel_powers(forward, turn):
    """
    Compute left and right wheel power values between -1 and 1.
    """
    left_power = forward + turn
    right_power = forward - turn

    # Normalize to ensure values stay within -1 to 1
    max_val = max(abs(left_power), abs(right_power), 1)
    left_power = (left_power / max_val)
    right_power = (right_power / max_val)

    return left_power, right_power

def main():
    # Initialize Pygame
    pygame.init()
    pygame.joystick.init()

    # Check for joystick
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Connected to {joystick.get_name()}")

    host = "172.26.229.47"  # Replace with your Raspberry Pi's IP address
    port = 5000  # Choose a port number

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    print("Connected to %s:%d" % (host, port))

    # Main loop
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Joystick control (if available)
        if joystick:
            # Get joystick inputs
            forward_input = -joystick.get_axis(1)  # Left joystick Y-axis (forward/backward)
            turn_input = joystick.get_axis(2)  # Right joystick X-axis (turn left/right)

            # Compute wheel power outputs
            left_power, right_power = compute_wheel_powers(forward_input, turn_input)

            print(f"Left Power: {left_power:.2f}, Right Power: {right_power:.2f}")

            # Create a JSON message
            message = json.dumps({"left": left_power ** 3, "right": right_power ** 3}) + "\n"

            try:
                sock.sendall(message.encode())  # Send to Raspberry Pi
            except BrokenPipeError:
                print("Lost connection to the server.")
                break

            print(f"Sent: {message}")

    pygame.quit()
    sock.close()



if __name__ == "__main__":
    main()