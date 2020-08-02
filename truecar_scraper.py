# truecar scraper
# Patrick Johnson 2020
from random import seed, random
import csv
import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
pages = 1
data_name = "test"


seed(1)

data = []
date = datetime.date(datetime.now())

for i in range(pages):
    time.sleep(2*random())  # try not to get banned here
    link = "https://www.truecar.com/used-cars-for-sale/listings/?page={}&sort[]=best_match".format(
        str(i+1))
    print(link)
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    cars = soup.find_all("div", {"data-qa": "Listings"})
    print("found " + str(len(cars)) + " cars")
    for car in cars:
        # get year, make, model, trim, price, mileage, owners, accidents, color, interior color, VIN, location
        row = {}

        # make and model are single element
        makeModel = car.find(
            "span", {"class": "vehicle-header-make-model"}).text.split(' ')
        make = makeModel[0]
        model = ''.join(makeModel[1:])
        year = car.find("span", {"class": "vehicle-card-year"}).text
        trim = car.find("div", {"data-test": "vehicleCardTrim"}).text
        price = car.find("h4", {"data-test": "vehicleCardPricingBlockPrice"})
        mileage = car.find("div", {"data-test": "vehicleMileage"}).text
        # some processing to do here
        condition = car.find("div", {"data-test": "vehicleCardCondition"}).text
        # some text processing to do here
        colorInfo = car.find("div", {"data-test": "vehicleCardColors"}).text
        exterior = colorInfo.split(', ')[0].split(' ')[0]
        interior = colorInfo.split(', ')[1].split(' ')[0]
        VIN = car.find("a", {"class": "vehicle-card"})["data-test-item"]
        location = car.find("div", {"data-test": "vehicleCardLocation"}).text

        # formatting, conversions, and exception handling
        row["make"] = make
        row["model"] = model
        row["year"] = year
        row["trim"] = trim
        row["VIN"] = VIN
        try:
            row["price"] = int(price.text[1:].replace(',', ''))
        except:
            row["price"] = ''

        row["mileage"] = int(mileage.split(' ')[0].replace(',', ''))
        try:
            accidents, owners, usage = condition.split(', ')
            accidents = accidents.split(' ')[0]
            if accidents == "No":
                accidents = 0
            else:
                accidents = int(accidents)
            owners = int(owners.split(' ')[0])
            usage = usage.split(' ')[0]
            row["accidents"] = accidents
            row["owners"] = owners
            row["usage"] = usage
        except:
            accidents, usage = condition.split(', ')
            accidents = accidents.split(' ')[0]
            if accidents == "No":
                accidents = 0
            else:
                accidents = int(accidents)
            row["accidents"] = accidents
            row["owners"] = 0
            row["usage"] = usage.split(' ')[0]

        row["location"] = location

        if row["price"] == '':
            pass
        else:
            data.append(row)
    print("\n page {} scraping finished".format(i+1))

# sort cars by VIN


def vin(data):
    return data["VIN"]


data.sort(key=vin)

# write data to csv file
with open('data/truecar/{}_truecar.csv'.format(date), 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

csvfile.close()


print("\n ** data extraction success!")
