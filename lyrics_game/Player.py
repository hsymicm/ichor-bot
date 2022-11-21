class Player():
  def __init__(self, name=None, health=None):
    self.name = name
    self.health = health
    self.score = 0

  def setName(self, name):
    self.name = name

  def getName(self):
    return self.name

  def modifyHealth(self, num):
    self.health += num

  def setHealth(self, num):
    self.health = num

  def getHealth(self):
    return self.health

  def modifyScore(self, num):
    self.score += num

  def setScore(self, num):
    self.score = num

  def getScore(self):
    return self.score