# Text-to-Speech converter
import subprocess  # Allows running terminal commands
#run in terminal: sudo apt-get install espeak

def speak(text):
    subprocess.Popen(["espeak", text], stderr=subprocess.DEVNULL)
