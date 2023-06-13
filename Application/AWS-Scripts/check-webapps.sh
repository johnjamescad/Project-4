#! /bin/bash
#
# Find process ID(s) associated with port 5000
pids=$(lsof -t -i :5000)
#
# Check if process ID list is empty
if [ -z "$pids" ]; then
	echo "No running process found for Webapps."
else
	echo "Webapps running."
	while read -r pid; do
		echo "Process: $pid"
	done <<< "$pids"
fi
