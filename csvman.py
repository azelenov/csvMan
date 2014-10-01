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
# from xlsxwriter.workbook import Workbook

class CSVMan: #main class for CSV files operations
    def __init__(self, path, dialect=None):
        self.path=path
        # try:
        #     self.auto_dialect_detection()
        # except (Exception):
        #     self.sniff()
        csv.register_dialect('cd',delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL,lineterminator='\n')
        self.dialect = 'cd'

        self.head=self.dRead().fieldnames
        self.data=self.dRead()

    def dRead(self): #read CSV file to dictionary
        f=open(self.path)
        r=csv.DictReader(f,dialect=self.dialect)
        self.head=r.fieldnames
        return r

    def dWrite(self,List,OutPath,header):
        mode=self.checkF(OutPath)
        with open (OutPath,mode) as out:
            w=csv.DictWriter(out,fieldnames=header,dialect=self.dialect)
            w.writeheader()
            try:
                w.writerows(List)
            except TypeError:
                sys.exit('Current CSV dialect incorect for file OR file has data without columns!!!Please repeat with other dialect or add columns manually.')
        print "File "+OutPath+" has been written,",len(List),' rows'


    def auto_dialect_detection(self):
        try:
            f=open(self.path,"rb")
        except IOError:
            sys.exit('No such file or directory:'+self.path)
        d=csv.Sniffer().sniff(f.read(1024))
        csv.register_dialect('a',d)
        print " a - dialect auto detection: delimiter=",\
            csv.get_dialect('a').delimiter,"quotechar=",csv.get_dialect('a').quotechar,\
            "quoting=",csv.get_dialect('a').quoting,"escapechar=",csv.get_dialect('a').escapechar
        self.dialect='a'


    def sniff(self): #search for CSV file dialect
        print "List of registered CSV dialects:"

        csv.register_dialect('cs',delimiter=',',quotechar="'",quoting=csv.QUOTE_ALL,lineterminator='\n')
        csv.register_dialect('cd',delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL,lineterminator='\n')
        csv.register_dialect('sd',delimiter=';',quotechar='"',quoting=csv.QUOTE_ALL,lineterminator='\n')
        csv.register_dialect('ss',delimiter=';',quotechar="'",quoting=csv.QUOTE_ALL,lineterminator='\n')
        csv.register_dialect('dnb',delimiter='|',quotechar="'",quoting=csv.QUOTE_ALL,lineterminator='\n')
        csv.register_dialect('ts',delimiter='\t',quotechar="'",quoting=csv.QUOTE_ALL,lineterminator='\n')
        csv.register_dialect('td',delimiter='\t',quotechar='"',quoting=csv.QUOTE_ALL,lineterminator='\n')

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
        ans=raw_input("Please choose CSV file dialect or create manually...")
        if ans=='a':
            self.dialect='a'
        elif ans=='cs':
            self.dialect='cs'
        elif ans=='cd':
            self.dialect='cd'
        elif ans=='ss':
            self.dialect='ss'
        elif ans=='sd':
            self.dialect='sd'
        elif ans=='sd':
            self.dialect='sd'
        elif ans=='dnb':
            self.dialect='dnb'
        elif ans=='ts':
            self.dialect='ts'
        elif ans=='td':
            self.dialect='td'
        else:
            print "!!UNREGISTERED dialect!!!!"
            self.sniff()
        print

    def headStat(self): #CSV header statistics
        self.dRead()
        print self.head
        print "Number of columns:",len(self.head)

    def get_column(self, column): #get not null values from CSV column as a list
        res=[]
        Dict=self.dRead()
        for row in Dict:
            if row[column]!="":
                res.append(row[column])
        return res

    def columnStat(self,column,limit=False): #statistics for column values
        rows=self.get_column(column)
        stats={}
        for row in rows:
            if stats.has_key(row) and row!='':
                stats[row]=stats[row]+1
            else:
                stats[row]=1
        return stats

    def average_stats(self, csv_column, csv_avg_column): #statistics for column values
        stats = {}
        for row in self.dRead():
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


    def sortDict(self, Dict, sort_index=1): #convert dictionary to sorted list
        sortedList=sorted(Dict.iteritems(), key=operator.itemgetter(sort_index), reverse=True)
        return sortedList

    def checkF(self,path):
        if os.path.exists(path):
            print "Please write 'w' for writing, 'a' for 'appending' or 's' for stoping program"
            ans=raw_input('File '+path+' exist! Rewrite(w), append(a) or stop program (s)?')
            if ans=='w':
                return 'w'
            elif ans=='a':
                return 'a'
            elif ans=='s':
                sys.exit()
            else:
                print "Please write 'w' for writing, 'a' for 'appending' or 's' for stoping program"
                self.checkF(path)
        else:
            return 'w'

    def cWrite(self,List,header,path='out.csv'): #write List to file with header
        mode=self.checkF(path)
        with open(path,mode) as out:
            w=csv.writer(out,dialect=self.dialect)
            w.writerow(header)
            w.writerows(List)
        print "File "+path+" has been written,",len(List),' rows.'

    def TopLevelDomain(self,column): #count Top Level Domain for domains in CSV column
        domains=self.get_column(column)
        sufixes={}
        for domain in domains:
            domain=domain.strip().lower()
            domain=re.sub("^https?://","",domain)
            domain=domain.replace("\\","/")
            domain=re.sub("/.*$","",domain)
            domain=re.sub("[.;>,]$","",domain)
            if domain.find('.')!=-1 and domain!='':
                parts=domain.split('.')
                main=parts[-1]
                if re.match('^[0-9]+$',main): main='IP address'
                if sufixes.has_key(main):
                    sufixes[main]=sufixes[main]+1
                else:
                    sufixes[main]=1
        head=['Sufix','Count']
        data=self.sortDict(sufixes)
        out=self.FileName('TLD')
        self.cWrite(data,head,out)
        return data

    def FileName(self, sufix): #generate New filename
        parts=self.path.split('.')
        name=parts[0]
        ext=parts[-1]
        newName=name+'%'+str(sufix)+'.'+ext
        return newName

    def Rand(self, List, num=None): #shuffle data and cut part
        data=List
        random.shuffle(data)
        if num: data=data[:num]
        return data

    def countUniq(self, TarCol):
        print self.path
        data=self.get_column(TarCol)
        udata=set(data)
        print "Count all values:",len(data)
        print "Count uniq values:",len(udata)

    def countrows(self):
        r=self.dRead()
        data=[d for d in r]
        print "File:",self.path,':',len(data),'rows'


