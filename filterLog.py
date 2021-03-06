#coding=utf-8

import os
import getopt
import sys
import string
import re
import operator  
import string

ms_factor = 1
second_factor = ms_factor * 1000
minute_factor = second_factor * 60
hour_factor = minute_factor * 60
day_factor = hour_factor * 24
month_factor = day_factor * 32
year_factor = month_factor * 12

def numTime(year, month, day, hour, minute, second, ms):
    num = int(year) * year_factor
    num = num + int(month) * month_factor
    num = num + int(day) * day_factor
    num = num + int(hour) * hour_factor
    num = num + int(minute) * minute_factor
    num = num + int(second) * second_factor
    num = num + int(ms) * ms_factor
    return num

def strTime(num):
    sTime = ""


    n =  int(num/year_factor)
    num = num - n*year_factor
    sTime = sTime + str(n) + '-'
    n =  int(num/month_factor)
    num = num - n*month_factor
    sTime = sTime + str(n) + '-'
    n =  int(num/day_factor)
    num = num - n*day_factor
    sTime = sTime + str(n) + '-'
    n =  int(num/hour_factor)
    num = num - n*hour_factor
    sTime = sTime + str(n) + '-'
    n =  int(num/minute_factor)
    num = num - n*minute_factor
    sTime = sTime + str(n) + '-'
    n =  int(num/second_factor)
    num = num - n*second_factor
    sTime = sTime + str(n) + '-'
    n =  int(num/ms_factor)
    num = num - n*ms_factor
    sTime = sTime + str(n)

    return sTime

def list_all_files(rootdir):
    _files = []
    list = os.listdir(rootdir) #列出文件夹下所有的目录与文件
    for i in range(0,len(list)):
           path = os.path.join(rootdir,list[i])
           if os.path.isdir(path):
              _files.extend(list_all_files(path))
           if os.path.isfile(path):
              _files.append(path)
    return _files

def formatLog(line):
    LevelStr = r'(?P<Level>\w+)\s*\['
    TimeStr = r'(?P<Month>\d+)\D(?P<Day>\d+)\D(?P<Hour>\d+)\D(?P<Minute>\d+)\D(?P<Second>\d+)\D(?P<MS>\d+)\D'
    FileStr = r'(?P<Code>[^\]]+)\]'
    SeqStr = r'\[(?P<SeqNum>\d+)\]'
    ModuleName = r'\s*(?P<MdName>\S*)\s*'
    ExtraInfo = r'(?P<Extra>.*)'
    reg = re.compile(LevelStr + TimeStr + FileStr + SeqStr + ModuleName + ExtraInfo)
    match = reg.match(line)
    info = match.groupdict()
    nTime = numTime('2018', info['Month'], info['Day'], info['Hour'], info['Minute'], info['Second'], info['MS'])
   
    b = {'Self':'', 'Time': nTime, 'Level': info['Level'],'MdName': info['MdName'], 'Extra': info['Extra']}
    return b
    

def filterLog(fileName, infoList, selfAlias, nodeIdAlias, accoundAlias):
        
    with open(fileName, "r", encoding='utf-8') as fidR:

        for line in fidR.readlines():
            try:
                if r"公布身份变更消息" in line:
                    # fidW.writelines(line.strip() + '\n')
                    info = formatLog(line)
                    info['Self'] = selfAlias
                    infoList.append(info) 

                elif r"区块生成" in line:
                    if r"本地发送区块验证请求" in line or r"网络发送区块验证请求" in line or r"区块插入及广播" in line:
                        # fidW.writelines(line.strip() + '\n')
                        info = formatLog(line)
                        info['Self'] = selfAlias
                        infoList.append(info) 
                        
                elif r"区块验证服务" in line:
                    if r"发出成功投票" in line or r"发出挖矿请求" in line or r"请求消息处理" in line or r"交易验证，交易数据错误" in line: 
                        # fidW.writelines(line.strip() + '\n')
                        info = formatLog(line)
                        info['Self'] = selfAlias
                        infoList.append(info) 

                elif "Miner_Work" in line:
                    if r"接收挖矿请求" in line or r"挖矿成功，高度=" in line:
                        # fidW.writelines(line.strip() + '\n')
                        info = formatLog(line)
                        info['Self'] = selfAlias
                        infoList.append(info) 

                elif "leader服务" in line:
                    if r"创建控制=成功" in line or r"Slaver" in line or r"Master" in line:
                        # fidW.writelines(line.strip() + '\n')
                        info = formatLog(line)
                        info['Self'] = selfAlias
                        infoList.append(info) 
            except:
                pass    
    return infoList

def getNodeInfo(fileName):

    nodeIdFindFlag = 0
    accoundFindFlag = 0
    nodeId = ""
    account = ""

    with open(fileName, "r", encoding='utf-8') as fidR:
        for line in fidR.readlines():
            try:
                if "main" in line and "nodeid=" in line:
                    searchObj = re.search( r'nodeid=(.*)', line, flags=0)
                    nodeId = searchObj.group(1)
                    if account != "":
                        break
                elif "Etherbase automatically configured" in line and "address=" in line:
                    searchObj = re.search( r'address=0x(.*)', line, flags=0)
                    account = searchObj.group(1)
                    if nodeId != "":
                        break                    
            except:
                pass

    return nodeId, account








if __name__=="__main__":

    opts, args = getopt.getopt(sys.argv[1:], "hi:o:")

    rootDir=""
    output_file=""

    for op, value in opts:
         if op == "-i":
             rootDir = value
         elif op == "-o":
             output_file = value
             
    if rootDir == "" or output_file == "":
        print("输入参数错误")
        sys.exit()
        
    file = list_all_files(rootDir)

   
    # with open(output_file, "w") as fidW:
    #     for v in file:
    #         nodeId, accound = getNodeInfo(v)
    #         if nodeId == '' or accound == '':
    #             continue
    #         name = {'NodeId': nodeId, 'Accound': accound, 'Alias':}
    #         infoList = filterLog(v, fidW, infoList)
    #         # print("NODE ID = %s, ACCOUND = %s\n"%(nodeId, accound))
    
    nodeCnt = 0
    file2Alias = {}
    nodeId2Alias = {}
    accound2Alias = {}
    for v in file:
        nodeId, accound = getNodeInfo(v)
        print(v + '\t')
        print(nodeId + '\t')
        print(accound + '\n')
        if nodeId == '' :
            continue
        Alias = 'Node' + str(nodeCnt)
        nodeCnt = nodeCnt + 1

        file2Alias[v] = Alias
        nodeId2Alias[nodeId] = Alias
        accound2Alias[accound] = Alias
        print("FILE:%s, NODEID:%s\n"%( v, Alias))
    
    infoList = []
    for v in file:
        if v in file2Alias.keys():
            infoList = filterLog(v, infoList, file2Alias[v], nodeId2Alias, accound2Alias)

    sorted_list = sorted(infoList, key=operator.itemgetter('Time'))
    # for v in sorted_list:
    #     print(v)
    with open(output_file, "w") as fidW:
        for v in sorted_list:
            fidW.writelines(v['Self'] + '\t\t\t')
            fidW.writelines(v['Level'] + '\t\t\t')
            fidW.writelines(strTime(v['Time']) + '\t\t\t')
            fidW.writelines(v['MdName'] + '\t\t\t')
            fidW.writelines(v['Extra'] + '\n')
