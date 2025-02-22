# import packages
from os.path import exists
from urllib3.exceptions import InsecureRequestWarning
import binascii
import json
import math
import requests
import subprocess
import vicariousnetwork

useMockData=False

# ------ Bitcoin Core Related ------------------------------------------------------

def getblock(blocknum, verbosity=1):
    if useMockData:
        if exists("../mock-data/getblock.json"):
            with open("../mock-data/getblock.json") as f:
                return json.load(f)
    cmd = "bitcoin-cli getblock `bitcoin-cli getblockhash " + str(blocknum) + "` " + str(verbosity)
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError as e:
        print(e)
        fakejson = "{\"confirmations\": 1, \"time\": 0}"
        return json.loads(fakejson)

def getblockhash(blocknumber=1):
    if useMockData:
        if exists("../mock-data/getblockhash.json"):
            with open("../mock-data/getblockhash.json") as f:
                return f.readline()
    cmd = "bitcoin-cli getblockhash " + str(blocknumber)
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "0000000000000000000000000000000000000000000000000000000000000000"

def getblockopreturns(blocknum):
    if useMockData:
        return ["This is an example OP_RETURN", "Another OP_RETURN found in the block", "Only utf-8 or ascii decodable OP_RETURNs are rendered","Support for\nmulti-line OP_RETURN values\nexists as well","Some spammy OP_RETURN values are excluded","There must be at least one space","Lengthy OP_RETURN values without new lines may end up running off the side of the image","It depends on the fontsize set, which is based on number of OP_RETURN\nentries in the block","NODEYEZ","Nodeyez - Display panels to get the most from your node","NODEYEZ","NODEYEZ"]

    b = getblock(blocknum, 2)
    opreturns = []
    if "tx" in b:
        txidx = 0
        for tx in b["tx"]:
            txidx += 1
            voutidx = 0
            if "vout" in tx:
                for vout in tx["vout"]:
                    voutidx += 1
                    if "scriptPubKey" in vout:
                        scriptPubKey = vout["scriptPubKey"]
                        if "asm" in scriptPubKey:
                            asm = scriptPubKey["asm"]
                            if "OP_RETURN" in asm:
                                ophex = asm.replace("OP_RETURN ", "")
                                # require even number of characters
                                if len(ophex) % 2 == 1:
                                    continue
                                # require more than one word
#                                if "20" not in ophex:
#                                    continue
                                #encodinglist = ["utf-8","gb18030","euc-kr","cp1253","utf-32","utf-16","euc-kr","cp1253","cp1252","iso8859-16","ascii","latin-1","iso8859-1"]
                                encodinglist = ["utf-8","ascii"]
                                hasError = True
                                try:
                                    opbytes = bytes.fromhex(ophex)
                                except Exception as e:
                                    print(f"error handling ophex '{ophex}'")
                                    print(f"error is {e}")
                                for encoding in encodinglist:
                                    if hasError == False:
                                        break
                                    try:
                                        optext = opbytes.decode(encoding)
#                                        print(f"successfully converted with encoding {encoding}: {optext}")
                                        hasError = False
                                        opreturns.append(optext)
                                    except Exception as e:
#                                        print(f"error converting hex to text with encoding {encoding} for tx[{txidx}].vout[{voutidx}]: {e}")
                                        pass
#                                if hasError:
#                                    opreturns.append(ophex)


    return opreturns

def getcurrentblock():
    if useMockData:
        return 726462
    cmd = "bitcoin-cli getblockchaininfo"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        blockcurrent = int(j["blocks"])
        return blockcurrent
    except subprocess.CalledProcessError as e:
        print(e)
        return 1

def getepochnum(blocknum):
    return int(math.floor(blocknum / 2016))

def getfirstblockforepoch(blocknum):
    epochnum = getepochnum(blocknum)
    return min(blocknum, (int(epochnum * 2016) + 1))



# ------ Lightning LND Related ------------------------------------------------------

pubkey_alias = {'pubkey':'alias'}

