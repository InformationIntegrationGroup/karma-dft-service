from __future__ import division
from numpy.fft import fft
import web
import csv


#Spit it out as a .csv


urls = (
    '/merge', 'merge'
)
app = web.application(urls, globals())



class merge:
    def GET(self):
        return "merge by nearest "

    def POST(self):

        def notEmpty(x):
            return x != ''

        def empty(x):
            return x == ''

        i = web.data()
        infile = open('inFile.csv', 'w+')#create infile, write (i), close it
        infile.write(i)
        infile.close()
        infile = open('inFile.csv')

        outfile = open('mergeOutfile.csv', 'w+')  # output file (csv)
        threshold = 30  # maximum allowed time-difference for rows r and r* (as described above)

        contents = []  # contents of the input file
        tsIdx = -1  # row index of timestamp
        spdIdx = -1  # row index of GPS speed
        accIdx = -1  # row index of GPS accuracy
        magIdx = -1  # row index of acceleration magnitude
        e1Idx = -1  # row index of DFT energy co-efficient at 1Hz
        e2Idx = -1  # row index of DFT energy co-efficient at 2Hz
        e3Idx = -1  # row index of DFT energy co-efficient at 3Hz

        colnames = 'timestamp,speed,accuracy,acceleration_magnitude,DFT_E1,DFT_E2,DFT_E3\n'

        # Reading the contents of the input file:
        with infile:
            c = csv.reader(infile)
            first = True
            for row in c:
                if first:
                    first = False
                    tsIdx = row.index('timestamp')
                    spdIdx = row.index('speed')
                    accIdx = row.index('accuracy')
                    magIdx = row.index('magnitude')
                    e1Idx = row.index('DFT_E1')
                    e2Idx = row.index('DFT_E2')
                    e3Idx = row.index('DFT_E3')
                else:
                    contents.append(row)
        new_contents = []
        done = False

        # Merging the r and r* type rows (as described above):
        # The two sources are GPS and accelerometer.
        # empty(contents[x][spdIdx]) indicates that the xth row is missing GPS data
        # empty(contents[x][magIdx]) indicates that the xth row is missing Accelerometer data
        for i in range(len(contents)):
            if done:
                done = False
                continue
            currentTs = float(contents[i][tsIdx])
            if notEmpty(contents[i][spdIdx]) and notEmpty(contents[i][magIdx]):
                new_contents.append([contents[i][tsIdx], contents[i][spdIdx], contents[i][accIdx], contents[i][magIdx], contents[i][e1Idx], contents[i][e2Idx], contents[i][e3Idx]])
            elif notEmpty(contents[i][spdIdx]):
                nearest = None
                if i != 0 and empty(contents[i - 1][spdIdx]) and notEmpty(contents[i - 1][magIdx]):
                    nearest = i - 1
                if i != (len(contents) - 1) and empty(contents[i + 1][spdIdx]) and notEmpty(contents[i + 1][magIdx]):
                    if nearest is None or abs(float((contents[i + 1][tsIdx])) - currentTs) <= abs(float(contents[nearest][tsIdx]) - currentTs):
                        nearest = i + 1
                if nearest is not None and abs(float((contents[nearest][tsIdx])) - currentTs) <= threshold:
                    new_row = [contents[i][tsIdx], contents[i][spdIdx], contents[i][accIdx], contents[nearest][magIdx], contents[nearest][e1Idx], contents[nearest][e2Idx], contents[nearest][e3Idx]]
                    if nearest == (i - 1):
                        x = new_contents.pop()
                    elif nearest == (i + 1):
                        done = True
                    new_contents.append(new_row)
                else:
                    new_contents.append([contents[i][tsIdx], contents[i][spdIdx], contents[i][accIdx], contents[i][magIdx], contents[i][e1Idx], contents[i][e2Idx], contents[i][e3Idx]])
            else:
                new_contents.append([contents[i][tsIdx], contents[i][spdIdx], contents[i][accIdx], contents[i][magIdx], contents[i][e1Idx], contents[i][e2Idx], contents[i][e3Idx]])

        # Writing merged data to file:
        with outfile:
            outfile.write(colnames)
            for row in new_contents:
                outfile.write(','.join(row) + '\n')

        outfile.close()
        outfile = open('mergeOutfile.csv')

        d = ''
        for curline in outfile:
            d = d+curline

        web.header('Content-Type','text/csv') #this makes browser autodownload
        #outfile.close()
        #infile.close()
        return d


if __name__ == "__main__":
    app.run()
