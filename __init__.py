from moviepy import *

from .Wav2lipCli import Wav2lipCli
from .Utils import Utils
from .ImmortalEntity import ImmortalEntity, NodeType
from moviepy.video.io import VideoFileClip
from . import ImmortalAgent,MovieMakerUtils

class ApplyVoiceConversion:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sceneEntity": ("IMMORTALENTITY",)
            }
        }
        pass

    RETURN_TYPES = ("IMMORTALENTITY",)
    # RETURN_NAMES = ("image_output_name",)

    FUNCTION = "process"

    # OUTPUT_NODE = False

    CATEGORY = "Immortal"

    def applyVC(self, node: dict):
        if node.keys().__contains__("Temporary"):
            temporay: dict = node["Temporary"]
            if temporay.keys().__contains__("VCTask") and len(temporay["VCTask"].keys()) > 0:
                inputvideokey = temporay["VCTask"]["inputvideokey"]
                voicePath = temporay["VCTask"]["voicepath"]

                print(f"vc: videokey: {inputvideokey}")
                _, sourceaudio = Utils.generatePathId(namespace="temp", exten="wav")
                clip = VideoFileClip.VideoFileClip(Utils.getPathById(id=inputvideokey))
                audio = clip.audio
                if audio is None:
                    return None, None
                audio.write_audiofile(sourceaudio)
                return sourceaudio, voicePath
        return None, None

    def process(self, sceneEntity):
        nodes = sceneEntity["Nodes"]
        idlist = []
        sourcelist = []
        speakerlist = []
        for node in nodes:
            source, dest = self.applyVC(node)
            if source is None:
                continue
            idlist.append(node['ID'])
            sourcelist.append(source)
            speakerlist.append(dest)
        resultlist = Wav2lipCli.xtts_vc(sourcelist, speakerlist)
        for i in range(0, len(idlist)):
            node = ImmortalEntity.getNodeById(sceneEntity, idlist[i])
            videopath = Utils.getPathById(id=node["VideoDataKey"])
            source: str = sourcelist[i]
            dest = resultlist[i]
            fid, fpath = ImmortalAgent.ImmortalAgent.replaceAudio(videopath, dest)

            # erase task
            node["Temporary"].pop("VCTask")
            # if os.path.exists(source):
            #     os.remove(source)
            node["VideoDataKey"] = fid
        newEntity = Utils.cloneDict(sceneEntity)
        return (newEntity,)
        pass


class ConcatNodeQueue:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "entity": ("IMMORTALENTITY", {"default": None}),
                "tail": ("NODE", {"default": None}),
                "autoRoot": (["YES", "NO"], {"default": "YES"}),
            },
            "optional": {
                "head": ("NODE", {"default": None}),
                "pointer": ("NODE", {"default": None}),
                "extraNodes": ("NODES", {"default": []}),
                "cleanafterconcat": (["yes","no"], {"default": "yes"}),
                "resizeWidth":("INT", {
                    "default": 720,
                    "min": 0,  # Minimum value
                    "step": 1,  # Slider's step
                    "display": "number"  # Cosmetic only: display as "number" or "slider"
                }),
                "resizeHeight":("INT", {
                    "default": 1280,
                    "min": 0,  # Minimum value
                    "step": 1,  # Slider's step
                    "display": "number"  # Cosmetic only: display as "number" or "slider"
                }),
            }
        }
        pass

    RETURN_TYPES = ("IMMORTALENTITY", "NODE")
    RETURN_NAMES = ("entity", "pointer")

    FUNCTION = "process"

    # OUTPUT_NODE = False

    CATEGORY = "Immortal"

    def getNodelistByTailHead(self, entity, tail, head):
        nodelist = []
        current = ImmortalEntity.getNodeById(entity, tail)
        while(current is not None):
            nodelist = [current] + nodelist
            if current['ID'] == head:
                break
            prevnodeid = ImmortalEntity.getPrevNode(current)
            if len(prevnodeid) == 0:
                break
            current = ImmortalEntity.getNodeById(entity, prevnodeid[0])
        return nodelist

    def process(self, entity, tail, autoRoot, head=None, pointer=None, extraNodes=[], cleanafterconcat="yes", resizeWidth=720, resizeHeight=1280):
        nodelist = self.getNodelistByTailHead(entity, tail, head)

        nodelistid = [n['ID'] for n in nodelist]
        applywav2lip = ImApplyWav2lip()
        entity = applywav2lip.process(entity,nodewhitelist=nodelistid)[0]

        nodelist = self.getNodelistByTailHead(entity, tail, head)
        print(nodelist)
        firstnode= nodelist[0]
        videos = [Utils.getPathById(id=video['VideoDataKey']) for video in nodelist]
        clips = [VideoFileClip.VideoFileClip(f) for f in videos]
        clips = [c.resized((resizeWidth, resizeHeight)) for c in clips]
        concateclip = concatenate_videoclips(clips=clips)
        id, path = Utils.generatePathId(namespace='concated', exten='mp4')
        Utils.mkdir(path)
        concateclip.write_videofile(path, fps=30)

        newNode = ImmortalEntity.getNode()
        newNode['Mapping'] = firstnode['Mapping']
        newNode['Title'] = firstnode['Title']
        newNode['Question'] = firstnode['Question']
        newNode['Events'] = firstnode['Events']
        newNode['Data'] = firstnode['Data']
        newNode['VideoDataKey'] = id
        #wav2lip already processed, drop temporary

        # link new node
        if pointer is None or len(pointer) == 0:
            if autoRoot == "YES":
                entity["Properties"]["root"] = newNode["ID"]
        else:
            ImmortalEntity.setPrevNode(newNode, pointer)
            if extraNodes is not None and len(extraNodes) > 0:
                for nd in [ImmortalEntity.getNodeById(entity, n) for n in extraNodes]:
                    ImmortalEntity.setPrevNode(newNode, nd["ID"])
        entity['Nodes'].append(newNode)

        # clean source nodes
        nodes:list = entity['Nodes']
        if cleanafterconcat == 'yes':
            for id in nodelistid:
                node = ImmortalEntity.getNodeById(entity, id)
                nodes.remove(node)

        newEntity = Utils.cloneDict(entity)

        return newEntity, newNode['ID']
        pass

