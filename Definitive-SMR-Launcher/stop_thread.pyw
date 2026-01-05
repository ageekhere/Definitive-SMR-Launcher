import __main__
def stopThread():
    __main__.gStopDownload.set()
    __main__.time.sleep(1.0)

