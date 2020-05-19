import pandas as pd
import matplotlib.pyplot as plt
import requests
import csv
import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error
#import seaborn as sns

SOURCE_COVID_19 = " https://pomber.github.io/covid19/timeseries.json"

def get_data_json(source):
    return requests.get(source).json()


data = requests.get(SOURCE_COVID_19).json()
df = pd.DataFrame.from_dict(data)

def get_average_speed_of_propagation_sorted_list(data,status ='confirmed', days = len(data[list(data.keys())[0]]), reverse = False):
    min_days = days
    speed = {}
    for key in data:
        if(len(data[key]) < min_days):
            min_days = len(data[key])
    for key in data:
        speed[key] = round(data[key][min_days - 1][status] / min_days,3)
    speed = {key:value for key, value in sorted(speed.items(), key = lambda item:item[1], reverse = reverse)}
    return speed

def print_speed_stats(data,days = len(data[list(data.keys())[0]]), reverse = False):
    print(f"Stats for {days} days:")
    statuses = ['confirmed' , 'deaths' , 'recovered']
    for i in range(len(statuses)):
        fig , ax = plt.subplots()
        fig =plt.figure(figsize=(50,40))
        speed = get_average_speed_of_propagation_list(data,status = statuses[i],days = days,reverse = reverse)
        print(f"Average speed for {statuses[i]} by day {days} (men per day):")
        for key in speed:
            print(f"{key}:{speed[key]}")

def draw_average_speed_of_propagation_sorted_list(data,days = len(data[list(data.keys())[0]]), reverse = False):   
    statuses = ['confirmed' , 'deaths' , 'recovered']
    colors = ['yellow' , 'red' ,'green']
    for i in range(3):
        fig , ax = plt.subplots()
        fig =plt.figure(figsize=(50,40))
        speed = get_average_speed_of_propagation_list(data,status = statuses[i],days = days,reverse = reverse)
        countries = list(speed.keys())
        values = list(speed.values())
        ax.bar(countries,values, color=colors[i])
        ax.set_title(f"{statuses[i]} for {days} days") 
        plt.show()

def draw_countries_covid_stats(df, count = len(df.columns)):
    for country_name in df.columns[:count]:
        country = df[country_name]
        x = [index for index in country.index]
        y = [obj['confirmed'] for obj in country]
        y1 = [obj['deaths'] for obj in country] 
        y2 = [obj['recovered'] for obj in country] 
        fig, ax = plt.subplots()
        ax.plot(x,y,label="confirmed")
        ax.plot(x,y1,label="deaths")
        ax.plot(x,y2,label="recovered")
        ax.set_title(country_name)  # Add a title to the axes.
        ax.set_xlabel("days")
        ax.set_ylabel("amount")
        ax.legend()

def create_country_stats_excel_file(df):
    writer = pd.ExcelWriter('covid-19.xlsx', engine='xlsxwriter')
    for country_name in df.columns:
        country = pd.DataFrame.from_dict(data[country_name])
        country_name = "".join([c for c in country_name if c.isalpha()])
        country.to_excel(writer ,sheet_name=country_name, index_label="day")
        #country.to_csv(f"{country_name}.csv" , index_label = "day")

def create_country_stats_excel_file_without_zeroes(df, by='confirmed'):
    writer = pd.ExcelWriter(f"covid-19_{by}.xlsx", engine='xlsxwriter')
    for country_name in df.columns:
        country = pd.DataFrame.from_dict(data[country_name])
        country = country.loc[country[by] > 0 , [by,'date']].reset_index(drop = True)
        country.index = country.index + 1 # если что, убрать
        #print(country)
        country_name = "".join([c for c in country_name if c.isalpha()])
        country.to_excel(writer ,sheet_name=country_name, index_label="day")
        #country.to_csv(f"{country_name}.csv" , index_label = "day")

def linear(x,a,b):
    return a*x + b

def exp(x,a,b,c):
    return a*np.exp(b*x)+c

def polynomial_2(x,a,b,c):
    return a*np.square(x) + b*x + c

def polynomial_3(x,a,b,c,d):
    return a*np.power(x,3) + b*np.square(x) + c*x + d

def log(x,a,b,c):
    return a*np.log(b*x) + c

def get_curve_fit_with_params(x,y,mse = False, mse_threshold = 100):
    functions = {"linear":linear , "exp":exp , "pol_2":polynomial_2 , "pol_3":polynomial_3, "log":log}
    function ="linear"
    params = ()
    r_square = 0
    for key in functions:
        if key =="exp":
            opt_params , pcov = curve_fit(functions[key],x,y , p0 = (-1, 0.01, 1))
        else:
            opt_params , pcov = curve_fit(functions[key],x,y)
        if mse:     
            mse_cur = mean_squared_error(y, function[key](*opt_params))
        else:
        # вычисляем r_square_cur или mse
            r_square_cur = r2_score(y, function[key](*opt_params))
            if r_square_cur > r_square:
                r_square = r_square_cur
                function = function[key]
                params = opt_params
    return (key, function , params, r_square)
        
def get_countries_by_status(df , status='confirmed' , count = len(df.columns) ):
    countries =[]
    for country_name in df.columns[:count]:
        country = pd.DataFrame.from_dict(data[country_name])
        country = country.loc[country[status] > 0 , ['date',status]].reset_index(drop = True)
        countries.append({"name":country_name  ,"data":country})
    return countries

countries = get_countries_by_status(df,'recovered' , count = 1)

def get_country_dependency(country, status):
    country_name = country['name']
    data = country['data']
    x = np.array(list(data.index))
    y = np.array(list(data[status]))
    

def get_dependencies(df , status='confirmed'):
    dependecies = []
    # {country:"Afghanistan", status:"confirmed", dependency:'exp' , function:"1,2*exp(2*x) + 4"}
