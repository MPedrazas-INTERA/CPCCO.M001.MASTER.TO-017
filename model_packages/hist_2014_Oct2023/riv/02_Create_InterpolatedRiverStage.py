"""CREATE Interpolated River Stage
Python version 2
"""

import numpy as np


def distance(x1, y1, x2, y2):
    """Calculates distance between two points (x1,y1) and (x2,y2)

    input
    -----
    x1,y1,x2,y2 - all float variables
    output
    ------
    returns float variable containing the distance
    """
    return ((x1 - x2) ** 2.0 + (y1 - y2) ** 2.0) ** 0.5


class CreateRiverPackage():
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.gauge_data = None
        self.welldict = None
        self.station_points = None
        self.interpfactor = None
        self.stage = None
        self.disdict = None
        self.model_ibound = None
        self.rivlocarr = None
        self.gap_cells = None
        self.friv = None
        self.cnxn = None
        self.dbcursor = None
        self.dictRIVCoverage = None
        self.single_layer = False

    def read_gauge_data(self, infile):
        """Reads and stores the Gauge Information (Location + Stages)
        :param infile: string - name of gauge input file
        :rtype gdata - dictionary-contains all the gauge data
        rec ={order:
                  {'name':gaugename,
                  'x':easting,
                  'y':northing),
                  'mile':mile along river),
                  'stationid':station id
                  'stage':list containing all the stages - in text format}}
        """
        gauge_data = {}
        fin = open(infile, 'r')
        fin.readline()

        for line in fin.readlines():
            vals = line.strip('\n').split('\t')
            rec = {int(vals[0]):
                       {'name': vals[1],
                        'x': float(vals[2]),
                        'y': float(vals[3]),
                        'mile': float(vals[4]),
                        'stationid': int(vals[5]),
                        'stage': vals[6:]}}

            gauge_data.update(rec)
        self.gauge_data = gauge_data

    def read_station_points(self, infile):
        """ Reads the file containing the interpolation points along the river
        :param infile: string - name of input file containing the interpolation points
        :rtype : object: dictionary containing the interpolation point info
        {stationid : {'x':easting, 'y' : northing, 'id2': alternate id}}
        """
        station_points = {}
        temp = {}
        fin = open(infile, 'r')
        fin.readline()  # Header
        for line in fin.readlines():
            vals = line.strip('\n').split('\t')
            temp.update({int(vals[0]): {
                'x': float(vals[1]),
                'y': float(vals[2]),
                'id2': int(vals[3])}})

        id = 0
        # Sort the temporary dictionary in case the original
        # input is unsorted
        for p in sorted(temp.keys()):
            rec = {p:
                       {'id': id,
                        'x': temp[p]['x'],
                        'y': temp[p]['y'],
                        'id2': temp[p]['id2']
                       }}
            id += 1
            station_points.update(rec)
        self.station_points = station_points

    def calculate_interpolation_factors(self):
        """ Calculates Interpolation Factors for each interpolation point as
        a function of all the gauges
        input
        -----
        gdata - dictionary - gauge data info
        station_points - dictionary - interpolation point info
        output
        ------
        2D numpy double array of interpolation factors
        (ngauge,npts) where,
        ngauge - number of river gauges
        npts   - number of interpolation station_points
        """
        # List of all Gauge IDs -upstream to downstream in ascending order
        gorder = []
        # List of all Gauge Station IDS  -upstream to downstream in ascending order
        gstnid = []
        for g in sorted(self.gauge_data.keys()):
            gorder.append(g)
            gstnid.append(self.gauge_data[g]['stationid'])

        # Calculate the distances between the gages
        ngauge = len(self.gauge_data.keys())
        gaugedist = np.zeros((ngauge - 1), dtype='double')
        for i in range(ngauge - 1):
            start_stnid = gstnid[i]
            end_stnid = gstnid[i + 1]
            flag = True
            for stnid in sorted(self.station_points.keys()):
                if start_stnid <= stnid <= end_stnid:
                    if flag:
                        x1, y1 = self.station_points[stnid]['x'], self.station_points[stnid]['y']
                        flag = False

                    x2, y2 = self.station_points[stnid]['x'], self.station_points[stnid]['y']
                    gaugedist[i] += distance(x1, y1, x2, y2)
                    #update x1,y1
                    x1, y1 = x2, y2

        #Calculate the interpolation factors
        npts = len(self.station_points.keys())
        interpfactor = np.zeros((ngauge, npts), dtype='double')
        ptid = 0

        for stnid in sorted(self.station_points.keys()):

            #Identify upstream and downstream gauges for each point
            if stnid < gstnid[0]:
                #Upstream of the first gauge
                g_upstream = -1
                g_downstream = 0
            elif stnid >= gstnid[ngauge - 1]:
                #downstream of the last gauge
                g_upstream = ngauge - 1
                g_downstream = -1
            else:
                #In between two gauges
                for i in range(ngauge - 1):
                    if gstnid[i] <= stnid < gstnid[i + 1]:
                        g_upstream = i
                        g_downstream = i + 1
                        break

            #Initialize variables for calculating distance
            #to the gauge from upstream
            d_upstream = 0.0
            d_dnstream = 0.0
            x1 = 0.0
            y1 = 0.0
            x2 = 0.0
            y2 = 0.0

            if g_upstream >= 0 and g_downstream >= 0:
                #We are in-between two gauges
                #Initialize at the start of the gauge
                x1, y1 = self.station_points[gstnid[g_upstream]]['x'], self.station_points[gstnid[g_upstream]]['y']
                for stnid2 in sorted(self.station_points.keys()):
                    if gstnid[g_upstream] <= stnid2 <= stnid:
                        x2, y2 = self.station_points[stnid2]['x'], self.station_points[stnid2]['y']
                        d_upstream += distance(x1, y1, x2, y2)
                        x1, y1 = x2, y2
                    if stnid2 > stnid:
                        #we have crossed the current point
                        break
                d_dnstream = gaugedist[g_upstream] - d_upstream
                #Update Interpolation factors
                # if gaugedist[g_upstream] < 0.01:
                # print g_upstream,ptid,d_dnstream,gaugedist[g_upstream]
                interpfactor[g_upstream, ptid] = d_dnstream / gaugedist[g_upstream]
                interpfactor[g_downstream, ptid] = d_upstream / gaugedist[g_upstream]

            elif g_upstream >= 0 and g_downstream < 0:
                #We are downstream of the last gauge
                gaugedistprev = gaugedist[g_upstream - 1]  #earlier gauge distance
                x1, y1 = self.station_points[gstnid[g_upstream]]['x'], self.station_points[gstnid[g_upstream]]['y']
                for stnid2 in sorted(self.station_points.keys()):
                    if gstnid[g_upstream] <= stnid2 <= stnid:
                        x2, y2 = self.station_points[stnid2]['x'], self.station_points[stnid2]['y']
                        d_upstream += distance(x1, y1, x2, y2)
                        x1, y1 = x2, y2
                    if stnid2 > stnid:
                        #we have crossed the current point
                        break
                #Update interpolation factors
                interpfactor[g_upstream, ptid] = (gaugedistprev + d_upstream) / gaugedistprev
                interpfactor[g_upstream - 1, ptid] = -d_upstream / gaugedistprev

            elif g_upstream < 0 and g_downstream >= 0:
                #We are upstream of the first gauge
                gaugedistnext = gaugedist[g_downstream]
                startstn = sorted(point.keys())[0]
                x1, y1 = self.station_points[startstn]['x'], self.station_points[startstn]['y']
                for stnid2 in sorted(self.station_points.keys()):
                    if stnid <= stnid2 <= gstnid[g_downstream]:
                        x2, y2 = self.station_points[stnid2]['x'], self.station_points[stnid2]['y']
                        d_dnstream += distance(x1, y1, x2, y2)
                        x1, y1 = x2, y2
                    if stnid2 > gstnid[g_downstream]:
                        #we have crossed the downstream gauge
                        break
                #Update interpolation factors
                interpfactor[g_downstream, ptid] = (gaugedistnext + d_dnstream) / gaugedistnext
                interpfactor[g_downstream + 1, ptid] = -d_dnstream / gaugedistnext

                #         if g_upstream >=0 and g_downstream >= 0 :
                #             print stnid, gstnid[g_upstream], gstnid[g_downstream],gaugedist[g_upstream], \
                #                 [interpfactor[x,ptid] for x in range(ngauge)]
                #         else:
                #             print stnid, g_upstream, g_downstream,[interpfactor[x,ptid] for x in range(ngauge)]

            ptid += 1
        self.interpfactor = interpfactor

    def calculate_stage(self):
        """ Calculates the interpolated river stage
        self.station_points      - dictionary - contains info for npts interpolation points
        gdata       - dictionary - contains info for ngauge river gauges
        output
        stage - 2d numpy double array (ntimes,npts) - interpolated river stage
        computed as dot product of interpfactor with measured gauge stages
        """
        # Get the dimensions for the profile array
        ntimes = len(self.gauge_data[self.gauge_data.keys()[0]]['stage'])
        npts = len(self.station_points.keys())
        stage = np.zeros((ntimes, npts), dtype='double')

        # Dictionary to hold the mapping between station name and station id
        for stnid in sorted(self.station_points.keys()):
            ptid = self.station_points[stnid]['id']
            for t in range(ntimes):
                #Get the stage vector at gauges
                stage_g = [float(self.gauge_data[x]['stage'][t]) for x in sorted(self.gauge_data.keys())]
                #Get the interpolation factors
                factor = self.interpfactor[:, ptid]
                #Calculate the stage at the current location
                stage[t, ptid] = np.dot(stage_g, factor)
        self.stage = stage

    def write_stage(self, outfile):
        """
        writes the inteprolated river stage to ASCII file

        input
        -----
        outfile - string - name of the output file
        stage - 2d numpy double array (ntimes,npts) - interpolated river stage
        station_points - dictionary - interpolation point info for npts station_points
        """
        ntimes = self.stage.shape[0]
        fout = open(outfile, 'w')
        # Header String
        outstr = '{:>10}'.format('stationid') + \
                 '{:>16}'.format('Easting(m)') + \
                 '{:>16}'.format('Northing(m)')
        for i in range(ntimes):
            outstr += '{:>10}'.format('stage_' + str(i + 1))
        fout.write(outstr + '\n')

        ptid = 0
        for stnid in sorted(self.station_points.keys()):
            outstr = '{:>10}'.format(stnid) + \
                     '{0:16.4f}'.format(self.station_points[stnid]['x']) + \
                     '{0:16.4f}'.format(self.station_points[stnid]['y'])
            for i in range(ntimes):
                outstr += '{0:10.3f}'.format(self.stage[i, ptid])
            fout.write(outstr + '\n')
            ptid += 1
        fout.close()
        print 'Interpolated river stages are written to: ' + outfile



if __name__ == "__main__":


    #New river package object
    riv = CreateRiverPackage(verbose=True)

    #Read Gauge Data
    #gauge_data_file = 'gaugedata2022_hp.dat'
    gauge_data_file = '01_GaugeData_Oct2023.dat'
    print 'Reading gauge data from ' + gauge_data_file + '\n'
    riv.read_gauge_data(gauge_data_file)

    #Read interpolation station_points along the river
    station_point_file = '02_riverstationpoints.dat'
    print 'Reading river station points for interpolatation from ' + \
          station_point_file + '\n'
    riv.read_station_points(station_point_file)

    #Calculate the interpolation factors
    print 'Calculating Interpolation Factors...\n'
    riv.calculate_interpolation_factors()

    #Calculate the interpolated stage
    print 'Calculating stage at interpolation points...\n'
    riv.calculate_stage()

    #Write output file - FOR QA/QC Purposes
    riv.write_stage('02_InterpolatedRiverStageOct2023.out')
    #write_stage_rounded('InterpolatedRiverStage_FORJIM.out',stage,station_points)
