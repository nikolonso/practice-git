import paramiko
host = 'host02.srv.local'
grep ='''| grep -A 12 \'Memory Device' | grep -A 11 'Location:' '''
try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username='root', password='PASS', port=22)
    stdin, stdout, stderr = client.exec_command('smbiosDump' + grep)
    data = stdout.read() + stderr.read()
    client.close()
except:
    print('connect SSH  Error')

data = data.decode("utf-8")
data = data.split('--')
out = {}
for i in range(0, len(data)):
    d ={}
    if len(data[i].split()) < 13:
        pass
    else:
        data_plank = data[i].split()
        index_key = data_plank.index('Size:')
        d.update({data_plank[index_key]:data_plank[index_key + 1]})
        index_key = data_plank.index('Location:')
        d.update({data_plank[index_key]:data_plank[index_key + 1]})
        index_key = data_plank.index('Manufacturer:')
        d.update({data_plank[index_key]:data_plank[index_key + 1]})
        index_key = data_plank.index('Serial:')
        d.update({data_plank[index_key]:data_plank[index_key + 1]})
        index_key = data_plank.index('Number:')
        d.update({data_plank[index_key]:data_plank[index_key + 1]})
        index_key = data_plank.index('Type:')
        d.update({data_plank[index_key]:data_plank[index_key + 2]})
        out.update({i:d})

print(out)

