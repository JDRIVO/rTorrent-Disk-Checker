import os
import sys

from remote_caller import SCGIRequest


def main(schedule=False):
	path = os.path.abspath(os.getcwd())
	rtxmlrpc = SCGIRequest()

	try:

		if schedule:
			interval, threshold = schedule
			rtxmlrpc.send(
				"schedule2",
				(
					"",
					"low_diskspace",
					"0",
					interval,
					"close_low_diskspace={}G".format(threshold),
				),
			)

		rtxmlrpc.send("system.file.allocate.set", ("", "0"))
		rtxmlrpc.send("execute.throw.bg", ("", "python3", path + "/server.py"))
		rtxmlrpc.send(
			"method.set_key",
			(
				"",
				"event.download.inserted_new",
				"checker",
				"branch=((and,((not,((d.is_meta)))),((d.state)))),((dcheck))",
			),
		)
		rtxmlrpc.send(
			"method.set_key",
			(
				"",
				"event.download.erased",
				"checker_erase",
				"execute.throw.bg=python3,{}/client.py,delete,$d.hash=,$d.name=,$d.directory=".format(path),
			),
		)

		try:
			rtxmlrpc.send(
				"method.insert",
				(
					"",
					"dcheck",
					"simple",
					"d.stop=",
					"execute.throw.bg=python3,{}/client.py,$d.name=,$d.hash=,$d.directory=,$d.size_bytes=".format(path),
				),
			)
		except Exception:
			# Setup has ran before / Method already inserted
			pass

		print("\nSetup.py completed successfully. Disk checker (server.py) is now running in the background.")

	except Exception as e:
		print("\nSetup.py failed:", e)


if __name__ == "__main__":

	if len(sys.argv) == 1:
		main()
	else:
		main((sys.argv[1], sys.argv[2]))
