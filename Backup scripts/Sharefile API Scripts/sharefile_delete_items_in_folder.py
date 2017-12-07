import json
import httplib
import os
import mimetypes
import time
import urlparse
import urllib
import urllib2
import time
import sys
import re

start = time.clock()

hostname = 'cumberlandcg.sharefile.com'
uri_path = '/oauth/token'
rtoken = 'NMxbcHOxY8gN1LcCIQFGnxj6TcfLs67K$$hJiD6SJAc4gZx6ChFULH1knzaWEga7LoT26plEEJ'
client_id = 'WtkEuqCLcTPco0f1jEMzLJQxAvWl0E5x'
client_secret = 'fs2GpV8MvZdee9az3wEIOe4bZcvyAiGVVzcSLjJ554nmkpBK'

args = sys.argv

folder_path = args[1]
print 'folder_path=' + str(folder_path)


# ~ url = 'https://cumberlandcg.sharefile.com/oauth/token?grant_type=refresh_token&refresh_token=O0uBzUWgBA6KjWiVf4vLYWk314sr4MMl$$gniE4nuPBqLv6vGJ3OMxrHVXLuCoxMDmT4ORehiK&client_id=WtkEuqCLcTPco0f1jEMzLJQxAvWl0E5x&client_secret=fs2GpV8MvZdee9az3wEIOe4bZcvyAiGVVzcSLjJ554nmkpBK'

# ~ result = urllib2.urlopen(url)
# ~ print result.read()

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


access_token = refresh_token(hostname, uri_path, rtoken, client_id, client_secret)


# print access_token


# ~ urllib.urlopen(url)
# ~ result = requests.get(url)
# ~ print result

# ~ headers = {'Content-Type':'application/x-www-form-urlencoded'}

# ~ http = httplib.HTTPSConnection(hostname)
# ~ http.request('GET', uri_path, urllib.urlencode(params), headers=headers)

# def refresh_token(hostname, rtoken, client_id, client_secret,):
#     """ Authenticate via username/password. Returns json token object.

#     Args:
#     string hostname - hostname like "myaccount.sharefile.com"
#     string client_id - OAuth2 client_id key
#     string client_secret - OAuth2 client_secret key
#     string username - my@user.name
#     string password - my password """

#     uri_path = '/oauth/token'

#     headers = {'Content-Type':'application/x-www-form-urlencoded'}
#     params = {'grant_type':'refresh', 'refresh_token':rtoken, 'client_id':client_id, 'client_secret':client_secret}

#     http = httplib.HTTPSConnection(hostname)
#     http.request('GET', uri_path, urllib.urlencode(params), headers=headers)
#     response = http.getresponse()

#     print response.status, response.reason
#     token = None
#     if response.status == 200:
#         token = json.loads(response.read())
#         print 'Received token info', token

#     http.close()
#     return token

def authenticate(hostname, client_id, client_secret, username, password):
    """ Authenticate via username/password. Returns json token object.

    Args:
    string hostname - hostname like "myaccount.sharefile.com"
    string client_id - OAuth2 client_id key
    string client_secret - OAuth2 client_secret key
    string username - my@user.name
    string password - my password """

    uri_path = '/oauth/token'

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {'grant_type': 'password', 'client_id': client_id, 'client_secret': client_secret,
              'username': username, 'password': password}

    http = httplib.HTTPSConnection(hostname)
    http.request('POST', uri_path, urllib.urlencode(params), headers=headers)
    response = http.getresponse()

    print response.status, response.reason
    token = None
    if response.status == 200:
        token = json.loads(response.read())
        print 'Received token info', token

    http.close()
    return token


def get_authorization_header(token):
    return {'Authorization': 'Bearer %s' % (token['access_token'])}


def get_hostname(token):
    return '%s.sf-api.com' % (token['subdomain'])


def get_root(token, get_children=False):
    """ Get the root level Item for the provided user. To retrieve Children the $expand=Children
    parameter can be added.

    Args:
    dict json token acquired from authenticate function
    boolean get_children - retrieve Children Items if True, default is False"""

    uri_path = '/sf/v3/Items(allshared)'
    if get_children:
        uri_path = '%s?$expand=Children' % (uri_path)
    print 'GET %s%s' % (get_hostname(token), uri_path)
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print response.status, response.reason
    items = json.loads(response.read())
    print items['Id'], items['CreationDate'], items['Name']
    if 'Children' in items:
        children = items['Children']
        for child in children:
            print child['Id'], items['CreationDate'], child['Name']


