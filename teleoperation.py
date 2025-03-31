import curses
import socket
import time

DEBOUNCE_TIME = 0.1 # Time in seconds to wait before registering a new key press
INACTIVE_TIME = 0.5  # Time to wait before stopping the robot when no key is pressed

def main(stdscr):
    HOST = "172.26.229.47"  # Replace with your Raspberry Pi's IP address
    DRIVE_PORT = 5000  # Choose a port number
    SERVO_PORT = 5001

    drive_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    drive_sock.connect((HOST, DRIVE_PORT))

    servo_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servo_sock.connect((HOST, SERVO_PORT))

    print("Drive connected to %s:%d" % (HOST, DRIVE_PORT))
    print("Servo connected to %s:%d" % (HOST, SERVO_PORT))

    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)  # Makes getch non-blocking
    stdscr.timeout(100)
    stdscr.keypad(True)

    key_mapping = {
        curses.KEY_UP: "FORWARD",
        curses.KEY_DOWN: "BACKWARD",
        curses.KEY_LEFT: "LEFT",
        curses.KEY_RIGHT: "RIGHT",
        ord("w"): "CAMERA_TOP",
        ord("s"): "CAMERA_MIDDLE",
        ord("x"): "CAMERA_BOTTOM",
        ord("o"): "TOGGLE_LEVER",
        ord("p"): "TOGGLE_CLAW",
    }

    last_command = None
    last_pressed_time = 0  # Time when the last key was pressed
    last_activity_time = time.time()  # Track last activity time to detect inactivity

    try:
        while True:
            key = stdscr.getch()
            current_time = time.time()  # Get the current time

            if key in key_mapping and (current_time - last_pressed_time > DEBOUNCE_TIME):
                command = key_mapping[key]
                last_pressed_time = current_time
                last_activity_time = current_time  # Update last activity time

            elif current_time - last_activity_time > INACTIVE_TIME:
                command = "STOP"

            else:
                command = last_command  # Keep the previous command if still active

            if command != last_command:
                stdscr.clear()
                stdscr.addstr(0, 0, f"Command: {command}")
                stdscr.refresh()

                # **Send command to the server**
                drive_sock.sendall(command.encode())
                servo_sock.sendall(command.encode())

                last_command = command

            time.sleep(0.02)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        pass

    finally:
        drive_sock.sendall(b"STOP")  # Ensure the robot stops
        drive_sock.close()
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)