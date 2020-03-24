from flask import (
  Flask,
  jsonify,
  request,
  abort
)
from gevent.pywsgi import WSGIServer
from multipledispatch import dispatch
from collections import namedtuple
from flask_restplus import Api, Resource, fields, reqparse
import json
import threading
import logging
from logging.handlers import RotatingFileHandler
import traceback
from time import strftime
app = Flask(__name__)
api = Api(app, version='1.0',title='코로나 바이러스 정보 제공 API',description='코로나 바이러스 정보 제공 API 입니다. \n본 서비스는 위키백과와 질병관리본부 사이트의 데이터를 활용합니다.\n Made By happycastle\n 오류나 문의사항은 이메일이나 페이스북으로 연락주세요', contact_email='soungmin114@gmail.com', 
default='APIs', default_label='정보 제공 API 입니다', contact_url='https://web.facebook.com/profile.php?id=100013984185945', contact='Son Soungmin')
location_data = []
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'
corona_data = []

def updateData(second = 360):
  global corona_data
  global location_data
  print('updating Data...')
  with open('data.json','r',encoding='utf-8') as f:
    corona_data = json.load(f)
    f.close()
  with open('data_location.json','r',encoding='utf-8') as f:
    location_data = json.load(f)
  print('successful Update')
  threading.Timer(second, updateData, [second]).start()

def searchCountry(country):
  for row in corona_data:
    if row['country'] == country:
      return row
  return []

def searchHospital(city, gu=None):
  result = []
  for row in location_data:
    if row['city'] in city:
      if gu == None:
        result.append(row)
      else:
        if row['gu'] in gu:
          result.append(row)
  return result

@api.route('/status')
@api.response(200, 'Found Data')
@api.response(404, 'Not Found')
@api.response(500, 'Internal Error')
@api.doc(params={'country':'국가 이름, 없을 시 모든 국가를 가져옵니다.'})
class Status(Resource):
  @api.doc('get')
  def get(self):
    ''' 값을 가지고 온다 '''
    parser = reqparse.RequestParser()
    parser.add_argument('country',type=str,help='국가 이름을 적어주세요')
    args = parser.parse_args()
    if not args['country'] == None:
      country = searchCountry(args['country'])
      if country == []:
        abort(404, 'Data Not Found')
      else:
        return jsonify(country)
    else:
      return jsonify(corona_data)

@api.route('/hospital')
@api.response(200, 'Found Data')
@api.response(404, 'Not Found')
@api.response(500, 'Internal Error')
@api.doc(params={'city': '광역시 또는 도 이름입니다. 없을 시 모든 데이터를 가지고 옵니다', 
'gu': '구 또는 시 이름 입니다. 없을 시 시 로만 검색합니다'})
class Hospital(Resource):
  @api.doc('get')
  def get(self):
    ''' 병원 정보를 가지고 오는 API 입니다.'''
    parser = reqparse.RequestParser()
    parser.add_argument('city', type=str, required=False)
    parser.add_argument('gu', type=str)
    args = parser.parse_args()

    if args['city'] == None:
      return jsonify(location_data)
    else:
      result = searchHospital(args['city'], args['gu'])
      if result == []:
        abort(404, 'Hospital Not Found')
      else:
        return jsonify(result)
    
@app.after_request
def after_request(response):
  timestamp = strftime('[%Y-%b-%d %H:%M]')
  logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
  return response

@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
    return e.status_code

if __name__ == "__main__":
  updateData()
  handler = RotatingFileHandler('app.log', maxBytes=100000)
  http_server = WSGIServer(('0.0.0.0',80), app)
  logger = logging.getLogger('tdm')
  logger.setLevel(logging.ERROR)
  logger.addHandler(handler)
  http_server.serve_forever()
    
