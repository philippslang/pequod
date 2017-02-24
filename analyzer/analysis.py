import queries
import requests

from timeseries import TimeSeries
from plots import Plot

from google.cloud import storage

import re, uuid

import mysite.dispatch as internal_requests


class AnalysisResults():
    def __init__(self, result, url_image=internal_requests.BAD_VALUE):
        self.result = result
        self.url_image = url_image
        
def open_pod_bay_doors(rpt_content):
    return AnalysisResults('I\'m afraid I can\'t do that, Jim.')
    
def meaning_of_life(rpt_content):
    return AnalysisResults('42.')
    
# TODO this should be curried so that we have one for error, warning and info
def entity_count(rpt_content, search):
    p = re.compile(r'[|][\s]*' + search + r'[\s,|]*\d+')
    occ = p.findall(rpt_content)
    if occ:
        count = int(occ[0].split()[-1])
        return AnalysisResults('There are {} {}(s).'.format(count, search.lower()))
    return AnalysisResults('{} count pattern could not be matched in file.'.format(search))

def error_count(rpt_content):
    return entity_count(rpt_content, 'ERROR')

def warning_count(rpt_content):
    return entity_count(rpt_content, 'WARNING')
    
def completion_count(rpt_content):
    return entity_count(rpt_content, 'Completions')
    
def well_count(rpt_content):
    return entity_count(rpt_content, 'Wells')
    
def region_count(rpt_content):
    return entity_count(rpt_content, 'Regions')

