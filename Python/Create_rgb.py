# Create the rgb.txt file for the wepod data for orbslam
import sys, os

# open the textfile
print "Opening textfile"
rgbtxtname = "rgb.txt"
textfile = open(rgbtxtname,'w')

print "reading arguments"
# get the imagefolder
imagefolder = sys.argv[1]

# get the fps
fps = float(sys.argv[2])

print "looping over files"
# loop over all the files in the imagefolder
i=0
for root, dirs, files in os.walk(imagefolder):
    files = sorted(files)
    for names in files:
        timestamp = i*1/fps
        newline = str(timestamp) + " " + imagefolder + "/" + names + "\n"
        textfile.write(newline)
        i=i+1

textfile.close
print "done"
