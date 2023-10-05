#!/usr/bin/env python3

import argparse
import os
import subprocess
import time
import random
import xmlrpc.client

#from shared import util

baseAddr = "http://localhost:"
baseClientPort = 7000
baseFrontendPort = 8001
baseServerPort = 9000

clientUID = 0
serverUID = 0

frontend = None
clientList = dict()
randdict= dict()

def add_nodes(k8s_client, k8s_apps_client, node_type, num_nodes, prefix=None):
    global clientUID
    global serverUID
    for i in range(0, num_nodes):
        if node_type == 'server':
            #server_spec = util.load_yaml('yaml/pods/server-pod.yml', prefix)
            #env = server_spec['spec']['containers'][0]['env']
            #util.replace_yaml_val(env, 'SERVER_ID', str(serverUID))
            #server_spec['metadata']['name'] = 'server-pod-%d' % serverUID
            #server_spec['metadata']['labels']['role'] = 'server-%d' % serverUID
            #k8s_client.create_namespaced_pod(namespace=util.NAMESPACE, body=server_spec)
            #util.check_wait_pod_status(k8s_client, 'role=server-%d' % serverUID, 'Running')
            os.system(f"./runserver.sh {serverUID}") 
            time.sleep(1)
            print(f"We added server: {serverUID}")
            result = frontend.addServer(serverUID)
            print(f"Server added, transaction log of server: {result}")
            serverUID += 1
        elif node_type == 'client':
            #client_spec = util.load_yaml('yaml/pods/client-pod.yml', prefix)
            #env = client_spec['spec']['containers'][0]['env']
            #util.replace_yaml_val(env, 'CLIENT_ID', str(clientUID))
            #client_spec['metadata']['name'] = 'client-pod-%d' % clientUID
            #client_spec['metadata']['labels']['role'] = 'client-%d' % clientUID
            #k8s_client.create_namespaced_pod(namespace=util.NAMESPACE, body=client_spec)
            #util.check_wait_pod_status(k8s_client, 'role=client-%d' % clientUID, 'Running')
            os.system(f"./runclient.sh {clientUID}") 
            time.sleep(1)
            print(f"We added client: {clientUID}")
            clientList[clientUID] = xmlrpc.client.ServerProxy(baseAddr + str(baseClientPort + clientUID))
            clientUID += 1
        else:
            print("Unknown pod type")
            exit()

def remove_node(k8s_client, k8s_apps_client, node_type, node_id):
    print("Shutting down server..")
    #name = node_type + '-pod-%d' % node_id
    #selector = 'role=' + node_type + '-%d' % node_id
    #k8s_client.delete_namespaced_pod(name, namespace=util.NAMESPACE)
    #util.check_wait_pod_status(k8s_client, selector, 'Terminating')

def addClient(k8s_client, k8s_apps_client, prefix):
    add_nodes(k8s_client, k8s_apps_client, 'client', 1, prefix)

def addServer(k8s_client, k8s_apps_client, prefix):
    add_nodes(k8s_client, k8s_apps_client, 'server', 1, prefix)

def listServer():
    result = frontend.listServer()
    print(result)

def killServer(k8s_client, k8s_apps_client, serverId):
    remove_node(k8s_client, k8s_apps_client, 'server', serverId)

def shutdownServer(k8s_client, k8s_apps_client, serverId):
    result = frontend.shutdownServer(serverId)
    remove_node(k8s_client, k8s_apps_client, 'server', serverId)
    print(result)

def put(key, value):
    result=clientList[random.randint(1, 100000) % len(clientList)].put(key, value)
    return result

def get(key):
    result = clientList[random.randint(1, len(clientList)) % len(clientList)].get(key)
    return result

def putdirect(key, value):
    x0=time.time()
    result=frontend.put(key, value)
    x1=time.time()
    return result+":"+str(x1-x0)

def getdirect(key):
    x0=time.time()
    result = frontend.get(key)
    x1=time.time()
    return result+":"+str(x1-x0)


def printKVPairs(serverId):
    result = frontend.printKVPairs(serverId)
    print(result)

def init_cluster(k8s_client, k8s_apps_client, num_client, num_server, ssh_key, prefix):
    global frontend

    print('Creating a frontend pod...')
    os.system(f"./runfrontend.sh") 
    time.sleep(1)
    print("Running front end")
    #frontend_spec = util.load_yaml('yaml/pods/frontend-pod.yml', prefix)
    #env = frontend_spec['spec']['containers'][0]['env']
    #k8s_client.create_namespaced_pod(namespace=util.NAMESPACE, body=frontend_spec)
    #util.check_wait_pod_status(k8s_client, 'role=frontend', 'Running')
    frontend = xmlrpc.client.ServerProxy(baseAddr + str(baseFrontendPort))

    print('Creating server pods...')
    add_nodes(k8s_client, k8s_apps_client, 'server', num_server, prefix)

    print('Creating client pods...')
    add_nodes(k8s_client, k8s_apps_client, 'client', num_client, prefix)

