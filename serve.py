from kyoto.server import BertRPCServer as Server
from misato.modules import FileManager, Office


server = Server([FileManager, Office], ('localhost', 1337))
server.serve_forever()
