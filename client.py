from socketIO_client import SocketIO, LoggingNamespace
from random import randrange
import numpy as np
from copy import deepcopy
import codecs
import pickle



class SecAggregator:
	def __init__(self,common_base,common_mod,dimensions,weights):
		self.secretkey = randrange(common_mod)
		self.base = common_base
		self.mod = common_mod
		self.pubkey = (self.base**self.secretkey) % self.mod
		self.sndkey = randrange(common_mod)
		self.dim = dimensions
		self.weights = weights
	def public_key(self):
		return self.pubkey
	def generate_weights(self,seed):
		np.random.seed(seed)
		return np.random.rand(self.dim)
	def prepare_weights(self,shared_keys):
		wghts = deepcopy(self.weights)
		for each in shared_keys:
			wghts+=generate_weights(each)
		wghts+=generate_weights(self.sndkey)
		return wghts


class secaggclient:
	def __init__(self,serverhost,serverport):
		self.sio = SocketIO(serverhost,serverport,LoggingNamespace)
		self.aggregator = SecAggregator(2,100255,(10,10),np.zeros((10,10)))
		self.id = ''
		self.register_handles()
		print("init")
		self.sio.emit("wakeup")
		self.sio.wait()

	def weights_encoding(self, x):
		return codecs.encode(pickle.dumps(x), 'base64').decode()

	def weights_decoding(self, s):
		return pickle.loads(codecs.decode(s.encode(),'base64'))

	def register_handles(self):
		def on_connect(*args):
			msg = args[0]
			self.sio.emit("connect")
			print("Connected and recieved this message",msg['message'])

		def on_send_pubkey(*args):
			msg = args[0]
			self.id = msg['id']
			pubkey = {
				'key': self.aggregator.public_key()
			}
			self.sio.emit('public_key',pubkey)

		def on_sharedkeys(*args):
			keydict = json.loads(args[0])
			sharedkeys = []
			pubkey = self.aggregator.public_key()
			for ids in keydict:
				if ids != self.id:
					sharedkeys.append(keydict[ids]**pubkey)
			weight = self.aggregator.prepare_weights(sharedkeys)
			weight = self.weights_encoding(weight)
			resp = {
				'weights':weight
			}
			self.sio.emit('weights',resp)

		def on_disconnect(*args):
			msg = args[0]
			self.sio.emit("disconnect")
			print("Disconnected",msg['message'])
		self.sio.on('connect', on_connect)
		self.sio.on('disconnect', on_disconnect)
		self.sio.on('send_public_key',on_send_pubkey)

if __name__=="__main__":
	secaggclient("127.0.0.1",2019)
	print("Ready")