
import csv
from datetime import datetime,timedelta
import getopt
import sys
from xml.dom.minidom import Document

__author__ = "John Stilley"
__copyright__ = "Copyright 2013, John Stilley"
__license__ = "GPLv3"
__version__ = "1.0.0"


def main():
    input_file = 'locations.csv'
    output_file = None
    icon = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png'

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:p:')
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit()

    for o,a in opts:
        if o == '-i':
            input_file = a
        elif o == '-o':
            output_file = a
        elif o == '-p':
            icon = a
        else:
            usage()
            sys.exit()

    csv_points = CSVPoints(input_file)
    kml = KMLFromCSVPoints(csv_points, output_file=output_file, icon=icon)
    kml.create_kml()
    kml.write_kml()

def usage():
    print('\nKML from CSV Points -- usage:\n')
    print('This program takes up to three flags (all optional).')
    print('    -i sets the path to the input CSV file.')
    print('    -o sets the path to the output KML file.')
    print('    -p sets the path to the icon used to identify your points.\n')
    print('To geolocate points, the input CSV file will need columns labeled:')
    print('    latitude or lat (case insensitive)')
    print('    longitude, lon, or long (case insensitive)\n')
    print('Optionally, to locate points in time, the CSV will need a column:')
    print('    date_time (case insensitive)\n')


