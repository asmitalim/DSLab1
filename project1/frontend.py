import xmlrpc.client
import xmlrpc.server
import datetime
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
import socket
import time
import threading
import random
from threading import Thread

kvsServers = dict() #all the servers which were allocated
perKeyLock=dict() #dict of locks for each key
baseAddr = "http://localhost:"
baseServerPort = 9000
primaryServer= None
tid=0
transactionLog=[]
lock = threading.Lock() #lock for list of KVSServers

class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
        pass

def updateMembership():
    global lock
    while True:
        temp=f""
        with lock:
            srvstopop=[]
            for srvid,srv in kvsServers.items():
                retrycount=20
                terminate=False 
                while(retrycount>0 and terminate==False):
                    try:
                        #socket.setdefaulttimeout(0.01) 
                        time.sleep((20-retrycount)*0.01)
                        ans=srv.heartbeatfunction()
                        #socket.setdefaulttimeout(None)
                        #temp+=f",UP:{srvid}"
                        terminate=True
                        #print(f"{ans} from {srvid} \n")
                    except:
                        retrycount-=1
                        #print(f"Server {srvid}:{srv} unreachable Retrycount={retrycount}")
                        if(retrycount==0):
                            terminate=True
                            srvstopop.append(srvid)
                            #temp+=f",DOWN:{srvid}"
            for srvid in srvstopop:
                kvsServers.pop(srvid) #removing down servers
            #print("Heart beating!"+temp)
        time.sleep(3)




class FrontendRPCServer:
    timeSinceLastCheck=0

    ## put: This function routes requests from clients to proper
    ## servers that are responsible for inserting a new key-value
    ## pair or updating an existing one.
       
    def put(self, key, value):
        global tid
        global lock
        global perKeyLock
        x0=time.time()

        with lock:
            if(len(kvsServers)==0):
                return "ERR_NOSERVERS"
            copyservers=kvsServers.copy() #making a list of KV servers
            tid+=1

        if key in perKeyLock:
            keylock=perKeyLock[key]
        else:
            perKeyLock[key]=threading.Lock()
            keylock=perKeyLock[key]
        if(keylock==None):
            return "Key lock does not exist!!"
        with keylock:
            for s,srv in copyservers.items():
                retrycount=100
                terminate=False
                while retrycount>0 and terminate==False:
                    try:
                        srv.put(key,value)
                        terminate=True
                    except:
                        retrycount-=1
                        if(retrycount==0):
                            terminate=False
        transactionLog.append((tid,key,value))
        x1=time.time()
        diff=x1-x0
        return str(key)+":"+str(value)+":"+str(diff)

    ## get: This function routes requests from clients to proper
    ## servers that are responsible for getting the value
    ## associated with the given key.
    def get(self, key):

        global lock
        global perKeyLock
        with lock: 
            copyservers=kvsServers.copy()
        if key in perKeyLock:
            keylock=perKeyLock[key]
        else:
            return "ERR_KEY"
        x0=time.time()
        length=len(copyservers)
        if length==0:
            return "ERR_NOSERVERS"
        random_variable=random.randint(1, length) % length
        srvid=list(copyservers)[random_variable]
        with keylock:
            retrycount=100
            terminate=False
            while retrycount>0 and terminate==False:
                try:
                    time.sleep((100-retrycount)*0.01)
                    retval=copyservers[srvid].get(key)
                    terminate=True
                except:
                    retrycount-=1
                    random_variable=random.randint(1, length) % length
                    srvid=list(copyservers)[random_variable]
                    if(retrycount==0):
                        terminate=False
                        return f"ERR_NOEXIST"
        x1=time.time()
        #return str(retval)+":"+str(x1-x0)
        return str(retval)

    ## printKVPairs: This function routes requests to servers
    ## matched with the given serverIds.
    def printKVPairs(self, serverId):
        if(serverId in kvsServers):
            return kvsServers[serverId].printKVPairs()
        else:
            return "ERR_NOEXIST"

    ## addServer: This function registers a new server with the
    ## serverId to the cluster membership.
    def addServer(self, serverId):
        retrycount=20
        terminate=False
        while retrycount>0 and terminate==False:
            try:
                time.sleep((20-retrycount)*0.01)
                temp = xmlrpc.client.ServerProxy(baseAddr + str(baseServerPort + serverId))
                terminate=True
            except:
                retrycount-=1
                if(retrycount==0):
                    terminate=True

        retrycount=20
        terminate=False
        while retrycount>0 and terminate==False:
            try:
                time.sleep((20-retrycount)*0.01)
                res=temp.applyLog(transactionLog)
                terminate=True
            except:
                retrycount-=1
                if(retrycount==0):
                    terminate=True

        with lock:
            kvsServers[serverId]=temp
        return res

    ## listServer: This function prints out a list of servers that
    ## are currently active/alive inside the cluster.
    def listServer(self):
        serverList = ""
        count=0
        with lock:
            for serverId, rpcHandle in sorted(kvsServers.items()):
                if(count==0):
                    serverList+=str(serverId)
                else:
                    serverList+=", "+str(serverId)
                count+=1
        if count==0:
            return "ERR_NOSERVERS"
        return serverList
    
    def getAllSums(self):
        sums=[]
        sumofsums=0
        srvcount=0
        for srvid,srv in kvsServers.items():
            tempsum=srv.sumDict()
            sums.append([srvid,tempsum])
            sumofsums ^=tempsum
            srvcount+=1
        return [str(sums), srvcount, sumofsums]


    ## shutdownServer: This function routes the shutdown request to
    ## a server matched with the specified serverId to let the corresponding
    ## server terminate normally.
    def shutdownServer(self, serverId):
        try:
            kvsServers[serverId].shutdownServer()
            time.sleep(1)
        except Exception as e:
            print(f"{e}")
        with lock:
            if serverId in kvsServers:
                kvsServers.pop(serverId)
        return "Server shutdown"
    
    def printTransactionLog(self):
        global transactionLog
        return transactionLog

server = SimpleThreadedXMLRPCServer(("localhost", 8001),logRequests=False)
server.register_instance(FrontendRPCServer())
membershipthread=Thread(target=updateMembership, name="membershipThread")
membershipthread.start()
server.serve_forever()
membershipthread.join()
