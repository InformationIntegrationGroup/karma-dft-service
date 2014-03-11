from __future__ import division
from numpy.fft import fft
import web
import csv


#Spit it out as a .csv


urls = (
    '/addDFT', 'addDFT'

)
app = web.application(urls, globals())



class addDFT:
    def POST(self):
        i = web.data()
        infile = open('DFTinFile.csv', 'w+')#create infile, write (i), close it
        infile.write(i)
        infile.close()
        infile = open('DFTinFile.csv')
        outfile = open('DataWithDFT9.csv', 'w+')  # output file (csv)

        nDFTValues = 3

        def getDFT(vals):
            """Returns DFT energy coefficients over a list of observations."""
            dft = fft(vals)
            dft_e = [(x.real ** 2) + (x.imag ** 2) for x in vals]
            # dft_e is a list of DFT energy coefficients at different frequencies
            return dft_e

        def appendToEnd(c, i, j, DFTvals, nDFT, uid):
            """Adds nDFT DFT energy coefficients to every row [from i to (j-1)] of c.

            'c' contains the original contents of the input file without the
            column names.
            DFT energy coefficients at frequencies 1Hz, 2Hz, ... , nDFT Hz are
            added to every row from row numbers 'i' to 'j-1' of 'c'.
            This also adds a unique id 'uid' at the end of each row to identify which
            rows were grouped together to calculate which DFT values.

            """
            for x in range(i, j):
                for y in range(nDFT):
                    c[x].append(str(DFTvals[y]))
                c[x].append(str(uid))

        tsIdx = -1  # row index of timestamp values
        magIdx = -1  # row index of acceleration-magnitude values
        last = None
        lastIdx = None
        c = []  # to hold the data
        cols = []  # to hold column names
        nFields = -1  # to hold the number of columns in the data

        # Reading the input file and updating the variables listed above:
        with infile:
            contents = csv.reader(infile, delimiter=',')
            first = True
            for row in contents:
                if first:
                    cols = row
                    tsIdx = row.index('timestamp')
                    magIdx = row.index('magnitude')
                    nFields = len(row)
                    first = False
                else:
                    c.append(row)

        length = len(c)
        uid = 0  # unique identifier for groups of rows used to calculate DFT

        # Grouping rows by windows of 1s time and calculating DFT values:
        for i in range(length):
            current = float(c[i][tsIdx])
            if last is None:
                lastIdx = i
                last = current
            elif (current - last) > 1.0:
                dft_e = getDFT([float(u[magIdx]) for u in c[lastIdx:i]])
                if (i - lastIdx) >= nDFTValues:
                # the DFT values will not be accurate enough if the number
                # of observations is inadequate
                    appendToEnd(c, lastIdx, i, dft_e, nDFTValues, uid)
                    uid = uid + 1
                lastIdx = i
                last = current

        if lastIdx != length - 1:
            dft_e = getDFT([float(u[magIdx]) for u in c[lastIdx:length]])
            appendToEnd(c, lastIdx, length, dft_e, nDFTValues, uid)
            uid = uid + 1

        # Appending column names for the added DFT energy coefficients
        # at different frequencies:
        for z in range(nDFTValues):
            cols.append("DFT_E%d" % (z + 1))
        cols.append('uid')

        # Saving the data to file:
        with outfile:
            outfile.write(','.join(cols) + '\n')
            for x in c:
                if len(x) > nFields:
                    outfile.write(','.join(x) + '\n')
                d = '' #this is return logic

        outfile.close()
        outfile = open('DataWithDFT9.csv', 'r')
        d = ''
        for curline in outfile:
            d = d+curline

        web.header('Content-Type','text/csv') #this makes browser autodownload
        #outfile.close()
        #infile.close()
        return d


if __name__ == "__main__":
    app.run()
