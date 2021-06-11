import os
from remote_caller import SCGIRequest

path = os.path.abspath(os.getcwd() )
rtxmlrpc = SCGIRequest()
rtxmlrpc.send("method.set_key", ("", "event.download.inserted_new", "checker", "branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))") )
rtxmlrpc.send("method.insert", ("", "dcheck", "simple", "d.stop=", f"execute.throw.bg=python3,{path}/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes=") )
rtxmlrpc.send("execute.throw.bg", ("", "python3", f"{path}/server.py") )
