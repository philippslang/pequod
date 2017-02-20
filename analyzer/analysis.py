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

    return 'The run finshed abnormally.'



# map supported queries to functions
SUPPORTED_ANALYSIS = {'error_count':error_count, 'warning_count':warning_count, 'finished_normally':finished_normally, 'cell_count':cell_count}


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