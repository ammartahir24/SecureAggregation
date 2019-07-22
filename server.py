from flask import *
from flask_socketio import SocketIO,emit
from flask_socketio import *
import json
import codecs
import pickle
import numpy as np


class secaggserver:
	def __init__(self,host,port,n,k):
		self.n = n
		self.k = k
		self.aggregate = np.zeros((10,10))
		self.host = host
		self.port = port
		self.numkeys = 0
		self.responses = 0
		self.secretresp = 0
		self.othersecretresp = 0
		self.respset = set()
		self.resplist = []
		self.ready_client_ids = set()
		self.client_keys = dict()
		self.app = Flask(__name__)
		self.socketio = SocketIO(self.app)
		self.register_handles()

	def weights_encoding(self, x):
		return codecs.encode(pickle.dumps(x), 'base64').decode()

	def weights_decoding(self, s):
		return pickle.loads(codecs.decode(s.encode(),'base64'))


	def register_handles(self):

		@self.socketio.on("wakeup")
		def handle_wakeup():
			print("Recieved wakeup from",request.sid)
			emit("send_public_key",{
        		"message":"hey I'm server",
        		"id":request.sid
				})

		@self.socketio.on("connect")
		def handle_connect():
			print(request.sid, " Connected")
			self.ready_client_ids.add(request.sid)
			print('Connected devices:', self.ready_client_ids)
			

		@self.socketio.on('public_key')
		def handle_pubkey(key):
			print(request.sid,'sent key:',key['key'])
			self.client_keys[request.sid] = key['key']
			self.numkeys+=1
			self.respset.add(request.sid)
			print('keys: ', self.client_keys)
			if(self.numkeys==self.n):
				print "Starting public key transfer"
				ready_clients = list(self.ready_client_ids)
				key_json = json.dumps(self.client_keys)
				for rid in ready_clients:
					emit('public_keys',key_json,room=rid)

		@self.socketio.on('weights')
		def handle_weights(data):
			print(request.sid,"sent weights")
			if self.responses<self.k:
				self.aggregate+=self.weights_decoding(data['weights'])
				emit('send_secret',{
					'msg':"Hey I'm server"
					})
				print("MESSAGE SENT TO",request.sid)
				self.responses+=1
				self.respset.remove(request.sid)
				self.resplist.append(request.sid)
			else:
				emit('late',{
					'msg':"Hey I'm server"
					})
				self.responses+=1
			if self.responses==self.k:
				print("k WIGHTS RECIEVED. BEGINNING AGGREGATION PROCESS.")
				absentkeyjson = json.dumps(list(self.respset))
				for rid in self.resplist:
					emit('send_there_secret',absentkeyjson,room=rid)

		@self.socketio.on('secret')
		def handle_secret(data):
			print request.sid,"sent SECRETTTT"
			self.aggregate+=self.weights_decoding(data['secret'])
			self.secretresp+=1
			if self.secretresp==self.k and self.othersecretresp==self.k:
				print("FINAL WEIGHTS:",self.aggregate)
				return self.aggregate

		@self.socketio.on('rvl_secret')
		def handle_secret_reveal(data):
			print request.sid,"sent SHAREDDDDD secrets"
			self.aggregate+=self.weights_decoding(data['rvl_secret'])
			self.othersecretresp+=1
			if self.secretresp==self.k and self.othersecretresp==self.k:
				print("FINAL WEIGHTS:",self.aggregate)
				return self.aggregate			

		@self.socketio.on('disconnect')
		def handle_disconnect():
			print(request.sid, " Disconnected")
			if request.sid in self.ready_client_ids:
				self.ready_client_ids.remove(request.sid)
			print(self.ready_client_ids)


	def start(self):
		self.socketio.run(self.app,host=self.host, port=self.port)


if __name__ == '__main__':
    server = secaggserver("127.0.0.1", 2019, 3, 2)
    print("listening on 127.0.0.1:2019");
    server.start()