class Ranges(CSVMan):#this class is DEPRECATED!!!
    def __init__(self,path):
        self.c=CSVMan(path)

    def rangeStat(self,column): #print main file ranges in CSV column
        print self.c.path
        ranges=self.c.get_column(column)
        ranges=sorted(ranges)
        print "all scores in file:",len(ranges)
        print "Max score:",ranges[-1]
        print "Min score:",ranges[0]
        print "Main range:",float(ranges[-1])-float(ranges[0])

    def rangesStat(self,column,values): #print ranges in CSV column according to values
        ranges=self.c.get_column(column)
        while len(values)!=1:
            #print values
            start=values[0]
            end=values[1]
            s=0
            for r in ranges:
                if int(r)>start and int(r)<=end:
                    s=s+1
            print "range",start+1,"-",end,":",s
            values.pop(0)

    def rangesCut(self,column, ranges):
        parts=[]
        i=1
        starts=[]
        ends=[]
        for r in ranges:
            if i in range (1,1000,2):
                starts.append(r)
            else:
                ends.append(r)
            i=i+1
        print starts
        print ends

    def OneRange(self,column, Rang):
        print Rang
        data=self.c.dRead()
        res=[]
        for row in data:
            try:
                cell=eval(row[column])
            except ValueError:
                print cell
            else:
                if float(row[column])==Rang:
                    #print row[column]
                    res.append(row)
                    #break
        print len(res)


class Folder:#All things with folders
    def __init__(self,path):
        self.Dir=path
        #print self.Dir

    def listF(self): #list files in Folder
        files=[]
        for p in sorted(os.listdir(self.Dir)):
            files.append(p)
        return files

    def createF(self): #smart create folder
        if not os.path.exists(self.Dir):
            os.mkdir(self.Dir)
            print "Folder "+self.Dir+" has been created."
        else:
            print "Folder "+self.Dir+" exists."
            print "Writing to", self.Dir


