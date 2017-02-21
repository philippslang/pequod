import re
import sys

# Analyses the time varying data in a PRT file

class TimeSeries:
    def __init__(self, prt_content):
        self._all_data = self._parse_prt_file(prt_content)
        
    def _parse_prt_file(self, prt_content):
        p = re.compile(r'.+\;.+')
        data = {}
        '''
        LOG            TIME  TSTEP       GOR      WCT      OPR      WPR      GPR      FPR      WIR      GIR  ITER  IMPL 
                          d      d   sm3/sm3  sm3/sm3    sm3/d    sm3/d    sm3/d      bar    sm3/d    sm3/d           % 
         -------------------------------------------------------------------------------------------------------------- 
          Init   ;    1.000  1.000    56.141    0.005  9361.42   50.614   525557  153.002  9703.23   567827    10   100
        '''
        column_spec = {
            'TIME': 2,
            'TSTEP': 3,
            'GOR': 4,
            'WCT': 5,
            'OPR': 6,
            'WPR': 7,
            'GPR': 8,
            'FPR': 9,
            'WIR': 10,
        }
        for key, index in column_spec.iteritems():
            data[key] = []
        for m in p.finditer(prt_content):
            columns = m.group().split()
            for key, index in column_spec.iteritems():
                data[key].append(float(columns[index]))

        print float('N/A')
        return data

    def _convert_to_number(self, s):
        
        try:
            float(s)
            return True
        except ValueError:
            return False
        
def main(fileName):
    series = TimeSeries(open(fileName).read())      ## No data check
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])