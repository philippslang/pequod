import queries
import requests

from timeseries import TimeSeries
from plots import Plot

from google.cloud import storage

import re

PRT_BUCKET = 'pequod'

class AnalysisResults():
    def __init__(self, result, url_image='na'):
        self.result = result
        self.url_image = url_image

# TODO this should be curried so that we have one for error, warning and info
def error_count(rpt_content):
    p = re.compile(r'[|][\s]*ERROR[\s,|]*\d+')
    occ = p.findall(rpt_content)
    if occ:
        count = int(occ[0].split()[-1])
        return AnalysisResults('There are {} error(s).'.format(count))
    return AnalysisResults('Error count pattern could not be matched in file.')


# TODO this should be curried so that we have one for error, warning and info
def warning_count(rpt_content):
    p = re.compile(r'[|][\s]*WARNING[\s,|]*\d+')
    occ = p.findall(rpt_content)
    if occ:
        count = int(occ[0].split()[-1])
        return AnalysisResults('There are {} warning(s).'.format(count))
    return AnalysisResults('Warning count pattern could not be matched in file.')

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
        return 'The run finshed normally.'
    return 'The run did not finish normally.'

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
    
def upload_plot(plot, fname):
    '''
    fname like 'something.png'
    '''
    # TODO fetch an app wide available encryption key
    client = storage.Client()
    bucket_name = PRT_BUCKET
    bucket = client.get_bucket(bucket_name)    
    blob = storage.Blob(fname, bucket)
    
    # now we need some
    print plot
    blob.upload_from_file(plot.getvalue(), content_type='image/png', size=len(plot.getvalue()), client=client)
    
    # TODO do we neeed this if we only access app wide?
    blob.make_public()

    return blob.public_url

def show_plot(rpt_content, item, title):
    series = TimeSeries(rpt_content) 
    seriesData = series.getSeries(item)
    plot = Plot()
    plot.setTimeData(seriesData[0])
    plot.setSeries(title, seriesData[1])
    plot_data = plot.savePlot()
    img_url = upload_plot(plot_data, item + '.png')
    # upload to bucket
    return AnalysisResults("Plot generated.", img_url)
    
def show_plot_pressure(rpt_content):
    return show_plot(rpt_content, 'FPR', 'Pressure')

# map supported queries to functions
SUPPORTED_ANALYSIS = {
    'cell_count'            : show_plot_pressure,
    'error_count'           : error_count,
    'finished_normally'     : finished_normally,
    'gas_in_place'          : gas_in_place,
    'oil_in_place'          : oil_in_place,
    'processor_count'       : processor_count,
    'run_time'              : run_time,
    'show_plot_pressure'    : show_plot_pressure,
    'simulation_time'       : simulation_time,
    'warning_count'         : warning_count,
    'water_in_place'        : water_in_place,
}

def analyze(supported_query, url_rpt):
    """
    Returns formatted text containing the analysis result.
    """
    url_image = r'na'
    
    if supported_query in SUPPORTED_ANALYSIS:
        rpt_request = requests.get(url_rpt)
        if rpt_request.ok:
            analysis_results = SUPPORTED_ANALYSIS[supported_query](rpt_request.content)
            print analysis_results.result, analysis_results.url_image
            return analysis_results.result, analysis_results.url_image
        else:
            bail_out_result = 'Can\'t access ' + url_rpt +', trying ' + supported_query + '.'
    else:
        bail_out_result = 'Analysis ' + supported_query + ' not supported, trying ' + url_rpt + '.'
 
    return bail_out_result, url_image
