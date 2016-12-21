from sys import argv
from sys import exit
import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import DirDeletedEvent
from watchdog.events import FileDeletedEvent
from watchdog.events import DirCreatedEvent
from watchdog.events import FileCreatedEvent
import requests
import urllib
import shutil

class MyDropBox(PatternMatchingEventHandler):

    """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
    """
    
    def __init__(self,path, host):
        super(MyDropBox,self).__init__()
        self.path = path
        self.host = host
        self.freezeUpdate = False
        self.freezed = False
        
        if not(self.path.endswith('/')):
            self.path = self.path + '/'
            
        self.listFiles = self.getLocalListFiles()
        self.update()
        self.start()

        
    def start(self):
        observer = Observer()
        observer.schedule(self, self.path, recursive=True)
        observer.start()
        self.ignoreEvent = False

        try:
            while True:
                time.sleep(1)
                if not self.freezeUpdate:
                    self.freezed = False
                    self.update()
                else:
                    self.freezed = True
                
        except KeyboardInterrupt:
            print("bye")
            observer.stop()
            observer.join()
    
    #Event of wachdogs lib
    def on_created(self,event):
        if(self.ignoreEvent):
            print ("ignorado", event.src_path)
            self.ignoreEvent = False
            return
        
        self.freezeUpdate = True

        while not self.freezed:
            pass
        
        if event.is_directory:
            self.putDirName(event.src_path)
        else:
            self.sendFile(event.src_path)

        self.listFiles = self.getServerListFiles()

        
        print ("criado", event.src_path)
        
        self.freezeUpdate = False
    
        
    #event of watchdogs lib
    def on_deleted(self,event):
        if self.ignoreEvent == "dir":
            return
        
        if(self.ignoreEvent):
            print ("ignorado", event.src_path)
            self.ignoreEvent = False
            return

        self.freezeUpdate = True

        while not self.freezed:
            pass
        
        if event.is_directory:
            self.removeDir(event.src_path)
        else:
            self.removeFile(event.src_path)

        self.listFiles = self.getServerListFiles()

        print ("deletado",event.src_path)

        self.freezeUpdate = False

        
        
    def sendFile(self,filename):
        fileOpened = open(filename)
        filename = filename.split(self.path)[1]
        files = {filename: fileOpened }
        
        response = requests.put('http://'+self.host+'/putFile',files=files)
        fileOpened.close()
        print("Enviado arquivo:",filename)
        return response

    def putDirName(self,dirname):
        dirname = dirname.split(self.path)[1]
        response = requests.put('http://'+self.host+'/putDir',data={'dirname':dirname})
        print("Enviado diretorio:",dirname)
        return response


    def removeDir(self,dirname):
        dirname = dirname.split(self.path)[1]
        requests.delete('http://'+self.host+'/removeDir?dirname='+dirname)
    
    def retrieveFile(self,filepath,location):
        if not(location.endswith('/')):
            location = location + '/'

        filename = filepath.split(location)[1]
        filepath = filepath.split(self.path)[1]
        
        print("baixando: "+filepath)
        urllib.urlretrieve ('http://'+self.host+'/getFile?filename='+filepath, location+filename)

        
    def removeFile(self,filename):
        filename = filename.split(self.path)[1]
        requests.delete('http://'+self.host+'/removeFile?filename='+filename)

        
    def getServerListFiles(self):
        return requests.get('http://'+self.host+'/listFiles').json()

    
    def getLocalListFiles(self,path = None):
        if path is None:
            path = self.path
        elif not(path.endswith('/')):
            path = path + '/'
            
        dirListFiles = os.listdir(path)
        l = []
        for f in dirListFiles:
            if os.path.isdir(path+f):
                l.append({u'directory':{u'name':unicode(f),u'content':self.getLocalListFiles(path+f)}})
            else:
                l.append({u'file': unicode(f)})

        return l

    def getDirList(self,listFiles,dirname):
        for f in listFiles:
            if ('directory' in f):
                if unicode(f['directory']['name']) == unicode(dirname):
                    return f['directory']['content']
        return None
    
    def updateDelete(self,serverListFiles,
                     path = None, localListFiles = None):

        if path is None:
            path = self.path
        elif not(path.endswith('/')):
            path = path + '/'

        if localListFiles is None:
            localListFiles = self.listFiles
        
        for f in localListFiles:
            if ('file' in f) and not(f in serverListFiles):
                self.ignoreEvent = True
                print("update removendo arquivo: ",path+f['file'])
                os.remove(path+f['file'])
                localListFiles.remove(f)
                
            elif ('directory' in f):

                
                dirServerListFiles = self.getDirList(serverListFiles, f['directory']['name'])
                
                if not(dirServerListFiles is None):
                    dirLocalListFiles = f['directory']['content']
                    self.updateDelete(dirServerListFiles,path+f['directory']['name'],dirLocalListFiles)

                else:
                    self.ignoreEvent = "dir"
                    print("update removendo direitorio"+path+f['directory']['name'])
                    shutil.rmtree(path+f['directory']['name'], ignore_errors=True)
                    localListFiles.remove(f)
                    self.ignoreEvent = False
                    

    

                
    def updateDownload(self,serverListFiles,path = None,localListFiles = None):
        if path is None:
            path = self.path
        elif not(path.endswith('/')):
            path = path + '/'

        if localListFiles is None:
            localListFiles = self.listFiles
        
            
        for f in serverListFiles:
            if ('file' in f) and not(f in localListFiles):
                self.ignoreEvent = True
                print("update baixando arquivo: "+path+f['file'])
                self.retrieveFile(path+f['file'],path)
                localListFiles.append(f)

            elif ('directory' in f):
                dirLocalList = self.getDirList(localListFiles,f['directory']['name'])
                if (dirLocalList is None):
                    self.ignoreEvent = True
                    print("update criando diretorio: "+path+f['directory']['name'])
                    os.mkdir(path+f['directory']['name'])
                    localListFiles.append({u'directory':{u'name':unicode(f['directory']['name']), u'content': []}})

                dirServerListFiles = f['directory']['content']
                dirLocalListFiles = self.getDirList(localListFiles,f['directory']['name'])
                self.updateDownload(dirServerListFiles,path+f['directory']['name'],dirLocalListFiles)
                

                
    def update(self):
        listFiles = self.getServerListFiles()

        self.updateDelete(listFiles)
        self.updateDownload(listFiles)
        
        self.listFiles = listFiles
        
        
        
if __name__ == "__main__":
    if len(argv) < 2:
        raise "You must pass the dir path to observe as argument!"
    if not(os.path.isdir(argv[1])):
        raise "The path informed is not a dir path"

    if len(argv) == 3:
        host = argv[2]
    else:
        host = 'localhost:8081'
        
    MyDropBox(argv[1],host)