class Extractor(CSVMan):#Split files into parts and more
    def __init__(self, path, dialect=None):
        self.c=CSVMan(path, dialect)

    def ReMatched(self,TarCol,regEx,cs=False,f=False):#filter values in target column using regular expressions
        data=self.c.dRead()
        if cs==False:
            reg=re.compile(regEx,re.I)
        else:
            reg=regEx
        res=[]
        for row in data:
            if f==False:
                if re.search(reg,row[TarCol]): res.append(row)
            elif f==True:
                if re.match(reg,row[TarCol]): res.append(row)
        oPath=self.c.FileName('re_matched')
        self.c.dWrite(res,oPath,data.fieldnames)

    def inList(self,TarCol,List,limit=None,sufix='matched'):#filter values in target column matched in List
        print 'max match=',limit
        #sys.exit()
        data=self.c.dRead()
        res=[]
        if limit!=None:
            maxcount=int(limit)
            columns=set(self.c.get_column(TarCol))
            stats={}
            for row in data:
                value=row[TarCol].lower()
                if value in List:
                    if stats.has_key(value):
                        stats[value]+=1
                    else:
                        stats[value]=1
                    if stats[value]<=maxcount:
                        res.append(row)
        elif limit==None:
            for row in data:
                value=row[TarCol].lower()
                if value in List:
                    res.append(row)
        if limit==None:
            oPath=self.c.FileName(sufix)
        else:
            oPath=self.c.FileName(sufix+'_limit='+str(limit))
        self.c.dWrite(res,oPath, data.fieldnames)

    def ReList(self,TarCol,List,sufix='REList'):#filter values in target column matched in regex List
        data=self.c.dRead()
        missed=[]
        hit=[]
        i=0
        print time.asctime()
        print "Processing rows.."
        start=time.clock()
        for row in data:
            cell=row[TarCol]
            flag=True
            for l in List:
                    reg=re.compile(l, re.I)
                    if re.search(reg, cell):
                        hit.append(row)
                        flag=False
                        break
            if flag: missed.append(row)
            i=i+1

        mPath=self.c.FileName(sufix+"_NOT_matched")
        hPath=self.c.FileName(sufix+"_matched")

        self.c.dWrite(missed,mPath,data.fieldnames)
        self.c.dWrite(hit,hPath,data.fieldnames)
        finish = time.clock() - start
        print "total=", i
        print "Processed time in seconds:", finish
        print "Speed:", int(round(i/round(finish))), "rows per second"


    def BlackList(self,TarCol,BlackList,sufix='BlackList'):#filter words in target column matched in Black List
        with open(BlackList) as f:
            List=[line.strip().lower() for line in f]
        data=self.c.dRead()
        missed=[]
        hit=[]
        i=0
        print time.asctime()
        print "Processing rows.."
        start=time.clock()
        for row in data:
            flag=True
            words=row[TarCol].lower().split(" ")
            #print words
            for word in words:
                if word in List:
                    #print i,"hit=",word
                    hit.append(row)
                    flag=False
                    break
            if flag:
                #print i,"missed"
                missed.append(row)

            i=i+1

        mPath=self.c.FileName(sufix+"_NOT_matched")
        hPath=self.c.FileName(sufix+"_matched")

        self.c.dWrite(missed,mPath,data.fieldnames)
        self.c.dWrite(hit,hPath,data.fieldnames)
        finish=time.clock()-start
        print "total=",i
        print "Processed time in seconds:",finish
        print "Speed:",int(round(i/round(finish))),"rows per second"


    def BlackList2(self,TarCol,BlackList,wordsmatch=False,sufix='BlackList'):#filter words in target column matched in Black List
        with open(BlackList) as f:
            List=[line.strip().lower() for line in f]
        data=self.c.dRead()
        missed=[]
        hit=[]
        i=0
        print time.asctime()
        print "Processing rows.."
        start=time.clock()
        for row in data:
            flag=True
            if wordsmatch==True:
                #rint 'wordsmatch'
                words=row[TarCol].lower().split(" ")
                #print words
                for word in words:
                    if word in List:
                        #print i,"hit=",word
                        hit.append(row)
                        flag=False
                        break
                if flag:
                    #print i,"missed"
                    missed.append(row)
            else:
                #print 'else function'
                line=row[TarCol].lower()
                if line in List:
                    hit.append(row)
                else:
                    missed.append(row)
            i=i+1

        mPath=self.c.FileName(sufix+"_NOT_matched")
        hPath=self.c.FileName(sufix+"_matched")

        self.c.dWrite(missed,mPath,data.fieldnames)
        self.c.dWrite(hit,hPath,data.fieldnames)
        finish=time.clock()-start
        print "total=",i
        print "Processed time in seconds:",finish
        print "Speed:",int(round(i/round(finish))),"rows per second"


    def NotiIList(self,TarCol,List):#filter values in target column matched in List
        data=self.c.dRead()
        res=[]
        for row in data:
            value=row[TarCol].lower()
            if value not in List:
                res.append(row)
        oPath=self.c.FileName('NOT_matched')
        self.c.dWrite(res,oPath,data.fieldnames)

    def inFile(self,TarCol,FileName,limit):#filter values in target column matched in File
        with open(FileName) as f:
            List=[line.strip().lower() for line in f]
        self.inList(TarCol,List,limit=limit)

    def ReFile(self,TarCol,FileName):#filter values in target column matched in File
        with open(FileName) as f:
            List=[line.strip().lower() for line in f]
        self.ReList(TarCol,List)

    def NotInFile(self,TarCol,FileName,limit=None):#filter values in target column matched in File
        with open(FileName) as f:
            List=[line.strip().lower() for line in f]
        self.NotiIList(TarCol,List)


    def inCSV(self,TarCol,CSVName,CSVcolumn,limit):
        c=CSVMan(CSVName)
        data=set(c.get_column(CSVcolumn))
        self.inList(TarCol,data,limit)

    def FilterFile(self,colValPairs):#filter file according multiple colums values
        print time.asctime()
        print "Processing rows.."
        start=time.clock()
        data=self.c.dRead()
        header=data.fieldnames
        path=self.c.FileName('filtered')
        for key in colValPairs:
            if key not in header:
                sys.exit("Input file don't have column: "+key+'\nAvailable column names in CSV header:'+str(header))
        newdata=[]
        for row in data:
            flag=False
            flags=[]
            for key in colValPairs:
                if row.has_key(key) and colValPairs[key].lower()==row[key].lower():
                    flag=True
                    flags.append(flag)
                else:
                    flag=False
                    flags.append(flag)
            if False not in flags:
                newdata.append(row)
        self.c.dWrite(newdata,path,header)

        finish=time.clock()-start
        print "Processed time in seconds:",finish

    def FilterFile2(self,colValPairs,oper):#filter file according multiple colums values
        data=self.c.dRead()
        header=data.fieldnames
        path=self.c.FileName('filtered')


        def makeEx(value,colValPairs,oper):
            i=0
            for key in colValPairs:
                if key not in header:
                    sys.exit("Input file don't have column: "+key+'\nAvailable column names in CSV header:'+str(header))
                else:
                    if i==0:
                        expr=colValPairs[key].lower()==value[key]
                    else:
                        if oper[i-1]=='and':
                            #print "and"
                            expr=expr and colValPairs[key].lower()==value[key]
                        elif oper[i-1]=='or':
                            #print "or"
                            expr=expr or colValPairs[key].lower()==value[key]
                i=i+1
            return expr

        newdata=[]
        for row in data:
            flag=False
            flags=[]
            for key in colValPairs:
                if row.has_key(key) and makeEx(row,colValPairs,oper):
                    flag=True
                    flags.append(flag)
                else:
                    flag=False
                    flags.append(flag)
            if False not in flags:
                newdata.append(row)
        self.c.dWrite(newdata,path,header)


    def split2Files(self, TarCol,  outFolder, empty):#split File into parts according to values in column
        total=0
        start=time.clock()
        data=self.c.dRead()
        #print data.fieldnames
        f=Folder(outFolder)
        f.createF()
        os.chdir(f.Dir)
        stat={}
        for cell in data:
            if cell[TarCol]=="":
                if empty==True:
                    p="EMPTY"
                else:
                    p=None
            else:
                p=cell[TarCol]
            if p!=None:
                if stat.has_key(p):
                    with open(p+'.csv','a') as out:
                        w=csv.DictWriter(out,fieldnames=data.fieldnames,dialect=self.c.dialect)
                        w.writerow(cell)
                    stat[p]=stat[p]+1
                else:
                    stat[p]=1
                    with open(p+'.csv','a') as out:
                        w=csv.DictWriter(out,fieldnames=data.fieldnames,dialect=self.c.dialect)
                        w.writeheader()
                        w.writerow(cell)
            total=total+1

        print "File has been splitted successfully into parts:"
        print stat
        print "Total rows count:",total
        finish=time.clock()-start
        print "Processed time in seconds:",finish

    def get_random(self,rand): #writing random set
        Dict=self.c.dRead()
        head=Dict.fieldnames
        data=[row for row in Dict]
        random.shuffle(data)
        data=data[:rand]
        path=self.c.FileName('random'+str(rand))
        with open(path,'a') as out:
            w=csv.DictWriter(out,fieldnames=head,dialect=self.c.dialect)
            w.writeheader()
            w.writerows(data)
        print "Random set has been writed to file:",path

    def CleanRow(self,row):
        for key in row:
            if key in self.clean:
                row[key]=""
        row['Status Description']=self.status
        return row


    def PrepareFile(self):
        self.split2Files(TarCol='check',empty=False,outFolder='ErrorsFeedback')
        try:
            os.rename('e.csv', 'Edited.csv')
        except:
            print "e column not exist"
        try:
            os.rename('d.csv', 'Deleted.csv')
        except:
            print "d column not exist"
        os.chdir(os.pardir)
        self.c.headStat()
        self.ans=raw_input("Please write your uniq ID column: ")
        stats=self.c.columnStat(self.ans)
        testdata=self.c.dRead()
        for d in testdata:
            if d['Status Description'].find("Successfully processed (No")!=-1:
                self.status=d['Status Description']
                notfound=d
                break
        self.clean=[]
        for key in notfound:
            if notfound[key]=="":
                self.clean.append(key)
        newdata=[]
        data=self.c.dRead()
        head=data.fieldnames
        for row in data:
            check=row['check']
            row.pop('check')
            if check=='d':
                stats[row[self.ans]]=stats[row[self.ans]]-1
                if stats[row[self.ans]]<=0:
                    row=self.CleanRow(row)
                    newdata.append(row)
            else:
                newdata.append(row)

        head.remove('check')
        path=self.c.FileName('FINAL')
        self.c.dWrite(newdata,path,head)



