My KV server works in the following way:
1. I have a lock for the list of total servers.
2. I also have a list of locks for each key.
3. HEARTBEAT: The heartbeat function runs every 3 seconds. It acquires a lock on the
list of servers, goes through this list, and calls a heartbeat function in server.py.
It retries this 20 times, with increasing amount of timeout.
If it fails, then it appends the server to a list of servers to remove.
It removes all the dead servers at the end.
4. PUT: The frontend acquires a lock on the list of servers, copies this over, updates transaction ID, and releases
the lock. Then, for the given key, it either acquires the keylock from the list of locks,
or, it creates a keylock if it hasn't seen the key before.
Now, with the keylock for the key, it tries to call the put operation of the server.
It retries this upto 100 times. Finally, it adds the put operation to the transaction log.
5. GET:
The frontend gets the serverlist lock, copies over the list of servers.
Then, it generates a random integer from [0,len(serverlist)], and accesses the server ID at this position.
It retries the get operation upto 100 times, with increasing timeout.
Everytime the get operation fails, it regenerates the random integer to try a different server id.
6. ADDSERVER:
Frontend tries to add a server at the port upto 20 times with increasing timeout.
It then tries to copy over the transactionLog so far, upto 20 times again with increasing timeout.
It finally acquires the serverlist lock and adds the serverID to this list.

Note: My code runs with all tests cases in testKVS command.

