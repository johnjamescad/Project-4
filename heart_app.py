from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
import boto3
import tensorflow as tf
import pickle
import json

session = boto3.session.Session()
s3 = session.resource('s3')
my_bucket = s3.Bucket('protected-06062023')
my_bucket.download_file('HeartDisease.h5', 'work/HeartDisease.h5')
my_bucket.download_file('HeartScaler.sav', 'work/HeartScaler.sav')
my_bucket.download_file('heart_model.sav', 'work/heart_model.sav')
my_bucket.download_file('ClassificationReport.json', 'work/ClassificationReport.json')

ec2 = session.resource('ec2', region_name='us-east-1')
vpc = ec2.Vpc("vpc-0fd39bdd1e131dcf1")

service_host = {
    "hostname": ""
}

for i in vpc.instances.all():
    service_host["hostname"] = "http://" + i.public_dns_name + ":5000/"
    break

with open("work/service_host.json", "w") as file:
    file.write(json.dumps(service_host))

my_bucket_public = s3.Bucket('public-06062023')
my_bucket_public.upload_file('work/service_host.json', 'service_host.json')

my_bucket_public = s3.Bucket('public-12062023')
with open('heart_app.html', 'rb') as file:
    my_bucket_public.Object('index.html').put(Body=file, ContentType='text/html')

columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal","target"]
target_columns = ["target"]
feature_columns = [x for x in columns if x not in target_columns]
categorical_columns = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
numerical_columns = [x for x in feature_columns if x not in categorical_columns]

scaler = joblib.load("work/HeartScaler.sav") 

model = tf.keras.models.load_model('work/HeartDisease.h5')
# model = pickle.load(open('work/heart_model.sav', 'rb'))

app = Flask(__name__)
cors = CORS(app)

@app.route("/", methods=["GET"])
def indexPage():
    response = ""
    with open('heart_app.html', 'r') as file:
        response = file.read()
    return response

@app.route("/predict", methods=["GET"])
def predictApi():
    result = predict(request.args)
    response = jsonify(result)
    return response


def predict(args):
    columns = ["age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak","slope","ca","thal"]

    for item in args.keys():
        if item not in columns:
            return jsonify({
                "status": "error",
                "message": "Invalid input"
            })

    age = float(args["age"])
    sex = float(args["sex"])
    cp = float(args["cp"])
    trestbps = float(args["trestbps"])
    chol = float(args["chol"])
    fbs = float(args["fbs"])
    restecg = float(args["restecg"])
    thalach = float(args["thalach"])
    exang = float(args["exang"])
    oldpeak =  float(args["oldpeak"])
    slope = float(args["slope"])
    ca = float(args["ca"])
    thal = float(args["thal"]) 

    result = {
        "age": age,
        "sex": sex,
        "cp": cp,
        "trestbps": trestbps,
        "chol": chol,
        "fbs": fbs,
        "restecg": restecg,
        "thalach": thalach,
        "exang": exang,
        "oldpeak": oldpeak,
        "slope": slope,
        "ca": ca,
        "thal": thal
    }

    test_df = pd.DataFrame(
        [[age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal]],
        columns=columns
    )
    data_scaled_df = scaler.transform(test_df[feature_columns])

    prediction = model.predict(data_scaled_df, verbose=0)
    result["prediction_actual"] = float(prediction[0][0])
    result["prediction_rounded"] = round(float(prediction[0][0]), 0)

    with open('work/ClassificationReport.json', 'r') as file:
        report = json.loads(file.read())
        result["accuracy"] = report["accuracy"]

    if "target" in args.keys():
        result["target"] = float(args["target"])
        result["match"] = (result["target"] == result["prediction_rounded"])
    
    return result

import requests
from io import StringIO

def transformTarget(df):
    if df > 0: 
        return 1
    return 0

def simulate():
    response = requests.get("https://public-06062023.s3.amazonaws.com/heart.txt")
    csvData = ""
    if response.status_code == 200:
        csvData = response.text
    data = pd.read_csv(StringIO(csvData))
    data["target"] = data["target"].apply(transformTarget)

    count = 0
    count_present = 0
    count_present_success = 0
    count_absent = 0
    count_absent_success = 0
    for row in data.iterrows():
        count = count + 1

        age=row[1][0]
        sex=row[1][1]
        cp=row[1][2]
        trestbps=row[1][3]
        chol=row[1][4]
        fbs=row[1][5]
        restecg=row[1][6]
        thalach=row[1][7]
        exang=row[1][8]
        oldpeak=row[1][9]
        slope=row[1][10]
        ca=row[1][11]
        thal=row[1][12]
        target=row[1][13]

        myRequest = {
            "age": age,
            "sex": sex,
            "cp": cp,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": restecg,
            "thalach": thalach,
            "exang": exang,
            "oldpeak": oldpeak,
            "slope": slope,
            "ca": ca,
            "thal": thal,
            "target": target
        }

        myResponse = predict(myRequest)

        if myResponse["target"] == 1:
            count_present = count_present + 1
            if myResponse["match"]:
                count_present_success = count_present_success + 1
        else:
            count_absent = count_absent + 1
            if myResponse["match"]:
                count_absent_success = count_absent_success + 1

    print(count)
    print(count_present)
    print(count_present_success)
    print(count_absent)
    print(count_absent_success)

    # End of method simulate()

# simulate()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