class Merger(CSVMan):#smart merge many file into one
    columns=0
    def __init__(self,Directory):
        self.iDir=Directory
        self.dialect=None

    def merge(self,etalonFile,All='All'):#merge many CSV files
        head=self.etalonHeader(etalonFile)
        self.checkcolumns(head)
        f=Folder(self.iDir)
        files=f.listF()
        All='All'
        f=Folder('All')
        f.createF()
        h=True
        out=open(All+'/'+All+'.csv','a')
        for path in files:
            c=CSVMan(path,self.dialect)
            data=c.dRead()
            w=csv.DictWriter(out,fieldnames=data.fieldnames,dialect=self.dialect)
            if h==True:
                w.writeheader()
                h=False
            for row in data:
                w.writerow(row)
            print path,'done'
        print "All files has been merged successfully to folder:",All

    def etalonHeader(self,etalonFile):#validating etalon CSV File
        print "Checking etalon file"
        def ask():
            ans=raw_input("Do you wanna proceed? (y,n)")
            if ans=='n':
                sys.exit('Please fix columns')
            elif ans=='y':
                pass
            else:
                print "answers only yes or no"
                ask()

        f=etalonFile
        c=CSVMan(f)
        self.dialect=c.dialect
        status=False
        header=c.dRead().fieldnames
        for h in header:
            if re.match('^\s*$',h):
                print 'Empty column detected in position :',header.index(h)+1,"value:'",h,"'"
                ask()
                status=False
            elif re.match('^Check|check|chek|cheak|delete|link|Link$',h) or re.search('search',h):
                print 'Suspisious column detected in position:',header.index(h)+1,", value:'"+str(h)+"'"
                ask()
                status=False
            else:
                status=True
        if status==True: print "Etalon file - OK"
        return len(header),header

    def checkcolumns(self,head):#validating CSV file headers
        ecol_num=head[0]
        eHeader=head[1]
        f=Folder(self.iDir)
        files=f.listF()
        s=[]
        fields=[]
        print "Validating CSV files according to etalon"
        for path in files:
            c=CSVMan(path,self.dialect)
            data=c.dRead()
            col_num=len(data.fieldnames)
            head=data.fieldnames
            print path,col_num
            if col_num!=ecol_num: s.append(path)
            if head!=eHeader:
                fields.append(path)
                for h in head:
                    if h not in eHeader:
                        print 'Wrong column!:',h
                print
        if s!=[]:
            print 'Columns sum does not match in files!:',s
            sys.exit()
        elif fields!=[]:
            print 'Not matched fieldnames in files!:',fields
            sys.exit()
        else:
            print 'All columns and fields matched'
            print



