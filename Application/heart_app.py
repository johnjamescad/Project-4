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

# Load files related to ML models.
my_bucket = s3.Bucket('protected-06062023')
my_bucket.download_file('HeartScaler.sav', 'work/HeartScaler.sav')
my_bucket.download_file('HeartDisease.h5', 'work/HeartDisease.h5')
my_bucket.download_file('heart_model.sav', 'work/heart_model.sav')
my_bucket.download_file('ClassificationReport.json', 'work/ClassificationReport.json')

# Load app config.
my_bucket_public = s3.Bucket('public-12062023')
my_bucket_public.download_file('app_config.json', 'work/app_config.json')

# Find the public DNS name of the EC2 instance.
ec2 = session.resource('ec2', region_name='us-east-1')
vpc = ec2.Vpc("vpc-0fd39bdd1e131dcf1")

with open("work/app_config.json", "r") as file:
    app_config = json.loads(file.read())

app_config["serviceUrl"] = ""
for i in vpc.instances.all():
    app_config["serviceUrl"] = "http://" + i.public_dns_name + ":5000"
    break

if app_config["model"] is None or len(str(app_config["model"]).strip()) == 0:
    app_config["model"] = "neural"
    app_config["modelDescription"] = "Neural Network"

with open("work/app_config.json", "w") as file:
    file.write(json.dumps(app_config))

with open('work/app_config.json', 'rb') as file:
    my_bucket_public.Object('app_config.json').put(Body=file, ContentType='application/json')
with open('heart_app.html', 'rb') as file:
    my_bucket_public.Object('index.html').put(Body=file, ContentType='text/html')

with open('heart_app.html', 'r') as file:
    indexPageHtml = file.read()

columns = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal","target"]
target_columns = ["target"]
feature_columns = [x for x in columns if x not in target_columns]
categorical_columns = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
numerical_columns = [x for x in feature_columns if x not in categorical_columns]

scaler = joblib.load("work/HeartScaler.sav") 

if app_config["model"] == "neural":
    model = tf.keras.models.load_model('work/HeartDisease.h5')
else:
    model = pickle.load(open('work/heart_model.sav', 'rb'))

with open('work/ClassificationReport.json', 'r') as file:
    report = json.loads(file.read())

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

app = Flask(__name__)
cors = CORS(app)

@app.route("/", methods=["GET"])
def indexPage():
    return indexPageHtml

@app.route("/predict", methods=["GET"])
def predictApi():
    result = predict(request.args)
    response = jsonify(result)
    return response

def predict(args):
    columns = ["age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak","slope","ca","thal"]

    for item in args.keys():
        if item not in columns or not is_float(args[item]):
            return {
                "status": "error",
                "message": "Invalid input"
            }

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
    data_scaled_df = pd.DataFrame(scaler.transform(test_df[feature_columns]), columns=feature_columns)

    if app_config["model"] == "neural":
        prediction = model.predict(data_scaled_df, verbose=0)
        result["prediction_actual"] = float(prediction[0][0])
        result["prediction_rounded"] = round(float(prediction[0][0]), 0)
    else:
        prediction = model.predict(data_scaled_df)
        result["prediction_actual"] = float(prediction[0])
        result["prediction_rounded"] = round(float(prediction[0]), 0)
    result["accuracy"] = report["accuracy"]

    if "target" in args.keys():
        result["target"] = float(args["target"])
        result["match"] = (result["target"] == result["prediction_rounded"])
    
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
