from sys import argv
import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler

class MyDropBox(PatternMatchingEventHandler):
    """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
    
    def on_created(self,event):
        print ("criado", event.src_path)
    def on_deleted(self,event):
        print ("deletado",event.src_path)

class SpyDir(threading.Thread):
    
    def __init__(self,path):
        threading.Thread.__init__(self)
        self.path = path

    def run(self):
        observer = Observer()
        observer.schedule(MyDropBox(), self.path, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

if __name__ == "__main__":
    if len(argv) < 2:
        raise "You must pass the path to observe as argument!"
    SpyDir(argv[1]).start()
