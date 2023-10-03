import xmlrpc.client
import xmlrpc.server
import datetime
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
import socket
import time

kvsServers = dict() #all the servers which were allocated
baseAddr = "http://localhost:"
baseServerPort = 9000
upServers=[] #list of serverIds which are reachable and valid
primaryServer= None
tid=0
transactionLog=[]

class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
        pass

class FrontendRPCServer:
    timeSinceLastCheck=0
    # TODO: You need to implement details for these functions.

    ## put: This function routes requests from clients to proper
    ## servers that are responsible for inserting a new key-value
    ## pair or updating an existing one.
    def updateValidServers(self):
    #returns a list of [srvids,srvs] which are up
    #TODO:make this a queue
        for srvid,srv in kvsServers.items():
            socket.setdefaulttimeout(1)  
            try:
                ans=srv.heartbeatfunction()
                print(f"{ans} from {srvid} \n")
                if srvid not in upServers:
                    upServers.append(srvid)
            except:
                print(f"Server {srvid}:{srv} unreachable")
                if srvid in upServers:
                    upServers.remove(srvid)

            socket.setdefaulttimeout(None)  
        return "Okay"

        
    def put(self, key, value):
        global primaryServer
        global tid
        now = datetime.datetime.now()
        #if((now-self.timeSinceLastCheck).total_seconds()>1):
            #self.updateValidServers()
        #if len(upServers) > 0:
        tid+=1
        flag=True
        ans=[]
        n=len(upServers)
        for s in upServers:
            ans.append(kvsServers[s].prepare(tid,key,value))
            print("PrepareLog"+kvsServers[s].printPrepareLog())
        if len(ans)==n:
            for res in ans:
                if res==False:
                    flag=False
        if flag==False or len(ans)!= n:
            print("Put failed!")
            return "ERR_PREPARE"

        for s in upServers:
            try:
                res=kvsServers[s].commit(tid,key,value)
            except:
                print("Dangerous system state, shutdown server")
                return "ERR_COMMIT"
        transactionLog.append((tid,key,value))
        return "put:"+str(key)+":"+str(value)

        #serverId = key % len(kvsServers)
        #return kvsServers[serverId].put(key, value)

    ## get: This function routes requests from clients to proper
    ## servers that are responsible for getting the value
    ## associated with the given key.
    def get(self, key):
        serverId = key % len(kvsServers)
        return kvsServers[serverId].get(key)

    ## printKVPairs: This function routes requests to servers
    ## matched with the given serverIds.
    def printKVPairs(self, serverId):
        return kvsServers[serverId].printKVPairs()

    ## addServer: This function registers a new server with the
    ## serverId to the cluster membership.
    def addServer(self, serverId):
        temp = xmlrpc.client.ServerProxy(baseAddr + str(baseServerPort + serverId))
        res=temp.applyLog(transactionLog)
        kvsServers[serverId]=temp
        self.updateValidServers()
        return res

    ## listServer: This function prints out a list of servers that
    ## are currently active/alive inside the cluster.
    def listServer(self):
        serverList = []
        for serverId, rpcHandle in kvsServers.items():
            serverList.append(serverId)
        return serverList

    ## shutdownServer: This function routes the shutdown request to
    ## a server matched with the specified serverId to let the corresponding
    ## server terminate normally.
    def shutdownServer(self, serverId):
        try:
            kvsServers[serverId].shutdownServer()
            time.sleep(1)
        except Exception as e:
            print(f"{e}")
        self.updateValidServers()
        kvsServers.pop(serverId)
        return "Server shutdown"
    
    def printTransactionLog(self):
        global transactionLog
        return transactionLog

server = SimpleThreadedXMLRPCServer(("localhost", 8001),logRequests=False)
server.register_instance(FrontendRPCServer())

server.serve_forever()
