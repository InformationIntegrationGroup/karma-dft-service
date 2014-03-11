from __future__ import division
from numpy.fft import fft
import web
import csv


#Spit it out as a .csv


urls = (
    '/extract', 'extract'

)
app = web.application(urls, globals())

class extract:
    def GET(self):
        return "extract Acc"

    def POST(self):
        i = web.data()
        infile = open('ExtractinFile.csv', 'w+')#create infile, write (i), close it
        infile.write(i)
        infile.close()
        infile = open('ExtractinFile.csv')
        #infile = open('DataWithDFT.csv')
        #print i
        outfile = open('ExtractedAccDFTData10.csv', 'w+')

        def avg_str(l):
            return str(int(round((sum(l) / len(l)))))

        tsIdx = -1  # row index of timestamp
        magIdx = -1  # row index of acceleration magnitude
        uid = -1  # row index of unique id added by addDFT.py
        e1Idx = -1  # row index of DFT energy co-efficient at 1Hz
        e2Idx = -1  # row index of DFT energy co-efficient at 2Hz
        e3Idx = -1  # row index of DFT energy co-efficient at 3Hz

        newData = []  # to hold the discretized data

        # Reading the contents of input file and discretizing it on the go:
        with infile:
            contents = csv.reader(infile, delimiter=',')
            first = True
            for row in contents:
                if first:
                    first = False
                    tsIdx = row.index('timestamp')
                    magIdx = row.index('magnitude')
                    uid = row.index('uid')
                    e1Idx = row.index('DFT_E1')
                    e2Idx = row.index('DFT_E2')
                    e3Idx = row.index('DFT_E3')
                else:
                    ruid = int(row[uid])
                    # ruid -> unique identifier for the group of rows over which
                    # a particular set of DFT values was calculated.
                    # The discretization step:
                    if len(newData) <= ruid:
                        newData.append([row])
                    else:
                        newData[ruid].append(row)
                        # this is used to find average timestamp value below
        # Writing the discretized data to file:
        with outfile:
            outfile.write('timestamp,magnitude,DFT_E1,DFT_E2,DFT_E3\n')
            for x in newData:
                ts = avg_str([float(y[tsIdx]) for y in x])
                new_row = ts + ',' + x[0][magIdx] + ',' + x[0][e1Idx] + ',' + x[0][e2Idx] + ',' + x[0][e3Idx] + '\n'
                outfile.write(new_row)

        d = '' #this is return logic
        outfile.close()
        outfile = open('ExtractedAccDFTData10.csv', 'r')
        a = 0
        for curline in outfile:
            d = d+curline

        web.header('Content-Type','text/csv') #this makes browser autodownload
        #outfile.close()
        #infile.close()
        return d


if __name__ == "__main__":
    app.run()
