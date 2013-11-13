from kyoto.helpers import Router, Server
from misato.modules import FileManager, Office


class RPC(Router):

  modules = [
    FileManager,
    Office,
  ]

server = Server(RPC)
server.start()