def attemptconnect(nodeinfo):
    nodestatus = 0
    pubkey = nodeinfo["node"]["pub_key"]
    addr = getnodeaddress(nodeinfo)
    if addr == "0.0.0.0:65535":
        return 0
    cmd = "lncli" + getlndglobaloptions() + " connect " + pubkey + "@" + addr + " --timeout 5s 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if "error" in cmdoutput:
            nodestatus = 0
        else:
            cmd = "lncli" + getlndglobaloptions() + " disconnect " + pubkey + " 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                if "error" in cmdoutput:
                    nodestatus = 0
                else:
                    nodestatus = 1
            except subprocess.CalledProcessError as e2:
                print(f"error calling disconnect in attempconnect: {e}")
                nodestatus = 0
    except subprocess.CalledProcessError as e:
        print(f"error in attemptconnect: {e}")
        nodestatus = 0
    return nodestatus

def attemptconnectrest(nodeinfo, node):
    if not nodeconfigvalid(node):
        return attemptconnect(nodeinfo)
    nodestatus = 0
    pubkey = nodeinfo["node"]["pub_key"]
    addr = getnodeaddressrest(nodeinfo, node)
    if addr == "0.0.0.0:65535":
        return nodestatus # 0
    errorResponse = '{"error":"failed command"}'
    connectData = '{"addr":"' + pubkey + '@' + addr + '","timeout":"5"}'
    connectResponse = noderestcommandpost(node, "/v1/peers", connectData, errorResponse)
    if "error" not in connectResponse:
        disconnectResponse = noderestcommanddelete(node, "/v1/peers/" + pubkey, errorResponse)
        if "error" not in disconnectResponse:
            nodestatus = 1
    return nodestatus

def getdefaultaliasfrompubkey(pubkey):
    return pubkey[0:10] + "..."

def getfwdinghistory():
    if useMockData:
        if exists("../mock-data/getfwdinghistory.json"):
            with open("../mock-data/getfwdinghistory.json") as f:
                return json.load(f)
    cmd = "lncli" + getlndglobaloptions() + " fwdinghistory --start_time -5y --max_events 50000 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getfwdinghistory: {e}")
        cmdoutput = '{\"forwarding_events\": []}'
    j = json.loads(cmdoutput)
    return j

def getfwdinghistoryrest(node):
    if useMockData or not nodeconfigvalid(node):
        return getfwdinghistory()
    postData = '{"start_time":0,"num_max_events":50000}'
    defaultResponse = '{"forwarding_events":[]}'
    return noderestcommandpost(node, "/v1/switch", postData, defaultResponse)

def getlndglobaloptions():
    return " --macaroonpath=${HOME}/.lnd/nodeyez.macaroon"

def getnodeaddress(nodeinfo):
    bestresult = ""
    for addr in nodeinfo["node"]["addresses"]:
        nodehostandport = addr["addr"]
        if bestresult == "":
            bestresult = nodehostandport
        elif "onion" in nodehostandport:
            if "onion" not in bestresult:
                bestresult = nodehostandport
            elif len(nodehostandport) > 56:
                bestresult = nodehostandport
    return bestresult

def getnodealias(nodeinfo):
    if "alias" in nodeinfo:
        return nodeinfo["alias"]
    if "node" in nodeinfo:
        return getnodealias(nodeinfo["node"])
    return "UNKNOWN ALIAS"

def getnodealiasandstatus(pubkey, nextnodepubkey):
    nodeinfo = getnodeinfo(pubkey)
    nodealias = getnodealias(nodeinfo)
    nodeonline = 0
    if isnodeconnected(pubkey):
        nodeonline = 1
    else:
        nodeonline = attemptconnect(nodeinfo)
    # look if there is a channel
    haschannel = 0
    if "channels" in nodeinfo:
        for channel in nodeinfo["channels"]:
            node1_pub = channel["node1_pub"]
            node2_pub = channel["node2_pub"]
            if pubkey == node1_pub and nextnodepubkey == node2_pub:
                haschannel = 1
                break
            if pubkey == node2_pub and nextnodepubkey == node1_pub:
                haschannel = 1
                break
    return (nodealias, nodeonline, haschannel, nodeinfo)

