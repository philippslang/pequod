import queries
import requests

import re

# TODO this should be curried so that we have one for error, warning and info
def error_count(rpt_content):
    p = re.compile(r'[|][\s]*ERROR[\s,|]*\d+')
    occ = p.findall(rpt_content)
    if occ:
        count = int(occ[0].split()[-1])
        return 'There are {} error(s).'.format(count)
    return 'Error count pattern could not be matched in file.'


# TODO this should be curried so that we have one for error, warning and info
def warning_count(rpt_content):
    p = re.compile(r'[|][\s]*WARNING[\s,|]*\d+')
    occ = p.findall(rpt_content)
    if occ:
        count = int(occ[0].split()[-1])
        return 'There are {} warning(s).'.format(count)
    return 'Warning count pattern could not be matched in file.'

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
    
        return "The simulation run time was {}.".format(duration_str)
    return 'Run time could not be determined from the file.'
    
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
        return "The simulation is for {} days starting on {} and ending on {}.".format(duration, start_date, stop_date)
    return 'Simulation time could not be determined from the file.'

# TODO this should be curried so that we have one for error, warning and info
def cell_count(rpt_content):
    p = re.compile(r'[|][\s]*Number of Cells[\s,|]*\d+')
    occ = p.findall(rpt_content)
    if occ:
        count = int(occ[0].split()[-1])
        return 'There are {} cells in this model.'.format(count)
    return 'Cell count pattern could not be matched in file.'

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
            return 'There were {} processors used for this model.'.format(count)
        else:
            return 'There was a single processor used for this model.'
    return 'Processor count pattern could not be matched in file.'

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
        return "The {} in place at time {} days is {}.".format(phase, time, fip)
    return 'Failed to find fluid in place from file.'

def oil_in_place(rpt_content, time=0.0):
    return fluid_in_place(rpt_content, 'oil', time)

def gas_in_place(rpt_content, time=0.0):
    return fluid_in_place(rpt_content, 'gas', time)

def water_in_place(rpt_content, time=0.0):
    return fluid_in_place(rpt_content, 'water', time)

# map supported queries to functions
SUPPORTED_ANALYSIS = {
    'cell_count'        : cell_count,
    'error_count'       : error_count,
    'finished_normally' : finished_normally,
    'gas_in_place'      : gas_in_place,
    'oil_in_place'      : oil_in_place,
    'processor_count'   : processor_count,
    'run_time'          : run_time,
    'simulation_time'   : simulation_time,
    'warning_count'     : warning_count,
    'water_in_place'    : water_in_place,
}

def analyze(supported_query, url_rpt):
    """
    Returns formatted text containing the analysis result.
    """

    if supported_query in SUPPORTED_ANALYSIS:
        rpt_request = requests.get(url_rpt)
        if rpt_request.ok:
            return SUPPORTED_ANALYSIS[supported_query](rpt_request.content)
        else:
            bail_out_result = 'Can\'t access ' + url_rpt +', trying ' + supported_query + '.'
    else:
        bail_out_result = 'Analysis ' + supported_query + ' not supported, trying ' + url_rpt + '.'
 
    return bail_out_result
