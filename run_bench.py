# -*- coding=utf-8 -*-

import subprocess

vendors = ['aliyun', 'huawei', 'tencent', 'ucloud']
regions = {
    'aliyun': ['cn-beijing', 'cn-shanghai', 'cn-shenzhen', 'cn-chengdu', 'cn-hongkong'],
    'huawei': ['cn-north-4', 'cn-east-3', 'cn-south-1', 'cn-southwest-2', 'ap-southeast-1'],
    'tencent': ['ap-beijing', 'ap-shanghai', 'ap-guangzhou', 'ap-chengdu', 'ap-hongkong'],
    'ucloud': ['cn-bj2', 'cn-sh2', 'hk']
}
instances = {
    'aliyun': ['ecs.g6.large', 'ecs.c6.xlarge', 'ecs.r6.large', 'ecs.g6e.large', 'ecs.c6e.xlarge', 'ecs.r6e.large'],
    'huawei': ['c6.xlarge.2', 's6.large.4', 'm6.large.8'],
    'tencent': ['S5.MEDIUM8', 'C3.LARGE8', 'M5.MEDIUM16'],
    'ucloud': ['N.2.8', 'N.4.8', 'N.2.16']
}
location = 0
location2 = 0
for i in range(4):
	k = location
	if i == 3:
		k = location2
    cmd = ['python3', 'run_bench_%s.py' % vendors[i], regions.get(vendors[i])[k], str(instances.get(vendors[i])).replace("'", "")]
    with open('bench_stdout/%s' % vendors[i], 'wb', buffering=0) as fout, open('bench_stderr/%s' % vendors[i], 'wb', buffering=0) as ferr:
        subprocess.Popen(cmd, stdout=fout, stderr=ferr, bufsize=0)
    