class HumanParts(CSVMan):

    def __init__(self,path,people):
        self.path=path
        self.people=[p for p in people]
        self.c=CSVMan(path)
        self.data=self.c.dRead()
        self.header=self.data.fieldnames

    def countrows(self):
        counter=0
        for d in self.data:
            counter+=1
        return counter

    def divide(self):#divide num of rows for people
        num=self.countrows()
        n=len(self.people)
        part=num/n
        rest=num-part*n
        parts={}
        for p in self.people:
            parts[p]=part
        while rest!=0:
            random.shuffle(self.people)
            dice=self.people[0]
            parts[dice]=parts[dice]+1
            rest=rest-1
        print "Count of rows:",num
        print "Num of persons:",n
        for p in parts:
            print p,':',parts[p]
        return parts

    def markFile(self):#mark file with person names
        data=self.c.dRead()
        self.header.insert(0,'whose')
        self.out_path=self.c.FileName('marked')
        parts=self.divide()
        temp_data=[d for d in data]
        with open (self.out_path,'w') as out:
            w=csv.DictWriter(out,fieldnames=self.header,dialect=self.c.dialect)
            w.writeheader()
            for key in sorted(parts.keys()):
                for i in range(1,int(parts[key])+1):
                    row=temp_data.pop(0)
                    row['whose']=key
                    w.writerow(row)
        print "Saved to file:",self.out_path


class ExcelMan:
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

class Plotter:
    title = "Default title"
    line_width = 2

    def plot_graph(self, x_axis, y_axis):
        plt.plot(x_axis, y_axis, linewidth=self.line_width)
        plt.title(self.title)
        plt.show()

    def convert_to_axises(self, dict_data):
        y_axis = []
        x_axis = []
        for pair in dict_data:
            x_axis.append(pair[0])
            y_axis.append(pair[1])
        print x_axis
        print y_axis
        return x_axis, y_axis

class Clusters:
    def get_clusters(self, input_list, num_of_clusters):
        input_list = [int(i) for i in input_list]
        input_list.sort()
        heap_list=[] # A *heap* would be faster
        for i in range(1, len(input_list)):
            heap_list.append((int(input_list[i])-int(input_list[i-1]), i))
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
            out.append(input_list[heap_list[i-1]:heap_list[i]])
        return out

    def generate_statistics(self, list_of_clusters, mark=''):
        stats = {}
        for cluster in list_of_clusters:
            key = max(cluster)
            stats[key] = len(cluster)
        return stats



def Scores(inFile,TarCol,scores=False):# count ranges of scores in CSV file
    r=Ranges(inFile)
    r.rangeStat(TarCol)
    if scores!=True:
        r.rangesStat(TarCol,range(650,1050,50))


def Frequency(path,TarCol,top=None):# count Domain Frequancy in file
    if os.path.isdir(path):
        print "Processing a folder"
        f=Folder(path)
        files=f.listF()
        print files
        for f in files:
            Frequency(path + '/' + f, TarCol)
    else:
        c=CSVMan(path)
        print "\nFrequency on column"
        head=[TarCol,'Count']
        data=c.sortDict(c.columnStat(TarCol))
        out=c.FileName('Frequency'+'%'+TarCol)
        if top: data=data[:top]
        c.cWrite(data,head,out)

def countCells(path,TarCol): #Count not empty cells in target column of CSV file
    f=Folder(path)
    files=f.listF()
    for f in files:
        c=CSVMan(f)
        data=c.get_column(TarCol)
        #print data
        print f,':',len(data)



def Split(in_file, target_column, parts_folder, empty_cells):#Split files into parts
    e=Extractor(in_file)
    if not parts_folder:
        parts_folder = "parts"
    if not empty_cells:
        empty_cells = False
    e.split2Files(target_column, parts_folder, empty_cells)

