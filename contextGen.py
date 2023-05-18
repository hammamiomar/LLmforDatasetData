import datamart_profiler
import io
import pandas as pd
import os
import openai
from math import radians, sin, cos, sqrt,asin
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim


openai.api_key = os.getenv("OPENAI_API_KEY")

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))

    return R * c

def unstack_ranges(ranges):
    coordinates_list = []
    for item in ranges:
        coordinates_list.append(item['range']['coordinates'][0])
        coordinates_list.append(item['range']['coordinates'][1])
    return coordinates_list

def find_furthest_pairs(coords_list):
    max_distance = 0
    furthest_pairs = None
    geolocator = Nominatim(user_agent="my-app")  # Specify your user agent

    coords_list= unstack_ranges(coords_list)
    furthest_pairs = [coords_list[0],coords_list[1]]
    furthestDist = haversine_distance(coords_list[0][1], coords_list[0][0], coords_list[1][1], coords_list[1][0])
    
    distFlag=0
    for item in coords_list[2:]:
        dist1 = haversine_distance(furthest_pairs[0][1], furthest_pairs[0][0], item[1], item[0])
        dist2 = haversine_distance(furthest_pairs[1][1], furthest_pairs[1][0], item[1], item[0])
        if dist1<dist2:
            distFlag=1

        if distFlag==0 and dist1>furthestDist:
            furthestDist = dist1
            furthest_pairs[1] = item
        elif distFlag==1 and dist2>furthestDist:
            furthestDist = dist2
            furthest_pairs[0] = item
        distFlag=0
    
    location = geolocator.reverse((furthest_pairs[0][1],furthest_pairs[0][0]), exactly_one=True)
    min_address = location.raw['address']
    min_city = min_address.get('city', '') or min_address.get('town', '') or min_address.get('village', '') or min_address.get('state', '')

    # Reverse geocode the maximum latitude and longitude
    location = geolocator.reverse((furthest_pairs[1][1],furthest_pairs[1][0]), exactly_one=True)
    max_address = location.raw['address']
    max_city = max_address.get('city', '') or max_address.get('town', '') or max_address.get('village', '') or max_address.get('state', '')

    return min_city,max_city

def getTimeRange(timeCoverage):
    epoch = datetime(1970, 1, 1)  # Unix epoch start date
    min_start_date = None
    max_start_date = None
    
    for range_item in timeCoverage:
        start_timestamp = range_item['range']['gte']
        end_timestamp = range_item['range']['lte']

        start_date = epoch + timedelta(seconds=start_timestamp)
        end_date = epoch + timedelta(seconds=end_timestamp)
        
        if min_start_date is None or start_date < min_start_date:
            min_start_date = start_date
        
        if max_start_date is None or end_date > max_start_date:
            max_start_date = end_date
    
    return min_start_date, max_start_date

def formatContext(contextArr,sample,spatial=None,temporal=None):
    result=""
    for d in contextArr:
        result+="Column "+d['name']+" is a "+d['structural_type']+". "
        if('num_distinct_values' in d.keys()):
            result+="There are "+str(d['num_distinct_values'])+" distinct values. "
        if('coverage' in d.keys()):
            result+="The range of values are from "+str(d['coverage'][0])+" to "+str(d['coverage'][1])+". "
        if(len(d['semantic_types'])>0):
            result+="The semantic types are: "
            for s in d['semantic_types']:
                result+=s+", "
        result=result[:-2]
        result+=". "
        result+="\n"
    result+="\n"
    if(spatial!=None):
        result+="The dataset covers an area ranging from"+spatial[0]+" to "+spatial[1]+". "
        result+="\n"
    if(temporal!=None):
        result+="The dataset covers a date time range from "+str(temporal[0].date())+" to "+str(temporal[1].date())+". \n"
        result+="The dataset covers a hour time range from "+str(temporal[0].time())+" to "+str(temporal[1].time())+". \n"
    final = "Input: \n" + sample + "\n\n" + "Context: \n" + result
    return final

def processDataset(datapath):
    print("Processing dataset:" +datapath)
    print('\n')
    metadata = datamart_profiler.process_dataset(datapath)
    contextArr=[]
    spatial=None
    temporal=None
    for i in range(len(metadata['columns'])):
        metDict = metadata['columns'][i]
        cDict={'name':metDict['name']
               ,'structural_type':metDict['structural_type'],
               'semantic_types':metDict['semantic_types']}
        if('num_distinct_values' in metDict.keys()):
            cDict['num_distinct_values'] = metDict['num_distinct_values']
        if('coverage' in metDict.keys()):
            low=0
            high=0
            for i in range(len(metDict['coverage'])):
                if(metDict['coverage'][i]['range']['gte']<low):
                    low=metDict['coverage'][i]['range']['gte']
                if(metDict['coverage'][i]['range']['lte']>high):
                    high=metDict['coverage'][i]['range']['lte']
            cDict['coverage'] = [low,high]
        contextArr.append(cDict)

    if('spatial_coverage' in metadata.keys()):
        min_city,max_city=find_furthest_pairs(metadata['spatial_coverage'][0]['ranges'])
        spatial=(min_city,max_city)
    if('temporal_coverage' in metadata.keys()):
        min_date,max_date=getTimeRange(metadata['temporal_coverage'][0]['ranges'])
        temporal=(min_date,max_date)
    df = pd.read_csv(datapath)
    df = df.sample(12)
    sample = df.to_csv(index=False)

    context=formatContext(contextArr,sample,spatial=spatial,temporal=temporal)
    return context,sample


if __name__ == "__main__":
    context = processDataset('datasets/meeting.csv')
    print(context)
    #genPrompts(context)