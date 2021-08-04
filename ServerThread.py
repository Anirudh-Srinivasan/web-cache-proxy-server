import threading
import socket
import requests
import pickle
totalHit = 0
totalMiss = 0
class ThreadedServer():
    def __init__(self, port):
        self.port=port
        self.host='localhost'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))        
        print("{} Connected to {}".format(self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            print("Got Address from:", address)
            #client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def fetch_response(self, capacity, cache,  url):
        if url in cache.keys(): 
            #print("Hit")
            global totalHit
            totalHit += 1
            requestStatus = 'Hit'
            cache[url][1] += 1
            return (cache[url][0], requestStatus)
        else:
            #print("Miss") 
            global totalMiss
            totalMiss += 1
            requestStatus = 'Miss'
            lowfreq=36000
            if(len(cache) == capacity):
                for key,val in cache.items():
                    if(lowfreq>val[1]):
                        lowfreq = val[1]
                        lowurl = key
                del cache[lowurl]
                cache[url] = [requests.get(url), 1]                   
            else:
                cache[url] = [requests.get(url), 1]
            self.write_to_cache(cache)
        return (cache[url][0], requestStatus)

    def write_to_cache(self, cache):
        with open('Cached.cache', 'wb') as fin:
            pickled = pickle.dumps(cache)
            fin.write(pickled)

    def listenToClient(self, client, address):
        print("Listening to ", address)
        size = 4096        
        url = client.recv(size).decode()       
        try:
            recv = b""
            with open('Cached.cache', 'rb') as fout:                
                recv = fout.read(-1)
                cache = pickle.loads(recv)
                response, requestStatus = self.fetch_response(3, cache, url)
        except FileNotFoundError as error: 
            #print("Miss")
            requestStatus = 'Miss'
            global totalMiss
            totalMiss += 1
            with open('Cached.cache', 'wb') as fin:                
                response = requests.get(url)
                cache = {url:[response,1]}
                pickled = pickle.dumps(cache)
                fin.write(pickled)
        # Sending Request Status and hit,miss in Cache
        cacheStatus = [requestStatus, totalHit, totalMiss]
        client.send(pickle.dumps(cacheStatus))
        # Receiving Acknowledgement
        if(client.recv(1024).decode() == 'OK'):
            # Sending the entire file
            client.send(pickle.dumps(response))        
        print("Bye! ", address)
        client.close()

if __name__ == "__main__":
    server = ThreadedServer(8085)
    server.listen()