def deleteColumns(path,columns):
    c=CSVMan(path)
    data=c.dRead()
    head=data.fieldnames
    edata=[]
    for d in data:
        for col in columns:
            d.pop(col)
        edata.append(d)
    h2=head
    for col in columns:
        h2.remove(col)
    print "new header\n",h2
    oPath=c.FileName('deleted_columns')
    c.dWrite(edata,oPath,h2)

def addColumns(path,column):
    c=CSVMan(path)
    data=c.dRead()
    head=data.fieldnames
    edata=[]
    for d in data:
        d.insert(0,column)
        edata.append(d)
    h2=head
    h2.insert(0,column)
    print "new header\n",h2
    oPath=c.FileName('deleted_columns')
    c.dWrite(edata,oPath,h2)


def Rand(inFile,rand):#create random set
    e=Extractor(inFile)
    print "Generating random..."
    e.get_random(rand)


def countrowsD(path):#rewrite
    f=Folder(path)
    files=f.listF()
    i=0
    for File in files:
        if i>0:
            c=CSVMan(File,c.dialect)
        else:
            c=CSVMan(File)
            i=i+1
        c.countrows()

def RandDomains(CSVfile,DomainColumn,rand,limit=None):
    c=CSVMan(CSVfile)
    #print c.dialect
    column=c.get_column(DomainColumn)
    ucolumn=set(column)
    List=[u for u in ucolumn]
    random.shuffle(List)
    e=Extractor(CSVfile,c.dialect)
    e.inList(DomainColumn,List[:rand],limit,sufix='rand'+str(rand)+str(DomainColumn))

def Average(path, csv_column, csv_avg_column):
    if os.path.isdir(path):
        print "Processing a folder"
        f=Folder(path)
        files=f.listF()
        print files
        for f in files:
            Average(path + '/' + f, csv_column, csv_avg_column)
    else:
        print 'Processing a file'
        c=CSVMan(path)
        print "\nAverage on column"
        head=[csv_column,'average_' + csv_avg_column]
        data=c.sortDict(c.average_stats(csv_column, csv_avg_column))
        out=c.FileName('Average'+'%'+csv_avg_column)
        c.cWrite(data, head, out)

def Plot(path, x_col, y_col):
    if os.path.isdir(path):
        print "Processing a folder"
        f=Folder(path)
        files=f.listF()
        print files
        for f in files:
            Plot(path + '/' + f, x_col, y_col)
    else:
        print 'Processing a file'
        c=CSVMan(path)
        data = {}
        for row in c.dRead():
            data[row[x_col]] = row[y_col]
        data = c.sortDict(data, 0)
        p = Plotter()
        x,y = p.convert_to_axises(data)
        p.plot_graph(x, y)

def CountClusters(csv_file, target_column, mark, num_of_clusters):
    if mark == None:
        mark = ''
    if num_of_clusters == None:
        num_of_clusters = 10
    else:
        num_of_clusters = int(num_of_clusters)
    c = CSVMan(csv_file)
    data = c.get_column(target_column)
    clus = Clusters()
    clusters = clus.get_clusters(data, num_of_clusters)
    results = clus.generate_statistics(clusters, mark)

    head=[target_column + ' ranges', 'count']
    out_file=c.FileName('Clusters'+'%'+target_column)
    c.cWrite(c.sortDict(results), head, out_file)




