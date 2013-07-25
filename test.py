from LogentriesSDK.client import Client

logentries = Client('cc639a67-1d48-448b-b5f2-85adbe16e79a')

new_host = logentries.create_host('myscripthost')

new_log = logentries.create_log_token( new_host, 'mynewlog' )

output = logentries.to_json()

#f = open('output.txt', 'w')
#f.write(output)
#f.close()
