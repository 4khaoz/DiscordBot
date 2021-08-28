class Song:
    def __init__(self, title: str, url, source, thumbnail):
        self.title = title
        self.url = url
        self.source = source
        self.thumbnail = thumbnail


class SongQueue:
    def __init__(self):
        self.queue = []

    def addSongToQueue(self, s: Song):
        self.queue.append(s)

    def getNextSong(self):
        if (not self.queue):
            return None
        return self.queue.pop(0)