import os, cgi, shutil, glob
import subprocess
from threading import Thread
import time
import thread
import json
import SocketServer , SimpleHTTPServer
import re

class BooleanFile():
    def __init__(self, fileName):
        self.booleanFileName = fileName
    
    def createFile(self, text =''):
        if not self.fileExists():
            booleanFile = open(self.booleanFileName, 'w')
            booleanFile.write(text)
            booleanFile.close()
    
    def readFile(self ):
        params = {}
        if self.fileExists():
            booleanFile = open(self.booleanFileName, 'r')
            params = json.load(booleanFile)
            
        return params        
    def fileExists(self):
        return os.path.lexists(self.booleanFileName)
    
    def removeFile(self):
        if os.path.lexists(self.booleanFileName):
            os.remove(self.booleanFileName)
        
    
class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def getPostVars(self):
        if int(self.headers.getheader('content-length')) > 0:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                postvars = {}
        else:
            postvars = {}
        return postvars
    
    def do_POST(self):
         
        p = self.path.split("?")
        path = p[0][1:].split("/")
        
        postvars = self.getPostVars()
        
        if postvars.has_key('videoDevice'):
            videoDevice = postvars['videoDevice'][0]
        else:
            videoDevice = self.server.WEBCAM[0]
                
        if path[-1] == 'stop':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

        
            #self.server.stopFile.createFile()
            self.server.stopSignal = True
            self.wfile.write(json.dumps({'status' :'stop sent'} ))
        
        elif path[-1] == 'getVideoDevices':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write( json.dumps(self.server.WEBCAM) )
            
        elif path[-1] == 'projectList':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            directoriesNames = os.listdir(self.server.mediaFolderDefault)
            projectObject = []
            for projectName in directoriesNames:
                folder = self.getProjectFolder( projectName )
                outputFileName = folder + self.server.outputFileName
                if os.path.lexists(outputFileName):
                    outputFilePath = outputFileName
                else:
                    outputFilePath = None
                    
                firstImageFileName = folder + self.server.firstImageFileName
                if os.path.lexists(firstImageFileName):
                    firstImageFileName = firstImageFileName
                else:
                    firstImageFileName = None
                    
                projectObject.append({'name': projectName,'outputFilePath':outputFilePath,'firstImageFileName': firstImageFileName})
            self.wfile.write( json.dumps({'list' : projectObject}))
            
        elif path[-1] == 'active':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            if self.server.isActive:
                params = self.server.lastActivationParams
                params['lastPictureTime'] = self.server.lastPictureTime
                if self.server.stopSignal:
                    self.wfile.write(json.dumps({'active' :True,'params':params,'message':'stopping on next cycle'} ))
                else:
                    self.wfile.write(json.dumps({'active' :True,'params':params,'message':'time lapse active'} ))
            else:
                self.wfile.write( json.dumps({'active' :False,'message':'time lapse not active'} ))
        
        elif path[-1] == 'samplePic':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            if postvars.has_key('imageWidth'):
                imageWidth = postvars['imageWidth'][0]
            else:
                imageWidth = self.server.imageWidthDefault
            if postvars.has_key('imageHeight'):
                imageHeight = postvars['imageHeight'][0]
            else:
                imageHeight = self.server.imageHeightDefault
            
            self.takePicture('' ,(imageWidth,imageHeight) ,videoDevice,fileName=self.server.sampleFileName)
        
        elif path[-1] == 'createMovie':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            projectName =  postvars['project'][0] 
            resolution = (postvars['imageWidth'][0] , postvars['imageHeight'][0])
            framesPerSecond =  postvars['fps'][0]
            outputFileName = self.createMovie(projectName, framesPerSecond, resolution)
            self.wfile.write( json.dumps({'movieFileName' :outputFileName} ))
                        
        elif path[-1] == 'start': 
            
            self.server.stopFile.removeFile()
                
            if postvars.has_key('project'):
                folder = self.getProjectFolder( postvars['project'][0] )
                if not os.path.lexists(folder):
                    os.mkdir(folder)

            #try:
            #	if not os.path.lexists(self.server.boxMediaFolder + folder):
            #		os.mkdir(self.server.boxMediaFolder + folder)
            #except:
            #	print('error creating box project folder')
            else:
                folder = self.server.mediaFolderDefault + '/'
            
            if postvars.has_key('imageWidth'):
                imageWidth = postvars['imageWidth'][0]
            else:
                imageWidth = self.server.imageWidthDefault
            
            if postvars.has_key('imageHeight'):
                imageHeight = postvars['imageHeight'][0]
            else:
                imageHeight = self.server.imageHeightDefault
                 
          
            if postvars.has_key('seconds') & postvars['seconds'][0].isdigit():
                thread.start_new_thread(self.activateCamera , (postvars['seconds'][0], videoDevice, folder, postvars['project'][0], (imageWidth, imageHeight) ) )
                cameraParam = {'seconds': postvars['seconds'][0],'device': videoDevice,'folder': folder}
                jsonResponse = json.dumps( {'status':'camera started','cameraParam': cameraParam} )
            else:
                cameraParam = {'seconds': postvars['seconds'][0],'device': videoDevice,'folder': folder}
                jsonResponse = json.dumps( {'status':'camera not started','cameraParam': cameraParam} )
                
            self.wfile.write(jsonResponse)        
            
 
        return
   
        
    def getProjectFolder(self, projectName):
        projectName = re.sub(' ', '-', projectName)
        return self.server.mediaFolderDefault + '/' + projectName + '/'
     
    def takePicture(self, directory , resolution, videoDevice, currtime=None, fileName=None):
        if currtime is None:
            currtime = str(time.strftime("%X"))
        if fileName is None:
            fileName = directory + currtime + ".jpeg"
        
        resolution = '%sx%s' % (resolution[0] , resolution[1])
        subprocess.call(["streamer", "-c", videoDevice, "-s", resolution, "-o", fileName,"-j","100"])
        self.server.lastPictureTime = currtime
        try:
        
            print(fileName)
            outputFile = self.server.sampleFileName
            shutil.copy (fileName, outputFile)
            #outputFile = self.server.boxMediaFolder + fileName
            #shutil.copy(fileName, outputFile)

        except:
            print('error copying %s to %s' % (fileName, outputFile) )

    
    def activateCamera(self, seconds, videoDevice, directory ='/tmp/',  project=None, resolution =('800','600'), fileName=None):
         
        self.server.lastActivationParams = {'seconds': seconds,'device': videoDevice,'folder': directory,'project':project, 'resolution': resolution}
        self.server.isActive = True
        self.takePicture(directory, resolution,videoDevice, fileName =directory + self.server.firstImageFileName)
        time.sleep(float(seconds))
        while not self.server.stopSignal:
            self.takePicture(directory, resolution,videoDevice, fileName =fileName)
            time.sleep(float(seconds))
            
        print('camera stopped')
        self.server.isActive = False
        self.server.stopSignal = False
    
    def createMovie(self, projectName, framesPerSecond, resolution):
        self.server.encodingInProgress = True
        folder = self.getProjectFolder( projectName )
        outputFileName = folder + self.server.outputFileName
        print("Creating movie: %s" % outputFileName)
        coderCommand = "mencoder mf://%s/*.jpeg -mf w=%s:h=%s:fps=%s:type=jpeg -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -of lavf -o %s" % (folder, resolution[0], resolution[1], framesPerSecond, outputFileName)
        proc = subprocess.Popen( coderCommand.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        Thread(target=self.stream_watcher, name='stdout-watcher', args=('STDOUT', proc.stdout)).start()
        Thread(target=self.stream_watcher, name='stderr-watcher', args=('STDERR', proc.stderr)).start()
        #(output, error) = proc.communicate()
        #print("Output:\n%s" % output)
        #print("Errors:\n%s" % error)
        proc.wait()
        print('done creating movie %s' % outputFileName)
        self.server.encodingInProgress = False
        return outputFileName
    
    
    def stream_watcher(self, identifier, stream):

        for line in stream:
            print(line)
            #print('%s:%s' %(identifier, line))
            #m_obj = re.search(r"(\d?%)", line)
            #m_obj2 = re.search(r"coder", line)
            #if m_obj is not None:
            #    print m_obj.group(1)
    
        if not stream.closed:
            stream.close()

    #def log_request(self, code=None, size=None):
    #    print('Request')

    #def log_message(self, format, *args):
    #    print('Message')


class MyHTTPServer(SocketServer.TCPServer):
    """this class is necessary to allow passing custom request handler into
       the RequestHandlerClass"""
    def __init__(self, server_address, RequestHandlerClass):
        self.sampleFileName = 'samplePic.jpeg'  
        self.imageWidthDefault = '800'
        self.imageHeightDefault = '600' 
        self.mediaFolderDefault = 'media'
        self.boxMediaFolder = '/media/box.com/'
        self.lastPictureTime = None
        self.lastActivationParams = {}
        self.isActive = False
        self.stopSignal = False
        self.encodingInProgress = False
        self.outputFileName = 'output.avi'
        self.firstImageFileName = 'firstImage.jpeg'

        self.WEBCAM = []

        if not os.path.lexists(self.mediaFolderDefault):
            os.mkdir(self.mediaFolderDefault)
        self.stopFile = BooleanFile('stop')
        self.stopFile.removeFile()
        self.activeFile = BooleanFile('active')
        self.activeFile.removeFile()
        self.sampleFile = BooleanFile(self.sampleFileName)
        self.sampleFile.removeFile()
        
        for videoDevice in glob.glob("/dev/video*"):
            self.WEBCAM.append( videoDevice )
                
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass) 
        #HTTPServer.__init__(self, server_address, RequestHandlerClass)   


def checkStreamerIsInstalled():
    if subprocess.call(["which", "streamer"] , stdout=subprocess.PIPE) is not 0:
        subprocess.call(["sudo", "apt-get", "install", "-y", "streamer"])
    if subprocess.call(["which", "mencoder"] , stdout=subprocess.PIPE) is not 0:
        subprocess.call(["sudo", "apt-get", "install", "-y", "mencoder"])


def getMyIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    my_ip =s.getsockname()[0] 
    s.close()
    return my_ip

if __name__ == "__main__":
    port = 8000
    try:
        url = "http://%s:%d" % (getMyIP(), port)
        print('Started http server. go to ' + url)
    except: 
        print('Some errro getting IP')

    try:
        checkStreamerIsInstalled()
        server = MyHTTPServer(('', port), MyHandler)
	#webbrowser.open(url,new='new')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()
        
