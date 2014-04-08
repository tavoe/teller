#needed for user input
import sys
import random
import shlex
import socket
import re
#importing our stuff
import json
from RefCode.Query_Explorer import *

#must have foobar
#can have arbitrary number of arguments and/or keyword arguments
#def func(foobar, *args, **kwargs)

#Nodes have: ID, type, value, & List of Edges
#

##Workflow

#Ask for Room
#Tell about Room -- comes back with relationships
#Keep list of all objects in the room
#Search input for one of those objects
#Query about objects
#Repeat

class noun:

    def __init__(self, id):
        self.id = id
        self.relationships = []

    def get_value(self, relationship_type, default="Something"):
        value = default
        for noun_relationship in self.relationships:
            if noun_relationship.type == relationship_type:
                value = noun_relationship.value
        return value

    def get_all(self, relationship_type):
        relationships = []
        for noun_relationship in self.relationships:
            if noun_relationship.type == relationship_type:
                relationships.append(noun_relationship)
        return relationships

    def get_relationship_types(self):
        relationship_types = set()
        for relationships in self.relationships:
            relationship_types.add(relationships.type)
        return relationship_types


    def print_noun(self):
        #Testing self.get_value() -- it works
        #print(self.get_value("named"))
        return self.get_value("named")
		
class relationship:
    def __init__(self, type, value, reguarding):
        self.type = type
        self.value = value
        self.reguarding = reguarding


#This is how we contact the database
def query(query_string):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 5005))
    #print (type(s))                 #What is the type of s... -- It's a socket!
    s.send(query_string)            #It doesn't seem to like this line...
    query_response = s.recv(10000) #our replies are VERY long. GOTTA fix that. At least, don't recurse into nodes that already exist
    s.close()
    #print("query_response: ")
    #print (query_response)
    return query_response


#Give node a name and a depth; 2 is default, but you could do 10 or something, if needed.
def describe_noun(noun_name, depth=2):
	#broke up the return into 2 lines to make it more readable
    txt = '{"type": "get", "params": {"depth":'+str(depth)+'}, "search": {"edges": [{"direction": "inbound","type": "describes","weight-time": "1",' +\
           '"terminal": {"type": "relationship","edges": [{"terminal": {"type": "type","value": "named"}},{"terminal": {"type": "value","value": "'+noun_name+'"}}]}}]}}'
    return txt
    

def get_node(node_id, depth=2):
    return '{"type": "get", ' \
           '"params": {"depth":'+str(depth)+'}, ' \
                                            '"search": {"id":"'+node_id+'"}}'


def translate_type(type):
    return type


def get_node_by_name(name):

    #exp = Query_Explorer()
    query_string = describe_noun(name, 2)

    noun = get_noun(json.loads(query(query_string)))
    noun = pipe(query_string, [
        query,
        json.loads,
        get_noun
    ])


    return noun

#This will contain all the dictionaries returned from our JSON code
encyclopedia = []

#List of room contents
roomConts = {"id" : 0, "rel_id" : 1, "value" : 2, "type" : 3, "edges" : 4}

#want to create a list of nodes.
nodes = {"info":[]}
edges = {"info":[]}

def addEdge(edge):
        edges["info"].append(edge)

def edgeInfo(edge_type, weight):
        edge = {}
        edge["type"] = edge_type
        edge["weight"] = weight
        addEdge(edge)

def addNode(node):
        nodes["info"].append(node)

def nodeInfo(node_id, node_type, value, edges):
        node = {}
        node["id"]= node_id
        node["type"]= node_type
        node["value"]= value
        node["edges"]= edges
        addNode(node)


def inspectObject(node, depth=0):
    #we'll want to adjust which attributes are told about at different depths
        s = "a"
        if len(node.get_all_type("color"))>0:
            s+= " " + node.get_all_type("color")[0].value
            #if there isn't a material, go ahead and say the color
            #if depth==0 or items[obj][attr["material"]] == "!=":
                #s += " "  + items[obj][attr["color"]]
        if len(node.get_all_type("material"))>0:
            s+= " " + node.get_all_type("material")[0].value
        if len(node.get_all_type("size"))>0:
            s+= " " + node.get_all_type("size")[0].value

        if len(node.get_all_type("named"))>0:
            s+= " " + node.get_all_type("named")[0].value #the name/type of the item

        '''
        if len(node.get_all_type("has_a"))>0:
            for att in node.get_all_type("has_a"):
                if depth==0:#if this is the first layer
                        s += " with " + inspectObject(att, depth+1)
                #else: #only one iteration
                        #s += " with " + items[obj][attr["with"]]
        '''
        #fix a/an issues
        s = re.sub('\\ba ([aeiou])', 'an \\1', s)
        return s

