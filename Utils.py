import json
import random
import shutil
import time
import os
from pathlib import Path
# from config import ImmortalConfig
from .config import ImmortalConfig
import wave
from pydub import AudioSegment


class Utils:
    @staticmethod
    def setObjectStoreKey(key, val):
        path = Utils.getPathByObjectStoreKey(key)
        exists = False
        if os.path.exists(path):
            exists = True
            os.remove(path)
        with open(path,"w", encoding='utf-8') as f:
            f.write(val)
        return exists

    @staticmethod
    def getObjectStoreKey(key):
        path = Utils.getPathByObjectStoreKey(key)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                value = f.read()
                return value
        else:
            return None
    @staticmethod
    def objectStorekeyExists(key):
        path = Utils.getPathByObjectStoreKey(key)
        return os.path.exists(path)

    @staticmethod
    def getPathByObjectStoreKey(key):
        path = os.path.join(ImmortalConfig.objectStorePath, key)
        return path

    @staticmethod
    def tryExtractPathByKey(keyMaybe):
        keypath = keyMaybe
        try:
            print(keypath)
            if os.path.exists(keyMaybe):
                return keyMaybe
            keypath = Utils.getPathById(id=keypath)
            print(keypath)
        except Exception as e:
            print(e)
            pass
        filepath = keypath
        return filepath

    @staticmethod
    def writetempfile(content):
        id, path = Utils.generatePathId(namespace='temp', exten='txt')
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return id, path

    @staticmethod
    def mkdir(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def generatePathId(basepath=ImmortalConfig.basepath, namespace="Immortal", exten=None):
        fnow = time.time()
        intNow = int(fnow * 1000)
        milliSec = intNow % 1000
        now = time.localtime(fnow)
        id = f'{namespace}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}_{milliSec}'
        if exten is not None:
            id += "." + exten
        destPath = os.path.join(basepath, f'{namespace}/{now.tm_year}_{now.tm_mon}/{now.tm_mday}/{id}')
        # destDir = os.path.dirname(destPath)
        # if not Path(destPath).exists():
        #     os.makedirs(destPath)
        time.sleep(0.001)
        return id, destPath

    @staticmethod
    def getPathById(basepath=ImmortalConfig.basepath, id: str = None):
        tokens = id.split('_')
        namespace = tokens[0]
        year = tokens[1]
        mon = tokens[2]
        mday = tokens[3]
        hour = tokens[4]
        min = tokens[5]
        sec = tokens[6]
        mill = tokens[7].split('.')[0]

        destpath = os.path.join(basepath,
                                f'{namespace}/{year}_{mon}/{mday}/{id}')
        # if len(id.split('.')) > 1:
        #     exten = id.split('.')[-1]
        #     destpath += '.' + exten
        return destpath

    @staticmethod
    def generateId(namespace="immortal"):
        fnow = time.time()
        intNow = int(fnow * 1000)
        milliSec = intNow % 1000
        now = time.localtime(fnow)
        id = f'{namespace}_{now.tm_year}_{now.tm_mon}_{now.tm_mday}_{now.tm_hour}_{now.tm_min}_{now.tm_sec}_{milliSec}'
        return id
    @staticmethod
    def randomPick(length):
        rand = random.Random()
        value = rand.random()
        return int(value * length)
    pass
    @staticmethod
    def cloneDict(dict:dict):
        dumps = json.dumps(dict)
        newDict = json.loads(dumps)
        return newDict

    @staticmethod
    def removeFileByKey(key:str):
        path = Utils.getPathById(id=key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
        pass

    @staticmethod
    def isJsonString(string):
        try:
            json.loads(string)
            return True
        except json.decoder.JSONDecodeError:
            return False
        return True

    @staticmethod
    def mergeDict(dict1:dict, dict2:dict):
        allkeys = set(list(dict1.keys()) + list(dict2.keys()))
        result = {}
        for key in allkeys:
            if dict1.keys().__contains__(key) and dict2.keys().__contains__(key):
                value = dict1[key]
                if type(value) == type([]):
                    merged = list(set([json.dumps(s) for s in value] + [json.dumps(s) for s in dict2[key]]))
                    merged = [json.loads(s) for s in merged]
                    result.setdefault(key, merged)
                elif type(value) == type({}):
                    merged = Utils.mergeDict(value, dict2[key])
                    result.setdefault(key, merged)
                else:
                    result.setdefault(key, value)
            elif dict1.keys().__contains__(key) and not dict2.keys().__contains__(key):
                result.setdefault(key, dict1[key])
            elif not dict1.keys().__contains__(key) and dict2.keys().__contains__(key):
                result.setdefault(key, dict2[key])
        return result
        pass

    @staticmethod
    def listAllFilesInSubFolder(input_dir):
        result = []
        listdir = os.listdir(input_dir)
        for l in listdir:
            f = os.path.join(input_dir, l)
            if os.path.isfile(f):
                result.append(f)
            elif os.path.isdir(f):
                result = result + Utils.listAllFilesInSubFolder(f)
        return result
        pass

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except:
            return False

    @staticmethod
    def split_wav(wavfile=r'r:\temp.wav', breakon=0, minsec=-1, maxssec=40, scanwindowlengthsec=0.2,
                  silentthresholdpercent=40):
        cuttedwavfile = wavfile + ".splited.wav"
        # wave = wave.Wave_read(r'D:\immortaldata\Immortal\temp\2024_10\13\temp_2024_10_13_21_59_59_794.wav')
        wav = wave.Wave_read(wavfile)
        frames = wav.readframes(wav.getnframes())
        sampwidth = wav.getsampwidth()
        framerate = wav.getframerate()
        windowlength = int(framerate * scanwindowlengthsec)

        convlist = []
        framecount = 0
        breakscount = 0
        for idx in range(0, len(frames), int(scanwindowlengthsec * framerate / 2)):
            window = frames[idx:idx + int(scanwindowlengthsec * framerate)]

            avg = sum(window) / len(window)
            reduce = 0
            for d in window:
                temp = d - avg
                if temp < 0:
                    temp = 0 - temp
                reduce += temp ** 2
            reduce /= len(window)
            print(f"reduce:{reduce}")
            issilent = True  # reduce < silentthreshold
            convlist.append([reduce, issilent, idx])
            if issilent and not convlist[-1][1]:
                breakscount += 1
            # seccount = framecount / framerate
            # if breakscount > breakon and (seccount > minsec or minsec < 0):
            #     break
            framecount += 1
        sortedconvlist = sorted(convlist, key=lambda x: x[0])
        silentthreshold = sortedconvlist[int(silentthresholdpercent / 100 * len(convlist))][0]
        print(f'threshold: {silentthreshold}')
        for conv in convlist:
            redu = conv[0]
            if redu < silentthreshold + 500:
                conv[1] = True
            else:
                conv[1] = False

        slientpiececount = 0
        offsetstart = 0
        silentflag = 0

        piecelist = []
        for idx, item in enumerate(convlist):
            avg = item[0]
            isslient = item[1]
            framecount = item[2]
            newOffset = int(framecount)
            if silentflag > 0:
                if isslient:
                    continue
                else:
                    slientpiececount += 1
                    offsetstart = newOffset
                    silentflag = 0
            else:
                if isslient or idx == len(convlist) - 1:
                    # handle output
                    cutted = frames[offsetstart:newOffset]
                    piecelist.append((cutted, offsetstart / framerate, newOffset / framerate))
                    silentflag = 1
                else:
                    continue
        print(f'pieces: {len(piecelist)}')

        if len(piecelist) > breakon:
            currentitem = piecelist[breakon]
        else:
            currentitem = piecelist[-1]
        breakonitem, start, stop = currentitem[0], currentitem[1], currentitem[2]
        if stop > minsec or minsec < 0:
            # output from 0 to stop
            clip = AudioSegment.from_file(wavfile)
            newclip = clip[0:stop * 1000]
            newclip.export(cuttedwavfile)
        else:
            found = False
            for item in piecelist:
                breakonitem = item[0]
                start = item[1]
                stop = item[2]
                if stop > minsec or minsec < 0:
                    clip = AudioSegment.from_file(wavfile)
                    newclip = clip[0:stop * 1000]
                    newclip.export(cuttedwavfile)
                    found = True
                    break
            if not found:
                print(f'max duration: {maxssec}')
                clip = AudioSegment.from_file(wavfile)
                maxduration = len(clip)
                if maxduration > maxssec:
                    maxduration = maxssec
                newclip = clip[0:maxduration * 1000]
                newclip.export(cuttedwavfile)

        return cuttedwavfile