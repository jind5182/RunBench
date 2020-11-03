# -*- coding=utf-8 -*-

from ucloud.core import exc
from ucloud.client import Client
import json, time, datetime, sys
import paramiko, subprocess
import settings

def run(public_ip, public_ip2, inner_ip2, threads_num):
	while True:
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(hostname=public_ip, port=22, username="ubuntu", password="Jd123456")
		except:
			pass
		else:
			break
	while True:
		try:
			ssh2 = paramiko.SSHClient()
			ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh2.connect(hostname=public_ip2, port=22, username="ubuntu", password="Jd123456")
		except:
			pass
		else:
			break

	content = ''
	with open('./bench_script_template.sh', 'r') as f:
		content = f.read()
	content = content.replace('--num-threads=xxxxx', '--num-threads='+str(threads_num))
	with open('./bench_script.sh', 'w') as f:
		f.write(content)
		
	sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
	sftp = ssh.open_sftp()
	sftp.put('./bench_script.sh', '/home/ubuntu/bench_script.sh')
	
	print('sysbench评测中...')
	stdin, stdout, stderr = ssh.exec_command ('chmod +x bench_script.sh', get_pty=True)
	stdin, stdout, stderr = ssh.exec_command ('sh bench_script.sh', get_pty=True)
	sysbench_result = []
	for line in stdout.readlines():
		if 'total time:' in line:
			sysbench_result.append(line.split(':')[1].strip())
	print('netperf评测中...')
	stdin, stdout, stderr = ssh2.exec_command ('netserver')

	netperf_result = []
	stdin, stdout, stderr = ssh.exec_command ('netperf -l 30 -t TCP_RR -H ' + inner_ip2)
	lines = stdout.readlines()
	netperf_result.append(lines[-2].split()[-1])
	stdin, stdout, stderr = ssh.exec_command ('netperf -l 30 -t TCP_STREAM -H ' + inner_ip2)
	lines = stdout.readlines()
	netperf_result.append(lines[-1].split()[-1])
	stdin, stdout, stderr = ssh.exec_command ('netperf -l 30 -t UDP_RR -H ' + inner_ip2)
	lines = stdout.readlines()
	netperf_result.append(lines[-2].split()[-1])
	stdin, stdout, stderr = ssh.exec_command ('netperf -l 30 -t UDP_STREAM -H ' + inner_ip2)
	lines = stdout.readlines()
	try:
		netperf_result.append(lines[-3].split()[-1])
		netperf_result.append(lines[-2].split()[-1])
	except:
		print(lines, type(lines[0]))
	return sysbench_result, netperf_result

def get_json(regionid, instancetype, sysbench_result, netperf_result, startup):
	print(sysbench_result, netperf_result, round(float(str(startup).split(':')[-1]),1))
	i = datetime.datetime.now()
	with open('./%s%02d%02d/ucloud_%s_%s_%s%02d%02d' % (i.year, i.month, i.day, instancetype, regionid, i.year, i.month, i.day), 'w') as f:
		f.write(str(sysbench_result)+'\n')
		f.write(str(netperf_result)+'\n')
		f.write(str(round(float(str(startup).split(':')[-1]),1)))

def destroy_instance(client, instance_ids, zoneid):
	try:
		for instance_id in instance_ids:
			resp = client.uhost().stop_uhost_instance({
				'UHostId': instance_id
			})
		resp = client.uhost().describe_uhost_instance({
			"Zone": zoneid,
			"UHostIds": instance_ids[0:1]
		})			
		while resp.get('UHostSet')[0].get('State') != 'Stopped':
			time.sleep(1)
			resp = client.uhost().describe_uhost_instance({
				"Zone": zoneid,
				"UHostIds": instance_ids[0:1]
			})
		resp = client.uhost().terminate_uhost_instance({
			'UHostId': instance_ids[0],
			'ReleaseEIP': True,
			'ReleaseUDisk': True
		})
		resp = client.uhost().describe_uhost_instance({
			"Zone": zoneid,
			"UHostIds": instance_ids[1:]
		})			
		while resp.get('UHostSet')[0].get('State') != 'Stopped':
			time.sleep(1)
			resp = client.uhost().describe_uhost_instance({
				"Zone": zoneid,
				"UHostIds": instance_ids[1:]
			})
		resp = client.uhost().terminate_uhost_instance({
			'UHostId': instance_ids[1],
			'ReleaseEIP': True,
			'ReleaseUDisk': True
		})
	except exc.ValidationException as e:
		print('参数校验错误' + str(e))
	except exc.RetCodeException as e:
		print('后端返回 RetCode 不为 0 错误' + str(e))
	except exc.UCloudException as e:
		print('SDK 其它错误' + str(e))
	except Exception as e:
		print('其它错误' + str(e))