#ideal length of method 5-15 
#http://programmers.stackexchange.com/questions/133404/what-is-the-ideal-length-of-a-method
def node(action):
	verb = ""; subject = ""
	for word in shlex.split(action):#divides the action by spaces
		if word in roomContents: subject = word; continue;
		if word in dialogsNode: verb = word; continue;
	if subject == "": return False
	if verb == "":
		print(inspectObject(subject))
	elif(verb in items[subject][attr["actions"]] ):
		print(dialogsNode[verb][0].replace("obj",subject))
	else : 
		print(dialogsNode[verb][1].replace("obj",subject))
	return True


dialogs = {             "sit"	: "You sit down cross-legged on the floor.",
			"dance"	: "You dance for a moment, though you are not sure why." 
						+ "\nIt is almost as if you are a puppet whose strings are being"
						+ "\npulled by the invisible hands of some unknown God..."
						+ "\nYou quickly dismiss that thought and return to a standing position.",
                        "lie" : "You lie down on the floor.",
                        "talk" : "You talk to yourself. Sadly, doing so provides you with no new information.",
                        "jump" : "You jump up and down. It's good for your buns and thighs."
}
def playerNode(action):
	isActionValid = False
	for d in dialogs:
		if d in action:
			isActionValid = True
			print(dialogs[d])
	if(not isActionValid):print("SYSTEM : Action not recognized")
				
    		
def Get_All_Edges(node):
    li = []
    for edge in node.get("edges"):
        terminal = edge.get("terminal")
        if terminal:
            li += [terminal]
    return li
            
def Check_Edge(node, searchFor, searchIn):
    for edge in node.get("edges"):
        if (edge.get(searchIn) == searchFor):
            #add to roomConts
            roomConts[edge.get("id")] = [edge.get("id"), edge.get("value"), edge.get("type"), edge.get("edges")]
            return edge
        else:
            tmp = Check_Terminal(edge, searchFor, searchIn)
            if tmp:
                return tmp

def Check_Terminal(edge, searchFor, searchIn):
    terminal = edge.get("terminal")
    if(terminal.get(searchIn) == searchFor):
        roomConts[terminal.get("id")] = [terminal.get("id"), terminal.get("value"), terminal.get("type"), terminal.get("edges")]
        return terminal
    else:
        tmp = Check_Edge(terminal, searchFor, searchIn)
        if tmp:
            return tmp



#Recursive Search -- look through all nodes until you find searchFor
#searchIn is the attribute to look for searchFor in.
def recSearch(queryResult, searchFor, searchIn):
    if queryResult.get("type") == "get-success":

        roomConts[queryResult.get("id")] = []
        
        for response_node in queryResult.get("reply"):

            #looks for evbery node in the edges of that node, and finds our target
            tmp = Check_Edge(response_node, searchFor, searchIn)
            if tmp:
                return tmp


def qrPrint(qrNode):
    #print("This is where more information would be... \nIF I HAD ANY!")
    pNode = qrNode.get("type")
    pNode += "; "
    pNode += qrNode.get("value")
    pNode += "; "
    pNode += qrNode.get("id")
    print(pNode)

    #nodeCheck = json.loads(query(get_node(qrNode.get("id"), 2)))
    #print(nodeCheck.get("type"))

def roomPrint():
    print("\nRoomContents: ")
    print(roomConts)

