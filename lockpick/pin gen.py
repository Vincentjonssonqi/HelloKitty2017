import csv
pins = []
pins.append("1234")
pins.append("4321")
pins.append("2580")
pins.append("0007")
pins.append("0070")
for i in range(10):
    for j in range(10):
        couplet = (str(i) + str(j))*2
        pins.append(couplet)
for day in range(1,32):
    for month in range(1, 13):
        date = str(day).zfill(2)+str(month).zfill(2)
        american_date = str(month).zfill(2)+str(day).zfill(2)
        for i in [date, american_date]:
            if i not in pins:
                pins.append(i)
for year in range(1900, 2018):
    if str(year) not in pins:
        pins.append(str(year))
for i in range(12):
    for j in range(12):
        for k in range(12):
            for l in range(12):
                pin = ""
                for m in [i,j,k,l]:
                    if m == 10:
                        pin += "*"
                    elif m == 11:
                        pin += "#"
                    else:
                        pin += str(m)
                if pin not in pins:
                    pins.append(pin)
file = open("test_order.csv", "w")
writer = csv.writer(file)
writer.writerow(pins)
