import os
from remote_caller import SCGIRequest

path = os.path.abspath(os.getcwd() )
rtxmlrpc = SCGIRequest()

try:
	rtxmlrpc.send("system.file.allocate.set", ("", "0") )
	rtxmlrpc.send("method.set_key", ("", "event.download.inserted_new", "checker", "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))") )
	rtxmlrpc.send("method.insert", ("", "dcheck", "simple", "d.stop=", f"execute.throw.bg=python3,{path}/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes=") )
	rtxmlrpc.send("execute.throw.bg", ("", "python3", f"{path}/server.py") )
	print("Setup.py completed successfully")
except Exception as e:
	print(f"Setup.py failed: {e}")