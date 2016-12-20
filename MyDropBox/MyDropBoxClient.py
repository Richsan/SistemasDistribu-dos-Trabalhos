from sys import argv
from sys import exit
import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
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
    
    def __init__(self,path):
        super(MyDropBox,self).__init__()
        self.path = path
        self.freezeUpdate = False

        if not(self.path.endswith('/')):
            self.path = self.path + '/'
            
        self.listFiles = self.getLocalListFiles()
        self.update()
        self.start()

        
    def start(self):
        observer = Observer()
        observer.schedule(self, self.path, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
                if not self.freezeUpdate:
                    self.update()
                
        except KeyboardInterrupt:
            print("bye")
            observer.stop()
            observer.join()
    
    #Event of wachdogs lib
    def on_created(self,event):
        print ("criado", event.src_path)

        self.freezeUpdate = True
        
        if event.is_directory:
            self.putDirName(event.src_path)
        else:
            self.sendFile(event.src_path)

        self.listFiles = self.getLocalListFiles()
        
        self.freezeUpdate = False
    
        
    #event of watchdogs lib
    def on_deleted(self,event):
        print ("deletado",event.src_path)

        self.freezeUpdate = True
        
        if event.is_directory:
            self.removeDir(event.src_path)
        else:
            self.removeFile(event.src_path)

        self.listFiles = self.getLocalListFiles()
        
        self.freezeUpdate = False

        
        
    def sendFile(self,filename):
        fileOpened = open(filename)
        filename = filename.split('client/')[1]
        files = {filename: fileOpened }
        
        print("Enviando: ",filename)
        response = requests.put('http://localhost:8081/putFile',files=files)
        fileOpened.close()
        return response

    def putDirName(self,dirname):
        dirname = dirname.split(self.path)[1]
        response = requests.put('http://localhost:8081/putDir',data={'dirname':dirname})
        return response


    def removeDir(self,dirname):
        dirname = dirname.split(self.path)[1]
        requests.delete('http://localhost:8081/removeDir?dirname='+dirname)
    
    def retrieveFile(self,filepath,location):
        if not(location.endswith('/')):
            location = location + '/'

        filename = filepath.split(location)[1]
        filepath = filepath.split(self.path)[1]
        
        print("baixando: "+filepath)
        urllib.urlretrieve ("http://localhost:8081/getFile?filename="+filepath, location+filename)

        
    def removeFile(self,filename):
        filename = filename.split(self.path)[1]
        requests.delete('http://localhost:8081/removeFile?filename='+filename)

        
    def getServerListFiles(self):
        return requests.get('http://localhost:8081/listFiles').json()

    
    def getLocalListFiles(self,path = None):
        if path is None:
            path = self.path
        elif not(path.endswith('/')):
            path = path + '/'
            
        dirListFiles = os.listdir(path)
        l = []
        for f in dirListFiles:
            if os.path.isdir(path+"/"+f):
                l.append({u'directory':{u'name':unicode(f),u'content':self.getLocalListFiles(path+f)}})
            else:
                l.append({u'file': unicode(f)})

        return l

    def getDirList(self,listFiles,dirname):
        for f in listFiles:
            if ('directory' in f):
                if f['directory']['name'] == dirname:
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
                os.remove(path+f['file'])
                localListFiles.remove(f)
                
            elif ('directory' in f):
                if not(f in serverListFiles):
                    shutil.rmtree(path+f['directory']['name'], ignore_errors=True)
                    localListFiles.remove(f)
                else:
                    dirServerListFiles = self.getDirList(serverListFiles, f['directory']['name'])
                    dirLocalListFiles = f['directory']['content']
                    self.updateDelete(dirServerListFiles,path+f['directory']['name'],dirLocalListFiles)

                
    def updateDownload(self,serverListFiles,path = None,localListFiles = None):
        if path is None:
            path = self.path
        elif not(path.endswith('/')):
            path = path + '/'

        if localListFiles is None:
            localListFiles = self.listFiles
        
            
        for f in serverListFiles:
            if ('file' in f) and not(f in localListFiles):
                self.retrieveFile(path+f['file'],path)
                localListFiles.append(f)

            elif ('directory' in f):
                if not(f in self.listFiles):
                    os.mkdir(path+f['directory']['name'])
                    localListFiles.append({"directory":{"name":f['directory']['name'], "content":[]}})
                    
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

    MyDropBox(argv[1])

