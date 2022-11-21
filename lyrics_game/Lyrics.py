import random, os
from difflib import SequenceMatcher

class Lyrics():
  
  # Constructor
  def __init__(self, path):
    self.path = path
    self.songs = self._listFilesForFolder(path)
    self.choosenSong = None
    self.answer = None
    self.question = None
    self.setQuestion()
    
  # Set a question
  def setQuestion(self):
    lyrics = self._splice(random.choice(self.songs))
    answerIndex = random.randint(0, len(lyrics)-1)
    self.answer = lyrics[answerIndex]
    lyrics[answerIndex] = "`--- *Guess this blank line* ---`"
    self.question = "\n".join(lyrics)

  # Get a question
  def getQuestion(self):
    return self.question

  # Get an answer
  def getAnswer(self):
    return self.answer

  # Compare player answer
  def checkPlayerAnswer(self, playerAnswer):
    s = SequenceMatcher(None, self.answer, playerAnswer)
    if s.ratio() > 0.7:
      return True
    else:
      return False

  # Returns array of songs
  def getSongList(self):
    return "\n".join([
      f"{count}. {songs}" for count, songs in enumerate([
        song.split("/")[-1].split(".")[0] for song in self.songs
      ], 1)])

  # Returns the choosen song
  def getChoosenSong(self):
    return self.choosenSong

  # Splice lyrics to a random phrase and split them
  def _splice(self, songPath):
    lyrics = self._readFile(songPath)
    self.choosenSong = songPath.split("/")[-1].split(".")[0]
    return random.choice(lyrics)

  # Generate list from folder
  def _listFilesForFolder(self, path):
    return [
      (path + filename) for filename in os.listdir(path) 
      if os.path.isfile(os.path.join(path, filename))
    ]

  # Read file from path
  def _readFile(self, path):
    f = open(path)
    lyrics = f.read()
    f.close()
    return [i.split("\n") for i in lyrics.split("\n\n")]
