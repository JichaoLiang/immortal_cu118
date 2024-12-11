from .Wav2lipCli import Wav2lipCli
from .Utils import Utils
from .ImmortalEntity import ImmortalEntity, NodeType
from moviepy.video.io import VideoFileClip
from . import ImmortalAgent

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


class ImApplyWav2lip:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sceneEntity": ("IMMORTALENTITY",),
                "use": (["musetalk", "wav2lip"], {"default": "musetalk"}),
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

    def process(self, sceneEntity, use="musetalk"):
        nodes = sceneEntity["Nodes"]
        idlist = []
        videolist = []
        voicelist = []
        for node in nodes:
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
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ApplyVoiceConversion": "ApplyVoiceConversion",
    "ImApplyWav2lip": "ImApplyWav2lip",
}
