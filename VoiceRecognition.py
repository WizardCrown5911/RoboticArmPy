import speech_recognition as sr

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()

    # Use the default microphone as the audio source
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now.")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        try:
            API= "OLBSHUX5DGNUTIB5RMIE2MMF657YNRIM"
            text = recognizer.recognize_wit(audio, key=API, )
            print(text)
            return text
        except sr.UnknownValueError:
            print("Wit could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Wit; {e}")

    except sr.WaitTimeoutError:
        print("Listening timed out while waiting for phrase to start.")
    except OSError as e:
        print(f"Microphone error: {e}")

if __name__ == "__main__":
    text=str(recognize_speech_from_mic()).lower()
    if "move" in text and "up" in text:
        print("moving up")
    if "move" in text and "left" in text:
        print("moving left")
    if "move" in text and "right" in text:
        print("moving right")
    if "move" in text and "down" in text:
        print("moving down")
    else:
        print("invalid command")