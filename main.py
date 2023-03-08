from flask import Flask, jsonify, request
import csv
from datetime import datetime
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

app = Flask(__name__)


@app.route("/predict_for_date")
def get_gas_prediction():
    if request.args['date']:
        try: 
            df_price = get_gas_price_for_date(request.args['date'])
            return convert_df_to_resp(df_price)
        except:
            return "Error"
    else: 
        return "Invalid date"

@app.route("/predict_for_dates")
def get_gas_prediction():
    if request.args['start'] and request.args['end']:
        try: 
            df_price = get_gas_price_for_date(request.args['date'])
            return convert_df_to_resp(df_price)
        except:
            return "Error"
    else: 
        return "Invalid date"


@app.route('/')
def home():
    return jsonify("home")


def get_gas_for_dates(start,end):
    ''' get the average, high, low, and buy date for a start and end date'''
    start_date = datetime.strptime(start,"%m/%d/%Y")
    end_date = datetime.strptime(end,"%m/%d/%Y")
    
def get_gas_price_for_date(dte):
    ''' given a UTC date return the predicted gas price for that date'''
    gwei = pd.read_csv("AvgGasPrice.csv")
    gwei = gwei.rename(columns={'Date(UTC)': 'date', 'UnixTimeStamp': 'timestamp','Value (Wei)':'price'})
    
    gwei.price = gwei.price/1000000000 #convert wei to gwei

    pred_date = datetime.strptime(dte,"%m/%d/%Y")
    end_of_data = datetime.strptime(gwei.tail(1).date.iloc[0],"%m/%d/%Y")
    
    delta = (pred_date - end_of_data).days

    ARMAmodel = SARIMAX(gwei.price.astype(int), order = (1, 0, 1))
    ARMAmodel = ARMAmodel.fit()


    y_pred_df = ARMAmodel.get_forecast(delta).conf_int(alpha = 0.5) 
    y_pred_df["Prediction"] = ARMAmodel.predict(start = y_pred_df.index[0], end = y_pred_df.index[-1])

    return  y_pred_df.tail(1)

def convert_df_to_resp(df):
    ''' helper function to convert a single line dataframe to an acceptable json response'''
    j = df.to_dict('dict')
    key = list(j['lower price'].keys())[0]

    return {
        "upper price":j['upper price'][key],
        "lower price":j['lower price'][key],
        "Expected Value":j['Prediction'][key]
    }

# example: print the dataframe predicting the gas price for 3/10/2023
gas_price = get_gas_price_for_date('3/10/2023')
print(gas_price)

#example: get the JSON formatted gas prediction for 3/10/2023
formatted_gas_price = convert_df_to_resp(gas_price)
print(formatted_gas_price)
