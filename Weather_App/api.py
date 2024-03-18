import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
from collections import defaultdict







load_dotenv()
apikey = os.getenv('API_KEY')
city = 'Kelowna'
url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'.format(city, apikey)
    #city = current_user.city
req = requests.get(url).json()
data = req['coord']
lon,lat = req['coord'].get('lon'), req['coord'].get('lat')

url2 = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}&units=metric'.format(lat,lon,apikey)

req2 = requests.get(url2).json()
listof = []
ha = -1
for i in req2['list']:
    if ha == -1:
        listof.append([int(i.get('main').get('temp_max')),int(i.get('main').get('temp_min')) , i.get('weather')[0].get('description'),i.get('dt_txt').split()[0], i.get('weather')[0].get('icon')])
        ha = ha+1
    else:
        if i.get('dt_txt').split()[0] == listof[ha][3]:
            listof[ha][0] = max(int(i.get('main').get('temp_max')),listof[ha][0])
            listof[ha][1] = min(int(i.get('main').get('temp_min')),listof[ha][1])
        else:
            ha = ha +1
            listof.append([int(i.get('main').get('temp_max')),int(i.get('main').get('temp_min')) , i.get('weather')[0].get('description'),i.get('dt_txt').split()[0], i.get('weather')[0].get('icon')])



print(listof)
        



#data2 = req2['list']
#hunger = 0
#max_temp = round(data2[0].get('main').get('temp_max'))
#print(data2)




#print(max_temp)
#for dat in data2: 
    #print(dat.get('dt_txt'))
    #if max_temp < round(dat.get('main').get('temp_max')):
    #    max_temp = round(dat.get('main').get('temp_max'))
#grouped_data = defaultdict(list)
#for item in data2:
#    date = item.get('dt_txt')
#    grouped_data[date].append(item)
#for date, data_list in grouped_data.items():
    #print(f"Date: {date}")
#for x in grouped_data:
#    print(x)

#print(max_temp)

    #data3 = dat.get('main')
    #data4 = round(data3.get('temp'))
    #print(data4)

#print(round(6.2))
#data3 = data2[1]
#data4 = data3.get('main')

#print(data3)
#print(data4)






