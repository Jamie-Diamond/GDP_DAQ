from pathlib import Path
from datetime import datetime
import json

file_data = {}

def getFile():
    filename  = input("Name of the file to be converted:")
    file_path = Path(filename)

    if not file_path.is_file():
        print('File name not found')
        getFile()

    return filename

def read_in_data(filename):
    file_object = open(filename, 'r')
    i = 0
    sensor_order = []

    for line in file_object:
        if i == 0:
            for title in line.split('\t'):
                if title != 'clientTime' and title != 'Local Time (hrs)':
                    title_split = title.replace(']','').replace('\n','').split('[')
                    file_data[title_split[1].strip()] = {
                        'verbose name': title_split[0].strip(),
                        'data': []
                    }
                    sensor_order.append(title_split[1].strip())
        else:
            j = 0
            datetime_obj = None
            line_split = line.split('\t')
            cleaned_line = []

            for entry in line_split:
                if entry.strip() != '' and entry.strip() != '\n':
                    cleaned_line.append(entry.strip())


            for data in cleaned_line:
                if j == 0:
                    datetime_obj = datetime.strptime(data + '0000', '%y%m%d-%H%M%S.%f')
                else:
                    file_data[sensor_order[j-1]]['data'].append([datetime_obj.timestamp(), 'null', data, 1])

                j += 1
        i += 1

def write_file(filename):
    new_file = open(filename.split('.')[0] + '.json', 'w')
    json_data = json.dumps(file_data)
    new_file.write(json_data)


filename = getFile()
read_in_data(filename)
write_file(filename)

#import pprint
#pprint.PrettyPrinter(indent=4).pprint(file_data)
input("Press enter to close.")
