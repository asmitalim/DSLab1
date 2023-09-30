import argparse
import xmlrpc.client
import xmlrpc.server
import sys

serverId = 0
basePort = 9000
localStore={}

class KVSRPCServer:
    # TODO: You need to implement details for these functions.

    ## put: Insert a new-key-value pair or updates an existing
    ## one with new one if the same key already exists.
    def put(self, key, value):
        localStore[key]=value
        return "[Server " + str(serverId) + "] Receive a put request: " + "Key = " + str(key) + ", Val = " + str(value)

    ## get: Get the value associated with the given key.
    def get(self, key):
        val=localStore.get(key,"ERR_KEY")
        return "[Server " + str(serverId) + "] Receive a get request: " +str(key) +":"+str(val)
        

    ## printKVPairs: Print all the key-value pairs at this server.
    def printKVPairs(self):
        retval=f"ListKVPairs: Server:{serverId} "
        for key,val in localStore.items():
            retval+=f"{key}:{val}\n"
        #return "[Server " + str(serverId) + "] Receive a request printing all KV pairs stored in this server"
        return retval
    
    ## shutdownServer: Terminate the server itself normally.
    def shutdownServer(self):
        sys.exit("Shutting down...")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '''To be added.''')

    parser.add_argument('-i', '--id', nargs=1, type=int, metavar='I',
                        help='Server id (required)', dest='serverId', required=True)

    args = parser.parse_args()

    serverId = args.serverId[0]

    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", basePort + serverId),logRequests=False)
    server.register_instance(KVSRPCServer())

    server.serve_forever()
