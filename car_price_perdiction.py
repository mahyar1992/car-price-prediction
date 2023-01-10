import requests
import re
import mysql.connector
from bs4 import BeautifulSoup
from sklearn import tree
from sklearn import preprocessing

res = requests.get('https://www.truecar.com/used-cars-for-sale/listings/ford/f-150/location-schenectady-ny/?searchRadius=5000&sort[]=price_asc')
car_name = 'Ford F-150'
soup = BeautifulSoup(res.text, 'html.parser')
pagination = soup.find_all('nav')
for i in pagination:    
    page = re.search(r'\d*.*of (\d*)', i.text)
    end_page = page.group(1)
cnx = mysql.connector.connect(user='root', password='***', #local DB password
                              host='127.0.0.1',
                              database='***') #local DB name
for i in range (1, int(end_page)+1):
    resp = requests.get('https://www.truecar.com/used-cars-for-sale/listings/ford/f-150/location-schenectady-ny/?page=%i&searchRadius=5000&sort[]=price_asc' %i)
    soup_2 = BeautifulSoup(resp.text, 'html.parser')
    all_ads = soup_2.find_all('li')
    for ads in all_ads:
        if re.search(r'(\d+).*\$(\d*,\d{3})(\d*,\d*)[a-zA-Z0-9, :\n-]{1,}.* Transmission: (\w+)', ads.text) != None:
            new_ads_values = re.search(r'(\d+).*\$(\d*,\d{3})(\d*,\d*)[a-zA-Z0-9, :\n-]{1,}.* Transmission: (\w+)', ads.text)
            year = new_ads_values.group(1)
            ads_price = new_ads_values.group(2)
            ads_usage = new_ads_values.group(3)
            transmission = new_ads_values.group(4)
            year_int = year.split()
            year_int = int(year_int[0])
            ads_price_float = ads_price.split(',')
            ads_price_float = int(ads_price_float[0])+(int(ads_price_float[1]))/(1000)
            ads_usage_float = ads_usage.split(',')
            ads_usage_float = int(ads_usage_float[0])+(int(ads_usage_float[1]))/(1000)
            cursor = cnx.cursor()
            query = 'INSERT INTO car_db VALUES(\'%s\',\'%i\', \'%f\', \'%f\', \'%s\')' %(car_name, year_int, ads_usage_float, ads_price_float, transmission) # I collected the transmission but more than 97% type was Automatic, so I ignored this parameter to ML model prediction
            cursor.execute(query)
            cnx.commit()
cursor = cnx.cursor()
query = "SELECT * FROM car_db"
cursor.execute(query)
car_list = list (cursor)
x=[]
y=[]
for i in car_list:
    i = list(i)
    x.append(i[1:3])
    y.append(i[3])
cnx.commit()
lab = preprocessing.LabelEncoder() #labeling data
y_transformed = lab.fit_transform(y)
clf = tree.DecisionTreeClassifier()
clf = clf.fit(x, y_transformed)
answer = clf.predict([[2008, 130]])# year = 2008 Kilometer = 130,000
answer_transformed = lab.inverse_transform(answer)
for i in answer_transformed:
    print('The predicted price for your inquery is %s $' % i)
cnx.close()