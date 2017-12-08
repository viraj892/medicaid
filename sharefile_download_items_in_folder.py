import time
import sys
import mysql.connector as mysql
import sharefile_lib as sf

start = time.clock()

args = sys.argv

folder_path = args[1]
local_path = args[2]
print 'parent_folder = ' + str(folder_path)
print 'local_path = ' + str(local_path)

con = mysql.connect(user='ccgremote', password='ncsuball', host='ccgazrbpo1.cumberlandcg.com', database='sharefile_api')
cursor = con.cursor()
query = "SELECT access_token from api;"
cursor.execute(query)
token = cursor.fetchone()[0]
access_token = {'access_token': token, 'subdomain': 'cumberlandcg', 'token_type': 'bearer', 'apicp': 'sharefile.com',
                'appcp': 'sharefile.com', 'admin_accounts': True, 'admin_users': True}
cursor.close()
con.close()

sf.download_all_items_in_folder(access_token, folder_path, local_path)

print 'Time elapsed: ' + str(time.clock() - start)