def get_item_by_id(token, item_id):
    """ Get a single Item by Id.

    Args:
    dict json token acquired from authenticate function
    string item_id - an item id """

    uri_path = '/sf/v3/Items(%s)' % (item_id)
    print 'GET %s%s' % (get_hostname(token), uri_path)
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print response.status, response.reason
    items = json.loads(response.read())
    print items['Id'], items['CreationDate'], items['Name']


def multipart_form_post_upload(url, filepath):
    """ Does a multipart form post upload of a file to a url.

    Args:
    string url - the url to upload file to
    string filepath - the complete file path of the file to upload like, "c:\path\to\the.file

    Returns:
    the http response """

    newline = '\r\n'
    filename = os.path.basename(filepath)
    data = []
    headers = {}
    boundary = '----------%d' % int(time.time())
    headers['content-type'] = 'multipart/form-data; boundary=%s' % boundary
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % ('File1', filename))
    data.append('Content-Type: %s' % get_content_type(filename))
    data.append('')
    data.append(open(filepath, 'rb').read())
    data.append('--%s--' % boundary)
    data.append('')

    data_str = newline.join(data)
    headers['content-length'] = len(data_str)

    uri = urlparse.urlparse(url)
    http = httplib.HTTPSConnection(uri.netloc)
    http.putrequest('POST', '%s?%s' % (uri.path, uri.query))
    for hdr_name, hdr_value in headers.items():
        http.putheader(hdr_name, hdr_value)
    http.endheaders()
    http.send(data_str)
    return http.getresponse()


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def upload_file(token, folder_id, local_path):
    """ Uploads a File using the Standard upload method with a multipart/form mime encoded POST.

    Args:
    dict json token acquired from authenticate function
    string folder_id - where to upload the file
    string local_path - the full path of the file to upload, like "c:\\path\\to\\file.name" """

    uri_path = '/sf/v3/Items(%s)/Upload' % (folder_id)
    print 'GET %s%s' % (get_hostname(token), uri_path)
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))

    response = http.getresponse()
    upload_config = json.loads(response.read())
    if 'ChunkUri' in upload_config:
        upload_response = multipart_form_post_upload(upload_config['ChunkUri'], local_path)
        print upload_response.status, upload_response.reason
    else:
        print 'No Upload URL received'


def download_item(token, item_id, local_path):
    """ Downloads a single Item. If downloading a folder the local_path name should end in .zip.

    Args:
    dict json token acquired from authenticate function
    string item_id - the id of the item to download
    string local_path - where to download the item to, like "c:\\path\\to\\the.file" """

    uri_path = '/sf/v3/Items(%s)/Download' % (item_id)
    print 'GET %s%s' % (get_hostname(token), uri_path)
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()
    location = response.getheader('location')
    redirect = None
    if location:
        redirect_uri = urlparse.urlparse(location)
        redirect = httplib.HTTPSConnection(redirect_uri.netloc)
        redirect.request('GET', '%s?%s' % (redirect_uri.path, redirect_uri.query))
        response = redirect.getresponse()

    with open(local_path, 'wb') as target:
        b = response.read(1024 * 8)
        while b:
            target.write(b)
            b = response.read(1024 * 8)

    print response.status, response.reason
    http.close()
    if redirect:
        redirect.close()


def get_item_by_path(token, path):
    path = urlify(path)
    uri_path = '/sf/v3/Items/ByPath?path=%s' % path
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()
    return json.loads(response.read())['Id']


def get_folder_with_query_parameters(token, item_id):
    """ Get a folder using some of the common query parameters that are available. This will
    add the expand, select parameters. The following are used:

    expand=Children to get any Children of the folder
    select=Id,Name,Children/Id,Children/Name,Children/CreationDate to get the Id, Name of the folder
    and the Id, Name, CreationDate of any Children

    Args:
    dict json token acquired from authenticate function
    string item_id - a folder id """

    uri_path = '/sf/v3/Items(%s)?$expand=Children&$select=Id,Name,Children/Id,Children/Name,Children/CreationDate' % (
        item_id)
    print 'GET %s%s' % (get_hostname(token), uri_path)
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print response.status, response.reason
    items = json.loads(response.read())
    print items['Id'], items['Name']
    if 'Children' in items:
        children = items['Children']
        for child in children:
            print child['Id'], child['CreationDate'], child['Name']

    http.close()


