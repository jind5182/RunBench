# -*- coding=utf-8 -*-

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.http.http_config import HttpConfig
# 导入指定云服务的库 huaweicloudsdk{service}
from huaweicloudsdkecs.v2 import *
from huaweicloudsdkeip.v2 import *
import json, time, datetime, sys
import paramiko, subprocess
import settings

def get_instance_detail_by_id(client, instance_id):
	while True:
		try:
			request = ShowServerRequest()
			request.server_id = instance_id
			response = client.show_server(request)
		except exceptions.ClientRequestException as e:
			pass
		else:
			return response

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
		print(lines, type(lines[0]))
	return sysbench_result, netperf_result

def get_json(regionid, instancetype, sysbench_result, netperf_result, startup):
	print(sysbench_result, netperf_result, round(float(str(startup).split(':')[-1]),1))
	i = datetime.datetime.now()
	with open('./%s%02d%02d/huawei_%s_%s_%s%02d%02d' % (i.year, i.month, i.day, instancetype, regionid, i.year, i.month, i.day), 'w') as f:
		f.write(str(sysbench_result)+'\n')
		f.write(str(netperf_result)+'\n')
		f.write(str(round(float(str(startup).split(':')[-1]),1)))

def destroy_instance(client, serverIds):
	try:
		request = DeleteServersRequest()
		listServerIdServersPypOJ = []
		for server_id in serverIds:
			listServerIdServersPypOJ.append(ServerId(id=server_id)) 
		request.body = DeleteServersRequestBody(
			delete_publicip=True,
			delete_volume=True,
			servers=listServerIdServersPypOJ
		)
		response = client.delete_servers(request)
	except exceptions.ClientRequestException as e:
		print(e.status_code)
		print(e.request_id)
		print(e.error_code)
		print(e.error_msg)

if __name__ == "__main__":
	regionid = sys.argv[1]  #cn-north-4
	InstanceTypes = []
	for item in sys.argv[2][1:-1].split(','):
		InstanceTypes.append(item.strip())
	threads_nums = {'small': 1, 'medium': 1, 'large': 2, 'xlarge': 4, '2xlarge': 8, '3xlarge': 12}
	project_ids = settings.Huawei.project_ids
	image_ids = settings.Huawei.image_ids
	vpcids = settings.Huawei.vpcids
	subnet_ids = settings.Huawei.subnet_ids

	AccessKeyId = settings.Huawei.AccessKeyId
	SecretAccessKey = settings.Huawei.SecretAccessKey
	endpoint = "https://ecs.%s.myhuaweicloud.com" % regionid
	project_id = project_ids.get(regionid)
	image_id = image_ids.get(regionid)
	name = "bench"
	adminPass = "Jd123456"
	vpcid = vpcids.get(regionid)
	nics = [{"subnet_id": subnet_ids.get(regionid)}]
	root_volume = {"volumetype": "GPSSD"}
	availability_zone = regionid + 'a'
	count = 2

	config = HttpConfig.get_default_config()
	credentials = BasicCredentials(AccessKeyId, SecretAccessKey, project_id)

	client = EcsClient.new_builder(EcsClient) \
		.with_http_config(config) \
		.with_credentials(credentials) \
		.with_endpoint(endpoint) \
		.build()

	for instancetype in InstanceTypes:
		print(instancetype)
		request = CreatePostPaidServersRequest()
		listPostPaidServerNicNics2pjka = [
			PostPaidServerNic(
				subnet_id=nics[0].get("subnet_id")
			)
		]
		bandwidthPostPaidServerEipBandwidth = PostPaidServerEipBandwidth(
			size=5,
			sharetype="PER",
			chargemode="traffic"
		)
		eipPostPaidServerEip = PostPaidServerEip(
			iptype="5_bgp",
			bandwidth=bandwidthPostPaidServerEipBandwidth
		)
		publicipPostPaidServerPublicip = PostPaidServerPublicip(
			eip=eipPostPaidServerEip
		)
		rootVolumePostPaidServerRootVolume = PostPaidServerRootVolume(
			volumetype=root_volume.get("volumetype")
		)
		server = PostPaidServer(
			admin_pass=adminPass,
			availability_zone=availability_zone,
			count=count,
			flavor_ref=instancetype,
			image_ref=image_id,
			is_auto_rename=True,
			name=name,
			nics=listPostPaidServerNicNics2pjka,
			publicip=publicipPostPaidServerPublicip,
			root_volume=rootVolumePostPaidServerRootVolume,
			vpcid=vpcid
		)
		request.body = CreatePostPaidServersRequestBody(
			server=server
		)
		start = datetime.datetime.now()
		print('创建实例12中...')
		response = client.create_post_paid_servers(request)
		serverIds = eval(str(response)).get("server_ids")
		try: 
			response = get_instance_detail_by_id(client, serverIds[0])
			detail = eval(str(response)) 
			while detail.get('server').get('status') == "BUILD":
				time.sleep(0.1)
				response = get_instance_detail_by_id(client, serverIds[0])
				detail = eval(str(response)) 
			stop = datetime.datetime.now()
			startup = stop - start
			
			while len(detail.get('server').get("addresses").get(vpcid)) < 2:
				time.sleep(1)
				response = get_instance_detail_by_id(client, serverIds[0])
				detail = eval(str(response)) 
			
			public_ip = detail.get('server').get("addresses").get(vpcid)[1].get('addr')

			response = get_instance_detail_by_id(client, serverIds[1])
			detail = eval(str(response)) 
			while len(detail.get('server').get("addresses").get(vpcid)) < 2:
				time.sleep(1)
				response = get_instance_detail_by_id(client, serverIds[1])
				detail = eval(str(response)) 
			public_ip2 = detail.get('server').get("addresses").get(vpcid)[1].get('addr')
			inner_ip2 = detail.get('server').get("addresses").get(vpcid)[0].get('addr')

		except exceptions.ClientRequestException as e:
			print(e.status_code)
			print(e.request_id)
			print(e.error_code)
			print(e.error_msg)

		threads_num = threads_nums[instancetype.split('.')[1]]
		try:
			print('进行评测...')
			sysbench_result, netperf_result = run(public_ip, public_ip2, inner_ip2, threads_num)
			get_json(regionid, instancetype, sysbench_result, netperf_result, startup)
		except BaseException as e:
			print(e)
			
		destroy_instance(client, serverIds)