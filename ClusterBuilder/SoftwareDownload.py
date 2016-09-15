import json
import os
import threading
import time
import warnings

import paramiko
import requests
from paramiko import WarningPolicy

def downloadSoftware(clusterDictionary):
    warnings.simplefilter("ignore")
    package = clusterDictionary["clusterType"]
    headers = {"Authorization": "Token " + os.environ.get("PIVNET_APIKEY")}

    # FIND PRODUCT
    response = requests.get("https://network.pivotal.io/api/v2/products")
    res = json.loads(response.text)
    for product in res["products"]:
        if package in product["slug"]:
            releasesURL = product["_links"]["releases"].get("href")
            productId = product["id"]
    response = requests.get(releasesURL)
    res = json.loads(response.text)
    # GET LATEST RELEASE
    latest = 0
    for versions in res["releases"]:
        versionInt = int(str(versions["version"]).replace(".", ""))
        if (versionInt > latest):
            latest = versionInt;
            latestVersion = versions

            # # GET DOWNLOAD URL AND FILENAME

    getURL = "https://network.pivotal.io/api/v2/products/" + package + "/releases/" + str(latestVersion["id"])
    response = requests.get(getURL, headers=headers)
    responseJSON = json.loads(response.text)
    downloads = []
    # ACCEPT EULA

    eulaURL = "https://network.pivotal.io/api/v2/products/" + package + "/releases/" + str(
        latestVersion["id"]) + "/eula_acceptance"
    response = requests.post(eulaURL, headers=headers)
    print "Software EULA Accepted:", response.text

    ### SHOULD ADD A FLAG TO TELL WHICH HOSTS THE SW GOES ON
    #   0 : CLUSTERWIDE
    #   1 : ACCESS
    #   2 : MASTERS
    #   3 : DATANODES OR SEGMENT DB HOST

    print clusterDictionary["clusterName"] + ": Downloading Software to Cluster Nodes"
    for fileInfo in responseJSON["file_groups"]:
        downloadFile = {}
        if "pivotal-gpdb" in clusterDictionary["clusterType"]:
            if "Database Server" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    if "Red Hat Enterprise Linux 5, 6" in file["name"]:
                        downloadFile["URL"] = file["_links"]["download"].get("href")
                        downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                        downloadFile["TARGET"] = 0

                        downloads.append(downloadFile)
            elif "Loader" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    if "Red Hat Enterprise Linux x86_64" in file["name"]:
                        downloadFile["URL"] = file["_links"]["download"].get("href")
                        downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                        downloadFile["TARGET"] = 0
                        downloads.append(downloadFile)
            elif "Analytics" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    if os.environ.get("MADLIB_VERSION") in file["name"]:  # NEED TO FIX THIS TO BE AUTOMATIC
                        downloadFile["URL"] = file["_links"]["download"].get("href")
                        downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                        downloadFile["TARGET"] = 2
                        downloads.append(downloadFile)
            elif "Language extensions" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    if "PL/R Extension for RHEL" in file["name"]:
                        downloadFile["URL"] = file["_links"]["download"].get("href")
                        downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                        downloadFile["TARGET"] = 2
                        downloads.append(downloadFile)
            elif "Clients" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    if "Clients for Red Hat Enterprise Linux x86_64" in file["name"]:
                        downloadFile["URL"] = file["_links"]["download"].get("href")
                        downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                        downloadFile["TARGET"] = 1
                        downloads.append(downloadFile)
        elif "pivotal-hdb" in clusterDictionary["clusterType"]:
            if "Software" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    if "RHEL" in file["name"]:
                        downloadFile["URL"] = file["_links"]["download"].get("href")
                        downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                        downloads.append(downloadFile)
            elif "Language" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    downloadFile["URL"] = file["_links"]["download"].get("href")
                    downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                    downloads.append(downloadFile)
            elif "MADlib" in fileInfo["name"]:
                for file in fileInfo["product_files"]:
                    if os.environ.get("MADLIB_VERSION") in file["name"]:
                        downloadFile["URL"] = file["_links"]["download"].get("href")
                        downloadFile["NAME"] = str(file["aws_object_key"]).split("/")[2]
                        downloads.append(downloadFile)

    if "pivotal-gpdb" in clusterDictionary["clusterType"]:

        # threads = []
        # for clusterNode in clusterDictionary["clusterNodes"]:
        #     prepFilesThread = threading.Thread(target=prepFiles, args=(clusterNode,))
        #     threads.append(prepFilesThread)
        #     prepFilesThread.start()
        # for x in threads:
        #     x.join()

        # Thread PER HOST

        threads = []

        for clusterNode in clusterDictionary["clusterNodes"]:
            hostDownloadsThread = threading.Thread(target=hostDownloads, args=(clusterNode, downloads,))
            threads.append(hostDownloadsThread)
            hostDownloadsThread.start()
        for x in threads:
            x.join()



    elif "pivotal-hdb" in clusterDictionary["clusterType"]:
        for node in clusterDictionary["clusterNodes"]:
            if "access" in node["role"]:
                connected = False
                attemptCount = 0
                while not connected:
                    try:
                        attemptCount += 1

                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(WarningPolicy())
                        ssh.connect(node["externalIP"], 22, os.environ.get("SSH_USERNAME"), None, pkey=None,
                                    key_filename=str(os.environ.get("CONFIGS_PATH")) + str(os.environ.get("SSH_KEY")),
                                    timeout=120)

                        for file in downloads:
                            (stdin, stdout, stderr) = ssh.exec_command(
                                "wget --header=\"Authorization: Token " + os.environ.get(
                                    "PIVNET_APIKEY") + "\" --post-data='' " + str(
                                    file['URL']) + " -O /tmp/" + str(file['NAME']))

                            stderr.readlines()
                            stdout.readlines()

                        connected = True
                    except Exception as e:
                        print e
                        print node["nodeName"] + ": Attempting SSH Connection"
                        time.sleep(3)
                        if attemptCount > 1:
                            print "Failing Process"
                            exit()
                    finally:
                        ssh.close()
    return downloads