def getnodealiasandstatusrest(pubkey, nextnodepubkey, node):
    if not nodeconfigvalid(node):
        return getnodealiasandstatus(pubkey, nextnodepubkey)
    nodeinfo = getnodeinforest(pubkey, node)
    nodealias = getnodealias(nodeinfo)
    nodeonline = 0
    if isnodeconnectedrest(pubkey, node):
        nodeonline = 1
    else:
        nodeonline = attemptconnectrest(nodeinfo, node)
    # look if there is a channel
    haschannel = 0
    if "channels" in nodeinfo:
        for channel in nodeinfo["channels"]:
            node1_pub = channel["node1_pub"]
            node2_pub = channel["node2_pub"]
            if pubkey == node1_pub and nextnodepubkey == node2_pub:
                haschannel = 1
                break
            if pubkey == node2_pub and nextnodepubkey == node1_pub:
                haschannel = 1
                break
    return (nodealias, nodeonline, haschannel, nodeinfo)

def getnodealiasfrompubkey(pubkey):
    return getnodealiasfrompubkeyrest(pubkey, {})

def getnodealiasfrompubkeyrest(pubkey, node):
    alias = getdefaultaliasfrompubkey(pubkey)
    if pubkey in pubkey_alias.keys():
        alias = pubkey_alias[pubkey]
        if len(alias) < 1:
            alias = getdefaultaliasfrompubkey(pubkey)
    else:
        if nodeconfigvalid(node):
            nodeinfo = getnodeinforest(pubkey, node)
        else:
            nodeinfo = getnodeinfo(pubkey)
        alias = getnodealias(nodeinfo)
        pubkey_alias[pubkey] = alias
    return alias

def getnodechannels():
    if useMockData:
        if exists("../mock-data/getnodechannels.json"):
            with open("../mock-data/getnodechannels.json") as f:
                r = json.load(f)
                return r
    cmd = "lncli" + getlndglobaloptions() + " listchannels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getnodechannels: {e}")
        cmdoutput = '{"channels": []}'
    j = json.loads(cmdoutput)
    return j

def getnodechannelsrest(node):
    if useMockData or not nodeconfigvalid(node):
        return getnodechannels()
    defaultResponse = '{"channels":[]}'
    return noderestcommandget(node, "/v1/channels", defaultResponse)

def getnodeinfo(pubkey):
    if useMockData:
        if exists("../mock-data/getnodeinfo.json"):
            with open("../mock-data/getnodeinfo.json") as f:
                r = json.load(f)
                r["node"]["alias"] = mockaliasforpubkey(pubkey)
                return r
    cmd = "lncli" + getlndglobaloptions() + " getnodeinfo --pub_key " + pubkey + " --include_channels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getnodeinfo: {e}")
        cmdoutput = '{"node":{"alias":"' + pubkey + '","pub_key":"' + pubkey + '","last_update":0,"addresses":[{"network":"tcp","addr":"0.0.0.0:65535"}]}}'
    j = json.loads(cmdoutput)
    return j

def getnodeinforest(pubkey, node):
    if not nodeconfigvalid(node):
        return getnodeinfo(pubkey)
    defaultResponse = '{"node":{"alias":"' + pubkey + '","pub_key":"' + pubkey + '","last_update":0,"addresses":[{"network":"tcp","addr":"0.0.0.0:65535"}]}}'
    return noderestcommandget(node, "/v1/graph/node/" + pubkey + "?include_channels=true", defaultResponse)

def getnodepayments():
    if useMockData:
        if exists("../mock-data/getnodepayments.json"):
            with open("../mock-data/getnodepayments.json") as f:
                return json.load(f)
    cmd = "lncli" + getlndglobaloptions() + " listpayments 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getnodepayments: {e}")
        cmdoutput = '{"payments": []}'
    j = json.loads(cmdoutput)
    return j

def getnodepaymentsrest(node):
    if useMockData or not nodeconfigvalid(node):
        return getnodepayments()
    defaultResponse = '{"payments":[]}'
    return noderestcommandget(node, "/v1/payments", defaultResponse)

