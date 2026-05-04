with open("app/static/audio/speech_20260329222337.mp3", "rb") as f:
    data = f.read(32)
    print(data)
    print(data.hex(" "))