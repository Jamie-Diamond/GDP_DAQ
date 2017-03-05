from pathlib import Path
from datetime import datetime
import json
import sys

file_data = {}

def getFile():
    filename  = input("Name of the file to be converted:")
    file_path = Path(filename)

    if not file_path.is_file():
        print('File name not found')
        getFile()

    return filename

def read_in_data(filename):
    print('Reading ' + filename)
    file_object = open(filename, 'r')
    i = 0
    sensor_order = []

    for line in file_object:
        if ((i+1) % 100) == 0:
            sys.stdout.write('\rReading line %s' % (i+1))
            sys.stdout.flush()

        line = line.strip().replace('\x00', '')

        if len(line) > 0:
            if i == 0:
                for title in line.split('\t'):
                    if title != 'clientTime' and title != 'Local Time (hrs)':
                        title_split = title.replace(']','').replace('\n','').split('[')
                        if(len(title_split) < 2):
                            title_split.append(title_split[0])

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
                        try:
                            datetime_obj = datetime.strptime(data + '0000', '%y%m%d-%H%M%S.%f')
                        except:
                            raise Exception('Datetime error for line: ' + str(i+1) + '\r\nLine Content (length: '+ str(len(line)) +'): ' + str(line.split('\t')))
                    elif len(data) < 1:
                        file_data[sensor_order[j - 1]]['data'].append([datetime_obj.timestamp(), 'null', 'null', 1])
                    else:
                        file_data[sensor_order[j-1]]['data'].append([datetime_obj.timestamp(), 'null', data, 1])

                    j += 1
        i += 1

    sys.stdout.write('\rReading line %s -> Done' % (i + 1))
    sys.stdout.flush()

def write_file(filename):
    print('\r')
    sys.stdout.write('\rWriting to ' + filename.split('.')[0] + '.json')
    sys.stdout.flush()
    new_file = open(filename.split('.')[0] + '.json', 'w')
    json_data = json.dumps(file_data)
    new_file.write(json_data)
    sys.stdout.write('\rWriting to ' + filename.split('.')[0] + '.json -> Done')
    sys.stdout.flush()

filename = getFile()
read_in_data(filename)
write_file(filename)

#import pprint
#pprint.PrettyPrinter(indent=4).pprint(file_data)
input("\r\nPress enter to close.")