class ImApplyWav2lip:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sceneEntity": ("IMMORTALENTITY",),
                "use": (["musetalk", "wav2lip"], {"default": "musetalk"}),
            },
            "optional": {
                "nodewhitelist": ("NODES", {"default": None}),
            }
        }
        pass

    RETURN_TYPES = ("IMMORTALENTITY",)
    # RETURN_NAMES = ("image_output_name",)

    FUNCTION = "process"

    # OUTPUT_NODE = False

    CATEGORY = "Immortal"

    def applyVA(self, node: dict):
        if node.keys().__contains__("Temporary"):
            temporay: dict = node["Temporary"]
            if temporay.keys().__contains__("wav2lip") and len(temporay["wav2lip"].keys()) > 0:
                inputvideokey = temporay["wav2lip"]["inputvideokey"]
                voicePath = temporay["wav2lip"]["voicepath"]
                videopath = Utils.getPathById(id=inputvideokey)
                return videopath, voicePath
        return None, None

    def process(self, sceneEntity, use="musetalk", nodewhitelist:list=None):
        nodes = sceneEntity["Nodes"]
        idlist = []
        videolist = []
        voicelist = []
        for node in nodes:
            if nodewhitelist is None or nodewhitelist.__contains__(node['ID']):
                source, dest = self.applyVA(node)
                if source is None:
                    continue
                idlist.append(node['ID'])
                videolist.append(source)
                voicelist.append(dest)
        resultidlist, resultPathlist = Wav2lipCli.convert_batch(videolist, voicelist, use)
        for i in range(0, len(idlist)):
            node = ImmortalEntity.getNodeById(sceneEntity, idlist[i])
            videopath = Utils.getPathById(id=node["VideoDataKey"])
            source: str = videolist[i]
            fid = resultidlist[i]

            # erase task
            node["Temporary"].pop("wav2lip")
            # if os.path.exists(source):
            #     os.remove(source)
            node["VideoDataKey"] = fid
        newEntity = Utils.cloneDict(sceneEntity)
        return (newEntity,)
        pass

NODE_CLASS_MAPPINGS = {
    "ApplyVoiceConversion": ApplyVoiceConversion,
    "ImApplyWav2lip": ImApplyWav2lip,
    "ConcatNodeQueue": ConcatNodeQueue,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ApplyVoiceConversion": "ApplyVoiceConversion",
    "ImApplyWav2lip": "ImApplyWav2lip",
    "ConcatNodeQueue": "ConcatNodeQueue",
}
