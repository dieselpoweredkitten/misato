from kyoto.server import BertRPCServer
from misato.modules import FileManager, Office


server = BertRPCServer([FileManager, Office])
server.serve_forever()