def event_trigger(k8s_client, k8s_apps_client, prefix):
    terminate = False
    while terminate != True:
        cmd = input("Enter a command: ")
        args = cmd.split(':')

        if args[0] == 'addClient':
            addClient(k8s_client, k8s_apps_client, prefix)
        elif args[0] == 'addServer':
            addServer(k8s_client, k8s_apps_client, prefix)
        elif args[0] == 'listServer':
            listServer()
        elif args[0] == 'killServer':
            serverId = int(args[1])
            killServer(k8s_client, k8s_apps_client, serverId)
        elif args[0] == 'shutdownServer':
            serverId = int(args[1])
            shutdownServer(k8s_client, k8s_apps_client, serverId)
        elif args[0] == 'put':
            key = int(args[1])
            value = int(args[2])
            put(key, value)
        elif args[0] == 'get':
            key = int(args[1])
            get(key)
        elif args[0] == 'printKVPairs':
            if len(args)==2:
                serverId = int(args[1])
                printKVPairs(serverId)
            else:
                print("Uses: printKVPairs:<serverid>")
        elif args[0] == 'terminate':
            terminate = True
        elif args[0]== 'heartbeat':
            frontend.updateValidServers()
        elif args[0]== 'printlog':
            print(frontend.printTransactionLog())
        elif args[0] == 'play':
            #print("Command is play!")
            playfile=str(args[1])
            try:
                with open(playfile) as f:
                    commandstrings=f.readlines()
                    for playitem in commandstrings:
                        #print("Playitem is", playitem.strip("\n"))
                        processcommands(k8s_client,k8s_apps_client,prefix,playitem.strip("\n"))
            except:
                print("Invalid command")
        else:
            print("Unknown command")


def runfunctionaltest(k8s_client, k8s_apps_client, prefix):

    global randdict
    randdict={}
    iopscount=0
    batchiop = 0 

    failpercent=10
    terminate=False
    sum=0
    sumoflatencies=0

    maxindx=100000
    maxIopSample = 1000
    maxTimeSec = 120


    starttime=time.time()
    batchstart = starttime

    while terminate != True and iopscount<maxindx*4:
        randomint=random.randint(0,maxindx-1)
        val=randomint+1
        res=putdirect(randomint,val)
        #print(f"Result of put: {res}")
        latency=res.split(":")[4]
        latency=float(latency)
        sumoflatencies+=latency
        randdict[randomint]=val

        curtime=time.time()
        difftime=curtime-starttime

        if iopscount > 0 and iopscount%maxIopSample==0:
            batchend = time.time()
            batchtime = batchend - batchstart
            batchstart = batchend
            print(f"PUT: {difftime:6.0f} Iopscount:{iopscount} iops:{batchiop/batchtime:7.3f}  latency(ms): {sumoflatencies*1000/maxIopSample:5.2f}")
            sumoflatencies=0
            batchiop = 0

        if(curtime-starttime > maxTimeSec):
            terminate=True











        iopscount+=1
        batchiop += 1








    for key,val in randdict.items():
        sum+=val
    res=frontend.getAllSums()
    print(f"All sums: {res[0]} No of servers: {res[1]} Sums: {res[2]/res[1]} Local sum: {sum}")
    print(f"Iops per second {(iopscount/difftime):7.2f}")
    return

