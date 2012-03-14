import numpy

class Voter(object):
    def init(self, utils):
        self.utils = utils
        
    def range_vote(self):
        maxu, minu = self.maxminu()
        span = (maxu - minu)
        return (self.utils - minu) / span
