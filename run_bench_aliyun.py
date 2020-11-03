# -*- coding=utf-8 -*-

from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526.DescribePriceRequest import DescribePriceRequest
from aliyunsdkecs.request.v20140526.CreateInstanceRequest import CreateInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest
from aliyunsdkecs.request.v20140526.AllocatePublicIpAddressRequest import AllocatePublicIpAddressRequest
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest
import time, datetime, sys, json
import paramiko
import subprocess
import settings

# 查询主机当前状态（初始化中、'Stopped'、'Running'）
def get_instance_detail_by_id(clt, instance_id, status='Stopped'):
	request = DescribeInstancesRequest()
	request.set_InstanceIds(json.dumps([instance_id]))
	response = clt.do_action_with_exception(request)
	response = json.loads(str(response, encoding = 'utf8'))
	instance_detail = None
	if response is not None:
		instance_list = response.get('Instances').get('Instance')
		for item in instance_list:
			if item.get('Status') == status:
				instance_detail = item
				break
		return instance_detail

def create_instance(clt, imageid, InstanceType, t):
	Request = CreateInstanceRequest()		# 创建主机
	InternetChargeType = 'PayByTraffic'		# 网络付费模式
	InternetMaxBandwidthOut = '5'# 带宽
	Request.set_ImageId(imageid)
	Request.set_InstanceType(InstanceType)
	Request.set_InternetChargeType(InternetChargeType)
	Request.set_InternetMaxBandwidthOut(InternetMaxBandwidthOut)
	Request.set_Password('Jd123456')
	if len(InstanceType.split('.')[1]) == 3:
		Request.set_SystemDiskCategory('cloud_essd')

	start = datetime.datetime.now()

	Response = clt.do_action_with_exception(Request)
	Response = json.loads(str(Response, encoding = 'utf8'))# 正确返回
	instance_id = Response.get('InstanceId')

	# 阿里云需要主机初始化完成之后才能分配公网ip，即需要主机状态为Stopped，再分配ip，否则报错
	detail = get_instance_detail_by_id(clt, instance_id)
	index = 0
	while detail is None and index < 60:
		detail = get_instance_detail_by_id(clt, instance_id)
		time.sleep(0.1)

	public_ip = allocate_ip(clt, instance_id)
		
	# 启动主机
	Request = StartInstanceRequest()
	Request.set_InstanceId(instance_id)
	clt.do_action_with_exception(Request)

	detail = get_instance_detail_by_id(clt, instance_id, 'Running')
	index = 0
	while detail is None and index < 60:
		detail = get_instance_detail_by_id(clt, instance_id, 'Running')
		time.sleep(0.1)

	stop = datetime.datetime.now()
	startup = stop - start

	if t == 1:
		return instance_id, public_ip, startup
	
	if t == 2:
		inner_ip = detail.get("VpcAttributes").get("PrivateIpAddress").get("IpAddress")[0]
		return instance_id, public_ip, inner_ip

def allocate_ip(clt, instance_id):
	# 分配公网ip
	Request = AllocatePublicIpAddressRequest()
	Request.set_InstanceId(instance_id)
	Response = clt.do_action_with_exception(Request)
	Response = json.loads(str(Response, encoding = 'utf8'))
	if Response is not None:
		public_ip = Response.get('IpAddress')
	return public_ip

def destrop_instance(clt, instance_id):
	Request = DeleteInstanceRequest()
	Request.set_InstanceId(instance_id)
	Request.set_Force(True)
	clt.do_action_with_exception(Request)

def run(public_ip, public_ip2, inner_ip2, threads_num):
	while True:
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(hostname=public_ip, port=22, username="root", password="Jd123456")
		except:
			pass
		else:
			break
	while True:
		try:
			ssh2 = paramiko.SSHClient()
			ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh2.connect(hostname=public_ip2, port=22, username="root", password="Jd123456")
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
	sftp.put('./bench_script.sh', '/root/bench_script.sh')
	
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
		print('netperf UDP_STREAM failed.')
	return sysbench_result, netperf_result

def get_json(regionid, instancetype, sysbench_result, netperf_result, startup):
	print(sysbench_result, netperf_result, round(float(str(startup).split(':')[-1]),1))
	i = datetime.datetime.now()
	with open('./%s%02d%02d/aliyun_%s_%s_%s%02d%02d' % (i.year, i.month, i.day, instancetype, regionid, i.year, i.month, i.day), 'w') as f:
		f.write(str(sysbench_result)+'\n')
		f.write(str(netperf_result)+'\n')
		f.write(str(round(float(str(startup).split(':')[-1]),1)))
	'''
	香港
	['18.0360s', '10.2192s', '0.4197s', '19.9332s', '0.0731s', '9.5118s', '4.4587s', '0.3217s', '19.9657s', '0.0505s', '9.5064s', '3.9224s', '22.4798s', '31.3399s', '14.6639s', '22.3882s'] 
	['11021.53', '3016.74', '11291.26', '16113.67', '3112.52'] 
	16.7
	'''
	
if __name__ == '__main__':
	regionid = sys.argv[1]
	imageids = settings.Aliyun.imageids
	imageid = imageids[regionid] 
	InstanceTypes = []
	for item in sys.argv[2][1:-1].split(','):
		InstanceTypes.append(item.strip())
	threads_nums = {'large': 2, 'xlarge': 4, '2xlarge': 8, '3xlarge': 12}

	# 阿里云的账户信息
	AccessKeyId = settings.Aliyun.AccessKeyId
	AccessKeySecret = settings.Aliyun.AccessKeySecret

	clt = client.AcsClient(AccessKeyId, AccessKeySecret, regionid)	# 连接账号
	for InstanceType in InstanceTypes:
		print(InstanceType)
		threads_num = threads_nums[InstanceType.split('.')[-1]]
		print('创建实例1中...')
		instance_id, public_ip, startup = create_instance(clt, imageid, InstanceType, 1)
		print('创建实例2中...')
		instance_id2, public_ip2, inner_ip2 = create_instance(clt, imageid, InstanceType, 2)
		try:
			print('进行评测...')
			sysbench_result, netperf_result = run(public_ip, public_ip2, inner_ip2, threads_num)
			get_json(regionid, InstanceType, sysbench_result, netperf_result, startup)
		except BaseException as e:
			print(e)
		destrop_instance(clt, instance_id)
		destrop_instance(clt, instance_id2)
		print('实例已删除')