### SHOULD ADD A FLAG TO TELL WHICH HOSTS THE SW GOES ON
#   0 : CLUSTERWIDE
#   1 : ACCESS
#   2 : MASTERS
#   3 : DATANODES OR SEGMENT DB HOST

def hostDownloads(node, downloads):
    connected = False
    attemptCount = 0
    while not connected:
        try:
            attemptCount += 1
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(WarningPolicy())
            ssh.connect(node["externalIP"], 22, os.environ.get("SSH_USERNAME"), None, pkey=None,
                        key_filename=str(os.environ.get("CONFIGS_PATH")) + str(os.environ.get("SSH_KEY")), timeout=120)
            for file in downloads:
                if (file["TARGET"] == 2) and ("master" in node["role"]):
                    (stdin, stdout, stderr) = ssh.exec_command("wget --header=\"Authorization: Token " + os.environ.get(
                        "PIVNET_APIKEY") + "\" --post-data='' " + str(file['URL']) + " -O /tmp/" + str(file['NAME']))
                    stderr.readlines()
                    stdout.readlines()
                elif (file["TARGET"] == 1) and ("access" in node["role"]):

                    (stdin, stdout, stderr) = ssh.exec_command("wget --header=\"Authorization: Token " + os.environ.get(
                        "PIVNET_APIKEY") + "\" --post-data='' " + str(file['URL']) + " -O /tmp/" + str(file['NAME']))
                    stderr.readlines()
                    stdout.readlines()
                elif (file["TARGET"] == 3) and ("worker" in node["role"]):

                    (stdin, stdout, stderr) = ssh.exec_command("wget --header=\"Authorization: Token " + os.environ.get(
                        "PIVNET_APIKEY") + "\" --post-data='' " + str(file['URL']) + " -O /tmp/" + str(file['NAME']))
                    stderr.readlines()
                    stdout.readlines()
                elif (file["TARGET"] == 0):  # and ("access" not in node["role"]):  Decided to put GPDB on ACCESS
                    (stdin, stdout, stderr) = ssh.exec_command("wget --header=\"Authorization: Token " + os.environ.get(
                        "PIVNET_APIKEY") + "\" --post-data='' " + str(file['URL']) + " -O /tmp/" + str(file['NAME']))
                    stderr.readlines()
                    stdout.readlines()

            connected = True
        except Exception as e:
            print e
            print node["nodeName"] + ": Attempting SSH Connection"
            time.sleep(3)
            if attemptCount > 1:
                print "Failing Process"
                exit()
        finally:
            ssh.close()
