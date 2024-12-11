from .Utils import Utils
from .Events import EventHandler
from .keywords import EntityKeyword

class ImmortalEntity:
    @staticmethod
    def getEntity():
        entity = {
                      "Properties": {
                          "context": {}
                      },
                      "Nodes": [],
                      "Actions": [],
                    }
        return entity

    @staticmethod
    def getNode():
        node = {
                  "ID": "",
                  "Mapping": [],
                  "VideoDataKey": "",
                  "Title": "",
                  "Question": "",
                  "Events": {
                    "OnEnter": [
                    ],
                    "OnLeave": {
                    }
                  },
                  "Data":{
                  },
                  "Temporary":{

                  }
              }
        id = Utils.generateId()
        node["ID"] = id
        return node

    def getActionNode(self):
        node = {
                  "ID": "",
                  "Mapping": [],
                  "VideoDataKey": "",
                  "Action": "",
                  "Title": "",
                  "Question": "",
                  "Events": {
                    "OnEnter": [
                    ],
                    "OnLeave": {
                    }
                  },
                  "Data":{
                  },
                  "Temporary":{

                  }
              }
        id = Utils.generateId()
        node["ID"] = id
        return node

    @staticmethod
    def getPrevNode(node)->list:
        print(f"getNode:{node}")
        mapping = node["Mapping"]
        prevKey = ''
        foundparent = False
        for item in mapping:
            if item.keys().__contains__("Parent"):
                prevKey = item["Parent"]
                foundparent = True
        if not foundparent:
            mapping.append({"Parent": ""})
        # if not mapping.keys().__contains__("Parent"):
        #     mapping.setdefault("Parent", [])
        # prevKey = mapping["Parent"]
        if prevKey is None or len(prevKey) == 0:
            return []
        return prevKey.split(',')

    @staticmethod
    def setPrevNode(node, key):
        prevNodes = ImmortalEntity.getPrevNode(node)
        if not prevNodes.__contains__(key):
            prevNodes.append(key)
        mapping = node["Mapping"]
        for item in mapping:
            # print(f"item {item}")
            # print(f"type of item {type(item)}")
            if item.keys().__contains__("Parent"):
                item["Parent"] = ",".join(prevNodes)
        pass

    @staticmethod
    def getNodeById(entity, nodeid):
        # print(f"node:{entity}")
        nodes = entity["Nodes"]
        for nd in nodes:
            if nd["ID"] == nodeid:
                return nd
        return None

    @staticmethod
    def getDataField(node:dict):
        dataname = EntityKeyword.data
        if not node.keys().__contains__(dataname):
            node.setdefault(dataname, {})
        return node[dataname]

    @staticmethod
    def setTitleOverride(node:dict, overridenodeid:str, newtitle:str):
        data:dict = ImmortalEntity.getDataField(node)
        overidekey = EntityKeyword.overridetitle
        if not data.keys().__contains__(overidekey):
            data.setdefault(overidekey, {})
        overridesection:dict = data[overidekey]
        if not overridesection.keys().__contains__(overridenodeid):
            overridesection.setdefault(overridenodeid, newtitle)
        else:
            overridesection[overridenodeid] = newtitle
        return node

    @staticmethod
    def getTitleOverride(node:dict, overridenodeid)->str:
        defaultTitle = node["Title"]
        data:dict = ImmortalEntity.getDataField(node)
        if not data.keys().__contains__(EntityKeyword.overridetitle):
            return defaultTitle
        overridesection:dict = data[EntityKeyword.overridetitle]
        if not overridesection.keys().__contains__(overridenodeid):
            return defaultTitle
        return overridesection[overridenodeid]


    @staticmethod
    def searchNext(entity, nodeid, context:dict)->tuple:
        listnode = []
        listactions = []
        nodes = entity["Nodes"]
        for nd in nodes:
            ismatched = EventHandler.conditionMapping(nodeid, context, nd)
            # nodeids = ImmortalEntity.getPrevNode(nd)
            # if nodeids.__contains__(nodeid):
            overrideTitle = ImmortalEntity.getTitleOverride(nd, nodeid)
            if ismatched:
                listnode.append({"ID": nd["ID"], "Title":overrideTitle, "Question": nd["Question"]})

        if entity.keys().__contains__('Actions'):
            actions = entity["Actions"]
            for nd in actions:
                ismatched = EventHandler.conditionMapping(nodeid, context, nd)
                # nodeids = ImmortalEntity.getPrevNode(nd)
                # if nodeids.__contains__(nodeid):
                overrideTitle = ImmortalEntity.getTitleOverride(nd, nodeid)
                if ismatched:
                    listactions.append({"ID": nd["ID"], "Title": overrideTitle, "Question": nd["Question"]})

        return listnode, listactions

    @staticmethod
    def searchNextNodes(entity, nodeid, context:dict)->list:
        listnode, _ = ImmortalEntity.searchNext(entity, nodeid, context)
        return listnode

    @staticmethod
    def searchNextActions(entity, nodeid, context:dict)->list:
        _, listactions = ImmortalEntity.searchNext(entity, nodeid, context)
        return listactions

    @staticmethod
    def getNodeType(node:dict):
        if node.keys().__contains__("Action"):
            return "Action"
        else:
            return "Node"

    @staticmethod
    def mergeNode(nodea, nodeb):
        # merge prev
        prevlista = ImmortalEntity.getPrevNode(nodea)
        prevlistb = ImmortalEntity.getPrevNode(nodeb)
        joined = set(prevlista + prevlistb)

        # merge data field
        newData = Utils.mergeDict(nodea[EntityKeyword.data], nodeb[EntityKeyword.data])

        newEvents = Utils.mergeDict(nodea[EntityKeyword.Events], nodeb[EntityKeyword.Events])
        # newMapping = list(set(nodea[EntityKeyword.Mapping] + nodeb[EntityKeyword.Mapping]))
        nodec = Utils.cloneDict(nodea)
        nodec[EntityKeyword.data] = newData
        nodec[EntityKeyword.Events] = newEvents
        # nodec[EntityKeyword.Mapping] = newMapping
        for i in joined:
            ImmortalEntity.setPrevNode(nodec, i)

        return nodec

    @staticmethod
    def getDisableKey(nodeid):
        return f"disabled_{nodeid}"

    @staticmethod
    def getContextField(entity):
        prop:dict = entity["Properties"]
        if not prop.keys().__contains__("context"):
            prop.setdefault("context", {})
        return prop["context"]

    @staticmethod
    def SetContext(entity, key, value):
        contextField:dict = ImmortalEntity.getContextField(entity)
        if not contextField.keys().__contains__(key):
            contextField.setdefault(key, value)
        else:
            contextField[key] = value
        return entity
        pass

    @staticmethod
    def mergeContext(entity1, entity2):
        contxt1 = ImmortalEntity.getContextField(entity1)
        contxt2 = ImmortalEntity.getContextField(entity2)
        print(f'====ctxt1 : {contxt1}')
        print(f'====ctxt2 : {contxt2}')
        merged = Utils.mergeDict(contxt1, contxt2)

        print(f'====merged : {merged}')
        # newEntity = Utils.cloneDict(entity1)
        entity1["Properties"]["context"] = merged
        return entity1

class NodeType:
    Action = "Action"
    Node = "Node"