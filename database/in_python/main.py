import SocketServer
import query_fielder
import ontology

class TCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print "Received comm from: " + self.client_address[0]
        self.data = self.request.recv(1024).strip()
        fielder = query_fielder.query_fielder()
        self.request.sendall( fielder.field_query(self.data, game_ontology) )



game_ontology = ontology.sampleOntology()
print "starting TCP listener"
server = SocketServer.TCPServer(("localhost", 5005), TCPHandler)
server.serve_forever()