if __name__ == "__main__":
	regionid = sys.argv[1]  #cn-bj2
	InstanceTypes = []
	for item in sys.argv[2][1:-1].split(','):
		InstanceTypes.append(item.strip())
	PublicKey = settings.Ucloud.PublicKey
	PrivateKey = settings.Ucloud.PrivateKey

	image_ids = settings.Ucloud.image_ids
	zone_ids = settings.Ucloud.zone_ids
		
	client = Client({"region": regionid, "public_key": PublicKey, "private_key": PrivateKey, "base_url": "https://api.ucloud.cn"})

	for instancetype in InstanceTypes:
		print(instancetype)
		MachineType = instancetype.split('.')[0]
		CPU = int(instancetype.split('.')[1])
		Memory = int(instancetype.split('.')[2]) * 1024
		print('实例12启动中...')
		start = datetime.datetime.now()
		resp = client.uhost().create_uhost_instance({
			'Zone': zone_ids.get(regionid),
			'MachineType': MachineType,
			'CPU': CPU,
			'Memory': Memory,
			'LoginMode': 'Password',
			'Password': 'Jd123456',
			'ChargeType': 'Dynamic',
			"Disks": [
				{
					"IsBoot": "True",
					"Type": "CLOUD_SSD",
					"Size": 40
				}
			],
			'ImageId': image_ids.get(regionid),
			"MaxCount": 2,
			"NetworkInterface": [
				{
					"EIP": {
						"Bandwidth": 5,
						"PayMode": "Traffic",
						"OperatorName": "Bgp"
					}
				}
			]
		})
		instance_ids = resp.get('UHostIds')
		try:
			resp = client.uhost().describe_uhost_instance({
				"Zone": zone_ids.get(regionid),
				"UHostIds": instance_ids
			})
			
			while resp.get('UHostSet')[0].get('State') == 'Initializing':
				time.sleep(0.1)
				resp = client.uhost().describe_uhost_instance({
					"Zone": zone_ids.get(regionid),
					"UHostIds": instance_ids
				})
			stop = datetime.datetime.now()
			startup = stop - start
			while len(resp.get('UHostSet')[0].get('IPSet')) < 2:
				time.sleep(1)
				resp = client.uhost().describe_uhost_instance({
					"Zone": zone_ids.get(regionid),
					"UHostIds": instance_ids
				})
			public_ip = resp.get('UHostSet')[0].get('IPSet')[1].get('IP')
			
			while resp.get('UHostSet')[1].get('State') == 'Initializing' or len(resp.get('UHostSet')[1].get('IPSet')) < 2:
				time.sleep(1)
				resp = client.uhost().describe_uhost_instance({
					"Zone": zone_ids.get(regionid),
					"UHostIds": instance_ids
				})
			inner_ip2 = resp.get('UHostSet')[1].get('IPSet')[0].get('IP')
			public_ip2 = resp.get('UHostSet')[1].get('IPSet')[1].get('IP')
		except exc.ValidationException as e:
			print('参数校验错误' + str(e))
		except exc.RetCodeException as e:
			print('后端返回 RetCode 不为 0 错误' + str(e))
		except exc.UCloudException as e:
			print('SDK 其它错误' + str(e))
		except Exception as e:
			print('其它错误' + str(e))

		threads_num = CPU
		try:
			print('进行评测...')
			sysbench_result, netperf_result = run(public_ip, public_ip2, inner_ip2, threads_num)
			get_json(regionid, instancetype, sysbench_result, netperf_result, startup)
		except BaseException as e:
			print(e)
		try:
			destroy_instance(client, instance_ids, zone_ids.get(regionid))
		except BaseException as e:
			print(e)