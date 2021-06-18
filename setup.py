import sys
import os
from subprocess import Popen
from remote_caller import SCGIRequest

def main(schedule=False):
	path = os.path.abspath(os.getcwd() )
	Popen([sys.executable, "{}/server.py".format(path)])
	rtxmlrpc = SCGIRequest()

	try:

		if schedule:
			interval, amount = schedule
			rtxmlrpc.send("schedule2", ('', "low_diskspace", "0", interval, "close_low_diskspace={}G".format(amount) ) )

		rtxmlrpc.send("system.file.allocate.set", ('', "0") )
		rtxmlrpc.send("method.set_key", ('', "event.download.inserted_new", "checker", "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))") )

		try:
			rtxmlrpc.send("method.insert", ('', "dcheck", "simple", "d.stop=", "execute.throw.bg=python3,{}/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes=".format(path) ) )
		except:
			# Setup has ran before / Method already inserted
			print("Setup has already been run")
			return

		print("Setup.py completed successfully")

	except Exception as e:
		print("Setup.py failed: " + str(e) )

if __name__ == "__main__":

	if len(sys.argv) == 1:
		main()
	else:
		main( ( sys.argv[1], sys.argv[2]) )