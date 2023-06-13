#! /bin/bash
while read -r pid; do
  echo "Killing process: $pid"
  kill "$pid"
done < <(lsof -t -i :5000)