#Game Loop
def testLoop():
    while(True):
        #create some space between this and last input/output
        print("\n"),
        #input() does not work on my system, don't know why, so if it doesn't work, just try raw_input instead
        action = raw_input().lower()    #convert to lower case to prevent problems where there are none (i.e. "SIT on Chair" should work just like "sit on chair")

        #leave the game if the user wants to -- Moving it here prevents the game from yelling at the user when he/she exits ~Joe
        if action == "exit" or action == "quit":
                print("Okay, bye!")
                break 


        
        success = False
        for word in shlex.split(action):
            #User's query is the action
            queryResult = json.loads(query(describe_noun(word, 2)))

            
            #check for action in value, type, id, terminal
            node = get_node_by_name(word)
            #node = recSearch(queryResult, word, "value")
            if not node:
                node = recSearch(queryResult, word, "type")
            if not node:
                node = recSearch(queryResult, word, "id")
            if not node:
                node = recSearch(queryResult, word, "terminal")
            if node:
                success = True
                #print(roomConts[node.get("id")])
                print(node.get_value("named"))
                print(node.get_value("type"))
                print(inspectObject(node))
                #print(Get_All_Edges(node))
                
        if success:
            pass
        #do stuff with objects
        elif not playerNode(action):
            #Only access player node if you don't refer to any of the objects
            #node(action)
            pass


#create a version of recSearch that is designed to list things
def listSearch(queryResult, searchFor, searchIn):
    ls = []

    if queryResult.get("type") == "get-success":
        roomConts[queryResult.get("id")] = []
        
        for response_node in queryResult.get("reply"):

            #looks for evbery node in the edges of that node, and finds our target
            #IMPORTANT!!! -- Need to make new versions of Check_Edge and Check_Terminal that return lists
            tmp = listEdge(response_node, searchFor, searchIn, ls)
            if tmp:
                #print (tmp)
                ls+=[tmp]
                
        return ls

def listEdge (node, searchFor, searchIn, DictToStore):
    
    for edge in node.get("edges"):
        if (edge.get(searchIn) == searchFor):
            #add to roomConts
            roomConts[edge.get("id")] = [edge.get("id"), edge.get("value"), edge.get("type"), edge.get("edges")]
            return edge

        else:
            tmp = listTerminal(edge, searchFor, searchIn, DictToStore)
            
            if tmp:
                DictToStore += tmp
                return edge

def listTerminal(edge, searchFor, searchIn, DictToStore):

    terminal = edge.get("terminal")
    if(terminal.get(searchIn) == searchFor):
        roomConts[terminal.get("id")] = [terminal.get("id"), terminal.get("value"), terminal.get("type"), terminal.get("edges")]
        return DictToStore
    else:
        #see if you got anything
        tmp = listEdge(terminal, searchFor, searchIn, DictToStore)

        #if tmp exists, add it to the list we want to store things in and return the list
        if tmp:
            DictToStore += tmp
            return terminal

#Working on a function to list room contents at game start
def listRoomConts(queryResult):
    
    returnDict = listSearch(queryResult, "noun", "type")
    #print ("1")
    i = 1
    for n in returnDict:
        print (str(i) + ": ")
        print (n)
        i += 1
        
    #pass
    return returnDict
    
#Class with ID and list of properties
    #fill up from initial query
    #take room object and use toString function to print things
    #player types something in
        #if any of those words are named properties of an object, find that object
        #loop forever

class room:
    def __init__(self, contents):
        self.contents = roomConts

    def rm_print(self):
        print (roomConts)


#GAME START
#This code runs as soon as the game starts...	
#Run the game!

print("Creating Room...")
#create room
edgeInfo("contains", 1)
nodeInfo(0, "noun", "A Room", "contains")

print("You are in a room.")

queryResult = json.loads(query(describe_noun("room", 2)))   #the 2 indicates we go down to a depth of 2

#this is the room
#rm = get_node_by_name("room")

#We have a set of functions that do the obnoxious node traversal!
qrNode = listSearch(queryResult, "room", "value")

#test to see if we are getting things in roomConts, as we are supposed to
roomPrint()

#rmcts is room contents
print("\nInside the room, you can see...\n")
#rmcts = recSearch(queryResult, "noun", "type")
#print(rmcts)

#print(rm.print_noun)
#print(rm.get_relationship_types)

#rmcts = str(get_node_by_name("chair"))
#rmcts += "\n" + str(get_node_by_name("table"))
#rmcts += "\n" + str(get_node_by_name("bed"))

#print (rmcts)


#This is...another way to make a room
#testRoom = room(get_node_by_name("room"))
#print("\n")
#testRoom.rm_print()

#get relationships in room
#room_rel = rm.get_relationship_types()
#print results
#print("\nRoom relations: " + str(room_rel))

rmcts = {"id" : 0, "rel_id" : 1, "value" : 2, "type" : 3, "edges" : 4}

#listRoomConts(qrNode)

#print (rmcts)

#wait for user input
testLoop()

#GAME END


