import argparse
import datetime
import os
import sys
import logging
import json

from dotenv import load_dotenv

from ClusterBuilder import ClusterBuilder
from ClusterBuilder import InstallGPDB
from ClusterBuilder import SoftwareDownload
from ClusterDestroyer import ClusterDestroyer
from QueryCluster import QueryCluster
from LabBuilder import StudentAccounts


def checkRequiredVars(args):
    logging.info('Checking Required Variables')
    # Check cloud auth params
    if os.environ["PROJECT"] is not None:
        logging.debug('PROJECT: ' + str(os.environ["PROJECT"]))
    else:
        sys.exit('Failed! Add PROJECT=<project name> to your ' + args.config +
                 ' file.\n')
    if os.environ["SSH_USERNAME"] is not None:
        logging.debug('SSH_USERNAME: ' + str(os.environ["SSH_USERNAME"]))
    else:
        sys.exit('Failed! Add SSH_USERNAME=<user name> to your ' +
                 args.config + ' file.\n')
    if os.environ["SVC_ACCOUNT"] is not None:
        logging.debug('SVC_ACCOUNT: ' + str(os.environ["SVC_ACCOUNT"]))
    else:
        sys.exit('Failed! Add SVC_ACCOUNT=<service account name> to your ' +
                 args.config + ' file.\n')
    if os.environ["SSH_KEY"] is not None:
        logging.debug('SSH_KEY: ' + str(os.environ["SSH_KEY"]))
    else:
        sys.exit('Failed! Add SSH_KEY=<filename of ssh keyfile> to your ' +
                 args.config + ' file.\n')
    if os.path.isfile(str(os.environ["CONFIGS_PATH"]) + '/' +
                      os.environ["SSH_KEY"]):
        logging.debug('SSH_KEY file exists and accessible')
    else:
        sys.exit('Failed! Cannot access: ' + str(os.environ["CONFIGS_PATH"]) +
                 '/' + str(os.environ["SSH_KEY"]) +
                 ' or file does not exist!' +
                 '\nFix SSH_KEY in your ' + args.config + ' file.\n')
    if os.path.isfile(str(os.environ["CONFIGS_PATH"]) + '/' +
                      os.environ["SVC_ACCOUNT_KEY"]):
        logging.debug('SVC_ACCOUNT_KEY file exists and accessible')
    else:
        sys.exit('Failed! Cannot access: ' + str(os.environ["CONFIGS_PATH"]) +
                 '/' + str(os.environ["SVC_ACCOUNT_KEY"]) +
                 ' or file does not exist!' +
                 '\nFix SVC_ACCOUNT_KEY in your ' + args.config + ' file.\n')
    # Check params used to deploy vms
    if os.environ["SERVER_TYPE"] is not None:
        logging.debug('SERVER_TYPE: ' + str(os.environ["SERVER_TYPE"]))
    else:
        sys.exit('Failed! Add SERVER_TYPE=<instance name> to your ' +
                 args.config + ' file.\n')
    if os.environ["IMAGE"] is not None:
        logging.debug('IMAGE: ' + str(os.environ["IMAGE"]))
    else:
        sys.exit('Failed! Add IMAGE=<image name> to your ' + args.config +
                 ' file.\n')
    if os.environ["ZONE"] is not None:
        logging.debug('ZONE: ' + str(os.environ["ZONE"]))
    else:
        sys.exit('Failed! Add ZONE=<zone name> to your ' + args.config +
                 ' file.\n')
    if os.environ["DISK_TYPE"] is not None:
        logging.debug('DISK_TYPE: ' + str(os.environ["DISK_TYPE"]))
    else:
        sys.exit('Failed! Add DISK_TYPE=<disk type> to your ' + args.config +
                 ' file.\n')
    if os.environ["DISK_SIZE"] is not None:
        logging.debug('DISK_SIZE: ' + str(os.environ["DISK_SIZE"]))
    else:
        sys.exit('Failed! Add DISK_SIZE=<disk size in MB> to your ' +
                 args.config + ' file.\n')
    if os.environ["DISK_QTY"] is not None:
        logging.debug('DISK_QTY: ' + str(os.environ["DISK_QTY"]))
    else:
        sys.exit('Failed! Add DISK_QTY=<num of drives> to your ' +
                 args.config + ' file.\n')
    if os.environ["GPADMIN_PW"] is not None:
        logging.debug('GPADMIN_PW: ' + str(os.environ["GPADMIN_PW"]))
    else:
        sys.exit('Failed! Add GPADMIN_PW=<desired gpadmin password> to your ' +
                 args.config + ' file.\n')
    if os.environ["ROOT_PW"] is not None:
        logging.debug('ROOT_PW: ' + str(os.environ["ROOT_PW"]))
    else:
        sys.exit('Failed! Add ROOT_PW=<desired root password> to your ' +
                 args.config + ' file.\n')
    if os.environ["PIVNET_APIKEY"] is not None:
        logging.debug('PIVNET_APIKEY: ' + str(os.environ["PIVNET_APIKEY"]))
    else:
        sys.exit('Failed! Add PIVNET_APIKEY=<your pivnet key> to your ' +
                 args.config + ' file.\n')
    # Check params we will use to deploy GPDB
    # Need to add a check for MADLIB_VERSION after Dan fixes it
    if os.environ["BASE_HOME"] is not None:
        logging.debug('BASE_HOME: ' + str(os.environ["BASE_HOME"]))
    else:
        sys.exit('Failed! Add BASE_HOME=<base path for data dirs> to your ' +
                 args.config + ' file.\n')
    if os.environ["SEGMENTDBS"] is not None:
        logging.debug('SEGMENTDBS: ' + str(os.environ["SEGMENTDBS"]))
        if os.environ["SEGMENTDBS"] < 16 and os.environ["SEGMENTDBS"] > 0:
            logging.debug('SEGMENTDBS in valid range')
        else:
            sys.exit('Failed! Set SEGMENTDBS=<number between 1-16> in your ' +
                     args.config + ' file.\n')
    else:
        sys.exit('Failed! Add SEGMENTDBS=<# of segs per node> to your ' +
                 args.config + ' file.\n')
    if os.environ["SEGMENTDBS"] < os.environ["DISK_QTY"]:
        logging.debug('Failed Check: SEGMENTDBS less than DISK_QTY ')
        sys.exit('Failed! You requested lesser segs per node ' +
                 'than the number of drives per node.\n Change SEGMENTDBS ' +
                 'to be equal to or greater than DISK_QTY.\n\n' +
                 'Fix SEGMENTDBS=<# of segs per node> in your ' + args.config +
                 ' file.\n')
    if os.environ["STANDBY"] is not None \
       and 'yes' or 'no' in os.environ["STANDBY"]:
        logging.debug('STANDBY: ' + os.environ["STANDBY"])
    else:
        sys.exit('Failed! Add STANDBY=<yes|no> to your ' +
                 args.config + ' file.\n')
    if os.environ["ACCESS"] is not None \
       and 'yes' or 'no' in os.environ["ACCESS"]:
        logging.debug('ACCESS: ' + os.environ["ACCESS"])
    else:
        sys.exit('Failed! Add ACCESS=<yes|no> to your ' +
                 args.config + ' file.\n')
    if os.environ["STANDBY"] == os.environ["ACCESS"]:
        logging.debug('STANDBY and ACCESS match')
    else:
        sys.exit('Failed! STANDBY and ACCESS do not match! ' +
                 'Set them both to either yes or no in your ' +
                 args.config + ' file.\n')