def runfunctionaltest2(k8s_client, k8s_apps_client, prefix):

    global randdict
    iopscount=0
    maxindx=100000
    maxIopSample = 1000
    maxTimeSec = 120
    failpercent=10
    terminate=False
    sum=0
    errcount=0
    sumoflatencies=0
    count=0
    batchIopCount = 0 

    starttime=time.time()
    batchstart = starttime

    while terminate != True and iopscount<maxindx*4:
        randomint=random.randint(0,maxindx-1)
        strval=getdirect(randomint)
        val=strval.split(":")[1]
        latency=strval.split(":")[3]
        latency=float(latency)
        sumoflatencies+=latency
        if val=="ERR_KEY" and randomint in randdict:
            print(f"Problem ide! Key:{randomint} Val:{strval}")
            errcount+=1
        elif randomint in randdict:
            temp=randdict[randomint]
            if(temp==int(val)):
                count+=1
        else:
            if val=="ERR_KEY":
                count+=1
            else:
                errcount+=1

        curtime=time.time()
        difftime=curtime-starttime

        if iopscount > 0 and iopscount%maxIopSample==0:
            batchend = time.time()
            batchdifftime = batchend - batchstart
            print(f"GET: {difftime:6.0f} Iops:{iopscount} ioprate:{batchIopCount/batchdifftime:7.3f} latency(ms): {(sumoflatencies*1000/maxIopSample):5.3f}ms")
            sumoflatencies=0
            batchIopCount = 0
            batchstart = batchend

        if(curtime-starttime > maxTimeSec):
            terminate=True

        iopscount+=1
        batchIopCount += 1

    #for key,val in randdict.items():
        #sum+=val
    print(f"Error count:{errcount} Success count {count} Loop counts: {iopscount}")
    #res=frontend.getAllSums()
    #print(f"All sums: {res[0]} No of servers: {res[1]} Sums: {res[2]/res[1]} Local sum: {sum}")
    print(f"Iops per second {(iopscount/difftime):7.2f}")
    return





    '''cmd = input("Enter a command: ")
        args = cmd.split(':')

        if args[0] == 'addClient':
            addClient(k8s_client, k8s_apps_client, prefix)
        elif args[0] == 'addServer':
            addServer(k8s_client, k8s_apps_client, prefix)
        elif args[0] == 'listServer':
            listServer()
        elif args[0] == 'killServer':
            serverId = int(args[1])
            killServer(k8s_client, k8s_apps_client, serverId)
        elif args[0] == 'shutdownServer':
            serverId = int(args[1])
            shutdownServer(k8s_client, k8s_apps_client, serverId)
        elif args[0] == 'put':
            key = int(args[1])
            value = int(args[2])
            put(key, value)
        elif args[0] == 'get':
            key = int(args[1])
            get(key)
        elif args[0] == 'printKVPairs':
            if len(args)==2:
                serverId = int(args[1])
                printKVPairs(serverId)
            else:
                print("Uses: printKVPairs:<serverid>")
        elif args[0] == 'terminate':
            terminate = True
        elif args[0]== 'heartbeat':
            frontend.updateValidServers()
        elif args[0]== 'printlog':
            print(frontend.printTransactionLog())
        elif args[0] == 'play':
            #print("Command is play!")
            playfile=str(args[1])
            try:
                with open(playfile) as f:
                    commandstrings=f.readlines()
                    for playitem in commandstrings:
                        #print("Playitem is", playitem.strip("\n"))
                        processcommands(k8s_client,k8s_apps_client,prefix,playitem.strip("\n"))
            except:
                print("Invalid command")
        else:
            print("Unknown command")'''

def processcommands(k8s_client, k8s_apps_client, prefix, cmd):
        args = cmd.split(':')
        if args[0] == 'addClient':
            addClient(k8s_client, k8s_apps_client, prefix)
        elif args[0] == 'addServer':
            addServer(k8s_client, k8s_apps_client, prefix)
        elif args[0] == 'listServer':
            listServer()
        elif args[0] == 'killServer':
            serverId = int(args[1])
            killServer(k8s_client, k8s_apps_client, serverId)
        elif args[0] == 'shutdownServer':
            serverId = int(args[1])
            shutdownServer(k8s_client, k8s_apps_client, serverId)
        elif args[0] == 'put':
            key = int(args[1])
            value = int(args[2])
            put(key, value)
        elif args[0] == 'get':
            key = int(args[1])
            get(key)
        elif args[0] == 'printKVPairs':
            serverId = int(args[1])
            printKVPairs(serverId)
        elif args[0] == 'terminate':
            return
        elif args[0] == 'play':
            #print("Command is play!")
            playfile=str(args[1])
            try:
                with open(playfile) as f:
                    commandstrings=f.readlines()
                    for playitem in commandstrings:
                        pass
                        #print("Playitem is", playitem.strip("\n"))
            except:
                print("Invalid command")
        else:
            print("Unknown command")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Create a KVS cluster using Kubernetes
                                    and Kubespray. If no SSH key is specified, we use the
                                    default SSH key (~/.ssh/id_rsa), and we expect that
                                    the corresponding public key has the same path and ends
                                    in .pub. If no configuration file base is specified, we
                                    use the default ($KVS_HOME/conf/kvs-base.yml).''')

    if 'KVS_HOME' not in os.environ:
        os.environ['KVS_HOME'] = "/home/" + os.environ['USER'] + "/projects/cs380d-f23/project1/"

    parser.add_argument('-c', '--client', nargs=1, type=int, metavar='C',
                        help='The number of client nodes to start with ' +
                        '(required)', dest='client', required=True)
    parser.add_argument('-s', '--server', nargs=1, type=int, metavar='S',
                        help='The number of server nodes to start with ' +
                        '(required)', dest='server', required=True)
    parser.add_argument('--ssh-key', nargs='?', type=str,
                        help='The SSH key used to configure and connect to ' +
                        'each node (optional)', dest='sshkey',
                        default=os.path.join(os.environ['HOME'], '.ssh/id_rsa'))

    args = parser.parse_args()

    prefix = os.environ['KVS_HOME']

    #k8s_client, k8s_apps_client = util.init_k8s()
    k8s_client, k8s_apps_client = 0,0

    init_cluster(k8s_client, k8s_apps_client, args.client[0], args.server[0], args.sshkey, prefix)

    #event_trigger(k8s_client, k8s_apps_client, prefix)
    runfunctionaltest(k8s_client, k8s_apps_client, prefix)
    runfunctionaltest2(k8s_client, k8s_apps_client, prefix)

