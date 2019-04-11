import sys, os, time

time.sleep(0.5)
directory = os.path.dirname(sys.argv[0])
files = os.listdir(directory)
[os.remove(file) for file in files if file.endswith('.txt')]
