import json
import httplib
import mysql.connector as mysql

con = mysql.connect(user='root', password='ncsuball', host='127.0.0.1', database='sharefile_api')
cursor = con.cursor()

query_string = "SELECT * FROM api LIMIT 1"
cursor.execute(query_string)
field_names = [d[0].lower() for d in cursor.description]
row = cursor.fetchone()

rtoken = row[1]
client_id = row[2]
client_secret = row[3]

hostname = 'cumberlandcg.sharefile.com'
uri_path = '/oauth/token'


# client_id = 'WtkEuqCLcTPco0f1jEMzLJQxAvWl0E5x'
# client_secret = 'fs2GpV8MvZdee9az3wEIOe4bZcvyAiGVVzcSLjJ554nmkpBK'


def refresh_token(hostname, uri_path, rtoken, client_id, client_secret):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # params = {'grant_type':'refresh', 'refresh_token':rtoken, 'client_id':client_id, 'client_secret':client_secret}
    http = httplib.HTTPSConnection(hostname)
    url = uri_path + '?grant_type=refresh_token&refresh_token=' + rtoken + '&client_id=' + client_id + '&client_secret=' + client_secret
    http.request('GET', url, headers=headers)
    response = http.getresponse()

    # url = hostname + uri_path + '?grant_type=refresh_token&refresh_token=' + rtoken + '&client_id=' + client_id + '&client_secret=' + client_secret
    # response = urllib2.urlopen(url)
    token = json.loads(response.read())
    return token


access_token = refresh_token(hostname, uri_path, rtoken, client_id, client_secret)['access_token']
print access_token
insert_query = "UPDATE api SET access_token='" + str(access_token) + "' WHERE refresh_token='" + str(rtoken) + "';"
print insert_query
cursor.execute(insert_query)
con.commit()
cursor.close()
con.close()

# token = {'access_token':'O0uBzUWgBA6KjWiVf4vLYWk314sr4MMl$$XbFnkejCRZB0UDbjYrCmwSqxQGymIRVo'}
