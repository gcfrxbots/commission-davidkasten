from threading import Thread
from Initialize import *
initSetup()
from Resources import *


def main():
    print("Starting")

    resetStartAgain()
    while True:
        time.sleep(2)
        try:
            startRequest()

        except Exception as e:
            print("Error detected - Trying again.")
            print(e)
            resetStartAgain()


def tick():
    prevTime = datetime.datetime.now()
    while True:
        time.sleep(0.4)

        if misc.timerActive:
            for timer in misc.timers:
                if datetime.datetime.now() > misc.timers[timer]:
                    misc.timerDone(timer)
                    break

        # Timers that send stuff every X seconds

        # if datetime.datetime.now() > prevTime + datetime.timedelta(minutes=settings["TIMER DELAY"]):
        #     chatConnection.sendToChat(resources.askChatAQuestion())
        #     prevTime = datetime.datetime.now()


if __name__ == "__main__":
    t1 = Thread(target=main)
    t2 = Thread(target=tick)

    t1.start()
    t2.start()