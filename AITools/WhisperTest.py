import time

import Whisper

w = Whisper.Whisper("C:\\Users\\RARI\\Documents\\Repos\\whisper-large-v3")
s = time.time()
print(w.transcribe(" ecording (5).mp3"))
print(time.time() - s)