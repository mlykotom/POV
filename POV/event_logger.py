import os
import datetime


class EventLogger:
    def __init__(self, filename):
        self.filename = filename
        self.events = []

    def save(self):
        with open(self.filename, 'w') as file:
            for event in self.events:
                file.write(event + '\n')

    def addEvent(self, time, eventType, description):
        # Python implicitly add 1 hear in from timestamp 
        eventDatetime = datetime.datetime.fromtimestamp(time / 1000.0) - + datetime.timedelta(hours=1)
        event = '{:%H:%M:%S.%f} {} {}'.format(eventDatetime, eventType, description)
        self.events.append(event)

    def addTouch(self, time, dummy):
        dummyId = dummy.get_player_index()
        # We internally index lines from 0 index but in result script there is indexed from 1
        self.addEvent(time, "TOUCH", str(dummyId[0] + 1) + ',' + str(dummyId[1]))

    def addGoal(self, time, playerId):
        self.addEvent(time, "GOAL", str(playerId))

    def print(self):
        print(self.events)