def main():
    iDir=os.getcwd()

    print
    parser=argparse.ArgumentParser()
    subparsers=parser.add_subparsers(dest='mode')

    headstat=subparsers.add_parser('hs',help='generate statistics for CSV header')
    headstat.add_argument('CSVfile',help='input CSV file',nargs='+')

    frequency=subparsers.add_parser('fq',help='generate frequency statistics for CSV file column')
    frequency.add_argument('CSVfile',help='input CSV file')
    frequency.add_argument('CSVcol',help='CSV file column')
    frequency.add_argument('-top',help='choose statistics row limit',type=int)

    matchinfile=subparsers.add_parser('mf',help='extract CSV rows mathed in list file to CSV column')
    matchinfile.add_argument('CSVfile',help='input CSV file')
    matchinfile.add_argument('CSVcol',help='column in CSV file')
    matchinfile.add_argument('ListFile',help='list of values for matching')
    matchinfile.add_argument('-l','--limit',help='limits per match',type=int)

    xmlfiles=subparsers.add_parser('x',help='copy xml file according to values that in CSVfile')
    xmlfiles.add_argument('CSVfile',help='input CSV file')
    xmlfiles.add_argument('CSVcol',help='column in CSV file')
    xmlfiles.add_argument('ListFile',help='list of values for matching')


    refile=subparsers.add_parser('rf',help='extract CSV rows matched to regular expressions list')
    refile.add_argument('CSVfile',help='input CSV file')
    refile.add_argument('CSVcol',help='column in CSV file')
    refile.add_argument('ListFile',help='list of regex values for matching')

    notinfile=subparsers.add_parser('nf',help='extract CSV rows NOT matched in list file to CSV column')
    notinfile.add_argument('CSVfile',help='input CSV file')
    notinfile.add_argument('CSVcol',help='column in CSV file')
    notinfile.add_argument('ListFile',help='list of values with files to DELETE')

    random=subparsers.add_parser('ra',help='generate random set from CSV file')
    random.add_argument('top',help='choose rows limit',type=int)
    random.add_argument('CSVfiles',help='input CSV file or files',nargs="+")

    split=subparsers.add_parser('sp',help='split CSV to parts according column values')
    split.add_argument('csv_file',help='input CSV file')
    split.add_argument('target_column',help='column in CSV file for grouping and splitting')
    split.add_argument('-e', '--empty',help="don't split empty rows",action='store_true')
    split.add_argument('-f', '--folder',help="parts folder name")

    rematch=subparsers.add_parser('re',help='extract rows from CSV file, which column value match regular expression')
    rematch.add_argument('CSVfile',help='input CSV file')
    rematch.add_argument('CSVcol',help='column in CSV file')
    rematch.add_argument('regex',help='regular expression for matching values')
    rematch.add_argument('-cs',help='case sensitive flag in regular expression',action='store_true')
    rematch.add_argument('-f','--fullmatch',help='match all characters in column',action='store_true')

    count=subparsers.add_parser('c',help='count rows in CSV file')
    count.add_argument('CSVfile',help='input CSV file')

    countD=subparsers.add_parser('cd',help='count rows in CSV files of current directory')

    countU=subparsers.add_parser('cu',help='count uniq values in CSV column')
    countU.add_argument('CSVfile',help='input CSV file')
    countU.add_argument('CSVcol',help='column in CSV file')

    topleveldomain=subparsers.add_parser('tld',help='generate top level domain statistics from CSV column')
    topleveldomain.add_argument('CSVfile',help='input CSV file')
    topleveldomain.add_argument('CSVcol',help='column in CSV file')

    merge=subparsers.add_parser('me',help='merge CSV files')
    merge.add_argument('CSVetalon',help='CSV file with correct header, checked manually')

    humanparts=subparsers.add_parser('hp',help="markup file according to team")
    humanparts.add_argument('CSVfile',help='input CSV file')
    humanparts.add_argument('team',help='person names in team',nargs='+')

    Filter=subparsers.add_parser('fi',help="filter file")
    Filter.add_argument('CSVfile',help='input CSV file')
    Filter.add_argument('Dict',help="Column-values pair in format: column1=value1 column2=value2\nAll values case insensitive",nargs="+")

    Filter2=subparsers.add_parser('fi2',help="NEED to test!! filter file with boolean operators")
    Filter2.add_argument('CSVfile',help='input CSV file')
    Filter2.add_argument('Expr',help="NEED to test!!,Column-values pair in format: column1=value1 column2=value2\nAll values case insensitive",nargs="+")

    randomDomains=subparsers.add_parser('rd',help='generate random set of domains (or other groups)')
    randomDomains.add_argument('rand',help='number of domains',type=int)
    randomDomains.add_argument('CSVfile',help='input CSV file')
    randomDomains.add_argument('column',help='domain column (or other column)')
    randomDomains.add_argument('-l','--limit',help='limit records per domain',type=int)

    delColumns=subparsers.add_parser('dc',help='delete columns from CSV file')
    delColumns.add_argument('CSVfile',help='input CSV file')
    delColumns.add_argument('columns',help='columns to delete',nargs='+')

    addColumns=subparsers.add_parser('ac',help='add columns to CSV file')
    addColumns.add_argument('CSVfile',help='input CSV file/files',nargs='+')
    addColumns.add_argument('columns',help='column to add')


    blackList=subparsers.add_parser('bl',help='validate CSV file according to black list')
    blackList.add_argument('CSVfile',help='input CSV file')
    blackList.add_argument('CSVcol',help='column in CSV file')
    blackList.add_argument('BlackList', help='black list file')

    blackList2=subparsers.add_parser('bl2',help='validate CSV file according to black list ver 2')
    blackList2.add_argument('-w','--wordsmatch',help='fullmatch or by word, default fullmatch',action='store_true')
    blackList2.add_argument('CSVfile',help='input CSV file')
    blackList2.add_argument('CSVcol',help='column in CSV file')
    blackList2.add_argument('BlackList', help='black list file')

    cleanFile=subparsers.add_parser('pr',help='Prepare file for delivery to customers and generates errors files')
    cleanFile.add_argument('CSVfile',help='input CSV file')

    avg_per_column = subparsers.add_parser('avg', help='generate average statistics for column values')
    avg_per_column.add_argument('csv_file', help='input CSV file or folder')
    avg_per_column.add_argument('csv_column', help='CSV file column for grouping')
    avg_per_column.add_argument('csv_avg_column', help='CSV file column for average')

    plot = subparsers.add_parser('plt', help='plot graphs')
    plot.add_argument('csv_file', help='input CSV file or folder')
    plot.add_argument('x_column', help='data for x column')
    plot.add_argument('y_column', help='data for y column')

    clusters = subparsers.add_parser('clu', help='generate clusters statistics')
    clusters.add_argument('csv_file', help='input CSV file')
    clusters.add_argument('target_column', help='csv column for analysis')
    clusters.add_argument('-m', '--mark',help='fullmatch or by word, default fullmatch')
    clusters.add_argument('-c', '--clusters',help='number of clusters')


    #rangescut=subparsers.add_parser('rc',help='extract rows according to ranges')
    #rangescut.add_argument('CSVfile',help='input CSV file')
    #rangescut.add_argument('CSVcol',help='column in CSV file')
    #rangescut.add_argument('ranges',help='ranges for exracting',nargs="+")

    #onerange=subparsers.add_parser('or',help='extract rows matching digit')
    #onerange.add_argument('CSVfile',help='input CSV file')
    #onerange.add_argument('CSVcol',help='column in CSV file')
    #onerange.add_argument('Range',help='range for exracting',type=float)


    args=parser.parse_args()

    if args.mode=='hs':
        print "\nHeader statistics output:"
        dia=True
        for f in args.CSVfile:
            print f
            if dia==True:
                c=CSVMan(f)
                dialect=c.dialect
                c.headStat()
                dia=False
            else:
                c=CSVMan(f,dialect)
                c.headStat()
    elif args.mode=='c':
        c=CSVMan(args.CSVfile)
        c.countrows()
    elif args.mode=='cd':
        countrowsD(iDir)
    elif args.mode=='cu':
        c=CSVMan(args.CSVfile)
        c.countUniq(args.CSVcol)
    elif args.mode=='tld':
        c=CSVMan(args.CSVfile)
        c.TopLevelDomain(args.CSVcol)
    elif args.mode=='fq':
        Frequency(args.CSVfile,args.CSVcol,args.top)
    elif args.mode=='mf':
        e=Extractor(args.CSVfile)
        print "\nMatching in  file:"
        e.inFile(args.CSVcol,args.ListFile,args.limit)
    elif args.mode=='ra':
        dia=True
        for f in args.CSVfiles:
            print f
            if dia==True:
                e=Extractor(f)
                dialect=e.c.dialect
                e.get_random(args.top)
                dia=False
            else:
                e=Extractor(f, dialect)
                e.get_random(args.top)
    elif args.mode=='sp':
        Split(args.csv_file, args.target_column, args.folder, args.empty)
    elif args.mode=='re':
        e=Extractor(args.CSVfile)
        print "\nGenerating rows:"
        e.ReMatched(args.CSVcol,args.regex,args.cs,args.fullmatch)
    elif args.mode=='me':
        m=Merger(iDir)
        m.merge(args.CSVetalon)
    elif args.mode=='hp':
        h=HumanParts(args.CSVfile,args.team)
        h.markFile()
    elif args.mode=='fi':
        keys=[]
        vals=[]
        for p in args.Dict:
            try:
                key,val=p.split('=')
            except ValueError:
                sys.exit("Incorrect column-values pairs!\nPlease write in format: column1=value1 column2=value2")
            keys.append(key)
            vals.append(val)
        Dict=dict(zip(keys,vals))
        print "Matching according to dictionary",Dict
        e=Extractor(args.CSVfile)
        e.FilterFile(Dict)
    if args.mode=='nf':
        e=Extractor(args.CSVfile)
        print "\nRows not in file:"
        e.NotInFile(args.CSVcol,args.ListFile)
    if args.mode=='rd':
        print 'max=',args.limit
        RandDomains(args.CSVfile,args.column,args.rand,args.limit)
    if args.mode=='rf':
        e=Extractor(args.CSVfile)
        print "\nAnalyzing cells according to regular expressions list.."
        e.ReFile(args.CSVcol,args.ListFile)
    if args.mode=='dc':
        deleteColumns(args.CSVfile,args.columns)
    if args.mode=='ac':
        print args.CSVfile
        for f in args.CSVfile:
            print f
            addColumns(f,args.columns)

    if args.mode=='bl':
        e=Extractor(args.CSVfile)
        e.BlackList(args.CSVcol,args.BlackList)

    if args.mode=='bl2':

        e=Extractor(args.CSVfile)
        if args.wordsmatch==True:
            e.BlackList2(args.CSVcol,args.BlackList,args.wordsmatch)
        else:

            e.BlackList2(args.CSVcol,args.BlackList)

    if args.mode=='fi2':
        print args.Expr
        keys=[]
        vals=[]
        oper=[]
        for exp in args.Expr:
            if '=' in exp:
                key,val=exp.split('=')
                keys.append(key)
                vals.append(val)
            elif exp.lower() in ['and','or','not']:
                oper.append(exp)
            else:
                sys.exit("invalid pairs or operants")
        #print keys
        #print vals
        Dict=dict(zip(keys,vals))
        print Dict
        print oper
        e=Extractor(args.CSVfile)
        e.FilterFile2(Dict,oper)
    if args.mode=='pr':
        e=Extractor(args.CSVfile)
        e.PrepareFile()
    if args.mode=='x':
        print 'copy xmls files'
    if args.mode == 'avg':
        print "average per column"
        Average(args.csv_file, args.csv_column, args.csv_avg_column)
    if args.mode == 'plt':
        print "plotting data"
        Plot(args.csv_file, args.x_column, args.y_column)
    if args.mode == 'clu':
        print "Cluster analysis"
        CountClusters(args.csv_file, args.target_column, args.mark, args.clusters)

if __name__=="__main__": main()

