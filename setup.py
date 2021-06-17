import sys
import os
from remote_caller import SCGIRequest

def main(schedule=False):
	path = os.path.abspath(os.getcwd() )
	rtxmlrpc = SCGIRequest()

	try:

		if schedule:
			interval, amount = schedule
			rtxmlrpc.send("schedule2", ("", "low_diskspace", "0", f"{interval}", f"close_low_diskspace={amount}G") )

		rtxmlrpc.send("system.file.allocate.set", ("", "0") )
		rtxmlrpc.send("method.set_key", ("", "event.download.inserted_new", "checker", "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))") )

		try:
			rtxmlrpc.send("method.insert", ("", "dcheck", "simple", "d.stop=", f"execute.throw.bg=python3,{path}/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes=") )
		except:
			# Setup has ran before / Method already inserted
			print("Setup has already been ran")
			return

		rtxmlrpc.send("execute.throw.bg", ("", "python3", f"{path}/server.py") )
		print("Setup.py completed successfully")

	except Exception as e:
		print(f"Setup.py failed: {e}")

if __name__ == "__main__":

	if len(sys.argv) == 1:
		main()
	else:
		main( ( sys.argv[1], sys.argv[2]) )
