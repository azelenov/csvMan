import ast
import glob

__author__ = 'ozelenov'

#!/usr/bin/python2.7

import os
import csv
import sys
import operator
import re
import random
import argparse
import time
import matplotlib.pyplot as plt
from scipy import stats, amin, amax, std, mean, linspace
# from xlsxwriter.workbook import Workbook


#main class for CSV files operations
class CSVMan:
    # noinspection PyArgumentList
    def __init__(self, path, dialect=None):
        self.path = path
        if not dialect:
            self.detect_csv_dialect()
        else:
            self.dialect = dialect
        self.head = self.read_as_dict().fieldnames
        self.data = self.read_as_dict()

    #read CSV file to dictionary
    def read_as_dict(self):
        f = open(self.path)
        r = csv.DictReader(f, dialect=self.dialect)
        self.head = r.fieldnames
        return r

    #write dictionary data to csv file
    def write_dictionary(self, data, out_path, header):
        mode = OSMan.check_path(out_path)
        with open(out_path, mode) as out:
            w = csv.DictWriter(out, fieldnames=header, dialect=self.dialect)
            w.writeheader()
            try:
                w.writerows(data)
            except TypeError:
                sys.exit(
                    'Current CSV dialect incorect for file OR file has data without columns!!!'
                    'Please repeat with other dialect or add columns manually.')
        print "File " + out_path + " has been written,", len(data), ' rows'

    def detect_csv_dialect(self):
        try:
            f = open(self.path, "rb")
        except IOError:
            sys.exit('No such file or directory:' + self.path)
        d = csv.Sniffer().sniff(f.read(1024))
        d.lineterminator = "\n"
        csv.register_dialect('auto', d)
        self.dialect = 'auto'
        print "Detected dialect:"
        print "delimiter=", csv.get_dialect(self.dialect).delimiter
        print "quote char=", csv.get_dialect(self.dialect).quotechar
        print "quoting=", csv.get_dialect(self.dialect).quoting
        print "line terminator=", csv.get_dialect(self.dialect)\
            .lineterminator.replace('\n', '\\n').replace('\r', "\\r")
        print "escape char=", csv.get_dialect(self.dialect).escapechar
        print "----------------------------"


    # noinspection PyArgumentList
    def sniff(self):  #search for CSV file dialect
        print "List of registered CSV dialects:"

        csv.register_dialect('cs', delimiter=',', quotechar="'", quoting=csv.QUOTE_ALL, lineterminator='\n')
        csv.register_dialect('cd', delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
        csv.register_dialect('sd', delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
        csv.register_dialect('ss', delimiter=';', quotechar="'", quoting=csv.QUOTE_ALL, lineterminator='\n')
        csv.register_dialect('dnb', delimiter='|', quotechar="'", quoting=csv.QUOTE_ALL, lineterminator='\n')
        csv.register_dialect('ts', delimiter='\t', quotechar="'", quoting=csv.QUOTE_ALL, lineterminator='\n')
        csv.register_dialect('td', delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')

        print
        print "Quoting ALL, lineterminator=\\n"
        print " cs - single qoute coma (delimiter=,  quotechar=')"
        print ' cd - double qoute coma (delimiter=,  quotechar=")'
        print " ss - single qoute semicolumn (delimiter=; quotechar=')"
        print ' sd - double qoute semicolumn (delimiter=; quotechar=" )'
        print " dnb - special dialect for DNB project(delimiter='|',quotechar=' quoting All,lineterminator=\\n)"
        print " ts - tab separeted single quoted(delimiter='TAB',quotechar=' quoting All,lineterminator=\\n)"
        print " td - tab separeted double quoted(delimiter='TAB',quotechar=' quoting All,lineterminator=\\n)"
        #print " m - specify dialect manually"
        ans = raw_input("Please choose CSV file dialect or create manually...")
        if ans == 'a':
            self.dialect = 'a'
        elif ans == 'cs':
            self.dialect = 'cs'
        elif ans == 'cd':
            self.dialect = 'cd'
        elif ans == 'ss':
            self.dialect = 'ss'
        elif ans == 'sd':
            self.dialect = 'sd'
        elif ans == 'sd':
            self.dialect = 'sd'
        elif ans == 'dnb':
            self.dialect = 'dnb'
        elif ans == 'ts':
            self.dialect = 'ts'
        elif ans == 'td':
            self.dialect = 'td'
        else:
            print "!!UNREGISTERED dialect!!!!"
            self.sniff()
        print

    def print_header(self):
        self.read_as_dict()
        print self.head
        print "Number of columns:", len(self.head)

    def get_column(self, column):  #get not null values from CSV column as a list
        res = []
        Dict = self.read_as_dict()
        for row in Dict:
            if row[column] != "":
                res.append(row[column])
        return res

    def print_size(self):
        r = self.read_as_dict()
        print "File:", self.path, ':', r.line_num, 'rows'

    #write List to file with header
    def write_list(self, List, header, path='out.csv'):
        mode = OSMan.check_path(path)
        with open(path, mode) as out:
            w = csv.writer(out, dialect=self.dialect)
            w.writerow(header)
            w.writerows(List)
        print "File " + path + " has been written,", len(List), ' rows.'


class SmartMan(CSVMan):
    def __init__(self, path):
        CSVMan.__init__(self, path)

    @staticmethod
    def sort_dictionary(dictionary, sort_index, reverse):
        converted_dict = SmartMan.convert_to_natural_types(dictionary)
        sorted_list = sorted(converted_dict.iteritems(), key=operator.itemgetter(sort_index), reverse=reverse)
        return sorted_list

    @staticmethod
    def convert_to_natural_types(dictionary):
        converted = {}
        for key, value in dictionary.iteritems():
            new_key = SmartMan.convert_type(key)
            new_value = SmartMan.convert_type(value)
            converted[new_key] = new_value
        return converted

    @staticmethod
    def convert_type(value):
        try:
            value = ast.literal_eval(value)
        except ValueError:
            pass
        return value

    @staticmethod
    def randomize(list_data, num=None):
        data = list_data
        random.shuffle(data)
        if num: data = data[:num]
        return data

    def column_frequency(self, column, limit=False):  #statistics for column values
        rows = self.get_column(column)
        results = {}
        for row in rows:
            if results.has_key(row) and row != '':
                results[row] += 1
            else:
                results[row] = 1
        return results

    #statistics for column values
    def average_stats(self, csv_column, csv_avg_column):
        stats = {}
        for row in self.read_as_dict():
            row_key = row[csv_column]
            row_value = row[csv_avg_column]
            if stats.has_key(row_key) and row != '':
                stats[row_key].append(float(row_value))
            else:
                stats[row_key] = [float(row_value)]
        avg_stats = {}
        for key in stats:
            list_of_values = stats[key]
            if len(list_of_values) > 0:
                avg_stats[key] = float(sum(list_of_values) / len(list_of_values))
        return avg_stats

    #count Top Level Domain for domains in CSV column
    def count_top_level_domains(self, column):
        domains = self.get_column(column)
        sufixes = {}
        for domain in domains:
            domain = domain.strip().lower()
            domain = re.sub("^https?://", "", domain)
            domain = domain.replace("\\", "/")
            domain = re.sub("/.*$", "", domain)
            domain = re.sub("[.;>,]$", "", domain)
            if domain.find('.') != -1 and domain != '':
                parts = domain.split('.')
                main_part = parts[-1]
                if re.match('^[0-9]+$', main_part): main_part = 'IP address'
                if sufixes.has_key(main_part):
                    sufixes[main_part] += 1
                else:
                    sufixes[main_part] = 1
        head = ['Suffix', 'Count']
        data = self.sort_dictionary(sufixes, 0, False)
        out = OSMan.new_filename(self.path, 'TLD')
        self.write_list(data, head, out)
        return data

    def count_unique(self, TarCol):
        print self.path
        data = self.get_column(TarCol)
        udata = set(data)
        print "Count all values:", len(data)
        print "Count unique values:", len(udata)

    def get_clusters(self, input_list, num_of_clusters):
        input_list = [int(i) for i in input_list]
        input_list.sort()
        heap_list = []  # A *heap* would be faster
        for i in range(1, len(input_list)):
            heap_list.append((int(input_list[i]) - int(input_list[i - 1]), i))
        heap_list.sort()
        # b now is [... (20, 6), (20, 9), (57, 3), (120, 7)]
        # and the last ones are the best split points.
        heap_list = map(lambda p: p[1], heap_list[-num_of_clusters:])
        heap_list.sort()
        # b now is: [3, 7]
        heap_list.insert(0, 0)
        heap_list.append(len(input_list) + 1)
        out = []
        for i in range(1, len(heap_list)):
            out.append(input_list[heap_list[i - 1]:heap_list[i]])
        return out


class RangeMan(CSVMan):
    def __init__(self, path):
        CSVMan.__init__(self, path)

    def rangeStat(self, column):  #print main file ranges in CSV column
        print self.path
        ranges = self.get_column(column)
        ranges = sorted(ranges)
        print "all scores in file:", len(ranges)
        print "Max score:", ranges[-1]
        print "Min score:", ranges[0]
        print "Main range:", float(ranges[-1]) - float(ranges[0])

    #print ranges in CSV column according to values
    def rangesStat(self, column, values):
        ranges = self.get_column(column)
        ranges = [SmartMan.convert_type(r) for r in ranges]
        values = [SmartMan.convert_type(v) for v in values]
        #Calculating min, max
        min_value = min(ranges)
        max_value = max(ranges)
        if min_value < values[0]:
            values.insert(0, min_value)
        if max_value > values[-1]:
            values.append(max_value)
        print "Ranges:", values
        print "Min:", min_value
        print "Max:", max_value
        print "Avg:", sum(ranges) / float(len(ranges))
        results = []

        while len(values) != 1:
            start = values[0]
            end = values[1]
            s = 0
            for r in ranges:
                if start < r <= end:
                    s += 1
            results.append(["range " + str(start) + "-" + str(end), s])
            values.pop(0)
        return results

    def generate_statistics(self, column):
        results = []
        data = self.get_column(column)
        data = [float(r) for r in data]
        results.append(["Count of all values", len(data)])
        results.append(["Min", amin(data)])
        results.append(["Max", amax(data)])
        results.append(["Mean(Average)", mean(data)])
        results.append(["Standard deviation (sigma)", std(data)])
        return results

    def rangesCut(self, column, ranges):
        i = 1
        starts = []
        ends = []
        for r in ranges:
            if i in range(1, 1000, 2):
                starts.append(r)
            else:
                ends.append(r)
            i += 1
        print starts
        print ends


    def OneRange(self, column, Rang):
        print Rang
        data = self.read_as_dict()
        res = []
        for row in data:
            try:
                cell = eval(row[column])
            except ValueError:
                pass
            else:
                if float(row[column]) == Rang:
                    #print row[column]
                    res.append(row)
                    #break
        print len(res)


#All things with folder and files
class OSMan:
    def __init__(self):
        pass

    @staticmethod
    def list_files(folder_name):
        files = []
        for p in sorted(os.listdir(folder_name)):
            files.append(p)
        return files

    @staticmethod
    def create_folder(folder_name):
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            print "Folder " + folder_name + " has been created."
        else:
            print "Folder " + folder_name + " exists."
            print "Writing to", folder_name

    @staticmethod
    def get_files_with_extension(folder_name, extension):
        return glob.glob(os.path.join(folder_name, extension))

    @staticmethod
    def get_csv_files(folder_name):
        return OSMan.get_files_with_extension(folder_name, '*.csv')

    @staticmethod
    def delete_file_if_exists(in_file):
        if os.path.exists(in_file):
            os.remove(in_file)
            print "Old file", in_file, "deleted!"
            print "_____________________________"

    @staticmethod
    def new_filename(path,  suffix):
        parts = path.split('.')
        name = parts[0]
        ext = parts[-1]
        new_name = name + '%' + str(suffix) + '.' + ext
        return new_name

    @staticmethod
    def check_path(path):
        if os.path.exists(path):
            print "Please write 'w' for writing, 'a' for 'appending' or 's' for stoping program"
            ans = raw_input('File ' + path + ' exist! Rewrite(w), append(a) or stop program (s)?')
            if ans == 'w':
                return 'w'
            elif ans == 'a':
                return 'a'
            elif ans == 's':
                sys.exit()
            else:
                print "Please write 'w' for writing, 'a' for 'appending' or 's' for stoping program"
                OSMan.check_path(path)
        else:
            return 'w'

    @staticmethod
    def process_each_file(path, function, ext='*.csv'):
        print "Processing the folder:", path
        files = OSMan.get_files_with_extension(path, ext)
        print files
        for f in files:
            global_args.csv_file = f
            function()


class DigMan(CSVMan):  #Split files into parts and more
    def __init__(self, path, dialect=None):
        CSVMan.__init__(self, path, dialect)
        self.ans = ""
        self.status = ""
        self.clean = []

    def ReMatched(self, TarCol, regEx, cs=False, f=False):  #filter values in target column using regular expressions
        data = self.read_as_dict()
        if not cs:
            reg = re.compile(regEx, re.I)
        else:
            reg = regEx
        res = []
        for row in data:
            if not f:
                if re.search(reg, row[TarCol]): res.append(row)
            elif f:
                if re.match(reg, row[TarCol]): res.append(row)
        oPath = OSMan.new_filename(self.path, 're_matched')
        self.write_dictionary(res, oPath, data.fieldnames)

    def inList(self, TarCol, List, limit=None, sufix='matched'):  #filter values in target column matched in List
        print 'max match=', limit
        #sys.exit()
        data = self.read_as_dict()
        res = []
        if limit is not None:
            maxcount = int(limit)
            columns = set(self.get_column(TarCol))
            stats = {}
            for row in data:
                value = row[TarCol].lower()
                if value in List:
                    if stats.has_key(value):
                        stats[value] += 1
                    else:
                        stats[value] = 1
                    if stats[value] <= maxcount:
                        res.append(row)
        elif limit is None:
            for row in data:
                value = row[TarCol].lower()
                if value in List:
                    res.append(row)
        if limit is None:
            oPath = OSMan.new_filename(self.path, sufix)
        else:
            oPath = OSMan.new_filename(self.path, sufix + '_limit=' + str(limit))
        self.write_dictionary(res, oPath, data.fieldnames)

    def ReList(self, TarCol, List, sufix='REList'):  #filter values in target column matched in regex List
        data = self.read_as_dict()
        missed = []
        hit = []
        i = 0
        print time.asctime()
        print "Processing rows.."
        start = time.clock()
        for row in data:
            cell = row[TarCol]
            flag = True
            for l in List:
                reg = re.compile(l, re.I)
                if re.search(reg, cell):
                    hit.append(row)
                    flag = False
                    break
            if flag: missed.append(row)
            i += 1

        mPath = OSMan.new_filename(self.path, sufix + "_NOT_matched")
        hPath = OSMan.new_filename(self.path, sufix + "_matched")

        self.write_dictionary(missed, mPath, data.fieldnames)
        self.write_dictionary(hit, hPath, data.fieldnames)
        finish = time.clock() - start
        print "total=", i
        print "Processed time in seconds:", finish
        print "Speed:", int(round(i / round(finish))), "rows per second"


    def BlackList(self, TarCol, BlackList, sufix='BlackList'):  #filter words in target column matched in Black List
        with open(BlackList) as f:
            List = [line.strip().lower() for line in f]
        data = self.read_as_dict()
        missed = []
        hit = []
        i = 0
        print time.asctime()
        print "Processing rows.."
        start = time.clock()
        for row in data:
            flag = True
            words = row[TarCol].lower().split(" ")
            #print words
            for word in words:
                if word in List:
                    #print i,"hit=",word
                    hit.append(row)
                    flag = False
                    break
            if flag:
                #print i,"missed"
                missed.append(row)

            i += 1

        mPath = OSMan.new_filename(self.path, sufix + "_NOT_matched")
        hPath = OSMan.new_filename(self.path, sufix + "_matched")

        self.write_dictionary(missed, mPath, data.fieldnames)
        self.write_dictionary(hit, hPath, data.fieldnames)
        finish = time.clock() - start
        print "total=", i
        print "Processed time in seconds:", finish
        print "Speed:", int(round(i / round(finish))), "rows per second"


    def BlackList2(self, TarCol, BlackList, wordsmatch=False,
                   sufix='BlackList'):  #filter words in target column matched in Black List
        with open(BlackList) as f:
            List = [line.strip().lower() for line in f]
        data = self.read_as_dict()
        missed = []
        hit = []
        i = 0
        print time.asctime()
        print "Processing rows.."
        start = time.clock()
        for row in data:
            flag = True
            if wordsmatch:
                #rint 'wordsmatch'
                words = row[TarCol].lower().split(" ")
                #print words
                for word in words:
                    if word in List:
                        #print i,"hit=",word
                        hit.append(row)
                        flag = False
                        break
                if flag:
                    #print i,"missed"
                    missed.append(row)
            else:
                #print 'else function'
                line = row[TarCol].lower()
                if line in List:
                    hit.append(row)
                else:
                    missed.append(row)
            i += 1

        mPath = OSMan.new_filename(self.path, sufix + "_NOT_matched")
        hPath = OSMan.new_filename(self.path, sufix + "_matched")

        self.write_dictionary(missed, mPath, data.fieldnames)
        self.write_dictionary(hit, hPath, data.fieldnames)
        finish = time.clock() - start
        print "total=", i
        print "Processed time in seconds:", finish
        print "Speed:", int(round(i / round(finish))), "rows per second"


    def NotiIList(self, TarCol, List):  #filter values in target column matched in List
        data = self.read_as_dict()
        res = []
        for row in data:
            value = row[TarCol].lower()
            if value not in List:
                res.append(row)
        oPath = OSMan.new_filename(self.path, 'NOT_matched')
        self.write_dictionary(res, oPath, data.fieldnames)

    def inFile(self, TarCol, FileName, limit):  #filter values in target column matched in File
        with open(FileName) as f:
            List = [line.strip().lower() for line in f]
        self.inList(TarCol, List, limit=limit)

    def ReFile(self, TarCol, FileName):  #filter values in target column matched in File
        with open(FileName) as f:
            List = [line.strip().lower() for line in f]
        self.ReList(TarCol, List)

    def NotInFile(self, TarCol, FileName, limit=None):  #filter values in target column matched in File
        with open(FileName) as f:
            List = [line.strip().lower() for line in f]
        self.NotiIList(TarCol, List)


    def inCSV(self, TarCol, CSVName, CSVcolumn, limit):
        c = CSVMan(CSVName)
        data = set(c.get_column(CSVcolumn))
        self.inList(TarCol, data, limit)

    def FilterFile(self, colValPairs):  #filter file according multiple colums values
        print time.asctime()
        print "Processing rows.."
        start = time.clock()
        data = self.read_as_dict()
        header = data.fieldnames
        path = OSMan.new_filename(self.path, 'filtered')
        for key in colValPairs:
            if key not in header:
                sys.exit(
                    "Input file don't have column: " + key + '\nAvailable column names in CSV header:' + str(header))
        newdata = []
        for row in data:
            flag = False
            flags = []
            for key in colValPairs:
                if row.has_key(key) and colValPairs[key].lower() == row[key].lower():
                    flag = True
                    flags.append(flag)
                else:
                    flag = False
                    flags.append(flag)
            if False not in flags:
                newdata.append(row)
        self.write_dictionary(newdata, path, header)

        finish = time.clock() - start
        print "Processed time in seconds:", finish

    def FilterFile2(self, colValPairs, oper):  #filter file according multiple colums values
        data = self.read_as_dict()
        header = data.fieldnames
        path = OSMan.new_filename(self.path, 'filtered')


        def makeEx(value, colValPairs, oper):
            i = 0
            expr = ""
            for key in colValPairs:
                if key not in header:
                    sys.exit("Input file don't have column: " + key + '\nAvailable column names in CSV header:' + str(
                        header))
                else:
                    if i == 0:
                        expr = colValPairs[key].lower() == value[key]
                    else:
                        if oper[i - 1] == 'and':
                            #print "and"
                            expr = expr and colValPairs[key].lower() == value[key]
                        elif oper[i - 1] == 'or':
                            #print "or"
                            expr = expr or colValPairs[key].lower() == value[key]
                i += 1
            return expr

        newdata = []
        for row in data:
            flag = False
            flags = []
            for key in colValPairs:
                if row.has_key(key) and makeEx(row, colValPairs, oper):
                    flag = True
                    flags.append(flag)
                else:
                    flag = False
                    flags.append(flag)
            if False not in flags:
                newdata.append(row)
        self.write_dictionary(newdata, path, header)


    def split2Files(self, TarCol, outFolder, empty):  #split File into parts according to values in column
        total = 0
        data = self.read_as_dict()
        #print data.fieldnames
        OSMan.create_folder(outFolder)
        os.chdir(outFolder)
        stat = {}
        results = {}
        for row in data:
            if row[TarCol] == "":
                if empty:
                    key = "EMPTY"
                else:
                    key = None
            else:
                key = row[TarCol]
            if key is not None:
                if key in stat:
                    stat[key] += 1
                    results[key].append(row)
                else:
                    stat[key] = 1
                    results[key] = []
            total += 1
        print "File has been splitted successfully into parts:"
        print "Total rows count:", total
        print stat
        return results

    def get_random(self, rand):  #writing random set
        Dict = self.read_as_dict()
        head = Dict.fieldnames
        data = [row for row in Dict]
        random.shuffle(data)
        data = data[:rand]
        path = OSMan.new_filename(self.path, 'random' + str(rand))
        with open(path, 'a') as out:
            w = csv.DictWriter(out, fieldnames=head, dialect=self.dialect)
            w.writeheader()
            w.writerows(data)
        print "Random set has been writed to file:", path

    def CleanRow(self, row):
        for key in row:
            if key in self.clean:
                row[key] = ""
        self.status = row['Status Description']
        return row

#smart merge many file into one
class MergeMan(CSVMan):
    columns = 0

    def __init__(self, files):
        CSVMan.__init__(self, files[0])
        self.files = files

    #merge CSV files
    def merge(self, out_path):
        OSMan.delete_file_if_exists(out_path)
        print "Merging csv files..."
        write_header = True
        with open(out_path, 'a') as out:
            for csv_file in self.files:
                c = CSVMan(csv_file, self.dialect)
                data = c.read_as_dict()
                head = data.fieldnames
                # data = [d for d in data]
                w = csv.DictWriter(out, fieldnames=head, dialect=self.dialect)
                if write_header:
                    w.writeheader()
                    write_header = False
                w.writerows(data)
                print csv_file, 'done'
        print "All files has been merged successfully to file:", out_path

    def validate(self):
        self.check_header(self.head)
        self.check_files(self.files, self.head)

    def check_header(self, header):
        for h in header:
            if re.match('^\s*$', h):
                print 'Empty column detected in position :', header.index(h) + 1, "value:'", h, "'"
                self.ask()

    def ask(self):
            ans = raw_input("Do you wanna proceed? (y,n)")
            if ans == 'n':
                sys.exit('Please fix columns')
            elif ans == 'y':
                pass
            else:
                print "answers only yes or no"
                self.ask()

    #validating CSV file headers
    def check_files(self, files, primary_header):
        s = []
        fields = []
        print "Validating CSV file headers..."
        for f in files:
            c = CSVMan(f, self.dialect)
            data = c.read_as_dict()
            file_head = data.fieldnames
            col_num = len(file_head)
            print f, col_num
            if col_num != len(primary_header):
                s.append(f)
            if file_head != primary_header:
                fields.append(f)
                for h in file_head:
                    if h not in primary_header:
                        print 'Wrong column!:', h
                print
        if s:
            print 'Columns sum does not match in files!:', s
            sys.exit()
        elif fields:
            print 'Not matched fieldnames in files!:', fields
            sys.exit()
        else:
            print 'All columns and fields matched'
            print


class MarkMan(CSVMan):
    def __init__(self, path, people):
        CSVMan.__init__(self, path)
        self.out_path = OSMan.new_filename(self.path, 'marked')
        self.path = path
        self.people = [p for p in people]
        self.data = self.read_as_dict()
        self.header = self.data.fieldnames

    def print_size(self):
        counter = 0
        for d in self.data:
            counter += 1
        return counter

    def divide(self):  #divide num of rows for people
        num = self.print_size()
        n = len(self.people)
        part = num / n
        rest = num - part * n
        parts = {}
        for p in self.people:
            parts[p] = part
        while rest != 0:
            random.shuffle(self.people)
            dice = self.people[0]
            parts[dice] += 1
            rest -= 1
        print "Count of rows:", num
        print "Num of persons:", n
        for p in parts:
            print p, ':', parts[p]
        return parts

    def markFile(self):  #mark file with person names
        data = self.read_as_dict()
        self.header.insert(0, 'whose')
        parts = self.divide()
        temp_data = [d for d in data]
        with open(self.out_path, 'w') as out:
            w = csv.DictWriter(out, fieldnames=self.header, dialect=self.dialect)
            w.writeheader()
            for key in sorted(parts.keys()):
                for i in range(1, int(parts[key]) + 1):
                    row = temp_data.pop(0)
                    row['whose'] = key
                    w.writerow(row)
        print "Saved to file:", self.out_path


class ExcelMan:
    def __init__(self):
        pass

    def import_to_excel(self, input_folder):
        pass
        # for csvfile in glob.glob(os.path.join(input_folder, '*.csv')):
        #     workbook = Workbook(csvfile + '.xlsx')
        #     worksheet = workbook.add_worksheet()
        #     with open(csvfile, 'rb') as f:
        #         reader = csv.reader(f)
        #         for r, row in enumerate(reader):
        #             for c, col in enumerate(row):
        #                 worksheet.write(r, c, col)
        #     workbook.close()


class PaintMan:
    def __init__(self):
        pass

    title = "Default title"
    line_width = 2

    def plot_graph(self, x_axis, y_axis):
        plt.plot(x_axis, y_axis, linewidth=self.line_width)
        plt.title(self.title)
        plt.show()

    @staticmethod
    def convert_to_axises(dict_data):
        y_axis = []
        x_axis = []
        for pair in dict_data:
            x_axis.append(pair[0])
            y_axis.append(pair[1])
        print x_axis
        print y_axis
        return x_axis, y_axis

    #Mean it's average, std - is standard deviation(sigma)
    def plot_stats(self, mean, std):
        x = linspace(-3 * std, 3 * std, 50)
        # SF at these values
        y = stats.norm.sf(x, loc=mean, scale=std)
        plt.plot(x, y, color="black")
        plt.xlabel("Variate")
        plt.ylabel("Probability")
        plt.title("SF for Gaussian of mean = {0} & std. deviation = {1}".format(
            mean, std))
        plt.draw()


def Scores(inFile, TarCol, scores=False):  # count ranges of scores in CSV file
    r = RangeMan(inFile)
    r.rangeStat(TarCol)
    if not scores:
        r.rangesStat(TarCol, range(650, 1050, 50))


def Frequency(path, TarCol, sort_by_keys, reverse, top):  # count Domain Frequancy in file
    if os.path.isdir(path):
        print "Processing a folder"
        files = OSMan.list_files(path)
        print files
        for f in files:
            Frequency(path + '/' + f, TarCol, sort_by_keys, reverse, top)
    else:
        c = SmartMan(path)
        print "\nFrequency on column"
        head = [TarCol, 'Count']
        sort_by_keys = get_default_sorting(sort_by_keys)
        data = c.sort_dictionary(c.column_frequency(TarCol), sort_by_keys, reverse)
        out = OSMan.new_filename(path, 'Frequency' + '%' + TarCol)
        if top:
            data = data[:top]
        c.write_list(data, head, out)


def countCells(path, target_column):  #Count not empty cells in target column of CSV file
    files = path.list_files(path)
    for f in files:
        c = CSVMan(f)
        data = c.get_column(target_column)
        #print data
        print f, ':', len(data)


def Split(in_file, target_column, parts_folder, empty_cells):  #Split files into parts
    start = time.clock()
    e = DigMan(in_file)
    if not parts_folder:
        parts_folder = "parts"
    if not empty_cells:
        empty_cells = False
    parts = e.split2Files(target_column, parts_folder, empty_cells)
    for part in parts.keys():
        e.write_dictionary(parts[part], part + ".csv", e.head)
    finish = time.clock() - start
    print "Processed time in seconds:", finish



def deleteColumns(path, columns):
    c = CSVMan(path)
    data = c.read_as_dict()
    head = data.fieldnames
    edata = []
    for d in data:
        for col in columns:
            d.pop(col)
        edata.append(d)
    h2 = head
    for col in columns:
        h2.remove(col)
    print "new header\n", h2
    oPath = OSMan.new_filename(path, 'deleted_columns')
    c.write_dictionary(edata, oPath, h2)


def addColumns(path, column):
    c = CSVMan(path)
    data = c.read_as_dict()
    head = data.fieldnames
    edata = []
    for d in data:
        d.insert(0, column)
        edata.append(d)
    h2 = head
    h2.insert(0, column)
    print "new header\n", h2
    oPath = OSMan.new_filename(path, 'deleted_columns')
    c.write_dictionary(edata, oPath, h2)


def Rand(inFile, rand):  #create random set
    e = DigMan(inFile)
    print "Generating random..."
    e.get_random(rand)


def countrowsD(path):  #rewrite
    files = OSMan.list_files(path)
    i = 0
    for File in files:
        if i > 0:
            c = CSVMan(File)
        else:
            c = CSVMan(File)
            i += 1
        c.print_size()


def RandDomains(CSVfile, DomainColumn, rand, limit=None):
    c = CSVMan(CSVfile)
    #print c.dialect
    column = c.get_column(DomainColumn)
    ucolumn = set(column)
    List = [u for u in ucolumn]
    random.shuffle(List)
    e = DigMan(CSVfile, c.dialect)
    e.inList(DomainColumn, List[:rand], limit, sufix='rand' + str(rand) + str(DomainColumn))


def Average():
    if os.path.isdir(global_args.csv_file):
        OSMan.process_each_file(global_args.csv_file, Average)
    else:
        print 'Processing a file'
        path = global_args.csv_file
        csv_column = global_args.csv_column
        csv_avg_column = global_args.csv_avg_column
        sort_by_keys = global_args.sort_by_keys
        reverse = global_args.reverse
        c = SmartMan(path)
        print "\nAverage on column"
        head = [csv_column, 'average_' + csv_avg_column]
        sort_by_keys = get_default_sorting(sort_by_keys)
        data = SmartMan.sort_dictionary(c.average_stats(csv_column, csv_avg_column), sort_by_keys, reverse)
        out = OSMan.new_filename(path, 'Average' + '%' + csv_avg_column)
        c.write_list(data, head, out)


def Plot(path, x_col, y_col):
    if os.path.isdir(path):
        print "Processing a folder"
        files = OSMan.list_files(path)
        print files
        for f in files:
            Plot(path + '/' + f, x_col, y_col)
    else:
        print 'Processing a file'
        c = CSVMan(path)
        data = {}
        for row in c.read_as_dict():
            data[row[x_col]] = row[y_col]
        data = SmartMan.sort_dictionary(data, 0, False)
        p = PaintMan()
        x, y = p.convert_to_axises(data)
        p.plot_graph(x, y)


def CountRanges(csv_file, target_column, write, ranges):
    r = RangeMan(csv_file)
    stats = r.rangesStat(target_column, ranges)
    for s in stats:
        print s[0], ":", s[1]
    if write:
        head = [target_column + ' ranges', 'count']
        out_file = OSMan.new_filename(csv_file, 'Ranges' + '%' + target_column)
        r.write_list(stats, head, out_file)


def ColumnStatistics(csv_file, target_column, write):
    r = RangeMan(csv_file)
    stats = r.generate_statistics(target_column)
    for s in stats:
        print s[0], ":", s[1]
    if write:
        head = ['Metrics', 'Value']
        out_file = OSMan.new_filename(csv_file, 'Statistics' + '%' + target_column)
        r.write_list(stats, head, out_file)


def MergeCSV(folder, out_path):
    if not out_path:
        out_path = "merged.csv"
    files =  OSMan.get_csv_files(folder)
    m = MergeMan(files)
    m.validate()
    m.merge(out_path)


def get_default_sorting(sort_by_keys):
    if not sort_by_keys:
        sort_by_keys = 1
    else:
        sort_by_keys = 0
    return sort_by_keys


def main():
    iDir = os.getcwd()

    print
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='mode')

    headstat = subparsers.add_parser('hs', help='generate statistics for CSV header')
    headstat.add_argument('CSVfile', help='input CSV file', nargs='+')

    matchinfile = subparsers.add_parser('mf', help='extract CSV rows mathed in list file to CSV column')
    matchinfile.add_argument('CSVfile', help='input CSV file')
    matchinfile.add_argument('CSVcol', help='column in CSV file')
    matchinfile.add_argument('ListFile', help='list of values for matching')
    matchinfile.add_argument('-l', '--limit', help='limits per match', type=int)

    xmlfiles = subparsers.add_parser('x', help='copy xml file according to values that in CSVfile')
    xmlfiles.add_argument('CSVfile', help='input CSV file')
    xmlfiles.add_argument('CSVcol', help='column in CSV file')
    xmlfiles.add_argument('ListFile', help='list of values for matching')

    refile = subparsers.add_parser('rf', help='extract CSV rows matched to regular expressions list')
    refile.add_argument('CSVfile', help='input CSV file')
    refile.add_argument('CSVcol', help='column in CSV file')
    refile.add_argument('ListFile', help='list of regex values for matching')

    notinfile = subparsers.add_parser('nf', help='extract CSV rows NOT matched in list file to CSV column')
    notinfile.add_argument('CSVfile', help='input CSV file')
    notinfile.add_argument('CSVcol', help='column in CSV file')
    notinfile.add_argument('ListFile', help='list of values with files to DELETE')

    random = subparsers.add_parser('ra', help='generate random set from CSV file')
    random.add_argument('top', help='choose rows limit', type=int)
    random.add_argument('CSVfiles', help='input CSV file or files', nargs="+")

    split = subparsers.add_parser('sp', help='split CSV to parts according column values')
    split.add_argument('csv_file', help='input CSV file')
    split.add_argument('target_column', help='column in CSV file for grouping and splitting')
    split.add_argument('-e', '--empty', help="don't split empty rows", action='store_true')
    split.add_argument('-f', '--folder', help="parts folder name")

    rematch = subparsers.add_parser('re',
                                    help='extract rows from CSV file, which column value match regular expression')
    rematch.add_argument('CSVfile', help='input CSV file')
    rematch.add_argument('CSVcol', help='column in CSV file')
    rematch.add_argument('regex', help='regular expression for matching values')
    rematch.add_argument('-cs', help='case sensitive flag in regular expression', action='store_true')
    rematch.add_argument('-f', '--fullmatch', help='match all characters in column', action='store_true')

    count = subparsers.add_parser('c', help='count rows in CSV file')
    count.add_argument('CSVfile', help='input CSV file')

    countD = subparsers.add_parser('cd', help='count rows in CSV files of current directory')

    countU = subparsers.add_parser('cu', help='count uniq values in CSV column')
    countU.add_argument('CSVfile', help='input CSV file')
    countU.add_argument('CSVcol', help='column in CSV file')

    topleveldomain = subparsers.add_parser('tld', help='generate top level domain statistics from CSV column')
    topleveldomain.add_argument('CSVfile', help='input CSV file')
    topleveldomain.add_argument('CSVcol', help='column in CSV file')

    merge = subparsers.add_parser('me', help='merge CSV files')
    merge.add_argument('folder', help='folder with CSV files for merging')
    merge.add_argument('-o', '--out_path', help='output path for merged file')

    humanparts = subparsers.add_parser('hp', help="markup file according to team")
    humanparts.add_argument('CSVfile', help='input CSV file')
    humanparts.add_argument('team', help='person names in team', nargs='+')

    Filter = subparsers.add_parser('fi', help="filter file")
    Filter.add_argument('CSVfile', help='input CSV file')
    Filter.add_argument('Dict',
                        help="Column-values pair in format: column1=value1 column2=value2\nAll values case insensitive",
                        nargs="+")

    Filter2 = subparsers.add_parser('fi2', help="NEED to test!! filter file with boolean operators")
    Filter2.add_argument('CSVfile', help='input CSV file')
    Filter2.add_argument('Expr',
                         help="NEED to test!!,Column-values pair in format: column1=value1 column2=value2\nAll values case insensitive",
                         nargs="+")

    randomDomains = subparsers.add_parser('rd', help='generate random set of domains (or other groups)')
    randomDomains.add_argument('rand', help='number of domains', type=int)
    randomDomains.add_argument('CSVfile', help='input CSV file')
    randomDomains.add_argument('column', help='domain column (or other column)')
    randomDomains.add_argument('-l', '--limit', help='limit records per domain', type=int)

    delColumns = subparsers.add_parser('dc', help='delete columns from CSV file')
    delColumns.add_argument('CSVfile', help='input CSV file')
    delColumns.add_argument('columns', help='columns to delete', nargs='+')

    addColumns = subparsers.add_parser('ac', help='add columns to CSV file')
    addColumns.add_argument('CSVfile', help='input CSV file/files', nargs='+')
    addColumns.add_argument('columns', help='column to add')

    blackList = subparsers.add_parser('bl', help='validate CSV file according to black list')
    blackList.add_argument('CSVfile', help='input CSV file')
    blackList.add_argument('CSVcol', help='column in CSV file')
    blackList.add_argument('BlackList', help='black list file')

    blackList2 = subparsers.add_parser('bl2', help='validate CSV file according to black list ver 2')
    blackList2.add_argument('-w', '--wordsmatch', help='fullmatch or by word, default fullmatch', action='store_true')
    blackList2.add_argument('CSVfile', help='input CSV file')
    blackList2.add_argument('CSVcol', help='column in CSV file')
    blackList2.add_argument('BlackList', help='black list file')

    avg_per_column = subparsers.add_parser('avg', help='generate average statistics for column values')
    avg_per_column.add_argument('csv_file', help='input CSV file or folder')
    avg_per_column.add_argument('csv_column', help='CSV file column for grouping')
    avg_per_column.add_argument('csv_avg_column', help='CSV file column for average')
    avg_per_column.add_argument('-k', '--sort_by_keys', help='sort by keys, default sort by values ',
                                action='store_true')
    avg_per_column.add_argument('-r', '--reverse', help='sort reverse ', action='store_true')

    frequency = subparsers.add_parser('fq', help='generate frequency statistics for CSV file column')
    frequency.add_argument('CSVfile', help='input CSV file')
    frequency.add_argument('CSVcol', help='CSV file column')
    frequency.add_argument('-top', help='choose statistics row limit', type=int)
    frequency.add_argument('-k', '--sort_by_keys', help='sort by keys, default sort by values ', action='store_true')
    frequency.add_argument('-r', '--reverse', help='sort reverse ', action='store_true')

    plot = subparsers.add_parser('plt', help='plot graphs')
    plot.add_argument('csv_file', help='input CSV file or folder')
    plot.add_argument('x_column', help='data for x column')
    plot.add_argument('y_column', help='data for y column')

    count_ranges = subparsers.add_parser('rc', help='generate statistics according to ranges arguments')
    count_ranges.add_argument('csv_file', help='input CSV file')
    count_ranges.add_argument('target_column', help='column in CSV file')
    count_ranges.add_argument('ranges', help='ranges for exracting', nargs="+")
    count_ranges.add_argument('-w', '--write', help='write to file instead of printing to console', action='store_true')

    column_statistics = subparsers.add_parser('cols', help='generate math statistics for column')
    column_statistics.add_argument('csv_file', help='input CSV file')
    column_statistics.add_argument('target_column', help='column in CSV file')
    column_statistics.add_argument('-w', '--write', help='write to file instead of printing to console',
                                   action='store_true')

    #onerange=subparsers.add_parser('or',help='extract rows matching digit')
    #onerange.add_argument('CSVfile',help='input CSV file')
    #onerange.add_argument('CSVcol',help='column in CSV file')
    #onerange.add_argument('Range',help='range for exracting',type=float)

    global global_args
    global_args = parser.parse_args()

    if global_args.mode == 'hs':
        print "\nHeader statistics output:"
        dia = True
        dialect = 'a'
        for f in global_args.CSVfile:
            print f
            if dia:
                c = CSVMan(f)
                dialect = c.dialect
                c.print_header()
                dia = False
            else:
                c = CSVMan(f, dialect)
                c.print_header()
    elif global_args.mode == 'c':
        c = CSVMan(global_args.CSVfile)
        c.print_size()
    elif global_args.mode == 'cd':
        countrowsD(iDir)
    elif global_args.mode == 'cu':
        s = SmartMan(global_args.CSVfile)
        s.count_unique(global_args.CSVcol)
    elif global_args.mode == 'tld':
        s = SmartMan(global_args.CSVfile)
        s.count_top_level_domains(global_args.CSVcol)
    elif global_args.mode == 'fq':
        Frequency(global_args.CSVfile, global_args.CSVcol, global_args.sort_by_keys, global_args.reverse, global_args.top)
    elif global_args.mode == 'mf':
        e = DigMan(global_args.CSVfile)
        print "\nMatching in  file:"
        e.inFile(global_args.CSVcol, global_args.ListFile, global_args.limit)
    elif global_args.mode == 'ra':
        dia = True
        dialect = 'a'
        for f in global_args.CSVfiles:
            print f
            if dia:
                e = DigMan(f)
                dialect = e.dialect
                e.get_random(global_args.top)
                dia = False
            else:
                e = DigMan(f, dialect)
                e.get_random(global_args.top)
    elif global_args.mode == 'sp':
        Split(global_args.csv_file, global_args.target_column, global_args.folder, global_args.empty)
    elif global_args.mode == 're':
        e = DigMan(global_args.CSVfile)
        print "\nGenerating rows:"
        e.ReMatched(global_args.CSVcol, global_args.regex, global_args.cs, global_args.fullmatch)
    elif global_args.mode == 'me':
        MergeCSV(global_args.folder, global_args.out_path)
    elif global_args.mode == 'hp':
        h = MarkMan(global_args.CSVfile, global_args.team)
        h.markFile()
    elif global_args.mode == 'fi':
        keys = []
        vals = []
        for p in global_args.Dict:
            try:
                key, val = p.split('=')
            except ValueError:
                sys.exit("Incorrect column-values pairs!\nPlease write in format: column1=value1 column2=value2")
            keys.append(key)
            vals.append(val)
        Dict = dict(zip(keys, vals))
        print "Matching according to dictionary", Dict
        e = DigMan(global_args.CSVfile)
        e.FilterFile(Dict)
    if global_args.mode == 'nf':
        e = DigMan(global_args.CSVfile)
        print "\nRows not in file:"
        e.NotInFile(global_args.CSVcol, global_args.ListFile)
    if global_args.mode == 'rd':
        print 'max=', global_args.limit
        RandDomains(global_args.CSVfile, global_args.column, global_args.rand, global_args.limit)
    if global_args.mode == 'rf':
        e = DigMan(global_args.CSVfile)
        print "\nAnalyzing cells according to regular expressions list.."
        e.ReFile(global_args.CSVcol, global_args.ListFile)
    if global_args.mode == 'dc':
        deleteColumns(global_args.CSVfile, global_args.columns)
    if global_args.mode == 'ac':
        print global_args.CSVfile
        for f in global_args.CSVfile:
            print f
            addColumns(f, global_args.columns)

    if global_args.mode == 'bl':
        e = DigMan(global_args.CSVfile)
        e.BlackList(global_args.CSVcol, global_args.BlackList)

    if global_args.mode == 'bl2':

        e = DigMan(global_args.CSVfile)
        if global_args.wordsmatch:
            e.BlackList2(global_args.CSVcol, global_args.BlackList, global_args.wordsmatch)
        else:

            e.BlackList2(global_args.CSVcol, global_args.BlackList)

    if global_args.mode == 'fi2':
        print global_args.Expr
        keys = []
        vals = []
        oper = []
        for exp in global_args.Expr:
            if '=' in exp:
                key, val = exp.split('=')
                keys.append(key)
                vals.append(val)
            elif exp.lower() in ['and', 'or', 'not']:
                oper.append(exp)
            else:
                sys.exit("invalid pairs or operants")
        #print keys
        #print vals
        Dict = dict(zip(keys, vals))
        print Dict
        print oper
        e = DigMan(global_args.CSVfile)
        e.FilterFile2(Dict, oper)
    if global_args.mode == 'x':
        print 'copy xmls files'
    if global_args.mode == 'avg':
        print "average per column"
        Average()
    if global_args.mode == 'plt':
        print "plotting data"
        Plot(global_args.csv_file, global_args.x_column, global_args.y_column)
    if global_args.mode == 'rc':
        CountRanges(global_args.csv_file, global_args.target_column, global_args.write, global_args.ranges)
    if global_args.mode == 'cols':
        ColumnStatistics(global_args.csv_file, global_args.target_column, global_args.write)


if __name__ == "__main__":
    main()