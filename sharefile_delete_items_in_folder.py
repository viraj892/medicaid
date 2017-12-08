import time
import sys
import mysql.connector as mysql

import sharefile_lib as sf

start = time.clock()

# hostname = 'cumberlandcg.sharefile.com'
# uri_path = '/oauth/token'
# rtoken = 'NMxbcHOxY8gN1LcCIQFGnxj6TcfLs67K$$hJiD6SJAc4gZx6ChFULH1knzaWEga7LoT26plEEJ'
# client_id = 'WtkEuqCLcTPco0f1jEMzLJQxAvWl0E5x'
# client_secret = 'fs2GpV8MvZdee9az3wEIOe4bZcvyAiGVVzcSLjJ554nmkpBK'

args = sys.argv

folder_path = args[1]
print 'folder_path=' + str(folder_path)

con = mysql.connect(user='ccgremote', password='ncsuball', host='ccgazrbpo1.cumberlandcg.com', database='sharefile_api')
cursor = con.cursor()
query = "SELECT access_token from api;"
cursor.execute(query)
token = cursor.fetchone()[0]
access_token = {'access_token': token, 'subdomain': 'cumberlandcg', 'token_type': 'bearer', 'apicp': 'sharefile.com',
                'appcp': 'sharefile.com', 'admin_accounts': True, 'admin_users': True}

cursor.close()
con.close()

sf.delete_all_items_in_folder(access_token, folder_path)

print 'Time elapsed: ' + str(time.clock() - start)