def cliParse():
    VALID_ACTION = ["create", "destroy", "query", "stage", "dbctl"]
    parser = argparse.ArgumentParser(description='Cluster Automation for Pivotal Education')
    subparsers = parser.add_subparsers(help='sub-command help', dest="subparser_name")
    parser_create = subparsers.add_parser("create", help="Create a Cluster")
    parser_destroy = subparsers.add_parser("destroy", help="Destroy a Cluster")
    parser_query = subparsers.add_parser("query", help="Query a Cluster")
    parser_stage = subparsers.add_parser("stage", help="Stage a Cluster")
    parser_gpdb = subparsers.add_parser("gpdb", help="Start/Stop, get state of GPDB")

    parser_create.add_argument("--type", dest='type', action="store",
                               help="Type of cluster to be create (gpdb/hdb/vanilla", required=True)
    parser_create.add_argument("--name", dest='clustername', action="store", help="Name of Cluster to be Created",
                               required=True)
    parser_create.add_argument("--nodes", dest='nodes', default=1, action="store", help="Number of Nodes to be Created",
                               required=True)

    parser_create.add_argument("-v", dest='verbose', action='store_true', required=False)

    parser_create.add_argument("--config", dest='config', default=str(os.getcwd())+'/configs/config.env', action="store", help="Config.env file",
                               required=False)
    parser_create.add_argument("--log", dest='logfile', default=str(os.getcwd())+'/cape.log', action="store", help="Location of cape log file",
                               required=False)
    parser_create.add_argument("--loglevel", dest='loglevel', default='DEBUG', action="store", help="Logging level of cape log file",
                               required=False)
    #parser_create.add_argument("-l", dest='lab', action='store_true', required=False,
    #                         help="Include Lab creation in Cluster Buildout")

    parser_stage.add_argument("--name", dest='clustername', action="store", help="Name of Cluster to be Staged",
                              required=True)
    parser_query.add_argument("--name", dest='clustername', action="store", help="Name of Cluster to be Queried",
                              required=True)
    parser_query.add_argument("--nodes", dest='nodes', default=1, action="store", help="Number of Nodes to be Queried",
                               required=True)
    parser_query.add_argument("--config", dest='config', default=str(os.getcwd())+'/configs/config.env', action="store", help="Config.env file",
                               required=False)
    # Adding in type as an optinoal arg for now. to be used in the future
    parser_query.add_argument("--type", dest='type', action="store",
                               help="Type of cluster to be create (gpdb/hdb/vanilla", required=False)
    parser_query.add_argument("--log", dest='logfile', default=str(os.getcwd())+'/cape.log', action="store", help="Location of cape log file",
                               required=False)
    parser_query.add_argument("--loglevel", dest='loglevel', default='DEBUG', action="store", help="Logging level of cape log file",
                               required=False)
    parser_gpdb.add_argument("--clustername", dest='clustername', action="store", help="Name of Cluster to be Staged",
                             required=True)

    parser_gpdb.add_argument("--action", dest='action', action="store", help="start/stop/state", required=True)

    parser_destroy.add_argument("--name", dest='clustername', action="store",help="Name of Cluster to be Deleted",required=True)

    parser_destroy.add_argument("--config", dest='config', default=str(os.getcwd())+'/configs/config.env', action="store", help="Config.env file",
                               required=False)
    parser_destroy.add_argument("--nodes", dest='nodes', default=1, action="store", help="Number of Nodes to be Created",
                               required=True)
    # Adding in type as an optinoal arg for now. to be used in the future
    parser_destroy.add_argument("--type", dest='type', action="store",
                               help="Type of cluster to be create (gpdb/hdb/vanilla", required=False)
    parser_destroy.add_argument("--log", dest='logfile', default=str(os.getcwd())+'/cape.log', action="store", help="Location of cape log file",
                               required=False)
    parser_destroy.add_argument("--loglevel", dest='loglevel', default='DEBUG', action="store", help="Logging level of cape log file",
                               required=False)
    args = parser.parse_args()

    clusterDictionary = {}

    startTime = datetime.datetime.today()
    logging.basicConfig(filename=args.logfile,level=args.loglevel, format='[%(asctime)s] %(pathname)s {%(module)s:%(funcName)s:%(lineno)d} %(levelname)s %(threadName)s - %(message)s')
    print  "Start Time: ", startTime
    logging.info('Cape Started with Args:' + str(sys.argv[1:]))
    logging.debug('CAPE_HOME=' + os.environ["CAPE_HOME"])

    if (args.subparser_name == "create"):

        if (args.config):
            print "Loading Configuration"
            load_dotenv(args.config)
            os.environ["CONFIGS_PATH"] = os.path.dirname(args.config) + '/'
            logging.debug('CONFIGS_PATH=' + os.environ["CONFIGS_PATH"])
        clusterDictionary["clusterName"] = args.clustername
        clusterDictionary["nodeQty"] = args.nodes
        clusterDictionary["clusterType"] = "pivotal-" + args.type
        clusterDictionary["segmentDBs"] = os.environ["SEGMENTDBS"]
        clusterDictionary["masterCount"] = 0
        clusterDictionary["accessCount"] = 0
        clusterDictionary["segmentCount"] = 0
        checkRequiredVars(args)
        if (args.type == "vanilla"):
            logging.info("Creating a base Cluster:" + clusterDictionary["clusterName"])
            logging.debug('With Dictionary: ' + json.dumps(clusterDictionary))
            ClusterBuilder.buildServers(clusterDictionary)
        elif (args.type == "gpdb"):
            print clusterDictionary["clusterName"] + ": Creating a Greenplum Database Cluster"
            logging.info("Creating a Greenplum Database Cluster:" + clusterDictionary["clusterName"])
            logging.debug('With Dictionary: ' + json.dumps(clusterDictionary))
            ClusterBuilder.buildServers(clusterDictionary)
            downloads = SoftwareDownload.downloadSoftware(clusterDictionary)
            InstallGPDB.installGPDB(clusterDictionary, downloads)
            stopTime = datetime.datetime.today()
            print  "Cluster " + sys.argv[1] + " Completion Time: ", stopTime
            logging.debug("Cluster " + sys.argv[1] + " Completion Time: " + str(stopTime))
            print  "Elapsed Time: ", stopTime - startTime
            logging.info('Elapsed Time: ' + str(stopTime - startTime))
        elif (args.type == "hdb"):
            print "HDB Builder"
            ClusterBuilder.buildServers(clusterDictionary)
            SoftwareDownload.downloadSoftware(clusterDictionary)
            #StudentAccounts.add(clusterDictionary)

            # if (args.verbose == True):
            #     clusterNodes = ClusterBuilder.buildServers(config)
            #     #createCluster(clusterDictionary,False)  #These are opposite because  the logging value is quiet_stdout so True is no logging
            #
            # else:
            #     ClusterBuilder.buildServers(clusterDictionary,config)
            #
            #    # createCluster(clusterDictionary,True)

            # elif (args.subparser_name == "destroy"):
            #     clusterDictionary["clusterName"] = args.clustername
            #     print "Not Yet Implemented"
            # elif (args.subparser_name == "query"):
            #     clusterInfo = queryCluster(args.clustername)
            #
            #
            # elif (args.subparser_name == "stage"):
            #     clusterInfo = queryCluster(args.clustername)
            #     # TEMPORARY    REMOVE!!!
            #     # with open("./" + clusterInfo["name"] + "/clusterInfo.json") as clusterInfoFile:
            #     #     clusterInfo = json.load(clusterInfoFile)
            #     #downloadSoftware(clusterDictionary, "pivotal-gpdb")
            #
            #     stageCluster(clusterInfo)
            #
            # elif (args.subparser_name == "gpdb"):
            #     clusterName = (args.clustername)
            #     with open("./" + clusterName + "/clusterInfo.json") as clusterInfoFile:
            #         clusterInfo = json.load(clusterInfoFile)
            #     Users.gpControl(clusterInfo,args.action)
            stopTime = datetime.datetime.today()
            print  "Cluster " + sys.argv[1] + " Completion Time: ", stopTime
            logging.debug("Cluster " + sys.argv[1] + " Completion Time: " + str(stopTime))
            print  "Elapsed Time: ", stopTime - startTime
            logging.info('Elapsed Time: ' + str(stopTime - startTime))
    elif (args.subparser_name == "query"):
        clusterDictionary["clusterName"] = args.clustername
        clusterDictionary["nodeQty"] = args.nodes
        if (args.config):
            print "Loading Configuration"
            load_dotenv(args.config)
            os.environ["CONFIGS_PATH"] = os.path.dirname(args.config) + '/'
        print clusterDictionary["clusterName"] + ": Querying Nodes in a Cluster"
        QueryCluster.checkServerState(clusterDictionary)
        stopTime = datetime.datetime.today()
        print  "Cluster " + sys.argv[1] + " Completion Time: ", stopTime
        logging.debug("Cluster " + sys.argv[1] + " Completion Time: " + str(stopTime))
        print  "Elapsed Time: ", stopTime - startTime
        logging.info('Elapsed Time: ' + str(stopTime - startTime))
    elif (args.subparser_name == "destroy"):
        clusterDictionary["clusterName"] = args.clustername
        clusterDictionary["nodeQty"] = args.nodes
        if (args.config):
            print "Loading Configuration"
            load_dotenv(args.config)
            os.environ["CONFIGS_PATH"] = os.path.dirname(args.config) + '/'
        print clusterDictionary["clusterName"] + ": Destroying Cluster"
        ClusterDestroyer.destroyServers(clusterDictionary)
        stopTime = datetime.datetime.today()
        print  "Cluster " + sys.argv[1] + " Completion Time: ", stopTime
        logging.debug("Cluster " + sys.argv[1] + " Completion Time: " + str(stopTime))
        print  "Elapsed Time: ", stopTime - startTime
        logging.info('Elapsed Time: ' + str(stopTime - startTime))


if __name__ == '__main__':

    os.environ["CAPE_HOME"] = os.getcwd()
    cliParse()