def getnodepeers():
    cmd = "lncli" + getlndglobaloptions() + " listpeers 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(f"error in getnodepeers: {e}")
        return '{"peers": []}'

def getnodepeersrest(node):
    if not nodeconfigvalid(node):
        return getnodepeers()
    defaultResponse = '{"peers":[]}'
    return noderestcommandget(node, "/v1/peers", defaultResponse)

def isnodeconnected(pubkey):
    nodepeers = getnodepeers()
    j = json.loads(nodepeers)
    for peer in j["peers"]:
        if pubkey == peer["pub_key"]:
            return True
    return False

def isnodeconnectedrest(pubkey, node):
    if not nodeconfigvalid(node):
        return isnodeconnected(pubkey)
    nodepeers = getnodepeersrest(node)
    if "peers" in nodepeers:
        for peer in j["peers"]:
            if pubkey == peer["pub_key"]:
                return True
    return False

def mockaliasforpubkey(pubkey):
    alias = "mockup node"
    mfn = "../mock-data/bip39words.txt"
    if exists(mfn):
        with open(mfn) as f:
            wordnum = int(pubkey[0:4], base=16)
            wordnum %= 2048
            for i, line in enumerate(f):
                if i == wordnum:
                    alias = line.replace("\n","") + "-" + str(i)
                    break
        pass
    return alias

def nodeconfigvalid(node):
    if "address" not in node:
        return False
    if "macaroon" not in node:
        return False
    if "port" not in node:
        return False
    return True

def noderestcommandget(node, suffix, defaultResponse="{}"):
    cmdoutput = ""
    try:
        nodeaddress = node["address"]
        nodeport = node["port"]
        nodemacaroon = node["macaroon"]
        useTor = False
        if "useTor" in node:
            useTor = node["useTor"]
        url = "https://" + nodeaddress + ":" + nodeport + suffix
        headers = {"Grpc-Metadata-macaroon": nodemacaroon}
        if useTor:
            proxies = vicariousnetwork.gettorproxies()
        else:
            proxies = {}
        timeout = vicariousnetwork.gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.get(url,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
        #print(f"{suffix} response \n\n{cmdoutput}")
    except Exception as e:
        print(f"error calling noderestcommandget for {suffix}: {e}")
        print(f"using default")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default")
        j = json.loads(defaultResponse)
    return j

def noderestcommanddelete(node, suffix, defaultResponse="{}"):
    cmdoutput = ""
    try:
        nodeaddress = node["address"]
        nodeport = node["port"]
        nodemacaroon = node["macaroon"]
        useTor = False
        if "useTor" in node:
            useTor = node["useTor"]
        url = "https://" + nodeaddress + ":" + nodeport + suffix
        headers = {"Grpc-Metadata-macaroon": nodemacaroon}
        if useTor:
            proxies = vicariousnetwork.gettorproxies()
        else:
            proxies = {}
        timeout = vicariousnetwork.gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.delete(url,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
    except Exception as e:
        print(f"error calling noderestcommanddelete for {suffix}: {e}")
        print(f"using default")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default")
        j = json.loads(defaultResponse)
    return j

def noderestcommandpost(node, suffix, postData="{}", defaultResponse="{}"):
    cmdoutput = ""
    try:
        nodeaddress = node["address"]
        nodeport = node["port"]
        nodemacaroon = node["macaroon"]
        useTor = False
        if "useTor" in node:
            useTor = node["useTor"]
        url = "https://" + nodeaddress + ":" + nodeport + suffix
        headers = {"Grpc-Metadata-macaroon": nodemacaroon}
        if useTor:
            proxies = vicariousnetwork.gettorproxies()
        else:
            proxies = {}
        timeout = vicariousnetwork.gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.post(url,data=postData,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
        #print(f"{suffix} response \n\n{cmdoutput}")
    except Exception as e:
        print(f"error calling noderestcommandpost for {suffix}: {e}")
        print(f"using default")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default")
        j = json.loads(defaultResponse)
    return j