def delete_item(token, item_id):
    """ Delete an Item by Id.

    Args:
    dict json token acquired from authenticate function
    string item_id - the id of the item to delete """

    uri_path = '/sf/v3/Items(%s)' % (item_id)
    print 'DELETE %s%s' % (get_hostname(token), uri_path)
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('DELETE', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print response.status, response.reason
    http.close()


def raw(text):
    escape_dict = {'\a': r'\a',
                   '\b': r'\b',
                   '\c': r'\c',
                   '\f': r'\f',
                   '\n': r'\n',
                   '\r': r'\r',
                   '\t': r'\t',
                   '\v': r'\v',
                   '\'': r'\'',
                   '\"': r'\"',
                   '\0': r'\0',
                   '\1': r'\1',
                   '\2': r'\2',
                   '\3': r'\3',
                   '\4': r'\4',
                   '\5': r'\5',
                   '\6': r'\6',
                   '\7': r'\7',
                   '\8': r'\8',
                   '\9': r'\9',
                   '\256': r'\256'}  # notice this line is the first 3 digits of the resolution

    for k in escape_dict:
        if text.find(k) > -1:
            text = text.replace(k, escape_dict[k])

    return text


# token=authenticate('cumberlandcg.sf-api.com','WtkEuqCLcTPco0f1jEMzLJQxAvWl0E5x','fs2GpV8MvZdee9az3wEIOe4bZcvyAiGVVzcSLjJ554nmkpBK','brian.coleman@cumberlandcg.com','Ncsuball#1')


# access_token = refresh_token(hostname, uri_path, rtoken, client_id, client_secret)['access_token']

# auth_header = get_authorization_header(token)
# print auth_header

# root= get_root(token, False)
# print 'root: '
# print root

# upload_file(access_token, 'foe8a907-3b64-4815-bab8-d662e4fb485e', 'test_file.pdf')
# get_folder_with_query_parameters(access_token, 'foe8a907-3b64-4815-bab8-d662e4fb485e')

def urlify(path):
    path = raw(path)
    return path.replace(' ', '%20').replace('\\', '/')


# Download item by path
def download_item_by_path(token, src_file, dest_file):
    print 'dest=' + str(dest_file)

    print 'src_id=' + str(get_item_by_path(access_token, src_file))

    """
    Downloads item from source to destination

    :param token: access_token
    :param src_file: absolute path (from the root folder) of the source file including filename
    :param dest_file: relative/absolute path (local) of the destination including filename
    """
    download_item(token, get_item_by_path(access_token, urlify(src_file)), dest_file)


def upload_item_by_path(token, src_file, dest_file):
    upload_file(token, src_file, get_item_by_path(access_token, urlify(dest_file)))


def delete_item_by_path(token, file_path):
    """
    :param token: access token
    :param file_path: absolute path (from the root folder) of the file to be deleted including filename
    :return: HTTP 204 if successful delete
    """
    delete_item(token, get_item_by_path(token, file_path))


# TODO
def copy_item_by_path(token, src, dest, overwrite=False):
    src_id = get_item_by_path(token, urlify(src))
    print 'src_id: ' + str(src_id)
    dest_id = get_item_by_path(token, dest)
    print 'dest_id: ' + str(dest_id)
    uri_path = "/sf/v3/Items(%s)/Copy" % src_id
    params = {"targetid": str(dest_id), "overwrite": overwrite}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    http = httplib.HTTPSConnection(get_hostname(token))
    # print 'request: POST' + str(uri_path) + str(urllib.urlencode(params))
    http.request('POST', uri_path, urllib.urlencode(params), headers=headers)
    response = http.getresponse()
    print 'Copy response:'
    print response.status, response.reason


def get_children_id(token, folder_id):
    """

    :param token: json dict access_token
    :param folder_id: item id of the parent folder
    :return: list of items ids of the children of parent folder
    """
    item_ids = []
    uri_path = "/sf/v3/Items(%s)/Children?includeDeleted=false" % folder_id
    print 'GET %s%s' % (get_hostname(token), uri_path)
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    http = httplib.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()
    print 'Get Children ID response:'
    print response.status, response.reason
    items = json.loads(response.read())['value']
    for item in items:
        item_ids.append(item['Id'])
    return item_ids


def get_children_id_by_path(parent_folder):
    """
    Get all the children of the specified folder
    :param token:
    :param parent_folder: absolute Sharefile path to the parent directory
    :return: list of items ids of the children of parent folder
    """
    return get_children_id(access_token, get_item_by_path(access_token, parent_folder))


def delete_all_items_in_folder(token, folder_path):
    item_ids = get_children_id_by_path(folder_path)
    for item_id in item_ids:
        print 'deleting item : ' + str(item_id)
        delete_item(token, item_id)


delete_all_items_in_folder(access_token, folder_path)

print 'Time elapsed: ' + str(time.clock() - start)
