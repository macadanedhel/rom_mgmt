#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os,glob
from os.path import join, getsize
import ConfigParser, argparse
import xmltodict
import datetime
from Crypto.Hash import SHA256
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset




def ReadXML (xml_file,xml_attribs=True ):
    with open(xml_file, "rb") as f:  # notice the "rb" mode
        d = xmltodict.parse(f, xml_attribs=xml_attribs)
    return d

class logcsv:
    USERCONFIG = "config/env.ini"
    Config = ConfigParser.ConfigParser()
    Config.read(USERCONFIG)
    filename = datetime.datetime.now().strftime("%Y%m%d")
    absfile = Config.get('LOG', 'path') + filename + ".csv"
    twitter_api = ""

    def __init__(self):
        if not os.path.exists(self.Config.get('LOG', 'path')):
            print ('Dir {0} not found, created').format(Config.get('LOG', 'path'))
            os.makedirs(self.Config.get('LOG', 'path'))
            self.df = open(self.absfile, 'w')
        elif not os.path.exists(self.absfile):
            self.df = open(self.absfile, 'w')
        else:
            self.df = open(self.absfile, 'w')
    def write (self, string2w):
        self.df.write(string2w)
    def close (self):
        self.df.close()

def hashfile (file,block_size=65536):
    hash = SHA256.new()
    with open(file, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hash.update(block)
    return hash.hexdigest()

parser = argparse.ArgumentParser(
    description='Process some file.',
    epilog='comments > /dev/null'
)
parser.add_argument('--list',   "-l",   action='store_true',               help='files used')
parser.add_argument('--hash',   "-s",   action='store_true',               help='files used')
parser.add_argument('--filename',  "-f", type=str, help='a filename to parse')
parser.add_argument('--mime',  "-m", action='store_true',               help='files used')

args = parser.parse_args()


VERBOSE = False
HASH = False
MIME = False

NOTUSED = False
WRITE = False
LIST = False
XML = False
IMAGE = False
MGMTTLSIZE = 0
TOTALSIZE = 0
NOMGMTTLSIZE = 0

percent = lambda x,y: (float(x)/float(y))*100 if y>0 else 0

log=""
ENVCONFIG = "config/env.ini"
EnvConfig = ConfigParser.ConfigParser()
Config = ConfigParser.ConfigParser()
EnvConfig.read(ENVCONFIG)
roms = EnvConfig.get('PATH', 'rom')
filelist = EnvConfig.get('PATH', 'gamelist')
DELIMITER = EnvConfig.get('PATH', 'delimiter')
MANAGED = EnvConfig.get('PATH', 'managed')
UNMANAGED = EnvConfig.get('PATH', 'unmanaged')
NOTEXISTS = EnvConfig.get('PATH', 'notexists')
TOTALUNMANAGED = EnvConfig.get('PATH', 'totalunmanaged')

MGMTTLSIZE = 0
TOTALSIZE = 0
NOMGMTTLSIZE = 0

def hike ():
    for root, directories, filenames in os.walk(roms,topdown=False):
        #print ("{0}-{1}-{2}").format(root, directories, filenames)
        # Existe filelist en el directorio ?
        dir_ = root.split("/")
        dir = dir_[len(dir_) - 1]
        print "DIRECTORY {0}".format(dir)
        total = len(filenames)
        #print root
        #print directories
        for i in filenames:
            print "\t{0}\t{1}\t".format(i,getsize(join(root, i)))
            if HASH:
                print "\t\t\t\t{0}".format(hashfile(join(root, i)))
            if MIME:
                pf=join(root, i)
                metadata = metadata_for(pf)
                print metadata

def metadata_for(filename):

    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
     print "Unable to parse file"
     exit(1)
    try:
     metadata = extractMetadata(parser)
    except HachoirError, err:
     print "Metadata extraction error: %s" % unicode(err)
     metadata = None
    if not metadata:
     print "Unable to extract metadata"
     exit(1)

    text = metadata.exportPlaintext()
    charset = getTerminalCharset()
    #for line in text:
     #print makePrintable(line, charset)

    return metadata


print ("Reading data from: {0}".format(roms))

if args.hash:
    HASH=True
if args.mime:
    MIME=True
if args.list:
    hike()
elif args.filename and  os.path.exists(args.filename):
    #dir_ = args.filename.split("/")
    #file = dir_[len(dir_) - 1]
    print "Current working dir : %s" % os.getcwd()
    #st = os.stat(args.filename)
    #git print st
    if HASH:
        print "\t\t\t\t{0}".format(hashfile(args.filename))
        #args.filename="/".join([os.getcwd(),file])
    if MIME:
        print ("Getting data from {}".format(args.filename));
        metadata = metadata_for(args.filename)
        print metadata


if WRITE:
    log.close()