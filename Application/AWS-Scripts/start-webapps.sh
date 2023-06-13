#! /bin/bash
./stop-webapps.sh
cd /home/ec2-user/webapps
source /opt/conda/etc/profile.d/conda.sh
conda activate MyML

# Start the Python application in the background
nohup python3 heart_app.py > output/output.log 2> output/error.log &
echo "Started application..."
