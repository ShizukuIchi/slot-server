from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
import os
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import pandas as pd
import numpy as np
import shutil
import xlrd
from random import shuffle

res_file = pd.ExcelFile("./output.xlsx")
df = res_file.parse("Sheet1")

def FilterContent(MRTstation, AverageCost, CostOption1, CostOption2, Rating, RatingOption1, Category):
  #Filter MRTstation
  if MRTstation == '都可以':
    dM = df
  elif MRTstation == '台北 101世貿站':
    dM = df[(df['鄰近捷運站'] == '台北101世貿站')]
  else:
    dM = df[(df['鄰近捷運站'] == MRTstation)]
  
  #Filter AverageCost, CostOption1 and CostOption2
  if CostOption2 == '是':
    if CostOption1 == "以上":
      dC = dM[(dM['平均消費金額'] >= AverageCost) | (dM['平均消費金額'] == 0)]
    elif CostOption1 == "以下":
      dC = dM[(dM['平均消費金額'] <= AverageCost)]
  elif CostOption2 == '否':
    if CostOption1 == "以上":
      dC = dM[(dM['平均消費金額'] >= AverageCost)]
    elif CostOption1 == "以下":
      dC = dM[(dM['平均消費金額'] <= AverageCost) & (dM['平均消費金額'] != 0)]

  #Filter Rating and RatingOption1
  if RatingOption1 == '是':
    dR = dC[(dC['餐廳評分分數'] >= Rating*10) | (dC['餐廳評分分數'] == 0)]
  elif RatingOption1 == '否':
    dR = dC[(dC['餐廳評分分數'] >= Rating*10)]

  #Filter Category
  if Category == '都可以':
    dCA = dR
  elif Category[0:2] == 'bu':
    dCA = dR[(dR['餐廳類型粗分'] == 'buffet自助餐')]
  elif Category[0:2] == '冰品':
    dCA = dR[(dR['餐廳類型粗分'] == '冰品、飲料、甜湯')]
  elif Category[0:2] == '烘焙':
    dCA = dR[(dR['餐廳類型粗分'] == '烘焙、甜點、零食')]
  elif Category[0:2] == '咖啡':
    dCA = dR[(dR['餐廳類型粗分'] == '咖啡、簡餐、茶')]
  else:
    dCA = dR[(dR['餐廳類型粗分'] == Category)]
  
  return dCA


def RestaurantFilter(MRTstation, AverageCost, CostOption1, CostOption2, Rating, RatingOption1, Category):
  #Filter data
  filterdata = FilterContent(MRTstation, AverageCost, CostOption1, CostOption2, Rating, RatingOption1, Category)
  #Transfer dataframe to list
  df_train = np.array(filterdata)
  df_list = df_train.tolist()
  #If length of data above 100, get only the first 100 data
  if len(df_list) > 100:
    df_list = df_list[1:100]
  #Shuffle list
  shuffle(df_list)
  #Transfer list of data to Dictionary type
  AllResInfo_dict = []
  for i in df_list:
    d = {}
    d["id"] = i[0]
    d["name"] = i[1]
    d["tel"] = i[2]
    d["nearMRT"] = i[4]
    d["BigCategory"] = i[5]
    d["SmallCategory"] = i[6]
    d["Rating"] = i[7]
    d["Adress"] = i[9]
    d["Cost"] = i[10]
    if i[12] == '無周一營業時間資料':
      d["bsMo"] = ''
    else:
      d["bsMo"] = i[12]
    if i[13] == '無周二營業時間資料':
      d["bsTu"] = ''
    else:
      d["bsTu"] = i[13]
    if i[14] == '無周三營業時間資料':
      d["bsWe"] = ''
    else:
      d["bsWe"] = i[14]
    if i[15] == '無周四營業時間資料':
      d["bsTh"] = ''
    else:
      d["bsTh"] = i[15]
    if i[16] == '無周五營業時間資料':
      d["bsFr"] = ''
    else:
      d["bsFr"] = i[16]
    if i[17] == '無周六營業時間資料':
      d["bsSa"] = ''
    else:
      d["bsSa"] = i[17]
    if i[18] == '無周日營業時間資料':
      d["bsSu"] = ''
    else:
      d["bsSu"] = i[18]
    d["OpenTime"] = i[19]
    d["Recommend"] = i[20]
    d["Quote"] = i[21]
    d["images"] = i[27].split(',')
    AllResInfo_dict.append(d)
  return AllResInfo_dict
@app.route('/')
def index():
  return "Welcome to slot server!"

@app.route('/getRestaurants')
@cross_origin()
def getRestaurants():

  MRTstation = request.args.get('region')
  AverageCost = int(request.args.get('price'))
  CostOption1 = request.args.get('costoption1')
  CostOption2 = request.args.get('costoption2')
  Rating = float(request.args.get('rating'))

  RatingOption1 = request.args.get('ratingoption1')
  Category = request.args.get('category')

  response = RestaurantFilter(MRTstation, AverageCost, CostOption1, CostOption2, Rating, RatingOption1, Category)

  return jsonify(response)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(debug=True, use_reloader=True, host="0.0.0.0", port=port)