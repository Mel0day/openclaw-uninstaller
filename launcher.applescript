on run
	set res to POSIX path of ((path to me as text) & "Contents:Resources:")
	set logFile to "/tmp/openclaw-ui.log"
	do shell script "python3 " & quoted form of (res & "server.py") & " > " & quoted form of logFile & " 2>&1 &"
end run
