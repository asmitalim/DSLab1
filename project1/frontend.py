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
                retrycount=4
                terminate=False
                #socket.setdefaulttimeout(1)  
                while(retrycount>=0 and terminate==False):
                    try:
                        ans=srv.heartbeatfunction()
                        temp+=f",UP:{srvid}"
                        terminate=True
                        #print(f"{ans} from {srvid} \n")
                    except:
                        retrycount-=1
                        print(f"Server {srvid}:{srv} unreachable Retrycount={retrycount}")
                        if(retrycount==0):
                            terminate=True
                            srvstopop.append(srvid)
                            temp+=f",DOWN:{srvid}"
                #socket.setdefaulttimeout(None)
            #for srvid in srvstopop:
                #kvsServers.pop(srvid)
            print("Heart beating!"+temp)
        time.sleep(4)




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
        now = datetime.datetime.now()
        #self.updateValidServers()
        #if((now-self.timeSinceLastCheck).total_seconds()>1):
            #self.updateValidServers()
        #if len(upServers) > 0:
        with lock:
            tid+=1
            flag=True
            ans=[]
            n=len(kvsServers)
            for s,srv in kvsServers.items():
                ans.append(srv.prepare(tid,key,value))
                #print("PrepareLog"+srv.printPrepareLog())
            if len(ans)==n:
                for res in ans:
                    if res==False:
                        flag=False
            if flag==False or len(ans)!= n:
                print("Put failed!")
                return "ERR_PREPARE"

            for s,srv in kvsServers.items():
                try:
                    res=srv.commit(tid,key,value)
                except:
                    print("Dangerous system state, shutdown server")
                    kvsServers.pop(s)
            transactionLog.append((tid,key,value))
        return "put:"+str(key)+":"+str(value)

        #serverId = key % len(kvsServers)
        #return kvsServers[serverId].put(key, value)

    ## get: This function routes requests from clients to proper
    ## servers that are responsible for getting the value
    ## associated with the given key.
    def get(self, key):
        #self.updateValidServers()
        #serverId = key % len(kvsServers)
        #random_variable=key % len(kvsServers)
        global lock
        with lock: 
            x0=time.time()
            length=len(kvsServers)
            random_variable=random.randint(1, length) % length
            srvid=list(kvsServers)[random_variable]
            #TODO: configure retries, lock
            retval=kvsServers[srvid].get(key)
            x1=time.time()
            return retval+":"+str(x1-x0)

    ## printKVPairs: This function routes requests to servers
    ## matched with the given serverIds.
    def printKVPairs(self, serverId):
        #self.updateValidServers()
        return kvsServers[serverId].printKVPairs()

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
        serverList = []
        with lock:
            for serverId, rpcHandle in kvsServers.items():
                serverList.append(serverId)
        return serverList
    
    def getAllSums(self):
        #self.updateValidServers()
        sums=[]
        sumofsums=0
        srvcount=0
        for srvid,srv in kvsServers.items():
            tempsum=srv.sumDict()
            sums.append([srvid,tempsum])
            sumofsums+=tempsum
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