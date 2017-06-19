import redis

client = redis.StrictRedis( host='localhost', port = 6379)

id = 1
users = client.smembers('users')

json = '{"users":['

i=0
for x in users:
    m = x.encode('ascii', 'ignore').split(':')
    if int(m[0]) != 1:
        if i!=0:
            json += ','
        json += '{{"id": {}, "username": "{}"}}'.format(m[0], m[1])
        i+=1

json += ']}'
print(json)