class KMLFromCSVPoints(object):

    def __init__(self, csv_points, output_file=None, icon=None):
        self.d = Document()
        self.csv = csv_points
        self.initial_position = (38.35, -99.1, 3862426)
        self.date_format_ge = '%Y-%m-%d'  # Google Earth date format
        self.date_range = (datetime.now(), datetime.now() + timedelta(days=1))
        self.icon = icon
        self.find_initial_position()
        self.get_date_range()

        # if no output file path, add '.kml' to input file path
        if output_file:
            self.output_file = output_file
        else:
            self.output_file = self.csv.input_file[:-3] + 'kml'

    def find_initial_position(self):
        """Find the Geometric Center of all the lat/lon points.
        Also find the Altitude needed to view all the points.
        This will be used to initially center the Google Earth view.
        """
        # find the lat/lon of all points
        lats = []
        lons = []
        for r in self.csv.rows:
            lats.append(float(r[self.csv.lat_col]))
            lons.append(float(r[self.csv.lon_col]))

        # find the (unweighted) center of the collection of points
        mid_lat = (max(lats) + min(lats)) / 2.0
        mid_lon = (max(lons) + min(lons)) / 2.0

        # use empirical formula to calculate the altitude of the initial view
        max_diff = max(max(lats) - min(lats), max(lons) - min(lons))
        alt = int(1000.0 * (125.5 * max_diff - 14.0))
        alt = max(10000, alt)     # set a lower limit of 10km
        alt = min(alt, 10000000)  # set an upper limit of 10,000km

        self.initial_position = (mid_lat, mid_lon, alt)

    def get_date_range(self):
        """Produce master date range for all rows in the CSV."""
        # if not date column in file, skip finding a range
        if self.csv.date_time_col == -1:
            return

        # get all dates from file
        dates = []
        for r in self.csv.rows:
            d = r[self.csv.date_time_col][:8]
            d = datetime.strptime(d, self.csv.date_format_in)
            dates.append(d)

        # find max and min dates
        min_d = min(dates)
        max_d = max(dates)

        self.date_range = (min_d, max_d + timedelta(days=1))

    def google_start_date(self):
        """Helper method to get begin date in Google Earth format."""
        return self.date_range[0].strftime(self.date_format_ge)

    def google_end_date(self):
        """Helper method to get end date in Google Earth format."""
        return self.date_range[1].strftime(self.date_format_ge)

    def create_kml(self):
        """Create lowest-level tags: kml & Document. Add styles.
        Then loop through the CSV rows and add placemarks.
        """
        base = self.d.createElement('kml')
        base.setAttribute('xmlns','http://earth.google.com/kml/2.2')
        self.d.appendChild(base)
        doc = self.d.createElement('Document')
        base.appendChild(doc)

        self.add_master_timespan(doc)
        self.add_initial_lookat(doc)
        self.add_style_map(doc)
        self.add_styles(doc)

        for row in self.csv.rows:
            self.add_single_placemark(doc, row)

    def add_element(self, *args):
        """simple helper method to reduce the amount of code duplication
        while adding final 1 (or 2)-deep elements that contain text
        """
        if len(args) == 3:
            new_node = self.d.createElement(args[1])
            text_node = self.d.createTextNode(args[2])
            new_node.appendChild(text_node)
            args[0].appendChild(new_node)
        elif len(args) == 4:
            new_master_node = self.d.createElement(args[1])
            new_node = self.d.createElement(args[2])
            text_node = self.d.createTextNode(args[3])
            new_node.appendChild(text_node)
            new_master_node.appendChild(new_node)
            args[0].appendChild(new_master_node)
        else:
            exit('The add_element method requires 3 or 4 arguments.')

    def add_master_timespan(self, doc):
        """The standard KML TimeSpan reference can be found at:
        https://developers.google.com/kml/documentation/kmlreference#timespan
        """
        master_timespan = self.d.createElement('TimeSpan')
        doc.appendChild(master_timespan)

        self.add_element(master_timespan, 'begin', self.google_start_date())
        self.add_element(master_timespan, 'end', self.google_end_date())

    def add_initial_lookat(self, doc):
        """The LookAt sets where the screen is initally centered.
        The standard KML LookAt reference can be found at:
        https://developers.google.com/kml/documentation/kmlreference#lookat
        """
        lookat = self.d.createElement('LookAt')
        doc.appendChild(lookat)

        # create local timespan
        lookat_timespan = self.d.createElement('TimeSpan')
        lookat.appendChild(lookat_timespan)

        self.add_element(lookat_timespan, 'begin', self.google_start_date())
        self.add_element(lookat_timespan, 'end', self.google_end_date())

        # create lat/lon tags
        self.add_element(lookat, 'latitude', str(self.initial_position[0]))
        self.add_element(lookat, 'longitude', str(self.initial_position[1]))
        self.add_element(lookat, 'altitude', str(self.initial_position[2]))
        self.add_element(lookat, 'altitudeMode', 'relativeToGround')

    def add_style_map(self, doc):
        """The standard KML StyleMap reference can be found at:
        https://developers.google.com/kml/documentation/kmlreference#stylemap
        """
        style_map = self.d.createElement('StyleMap')
        style_map.setAttribute('id','point')
        doc.appendChild(style_map)

        p1 = self.d.createElement('Pair')
        self.add_element(p1, 'key', 'normal')
        self.add_element(p1, 'styleUrl', '#point_unfocused')
        style_map.appendChild(p1)

        p2 = self.d.createElement('Pair')
        self.add_element(p2, 'key', 'highlight')
        self.add_element(p2, 'styleUrl', '#point_focused')
        style_map.appendChild(p2)

    def add_styles(self, doc):
        """The standard KML Style reference can be found at:
        https://developers.google.com/kml/documentation/kmlreference#style
        """
        self.add_focused_style(doc)
        self.add_unfocused_style(doc)

    def add_focused_style(self, doc):
        """create Point Focused Style"""
        style_foc = self.d.createElement('Style')
        style_foc.setAttribute('id','point_focused')

        self.add_element(style_foc, 'LabelStyle', 'scale', '1.0')

        icon_style = self.d.createElement('IconStyle')
        self.add_element(icon_style, 'scale', '1.0')
        self.add_element(icon_style, 'heading', '0.0')

        icon = self.d.createElement('Icon')
        self.add_element(icon, 'href', self.icon)
        self.add_element(icon, 'refreshInterval', '0.0')
        self.add_element(icon, 'viewRefreshTime', '0.0')
        self.add_element(icon, 'viewBoundScale', '0.0')
        icon_style.appendChild(icon)
        style_foc.appendChild(icon_style)
        doc.appendChild(style_foc)

    def add_unfocused_style(self, doc):
        """create Point Unfocused Style"""
        style_unfoc = self.d.createElement('Style')
        style_unfoc.setAttribute('id','point_unfocused')

        self.add_element(style_unfoc, 'LabelStyle', 'scale', '0.0')

        icon_style = self.d.createElement('IconStyle')
        self.add_element(icon_style, 'scale', '1.0')
        self.add_element(icon_style, 'heading', '0.0')

        icon = self.d.createElement('Icon')
        self.add_element(icon, 'href', self.icon)
        self.add_element(icon, 'refreshInterval', '0.0')
        self.add_element(icon, 'viewRefreshTime', '0.0')
        self.add_element(icon, 'viewBoundScale', '0.0')
        icon_style.appendChild(icon)
        style_unfoc.appendChild(icon_style)
        doc.appendChild(style_unfoc)

    def add_single_placemark(self, doc, csv_row):
        """Create a single Placemark (one for each point).
        The standard KML Placemark reference can be found at:
        https://developers.google.com/kml/documentation/kmlreference#placemark
        """
        # get date info
        if self.csv.date_time_col == -1:
            start = datetime.now()
            end = datetime.now() + timedelta(days=1)
        else:
            date = csv_row[self.csv.date_time_col][:8]
            start = datetime.strptime(date, self.csv.date_format_in)
            end = start + timedelta(days=1)

        date_start = start.strftime(self.date_format_ge)
        date_end = end.strftime(self.date_format_ge)

        # get location info
        lat = str(csv_row[self.csv.lat_col])
        lon = str(csv_row[self.csv.lon_col])
        alt = '0'

        # create placemark
        placemark = self.d.createElement('Placemark')
        doc.appendChild(placemark)

        self.add_element(placemark, 'name', csv_row[0] + ' on ' + date_start)

        #    fill description with HTML table of all the CSV columns
        desc = self.d.createElement('description')
        table = self.add_html_table(csv_row)
        desc.appendChild(table)
        placemark.appendChild(desc)

        point_timespan = self.d.createElement('TimeSpan')
        placemark.appendChild(point_timespan)
        self.add_element(point_timespan, 'begin', date_start)
        self.add_element(point_timespan, 'end', date_end)

        self.add_element(placemark, 'styleUrl', '#point')

        coord = lon +',' + lat + ',' + alt
        self.add_element(placemark, 'Point', 'coordinates', coord)

    def add_html_table(self, csv_row):
        """add HTML table to description"""
        table = self.d.createElement('table')
        table.appendChild(self.add_table_header())

        # loop over all point attributes (CSV columns)
        col_num = 0
        for col in csv_row:
            table.appendChild(self.add_table_row(self.csv.header[col_num], col))
            col_num += 1

        return table

    def add_table_row(self, key, value):
        """Add an HTML row for each CSV column."""
        new_row = self.d.createElement('tr')

        self.add_element(new_row, 'td', key)
        self.add_element(new_row, 'td', value)
        
        return new_row
        
    def add_table_header(self):
        """Add a Bold HTML header to the placemark header."""
        new_row = self.d.createElement('tr')
        
        self.add_element(new_row, 'td', 'b', 'Field')
        self.add_element(new_row, 'td', 'b', 'Value')
        
        return new_row

    def write_kml(self):
        """Write out the final KML file."""
        f = open(self.output_file, 'w')
        f.write(self.d.toxml(encoding='utf-8'))
        f.close()


