from flask import Flask, jsonify, request
import pandas as pd
import boto3
import tensorflow as tf
import pickle
import json

session = boto3.session.Session()
s3 = session.resource('s3')
my_bucket = s3.Bucket('protected-06062023')
my_bucket.download_file('HeartDisease.h5', 'HeartDisease.h5')
my_bucket.download_file('heart_model.sav', 'heart_model.sav')
my_bucket.download_file('ClassificationReport.json', 'ClassificationReport.json')

model = tf.keras.models.load_model('HeartDisease.h5')
# model = pickle.load(open('heart_model.sav', 'rb'))

app = Flask(__name__)

def addCommonHeaders(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route("/predict", methods=["GET"])
def predictApi():
    result = predict(request.args)
    response = jsonify(result)
    return addCommonHeaders(response)


def predict(args):
    columns = ["age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak","slope","ca","thal"]

    for item in columns:
        if item not in args.keys():
            return addCommonHeaders(
                    jsonify({
                        "status": "error",
                        "message": "Invalid input"
                    })
                )

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

    prediction = model.predict(test_df, verbose=0)
    result["prediction_actual"] = float(prediction[0][0])
    result["prediction_rounded"] = round(float(prediction[0][0]), 0)

    with open('ClassificationReport.json', 'r') as file:
        report = json.loads(file.read())
        result["accuracy"] = report["accuracy"]

    if "target" in args.keys():
        result["target"] = float(args["target"])
        result["match"] = (result["target"] == result["prediction_rounded"])
    
    return result

import pprint
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
