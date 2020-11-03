# -*- coding=utf-8 -*-

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
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
	with open('./%s%02d%02d/tencent_%s_%s_%s%02d%02d' % (i.year, i.month, i.day, instancetype, regionid, i.year, i.month, i.day), 'w') as f:
		f.write(str(sysbench_result)+'\n')
		f.write(str(netperf_result)+'\n')
		f.write(str(round(float(str(startup).split(':')[-1]),1)))

def destroy_instance(client, serverIds):
	try: 
		req = models.TerminateInstancesRequest()
		params = {
			"InstanceIds": serverIds
		}
		req.from_json_string(json.dumps(params))
		resp = client.TerminateInstances(req)
	except TencentCloudSDKException as err: 
		print(err) 

if __name__ == "__main__":
	regionid = sys.argv[1]  
	InstanceTypes = []
	for item in sys.argv[2][1:-1].split(','):
		InstanceTypes.append(item.strip())
	threads_nums = {'SMALL': 1, 'MEDIUM': 2, 'LARGE': 4, '2XLARGE': 8, '3XLARGE': 12}
	
	SecretId = settings.Tencent.SecretId
	SecretKey = settings.Tencent.SecretKey

	image_ids = settings.Tencent.image_ids
	zone_ids = settings.Tencent.zone_ids
	
	for instancetype in InstanceTypes:
		print(instancetype)
		cred = credential.Credential(SecretId, SecretKey) 
		httpProfile = HttpProfile()
		httpProfile.endpoint = "cvm.tencentcloudapi.com"

		clientProfile = ClientProfile()
		clientProfile.httpProfile = httpProfile
		client = cvm_client.CvmClient(cred, regionid, clientProfile) 

		req = models.RunInstancesRequest()
		params = {
			"Placement": {
				"Zone": zone_ids.get(regionid)
			},
			"InternetAccessible": {
				"InternetChargeType": "TRAFFIC_POSTPAID_BY_HOUR",
				"InternetMaxBandwidthOut": 5,
				"PublicIpAssigned": True
			},
			"LoginSettings": {
				"Password": "Jd123456"
			},
			"InstanceCount": 2,
			"InstanceType": instancetype,
			"ImageId": image_ids.get(regionid)
		}
		req.from_json_string(json.dumps(params))
		resp = client.RunInstances(req) 
		print('实例12创建中...')
		start = datetime.datetime.now()
		instance_ids = json.loads(resp.to_json_string(), encoding='utf-8').get('InstanceIdSet')
		try: 
			req = models.DescribeInstancesStatusRequest()
			params = {
				"InstanceIds": instance_ids
			}
			req.from_json_string(json.dumps(params))
			resp = client.DescribeInstancesStatus(req) 
			status = json.loads(resp.to_json_string(), encoding='utf-8').get('InstanceStatusSet')
			while status[0].get("InstanceState") == 'PENDING':
				time.sleep(0.1)
				resp = client.DescribeInstancesStatus(req) 
				status = json.loads(resp.to_json_string(), encoding='utf-8').get('InstanceStatusSet')
			stop = datetime.datetime.now()
			startup = stop - start
			while status[1].get("InstanceState") == 'PENDING':
				time.sleep(0.1)
				resp = client.DescribeInstancesStatus(req) 
				status = json.loads(resp.to_json_string(), encoding='utf-8').get('InstanceStatusSet')
			req = models.DescribeInstancesRequest()
			params = {
				"InstanceIds": instance_ids
			}
			req.from_json_string(json.dumps(params))
			resp = client.DescribeInstances(req) 
			detail = json.loads(resp.to_json_string(), encoding='utf-8').get('InstanceSet')
			public_ip = detail[0].get('PublicIpAddresses')[0]
			public_ip2 = detail[1].get('PublicIpAddresses')[0]
			inner_ip2 = detail[1].get('PrivateIpAddresses')[0]
		
		except TencentCloudSDKException as err: 
			print(err) 

		threads_num = 0
		for key, value in threads_nums.items():
			if key in instancetype.split('.')[-1]:
				threads_num = value
				break
		
		try:
			print('进行评测...')
			sysbench_result, netperf_result = run(public_ip, public_ip2, inner_ip2, threads_num)
			get_json(regionid, instancetype, sysbench_result, netperf_result, startup)
		except BaseException as e:
			print(e)

		destroy_instance(client, instance_ids)