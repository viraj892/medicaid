import cx_Oracle
import mysql.connector
import datetime
import csv
import sys
import re
import string
import itertools

print datetime.datetime.now()

logic = {}

con = mysql.connector.connect(user='root', password='ncsuball', host='127.0.0.1', database='medicaid')
cursor = con.cursor()

inv_qtr = ''
util_qtr = ''
human = []
cms = []
cmsd = {}
type = 'FFSU'

ndc_map = {
'42192-0105-15':'BPO 4% GEL',
'42192-0133-16':'SODIUM SUL',
'42192-0135-10':'SALICYLIC',
'42192-0321-30':'PNV-DHA',
'42192-0329-01':'NP THYROID',
'42192-0338-01':'HYOSCYAMIN',
'42192-0340-01':'HYOSCYAMIN',
'42192-0607-04':'BROMPHENIR',
'42192-0607-16':'BROMPHENIR',
'42192-0708-10':'ANTIPYRINE',
'42192-0710-15':'ANTIPYRINE',
'42192-0710-15':'Antipyrine',
'42192-0110-03':'BPO'
}

#file = 'F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\3 - raw_text\\2017Q1_42192_KS_MMCO_Invoice.txt'
file = 'F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\3 - raw_text\\2017Q1_42192_MD_MMCO_Invoice.txt'
#~ key = 'KS_MMCO'
key = 'MD_MMCO'

querystring = ("SELECT * FROM invoice_logic WHERE `key` = '%s'")%key
cursor.execute(querystring)

field_names = [d[0].lower() for d in cursor.description]
rows = cursor.fetchmany()
for row in rows:
        logic.update(dict(itertools.izip(field_names, row)))

lines = open(file).read().splitlines()

for r in lines:
        for x in logic['garbage'].split(','):
                print x
                print r
                r = r.replace(str(x),'')
                print r
        
        #identification of invoice type
        #~ if logic['type'] in r:
                #~ type = str(logic['std_type'])
        
        #identification/confirmation of state code
        #~ if logic['state_code'] in r:
                #~ info = r.split(logic['state_code'])
                #~ state = info[1][:2]
        
        state = str(logic['state'])
        type = str(logic['type'])
        
        #identification of invoice number
        if logic['inv_num'] in r:
                info = r.split(logic['inv_num'])
                inv_num = info[1].strip(' ')
        
        #identification of submission/invoice quarter
        if r.startswith(logic['inv_qtr']):
                info = r.split(':')
                info = info[1].strip().split('/')
                inv_qtr = info[0]+info[1]
                qtr = info[1]+"Q"+info[0]
                util_qtr = inv_qtr
        
        #identification of billing quarter
        if r.startswith(logic['period_covered']):
                info = r.split(':')
                info = info[1].strip().split('/')
                util_qtr = info[0]+info[1]
        
        #identification and processing of invoice line item
        #assumes invoice detail lines will start with 5 numeric characters (ndc) whereas other lines will not
        if r[:5].isdigit() and r[5:6] == '-':
                
                print r
                
                #identifies product name start position with first space
                start = r.index(' ')
                
                #identifies product name ending position with key character fed in from database
                length = 6
                pattern= r"\D(\d{%d})\D" % length   # \D to avoid matching 567
                ura_string = re.findall(pattern, r)
                print ura_string
                end = r.index(ura_string[0])-3
                print end, r[end]
                
                #old way of identifying product name end position
                #~ end = r.index(logic['prod_name_end']) - 1
                
                #replaces product name from invoice line item detail
                r = r.replace(r[start:end],'')
                
                #used previously to clear out product name from invoice line item detail, however new code above attempts to do that by removing with indexing product name start/end position
                #~ for k,v in ndc_map.iteritems():
                        #~ r = r.replace(v,'').replace('  ',' ').replace('$','').replace(',','')
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
                
                human.append({'type':type,'state':state,'labeler':labeler,'prod':prod,'size':size,'inv_qtr':inv_qtr,'util_qtr':util_qtr,'inv_num':inv_num,'ndc':ndc,'name':name,'ura':ura,'units':units,'claimed':claimed,'scripts':scripts,'medi_reimb':medi_reimb,'non_medi_reimb':non_medi_reimb,'total_reimb':total_reimb,'corr_flag':corr_flag})
                
                #~ split out acella into a file for each quarter
                if labeler == '42192':
                        if util_qtr in cmsd:
                                cmsd[util_qtr].append(type+state+labeler+prod+size+util_qtr+name+ura+units+claimed+scripts+medi_reimb+non_medi_reimb+total_reimb+corr_flag)
                        else:
                                cmsd[util_qtr] = [type+state+labeler+prod+size+util_qtr+name+ura+units+claimed+scripts+medi_reimb+non_medi_reimb+total_reimb+corr_flag]

                cms.append(type+state+labeler+prod+size+util_qtr+name+ura+units+claimed+scripts+medi_reimb+non_medi_reimb+total_reimb+corr_flag)

inv_header = ['type','state','labeler','prod','size','inv_qtr','util_qtr','inv_num','ndc','name','ura','units','claimed','scripts','medi_reimb','non_medi_reimb','total_reimb','corr_flag']
with open('F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\4 - cms_format\\KS_csv.txt', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, inv_header)
        dict_writer.writeheader()
        dict_writer.writerows(human)

if labeler == '42192':
        for k,v in cmsd.iteritems():
                qtr = k[1:5]+"Q"+k[:1]
                print qtr
                with open('F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\4 - cms_format\\%s_%s_%s_%s_data.txt'%(qtr,labeler,state,type), 'wb') as output_file:
                        for r in v:
                                output_file.write(r + '\r\n')
else:
        with open('F:\\sharefile\\Shared Folders\\mft\\out\\medicaid\\4 - cms_format\\%s_%s_%s_%s_data.txt'%(qtr,labeler,state,type), 'wb') as output_file:
                for r in cms:
                        output_file.write(r + '\r\n')
print datetime.datetime.now()