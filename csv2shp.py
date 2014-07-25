import csv
import getopt
from osgeo import ogr
from osgeo import osr
from pyproj import Proj
import sys

# CONSTANTS
PROJECTION = '+proj=lcc +lat_1=30 +lat_2=60 +lat_0=37 +lon_0=-120.5 +units=m'
REPROJECT = Proj(proj=PROJECTION[6:])
OUTPUT_DIR = 'output/'
    

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:p:", ["-i=", "-o=", "-p="])
    except getopt.GetoptError, err:
        usage()

    in_path = ''
    out_path = ''

    for o, a in opts:
        if o == '-i':
            in_path = str(a)
        elif o == '-o':
            out_path = str(a)
        elif o == '-p':
            PROJECTION = str(a)
            REPROJECT = Proj(proj=PROJECTION[6:])
        else:
            usage()

    # validate file paths
    if in_path == '':
        usage()
    elif out_path == '':
        out_path = OUTPUT_DIR + in_path.split('/')[-1][:-3] + 'shp'

    # read input CSV
    data, fields = read_csv(in_path)
    # create output ESRI-type shapefile
    create_shapefile(out_path, data, fields)


def usage():
    """simple usage statement, for new users"""
    print('\nPurpose:\n')
    print('This script will convert a lon/lat CSV file into a ESRI-type shapefile.')
    print('The CSV file is only required to have two lon/lat fields, but the spelling is flexible:')
    print('"lat", "Lat", "lAtiTude", "LON", "Long", "LONGitude", etcetera.')
    print('Any extra collumns will be appended to the shapefile as feature attributes.\n')
    print('NOTE: This script will only work with point data.')
    print('NOTE: The example default projection is a Lambert Conformal grid in California.\n\n')
    print('Usage:\n')
    print('python csv2shp.py -i /path/to/input.csv')
    print('or')
    print('python csv2shp.py -i /path/to/input.csv -o /path/to/output.shp')
    print('or')
    print('python csv2shp.py -i /path/to/input.csv -p "+proj=lcc +lat_1=30 +lat_2=60"\n')
    exit()


def create_shapefile(filepath, data, fields):
    """Create an ESRI-type shapefile from arbitary CSV point data.
    All data not associated with lon/lat or x/y will be appended as an
    attribute to each point.
    """
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromProj4(PROJECTION)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shape_data = driver.CreateDataSource(filepath)
    layer = shape_data.CreateLayer('customs', spatial_ref, ogr.wkbPoint)
   
    # create fields
    for i, nf, tp in fields:
        if tp == float:
            new_field = ogr.FieldDefn(nf, ogr.OFTReal)
            layer.CreateField(new_field)
        else:
            new_field = ogr.FieldDefn(nf, ogr.OFTString)
            layer.CreateField(new_field)
   
    layer_defn = layer.GetLayerDefn()
    point = ogr.Geometry(ogr.wkbPoint) 
   
    # create all of the points, and give them the correct attributes
    for fid in data.keys():
        point.AddPoint(data[fid]['x'], data[fid]['y'])
        feature_index = fid
        feature = ogr.Feature(layer_defn) 
        feature.SetGeometry(point)
        feature.SetFID(feature_index)
        for i, f in data[fid]['fields']:
            feature.SetField(i, f)
        layer.CreateFeature(feature)
   
    # Close the shapefile
    shape_data.Destroy()


def read_csv(filepath):
    """Read CSV into special data dictionary.
    Example CSV file:

    lon,fac_id,lat,weight1,weight2,random_text,location_name
    -119.588652,12,37.749842,8,2,nice diorama,Yosemite Valley
    -121.182531,24,36.490335,27,3,rocks!,Pinnacles
    -122.456037,68,37.794759,0,1,geeks,San Fancisco
    """
    # open the file
    reader = csv.DictReader(open(filepath, 'r'))
    
    data = {}
    field_names = []
    fid = 0
    
    # loop through the CSV and fill output data
    for row in reader:
        lat = None
        lon = None
        fields = []
        field_id = 0
        
        # separate lon/lat from other CSV columns
        for key, value in row.iteritems():
            if key.lower() in ['lat', 'latitude']:
                lat = float(value)
            elif key.lower() in ['lon', 'long', 'longitude']:
                lon = float(value)
            else:
                # TODO: This is a bit slow, but we need to separate numbers from words.
                try:
                    fields.append((field_id, float(value)))
                    # first time through, build a header
                    if fid == 0:
                        field_names.append((field_id, key, float))
                    field_id += 1
                except:
                    fields.append((field_id, value))
                    # first time through, build a header
                    if fid == 0:
                        field_names.append((field_id, key, str))
                    field_id += 1
        
        if lat == None or lon == None:
            raise KeyError('Lon/Lat not found.')
        
        # convert lon/lat to projection
        x, y = lon_lat_to_projection(lon, lat)
    
        # fill output data
        data[fid] = {'x': x, 'y': y, 'fields': fields}
        fid += 1

    return data, field_names


def lon_lat_to_projection(lon, lat):
    """Reproject a lat/lon pair to the desired modeling domain.
    """
    return REPROJECT(lon, lat)


if __name__ == "__main__":
    main()

