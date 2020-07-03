import pytube
url = "https://www.youtube.com/watch?v=M2bz7YyRGdY"
yt = pytube.YouTube(url)
yt.streams.first().download()