def run_time(rpt_content):
    p = re.compile(r'Simulation complete.*[=]')
    m = p.findall(rpt_content)
    if m:
        secs = int(re.sub(r'\D+', '', m[0].split()[-2]))
        duration = timedelta(seconds=secs)
        duration_str = ''
        if secs >= 3600:
            duration_str += "{} hours ".format(secs//3600)
            secs = secs % 3600
        if secs >= 60:
            duration_str += "{} minutes ".format(secs//60)
            secs = secs % 60
        duration_str += "{} seconds".format(duration.seconds)
    
        return AnalysisResults("The simulation run time was {}.".format(duration_str))
    return AnalysisResults('Run time could not be determined from the file.')
    
def simulation_time(rpt_content):
    start_date = None
    stop_date = None
    duration = None
    p = re.compile(r'SECTION\s*Starting the simulation on (.+)\.')
    m = p.findall(rpt_content)
    if m:
        start_date = m[0].split()[0]
    
    p = re.compile(r'SECTION\s*The simulation has reached (\d.*\d) (\d+) d\.')
    for m in p.finditer(rpt_content):
        stop_date = m.group(1)
        duration = m.group(2)
    
    if duration is not None:
        return AnalysisResults("The simulation is for {} days starting on {} and ending on {}.".format(duration, start_date, stop_date))
    return AnalysisResults('Simulation time could not be determined from the file.')

# TODO this should be curried so that we have one for error, warning and info
def cell_count(rpt_content):
    p = re.compile(r'[|][\s]*Number of Cells[\s,|]*\d+')
    occ = p.findall(rpt_content)
    if occ:
        count = int(occ[0].split()[-1])
        return AnalysisResults('There are {} cells in this model.'.format(count))
    return AnalysisResults('Cell count pattern could not be matched in file.')

def finished_normally(rpt_content):
    normal = 'finished normally' in rpt_content
    if normal:
        return AnalysisResults('The run finshed normally.')
    return AnalysisResults('The run did not finish normally.')

def processor_count(rpt_content):
    p = re.compile(r'Run Type\s+:\s*(.*)')
    occ = p.findall(rpt_content)
    if occ:
        count = 1       ## Default is serial
        p = re.compile(r'Parallel with (\d+) processes')
        occ = p.match(occ[0])
        if occ:
            count = occ.group(1)
            return AnalysisResults('There were {} processors used for this model.'.format(count))
        else:
            return AnalysisResults('There was a single processor used for this model.')
    return AnalysisResults('Processor count pattern could not be matched in file.')

def fluid_in_place(rpt_content, phase='oil', time=0.0):
    p = re.compile(r"REPORT\s*Surface fluids in place .* 'RESERVOIR' .* time (\d+)\s*d:")
    start = -1
    min_diff = 1E20
    for m in p.finditer(rpt_content):
        diff = abs(time - float(m.group(1)))
        if diff < min_diff:
            min_diff = diff
            start = m.start()

    fip = None
    if start > 0:
        end = start + 600       ## This number of characters should be enough 
        lines = rpt_content[start:end].split('\n')
        for line in lines:
            if 'RESERVOIR' in line and 'Surface' not in line:
                columns = line.split('|')
                if phase=='gas':
                    fip = float(columns[4])
                elif phase=='water':
                    fip = float(columns[5])
                else:
                    fip = float(columns[3])
                break
    if fip is not None:
        return AnalysisResults("The {} in place at time {} days is {}.".format(phase, time, fip))
    return AnalysisResults('Failed to find fluid in place from file.')

def oil_in_place(rpt_content, time=0.0):
    return fluid_in_place(rpt_content, 'oil', time)

def gas_in_place(rpt_content, time=0.0):
    return fluid_in_place(rpt_content, 'gas', time)

def water_in_place(rpt_content, time=0.0):
    return fluid_in_place(rpt_content, 'water', time)
    

def upload_plot_google_storage(plot_io):
    """
    Returns public url to image, or raises EnvironmentError if not able to upload.
    """
    client = storage.Client()
    bucket_name = internal_requests.TEMP_IMG_BUCKET
    file_name = str(uuid.uuid1())+'.png'
    bucket = client.get_bucket(bucket_name)    
    blob = storage.Blob(file_name, bucket)
    
    try:
        plot_io.seek(0)
        blob.upload_from_file(plot_io, content_type=r'image/png', size=len(plot_io.getvalue()))
        blob.make_public()        
        print 'ANALYZER::analysis::upload_plot: Uploaded {0} to bucket {1}'.format(file_name, bucket_name)
        return blob.public_url
    except ValueError:
        print 'ANALYZER::analysis::upload_plot: Could not upload {0} to bucket {1}'.format(file_name, bucket_name)
        raise EnvironmentError('Could not upload to Google Storage, trying to move {0} to bucket {1}'.format(file_name, bucket_name))


def upload_plot(plot_io):
    try:
        img_url = upload_plot_google_storage(plot_io)
        return AnalysisResults("Plot generated.", img_url)
    except EnvironmentError:
        return AnalysisResults("Plot upload failed.", internal_requests.BAD_VALUE)


def generate_plot(rpt_content, series, item, title):
    seriesData = series.getSeries(item)
    plot = Plot()
    plot.setXData(seriesData[0])
    plot.setYData(seriesData[1], title)
    plot.setTitle(series.getCaseName() + ' - ' + title)
    plot_io = plot.getPlotImage()
    return plot_io

def show_plot(rpt_content, item, title):
    series = TimeSeries(rpt_content) 
    plot_io = generate_plot(rpt_content, series, item, title)
    return upload_plot(plot_io)
    
def show_plot_pressure(rpt_content):
    return show_plot(rpt_content, 'FPR', 'Pressure')
def show_plot_oil_production(rpt_content):
    return show_plot(rpt_content, 'OPR', 'Oil production rate')
def show_plot_gas_production(rpt_content):
    return show_plot(rpt_content, 'GPR', 'Gas production rate')
def show_plot_gas_injection(rpt_content):
    return show_plot(rpt_content, 'GIR', 'Gas injection rate')
def show_plot_water_injection(rpt_content):
    return show_plot(rpt_content, 'WIR', 'Water injection rate')
def show_plot_water_production(rpt_content):
    return show_plot(rpt_content, 'WPR', 'Water production rate')
def show_plot_water_cut(rpt_content):
    return show_plot(rpt_content, 'WCT', 'Water-cut')
def show_plot_gas_oil_ratio(rpt_content):
    return show_plot(rpt_content, 'GOR', 'Gas-oil-ratio')


# map supported queries to functions
SUPPORTED_ANALYSIS = {
    'cell_count'                    : cell_count,
    'error_count'                   : error_count,
    'finished_normally'             : finished_normally,
    'gas_in_place'                  : gas_in_place,
    'oil_in_place'                  : oil_in_place,
    'processor_count'               : processor_count,
    'run_time'                      : run_time,
    'show_plot_pressure'            : show_plot_pressure,
    'show_plot_oil_production'      : show_plot_oil_production,
    'show_plot_gas_production'      : show_plot_gas_production,
    'show_plot_water_production'    : show_plot_water_production,
    'show_plot_gas_injection'       : show_plot_gas_injection,
    'show_plot_water_injection'     : show_plot_water_injection,
    'show_plot_water_cut'           : show_plot_water_cut,
    'show_plot_gas_oil_ratio'       : show_plot_gas_oil_ratio,
    'simulation_time'               : simulation_time,
    'warning_count'                 : warning_count,
    'water_in_place'                : water_in_place,
    'open_pod_bay_doors'            : open_pod_bay_doors,
    'meaning_of_life'               : meaning_of_life,
    'completion_count'              : completion_count,
    'well_count'                    : well_count,
    'region_count'                  : region_count,
}

def analyze(supported_query, url_rpt):
    """
    Returns formatted text containing the analysis result.
    """
    
    if supported_query in SUPPORTED_ANALYSIS:
        rpt_request = requests.get(url_rpt)
        if rpt_request.ok:
            analysis_results = SUPPORTED_ANALYSIS[supported_query](rpt_request.content)
            print 'ANALYZER::analysis::analyze: Successful analysis \"{0}\", \"{1}\"'.format(analysis_results.result, analysis_results.url_image)
            return analysis_results.result, analysis_results.url_image
        else:
            result = 'Can\'t access ' + url_rpt +', trying ' + supported_query + '.'
    else:
        url_image = internal_requests.BAD_VALUE
        result = 'Analysis ' + supported_query + ' not supported, trying ' + url_rpt + '.'
 
    return result, url_image
