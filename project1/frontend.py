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
perKeyLock=dict()
baseAddr = "http://localhost:"
baseServerPort = 9000
#upServers=[] #list of serverIds which are reachable and valid
primaryServer= None
tid=0
transactionLog=[]
lock = threading.Lock()

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
                        temp+=f",UP:{srvid}"
                        terminate=True
                        #print(f"{ans} from {srvid} \n")
                    except:
                        retrycount-=1
                        #print(f"Server {srvid}:{srv} unreachable Retrycount={retrycount}")
                        if(retrycount==0):
                            terminate=True
                            srvstopop.append(srvid)
                            temp+=f",DOWN:{srvid}"
            for srvid in srvstopop:
                kvsServers.pop(srvid)
            #print("Heart beating!"+temp)
        time.sleep(3)




class FrontendRPCServer:
    timeSinceLastCheck=0
    # TODO: You need to implement details for these functions.

    ## put: This function routes requests from clients to proper
    ## servers that are responsible for inserting a new key-value
    ## pair or updating an existing one.
    def updateValidServers1(self):
    #returns a list of [srvids,srvs] which are up
    #TODO:make this a queue
        with lock:
            for srvid,srv in kvsServers.items():
                socket.setdefaulttimeout(1)  
                try:
                    ans=srv.heartbeatfunction()
                    #print(f"{ans} from {srvid} \n")
                except:
                    print(f"Server {srvid}:{srv} unreachable")
                    kvsServers.pop(srvid)

                socket.setdefaulttimeout(None)  
        return "Okay"

        
    def put(self, key, value):
        global tid
        global lock
        global perKeyLock

        #return "put:"+str(key)+":"+str(value)+":"+str("1111.111")

        #perkeylock
        #increasing timeout
        #no return from put except ERR_NOSERVERS
        #maximum timeout
        x0=time.time()

        with lock:
            if(len(kvsServers)==0):
                return "ERR_NOSERVERS"
            copyservers=kvsServers.copy()
            tid+=1

        '''for s,srv in copyservers.items():
            retrycount=5
            terminate=False
            while retrycount>0 and terminate==False:
                try:
                    res=srv.prepare(tid,key,value)
                    if res==False:
                        return "ERR_PUT"
                    terminate=True
                except:
                    retrycount-=1
                    if(retrycount==0):
                        return "ERR_PUT"
        srvstopop=[]
        for s,srv in copyservers.items():
            retrycount=5
            terminate=False
            while retrycount>0 and terminate==False:
                try:
                    res=srv.commit(tid,key,value)
                    terminate=True
                    if(res==False):
                        srvstopop.append(s)
                except:
                    retrycount-=1
                    if(retrycount==0):
                        srvstopop.append(s)'''
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
        #self.updateValidServers()
        #serverId = key % len(kvsServers)
        #random_variable=key % len(kvsServers)

        #return f"{key}:{key}" +  ":"  +   str("99999.9999")


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
            retrycount=20
            terminate=False
            while retrycount>0 and terminate==False:
                try:
                    retval=copyservers[srvid].get(key)
                    terminate=True
                except:
                    retrycount-=1
                    random_variable=random.randint(1, length) % length
                    srvid=list(copyservers)[random_variable]
                    if(retrycount==0):
                        terminate=False
                        return f"ERR_NOEXIST+{srvid}"
        x1=time.time()
        return str(retval)+":"+str(x1-x0)
        #return str(retval)

    ## printKVPairs: This function routes requests to servers
    ## matched with the given serverIds.
    def printKVPairs(self, serverId):
        #self.updateValidServers()
        if(serverId in kvsServers):
            return kvsServers[serverId].printKVPairs()
        else:
            return "ERR_NOEXIST"

    ## addServer: This function registers a new server with the
    ## serverId to the cluster membership.
    def addServer(self, serverId):
        temp = xmlrpc.client.ServerProxy(baseAddr + str(baseServerPort + serverId))
        res=temp.applyLog(transactionLog)
        with lock:
            kvsServers[serverId]=temp
        return res

    ## listServer: This function prints out a list of servers that
    ## are currently active/alive inside the cluster.
    def listServer(self):
        #self.updateValidServers()
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
        #self.updateValidServers()
        sums=[]
        sumofsums=0
        srvcount=0
        for srvid,srv in kvsServers.items():
            tempsum=srv.sumDict()
            sums.append([srvid,tempsum])
            #sumofsums+=tempsum
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
