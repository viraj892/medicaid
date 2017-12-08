import time
import sys
import mysql.connector as mysql
import sharefile_lib as sf

start = time.clock()

args = sys.argv

file_path = args[1]

print 'src = ' + str(file_path)

con = mysql.connect(user='ccgremote', password='ncsuball', host='ccgazrbpo1.cumberlandcg.com', database='sharefile_api')
cursor = con.cursor()
query = "SELECT access_token from api;"
cursor.execute(query)
token = cursor.fetchone()[0]
access_token = {'access_token': token, 'subdomain': 'cumberlandcg', 'token_type': 'bearer', 'apicp': 'sharefile.com',
                'appcp': 'sharefile.com', 'admin_accounts': True, 'admin_users': True}
cursor.close()
con.close()
sf.delete_item_by_path(access_token, file_path)

print 'Time elapsed: ' + str(time.clock() - start)
