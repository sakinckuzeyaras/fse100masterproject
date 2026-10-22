# Text-to-Speech converter

def speak(text):
    text = text.replace(" ", "_")  # Replace spaces with underscores to prevent parsing issues
    subprocess.run((
        "espeak \"" + text + "\" 2>/dev/null"
    ).split(" "))  # Construct the command and split into tokens for subprocess.run