class CSVPoints(object):

    def __init__(self, input_file):
        self.input_file = input_file
        self.header =[]
        self.rows = []
        self.lat_col = 0
        self.lon_col = 1
        self.date_time_col = -1
        self.date_format_in = '%Y%m%d'
        self.read_csv()
        self.get_lat_lon_col_nums()
        self.get_date_time_col_num()

    def read_csv(self):
        """Reads the CSV header into a list,
        and all following lines into a list of lists.
        """
        f = open(self.input_file, 'r')
        reader = csv.reader(f)

        rows = []
        for row in reader:
            rows.append([col.decode('utf-8') for col in row])
        f.close()

        if len(rows) < 2:
            exit('The input CSV file has too few rows.')
        elif len(row[0]) < 2:
            exit('The input CSV file has too few columns.')

        self.header = rows[0]
        self.rows = rows[1:]

    def get_lat_lon_col_nums(self):
        """Get the numbers of the lat/lon columns."""
        header = [c.lower() for c in self.header]

        lats = ['latitude', 'lat']
        lat = set(header).intersection(set(lats))
        if len(lat) > 0:
            self.lat_col = header.index(lat.pop())
        else:
            exit('Could not find a column labeled: ' + str(lats))

        lons = ['longitude', 'lon', 'long']
        lon = set(header).intersection(set(lons))
        if len(lon) > 0:
            self.lon_col = header.index(lon.pop())
        else:
            exit('Could not find a column labeled: ' + str(lons))

    def get_date_time_col_num(self):
        """Get the number of the 'date_time' column."""
        header = [c.lower() for c in self.header]
        if 'date_time' in header:
            self.date_time_col = header.index('date_time')


if __name__ == "__main__":
    main()


