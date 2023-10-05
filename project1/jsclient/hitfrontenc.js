xmlrpc = require('node-xmlrpc')



var client = xmlrpc.createClient({
    host:'localhost',
    port: 8001,
    path : '/RPC2',
   
});

console.log(client)

console.log("Calling put first");



client.methodCall('put',[1004,2300], (err,val) => {
    console.log('put responded with data');
    if(err) {
        console.log("1.Error: ",err);
        } else {
            console.log("Value is ", val);

                for( i = 0 ; i < 1000 ; i ++) {
                client.methodCall('get',[i], (err,val) => {
                    console.log('get responded with data');
                    if(err) {
                        console.log("2.Error: ",err);
                        } else {
                            console.log("Value is ", val);
                            }
                    });
                }

            }
    });
