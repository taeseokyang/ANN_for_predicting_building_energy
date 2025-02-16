import subprocess
import time
from eppy.modeleditor import IDF
import random

IDD_FILE_PATH = "/Applications/EnergyPlus-23-1-0/Energy+.idd"
WORK_DIR = "/Users/yangts/research/"
ORIGINAL_FILE = "original.idf"
CHANGED_FILE = "changed.idf"
WEATHER_FILE = "USA_TX_El.Paso.Intl.AP.722700_TMY3.epw"
TEST_TIME = 100

def change_window_ratio(idf):
    value = 0
    for window in idf.idfobjects["Window"]:
        value = window.Length
    return value
def change_window_transfer(idf):
    MAX = 6.0
    MIN = 1.6
    value = random.uniform(MIN, MAX)
    idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][0].UFactor = value
    return [idf.idfobjects["WindowMaterial:SimpleGlazingSystem"][0].UFactor, (value - MIN)/(MAX-MIN)]
def change_wall_transfer(idf):
    MAX = 2.8
    MIN = 0.1
    value = random.uniform(MIN, MAX)
    idf.idfobjects["Material"][5].Conductivity = value
    return [idf.idfobjects["Material"][5].Conductivity, (value - MIN)/(MAX-MIN)]
def change_roof_transfer(idf):
    MAX = 2.8
    MIN = 0.1
    value = random.uniform(MIN, MAX)
    idf.idfobjects["Material"][11].Conductivity = value
    return [idf.idfobjects["Material"][11].Conductivity, (value - MIN)/(MAX-MIN)]
def change_orientation(idf):
    MAX = 180
    MIN = -180
    value = random.randint(MIN, MAX)
    idf.idfobjects['BUILDING'][0].North_Axis = value
    return [idf.idfobjects['BUILDING'][0].North_Axis, (value - MIN)/(MAX-MIN)]

def change():
    fname = WORK_DIR + ORIGINAL_FILE
    IDF.setiddname(IDD_FILE_PATH)
    idf = IDF(fname)

    orientation = change_orientation(idf)
    roof_transfer = change_roof_transfer(idf)
    wall_transfer = change_wall_transfer(idf)
    window_transfer = change_window_transfer(idf)
    # window_ratio = change_window_ratio(idf)

    idf.save(WORK_DIR + CHANGED_FILE)
    time.sleep(1)
    return [orientation, roof_transfer, wall_transfer, window_transfer]

def simulate():
    command = [
        "energyplus",
        "-w", WEATHER_FILE,
        "-r",
        CHANGED_FILE
    ]
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr)

def get_output():
    file_path = "eplustbl.csv"
    line_number1 = 199

    start_index = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for current_line_number, line in enumerate(file, start=1):
            if current_line_number == line_number1:
                datas = line.strip().split(",")
                data1 = (8760.0-float(datas[2]))/8760.0

            if line.strip() == "FOR:,LIVING_UNIT1":
                start_index = current_line_number
            if start_index != 0 and current_line_number - start_index == 17:
                datas = line.strip().split(",")
                data2 = float(datas[2])+float(datas[3])
                break
    return [data1, data2]

def main():
    with open(WORK_DIR + "result.txt", "w", encoding="utf-8") as f:
        for i in range(TEST_TIME):
            print(i,"/",TEST_TIME)
            input = change()
            simulate()
            output = get_output()

            f.write(f"{i},")
            for j in input:
                f.write(f"{','.join(map(str, j))},")
            f.write(f"{','.join(map(str, output))}\n")
main()