import cx_Oracle
import mysql.connector
import datetime
import csv
import sys
import re
import string
import itertools

print datetime.datetime.now()

con = mysql.connector.connect(user='root', password='ncsuball', host='127.0.0.1', database='medicaid')
cursor = con.cursor()

inv_qtr = ''
inv_num = ''
util_qtr = ''

qmap = {'01':'1','02':'1','03':'1','04':'2','05':'2','06':'2','07':'3','08':'3','09':'3','10':'4','11':'4','12':'4'}

test_list = {
'F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\3 - raw_text\\2017Q1_42192_KS_MMCO_Invoice.txt':'KS_MMCO',
'F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\3 - raw_text\\2017Q1_42192_MD_MMCO_Invoice.txt':'MD_MMCO',
'F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\3 - raw_text\\2017Q1_42192_MD_MMCOEXP_Invoice.txt':'MD_MMCOEXP',
'F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\3 - raw_text\\2017Q1_42192_MD_CHIPMCO_Invoice.txt':'MD_CHIPMCO',
'F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\3 - raw_text\\2017Q1_67877_NY_MEDI_Invoice.txt':'NY_MEDI'
}

inv_qtr = '2017Q1'

for k, v in test_list.iteritems():
        human = []
        cms = []
        cmsd = {}
        logic = {}
        file = k
        key = v

        length = 5
        pattern= r"\D(\d{%d})\D" % length
        labeler_extract = re.findall(pattern, file)
        file_labeler = labeler_extract[0]

        querystring = ("SELECT * FROM invoice_logic WHERE `key` = '%s'")%key
        cursor.execute(querystring)

        field_names = [d[0].lower() for d in cursor.description]
        rows = cursor.fetchmany()
        for row in rows:
                logic.update(dict(itertools.izip(field_names, row)))

        lines = open(file).read().splitlines()

        for r in lines:
                #row cleanup and garbage removal
                r = r.upper()
                for x in logic['garbage'].split('|'):
                        r = r.replace(str(x),'')
        
                state = str(logic['state'])
                type = str(logic['type'])
                std_type = str(logic['std_type'])
                
                #identification of invoice number
                if not inv_num:
                        if logic['inv_num'] in r:
                                info = r.split(logic['inv_num'])
                                inv_num = info[1].strip(' ')
                
                #identification of submission/invoice quarter
                #~ if r.startswith(logic['inv_qtr']):
                        #~ info = r.split(':')
                        #~ info = info[1].strip().split('/')
                        #~ inv_qtr = info[0]+info[1]
                        #~ qtr = info[1]+"Q"+info[0]
                        #~ util_qtr = inv_qtr
                
                #identification of billing quarter
                if logic['period_covered'] in r:
                        if logic['period_type'] == '#QYYYY':
                                info = r.split(': ')
                                util_qtr = info[1][:1]+info[1][2:7]
                        elif logic['period_type'] == '#/YYYY':
                                info = r.split(': ')
                                util_qtr = info[1][:1]+info[1][2:7]
                        elif logic['period_type'] == 'MM/DD/YY':
                                info = r.split(': ')
                                util_qtr = qmap[info[1][:2]]+'20'+info[1][6:8]
                        #~ print util_qtr
                
                #if billing quarter is not listed in the file, default to invoice quarter
                if not util_qtr:
                        util_qtr = inv_qtr[5:6]+inv_qtr[:4]
                
                length = 6
                pattern= r"\D(\d{%d})\D" % length
                inv_detail_check = re.findall(pattern, r)
                
                #identification and processing of invoice line item
                #assumes invoice detail lines will start with 5 numeric characters (ndc) whereas other lines will not
                if r[:4].isdigit() and inv_detail_check:
                        
                        #add labeler code for invoices that only include product code and size
                        if not r[:5].isdigit():
                                r = file_labeler+'-'+ r
                        
                        #check for dashes and add if necesssary
                        
                        #remove spaces in ndc area
                        ndc_area = r[:13]
                        r = r.replace(ndc_area,ndc_area.replace(' ',''))
                        
                        #identifies product name start position with first space
                        start = r.index(' ')
                        
                        #identifies product name ending position with key character fed in from database - removes product name from line
                        ura_string = re.findall(pattern, r)
                        end = r.index(ura_string[0])-3
                        r = r.replace(r[start:end],'')
        
                        r = re.sub("[^0-9\d.\-\s]", "", r)
                        r = r.replace('  ',' ')
                        r = r.replace('  ',' ')
        
                        info = r.split(' ')
                        ndc = info[int(logic['ndc'])].replace('-','')
                        labeler = ndc[:5]
                        prod = ndc[5:9]
                        size = ndc[9:11]
                        name = str("          ")
                        ura = str("%012.6f"%float(info[int(logic['ura'])]))
                        units = str("%015.3f"%float(info[int(logic['units'])]))
                        claimed = str("%012.2f"%float(info[int(logic['claimed'])]))
                        scripts = str("%08.0f"%float(info[int(logic['scripts'])]))
                        medi_reimb = str("%013.2f"%float(info[int(logic['medi_reimb'])]))
                        non_medi_reimb = str("%013.2f"%float(info[int(logic['non_medi_reimb'])]))
                        total_reimb = str("%014.2f"%float(info[int(logic['total_reimb'])]))
                        if logic['corr_flag']:
                                corr_flag = info[int(logic['corr_flag'])]
                        else:
                                corr_flag = str(0)
                        
                        human.append({'type':type,'state':state,'labeler':labeler,'prod':prod,'size':size,'inv_qtr':inv_qtr,'util_qtr':util_qtr,'inv_num':inv_num,'ndc':ndc,'name':name,'ura':ura,'units':units,'claimed':claimed,'scripts':scripts,'medi_reimb':medi_reimb,'non_medi_reimb':non_medi_reimb,'total_reimb':total_reimb,'corr_flag':corr_flag})
                        
                        #~ split out acella into a file for each quarter
                        if labeler == '42192':
                                if util_qtr in cmsd:
                                        cmsd[util_qtr].append(std_type+state+labeler+prod+size+util_qtr+name+ura+units+claimed+scripts+medi_reimb+non_medi_reimb+total_reimb+corr_flag)
                                else:
                                        cmsd[util_qtr] = [std_type+state+labeler+prod+size+util_qtr+name+ura+units+claimed+scripts+medi_reimb+non_medi_reimb+total_reimb+corr_flag]
        
                        cms.append(std_type+state+labeler+prod+size+util_qtr+name+ura+units+claimed+scripts+medi_reimb+non_medi_reimb+total_reimb+corr_flag)
        
        print state, type, inv_qtr, util_qtr
        inv_header = ['type','state','labeler','prod','size','inv_qtr','util_qtr','inv_num','ndc','name','ura','units','claimed','scripts','medi_reimb','non_medi_reimb','total_reimb','corr_flag']
        with open('F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\4 - cms_format\\%s_%s_%s.txt'%(inv_qtr,state,type), 'wb') as output_file:
                dict_writer = csv.DictWriter(output_file, inv_header)
                dict_writer.writeheader()
                dict_writer.writerows(human)
        
        if labeler == '42192':
                for k,v in cmsd.iteritems():
                        qtr = k[1:5]+"Q"+k[:1]
                        with open('F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\4 - cms_format\\%s_%s_%s_%s_data.txt'%(qtr,labeler,state,type), 'wb') as output_file:
                                for r in v:
                                        output_file.write(r + '\r\n')
        else:
                with open('F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\4 - cms_format\\%s_%s_%s_%s_data.txt'%(inv_qtr,labeler,state,type), 'wb') as output_file:
                        for r in cms:
                                output_file.write(r + '\r\n')
        print datetime.datetime.now()