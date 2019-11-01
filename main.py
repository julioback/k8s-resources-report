import json
import sys
import re
from tabulate import tabulate
from subprocess import Popen, PIPE
import subprocess

def runShell(command):
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")


def formatUnity(value):
    result = value

    if 'Gi' in value:
        result = int(value.replace('Gi', '')) * 1000
        return result

    if 'Mi' in value:
        result = int(value.replace('Mi', ''))
        return result

    if 'm' in value or 'M' in value:
        result = value.replace('m', '')
        result = result.replace('M', '')
        result = int(result)
        return result

    if 'k' in value:
        result = value.replace('k', '')
        result = int(result) / 1000
        return result

    if 'Ki' in value:
        result = value.replace('Ki', '')
        result = (int(result) / 1000)
        return result

    if value.isnumeric():
        result = int(value) * 1000
        return result

    return None

command = "kubectl get nodes -o json"
nodes = runShell(command)
nodes = json.loads(nodes)
clusterReport = []
totalAllocCpu = 0
totalAllocMemory = 0
totalCapCpu = 0
totalCapMemory = 0
for item in nodes["items"]:

    kNode = item["metadata"]["labels"]["kubernetes.io/hostname"]
    
    kAllocCpu = item["status"]["allocatable"]["cpu"]
    allocCpu = formatUnity(kAllocCpu)
    totalAllocCpu += allocCpu

    kCapCpu = item["status"]["capacity"]["cpu"]
    capCpu = formatUnity(kCapCpu)
    totalCapCpu += capCpu
    
    kAllocMemory = item["status"]["allocatable"]["memory"]
    allocMemory = formatUnity(kAllocMemory)
    totalAllocMemory += allocMemory

    kCapMemory = item["status"]["capacity"]["memory"]
    #print(kCapMemory)
    #sys.exit()
    capMemory = formatUnity(kCapMemory)
    totalCapMemory += capMemory

    result = []
    result.append(kNode)
    result.append(allocCpu)
    result.append(capCpu)
    result.append(allocMemory)
    result.append(capMemory)
    clusterReport.append(result)

result = []
result.append('TOTALS')
result.append(totalAllocCpu)
result.append(totalCapCpu)
result.append(totalAllocMemory)
result.append(totalCapMemory)
clusterReport.append(result)

print(tabulate(clusterReport, headers=['Node', 'Alloc. CPU', 'Cap. CPU', 'Alloc. Memory', 'Cap. Memory']))
print("")

command = "kubectl get resourcequotas --all-namespaces -o json"
resourceQuotas = runShell(command)
resourceQuotas = json.loads(resourceQuotas)

rqReport = []
totalHardCpu = 0
totalHardMemory = 0
totalUsedCpu = 0
totalUsedMemory = 0

for item in resourceQuotas["items"]:
    #print(item["metadata"])
    #sys.exit()
    rqNamespace = item["metadata"]["namespace"]
    rqName = item["metadata"]["name"]

    rqHardCpu = item["spec"]["hard"]["limits.cpu"]
    hardCpu = formatUnity(rqHardCpu)
    totalHardCpu += hardCpu

    rqUsedCpu = item["status"]["used"]["limits.cpu"]
    usedCpu = formatUnity(rqUsedCpu)
    totalUsedCpu += usedCpu
    
    rqHardMemory = item["spec"]["hard"]["limits.memory"]
    hardMemory = formatUnity(rqHardMemory)
    totalHardMemory += hardMemory

    rqUsedMemory = item["status"]["used"]["limits.memory"]
    usedMemory = formatUnity(rqUsedMemory)
    totalUsedMemory += usedMemory

    result = []
    result.append(rqNamespace+"/"+rqName)
    result.append(hardCpu)
    result.append(usedCpu)
    result.append(hardMemory)
    result.append(usedMemory)
    rqReport.append(result)

result = []
result.append('TOTALS')
result.append(totalHardCpu)
result.append(totalUsedCpu)
result.append(totalHardMemory)
result.append(totalUsedMemory)
rqReport.append(result)
#print("totalHardCpu: %s", totalHardCpu)
print(tabulate(rqReport, headers=['Resource Quota', 'Hard CPU', 'Used CPU', 'Hard Memory', 'Used Memory']))
print("")

diffReport = []
result = []
result.append(totalAllocCpu - totalHardCpu)
result.append(totalAllocCpu - totalUsedCpu)
result.append(totalCapCpu - totalHardCpu)
result.append(totalCapCpu - totalUsedCpu)
diffReport.append(result)

print(tabulate(diffReport, headers=['CPU Alloc - Hard', 'CPU Alloc - Used', 'CPU Cap - Hard', 'CPU Cap - Used']))
print("")

diffReport = []
result = []
result.append(totalAllocMemory - totalHardMemory)
result.append(totalAllocMemory - totalUsedMemory)
result.append(totalCapMemory - totalHardMemory)
result.append(totalCapMemory - totalUsedMemory)
diffReport.append(result)

print(tabulate(diffReport, headers=['Mem Alloc - Hard', 'Mem Alloc - Used', 'Mem Cap - Hard', 'Mem Cap - Used']))
print("")

