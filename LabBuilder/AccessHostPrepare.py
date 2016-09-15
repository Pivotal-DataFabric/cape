import paramiko
from paramiko import WarningPolicy
import warnings
import requests
import json
import time
import os
import threading
import queries
import socket


def installComponents(clusterDictionary):
    print clusterDictionary["clusterName"] + ": Installing Instructor Requirements (Python27/Numpy,etc)"

    for clusterNode in clusterDictionary["clusterNodes"]:
        if  "access" in  clusterNode["role"]:
            accessNode = clusterNode

    connected = False
    attemptCount = 0

    while not connected:
        try:
            attemptCount += 1
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(WarningPolicy())
            ssh.connect(accessNode["externalIP"], 22, str(os.environ.get("SSH_USERNAME")), None, pkey=None,key_filename=str(os.environ.get("CONFIGS_PATH")) + str(os.environ.get("SSH_KEY")),timeout=120)
            (stdin, stdout, stderr) = ssh.exec_command("source /opt/rh/python27/enable")
            stdout.readlines()
            stderr.readlines()
            #create a instructor account
            (stdin, stdout, stderr) = ssh.exec_command("sudo useradd -s /bin/bash -c 'Instructor Account' -m instructor")
            stderr.readlines()
            stdout.readlines()
            print "sudo echo " + str(os.environ.get("INSTRUCTOR_PW")) + " | sudo passwd --stdin instructor"
            (stdin, stdout, stderr) = ssh.exec_command( "sudo echo " + str(os.environ.get("INSTRUCTOR_PW")) + " | sudo passwd --stdin instructor")
            stdout.readlines()
            stderr.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo chown -R instructor: /home/instructor")
            stderr.readlines()
            stdout.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo echo 'source /opt/rh/python27/enable' >> ~/.bashrc;sudo cp ~/.bashrc /root/.bashrc;sudo cp ~/.bashrc /home/instructor/.bashrc")
            stderr.readlines()
            stdout.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo -i pip install pip -U")
            stderr.readlines()
            stdout.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo -i pip install setuptools -U")
            stderr.readlines()
            stdout.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo -i pip install numpy -U")
            stderr.readlines()
            stdout.readlines()
            #(stdin, stdout, stderr) = ssh.exec_command("pip install scipy -U >> /tmp/scipyinstall.out")
            #stderr.readlines()
            #stdout.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo -i pip install scikit-learn -U")
            stderr.readlines()
            stdout.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo -i pip install nltk -U ;sudo -i python -m nltk.downloader all")
            stderr.readlines()
            stdout.readlines()
            (stdin, stdout, stderr) = ssh.exec_command("sudo -i pip install gensim -U ")
            stderr.readlines()
            stdout.readlines()


            connected = True

        except Exception as e:
            print e
            print accessNode["nodeName"] + ": Waiting on SSH Connection"
            time.sleep(3)
            if attemptCount > 10:
                print "Failing Process"
                exit()

