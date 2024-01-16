import Whisper

w = Whisper.Whisper("C:\\Users\\RARI\\Documents\\Repos\\whisper-large-v3")
print(w.get_text("C:\\Users\\RARI\\Documents\\Sound Recordings\\test.mp3"))