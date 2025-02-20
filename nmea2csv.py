from functools import reduce
from datetime import datetime, timedelta
def checksum(nmea:str) -> bool:
    """
    This function calculates and tests the checksum for nmea data set.
    @param nmea: nmea data set including $ , * and checksum
    @return bool
    """
    start = nmea.find("$")
    stop = nmea.find("*")
    if start == -1 or stop == -1:
        return False
    substr = nmea[start+1:stop]
    chsum = nmea[stop+1:] # checksum from the sensor
    return chsum == hex(reduce(lambda x, y: x^y, map(ord, substr))).lstrip("0x").upper()


def parse_latitude(lat:str,direction:str) -> float:
    """
    This function converts nmea latitude to decimal degree.
    @param lat: nmea latitude (DDMM.MMM)
    @param direction: nmea direction (N, S)
    @return decimal degree
    """
    if direction not in ["N", "S"]:
        raise Exception("wrong direction definision, only N or S")
    latitude = float(lat[:2]) + float(lat[2:])/60.0
    if direction == "S":
        latitude *= -1
    return latitude

def parse_longitude(lon:str, direction:str) -> float:
    """
    This function converts nmea longitude to decimal degree.
    @param lat: nmea longitude (DDDMM.MMM)
    @param direction: nmea direction (W, E)
    @return decimal degree
    """
    if direction not in ["W", "E"]:
        raise Exception("wrong direction definision, only W or E")
    longitude = float(lon[:3]) + float(lon[3:])/60.0
    if direction == "W":
        longitude *= -1
    return longitude

def nmea2csv(input_file, output_file, sat=0, qlt=0, start_time=None, duration=None, verbose=False):
    report = {'checksum': 0, 'checksumpos': [], 'GPGGA': 0, 'sat': 0, 'qlt': 0}
    with input_file as f, output_file as o:
        for idx, line in enumerate(f):
            line = line.strip() # removing line feed from str obj
            if not checksum(line):
                report['checksum'] += 1
                report['checksumpos'].append(idx+1)
                if verbose:
                    print(f"checksum error: {idx+1}")
                continue
            if "$GPGGA" not in line:
                continue
            report['GPGGA'] += 1
            data = line.split(",")
            if int(data[7]) < sat:
                report['sat'] += 1
                if verbose:
                    print(f"number of sat < {sat}: {idx+1}")
                continue
            if int(data[6]) < qlt:
                report['qlt'] += 1
                if verbose:
                    print(f"position quality < {qlt}: {idx+1}")
                continue
            lat = parse_latitude(data[2], data[3])
            lon = parse_longitude(data[4], data[5])
            ts = datetime.strptime("2024-10-28 " + data[1], "%Y-%m-%d %H%M%S.%f")
            ts += timedelta(hours=1)
            print(f"{ts.strftime('%Y-%m-%d,%H:%M:%S')},{lat:.3f},{lon:.3f}", file=o)
    return report


if __name__ == "__main__":
    print(nmea2csv(open("scripts/sample.nmea", "r"), open("scripts/output.csv", "w"), qlt=1, verbose=True))