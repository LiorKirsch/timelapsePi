TimelapsePi
=================
Makes your Pi a timelapse server and control it with the browser.

First make sure you installed 'streamer' and 'mencoder'.
>sudo apt-get install -y streamer mencoder

To run type:
>python2.7 timeLapseServer.py

To run it at startup please create a file called /etc/init.d/timeLapse
The content of the file should be:
> cd the_folder_contating_the_python_script
> sudo -u pi python timeLapseServer.py > ./time.log &

Then go to the browser to control it.
> http://your_address:8000/



