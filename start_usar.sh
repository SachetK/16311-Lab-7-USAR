#!/bin/bash

# Raspberry Pi SSH details
PI_USER="pi"
PI_HOST="172.26.229.47"

# Robot directory on the Pi
ROBOT_DIR="/home/pi/robot/usar/"

# Paths to virtual environments and scripts on the Pi
VENV1="robot/bin/activate"
SCRIPT1="usar_control.py"

VENV2="env/bin/activate"
SCRIPT2="robot_stream.py"

# Path to the directory containing the local program
LOCAL_PROGRAM_DIR="$HOME/PycharmProjects/Lab 7"
LOCAL_SCRIPT="teleoperation.py"  # Adjust this to the actual script name

echo "Connecting to Raspberry Pi..."

# SSH into the Raspberry Pi and run the programs
ssh $PI_USER@$PI_HOST << EOF
  set -e  # Exit immediately if a command fails
  cd "$ROBOT_DIR"
  echo "Switched to directory: $ROBOT_DIR"

  # Start first script in background with its virtual environment
  source "$VENV1"
  python3 "$SCRIPT1" &
  PID1=\$!
  echo "Started $SCRIPT1 with PID \$PID1"

  # Start second script in background with its virtual environment
  source "$VENV2"
  python3 "$SCRIPT2" &
  PID2=\$!
  echo "Started $SCRIPT2 with PID \$PID2"

  # Wait for the processes to start successfully
  wait \$PID1
  wait \$PID2

  echo "Both scripts started successfully on the Raspberry Pi."
EOF

# Run a program on your local machine only if SSH commands succeeded
echo "Running local program..."
source "$LOCAL_PROGRAM_DIR/.venv/bin/activate"
python3 "$LOCAL_PROGRAM_DIR/$LOCAL_SCRIPT"