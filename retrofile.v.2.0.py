#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os,glob,re, pprint
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
parser.add_argument('--hidden',   "-n",   action='store_true',               help='silent mode')
parser.add_argument('--filename',  "-f", type=str, help='a filename to parse')
parser.add_argument('--mime',  "-m", action='store_true',               help='files used')


args = parser.parse_args()


VERBOSE = False
HASH = False
MIME = False
HIDDEN = True

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

def fileinfo (path, file):
    meta={}
    meta['name']=file
    meta['bytes']=getsize(join(path, file))
    if HIDDEN:
        print "\t{0}\t{1} bytes\t".format(file, getsize(join(path, file)))
    if HASH:
        hash = hashfile(join(path, file))
        if HIDDEN :
            print "\t\t\t\t{0}".format(hash)
        meta ['hash'] = hash
    if MIME:
        pf = join(path, file)
        metadata = metadata_for(pf)
        charset = getTerminalCharset()
        if HIDDEN:
            for line in metadata:
                print makePrintable(line, charset)
        meta ['mime'] = metadata
    return meta


def hike ():
    for root, directories, filenames in os.walk(roms,topdown=False):
        dir_ = root.split("/")
        dir = dir_[len(dir_) - 1]
        print "DIRECTORY {0}".format(dir)
        #total = len(filenames)
        for i in filenames:
            meta = fileinfo(root, i)
            data2dict(meta)

def metadata_for(filename):

    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
     print "Unable to parse file [{0}]".format(filename)
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
    return text

def data2dict (meta):
    filexpresion = 'File "(\w+[\s*\(\)\w*\[\]_-]*\.\w+)":'
    sizexpresion = '- File size: (\w+.\w+ \w+)'
    cfsexpresion = '- Compressed file size: (\w+.\w+ \w+)'
    crateexpresion = '- Compression rate: (\w+.\w+)'
    cdateexpresion = '- Creation date: (\d+ - \d+ - \d+ \d+:\d+:\d+)'
    compexpresion = '- Compression: (\w+)'
    mimexpresion = '- MIME type: (\w+[\s+\/]*\w+)'
    endianexpresion = '- Endianness: (\w+[\s*\w*]*)'

    files = []
    file = {}
    rom = {}
    rom['name'] = meta['name']
    rom['bytes'] = meta['bytes']
    for element in meta['mime'][:3]:
        if re.search(mimexpresion, element):
            rom['mime'] = re.search(mimexpresion, element).group(1)
        elif (re.search(endianexpresion, element)):
            rom['endian'] = re.search(endianexpresion, element).group(1)
    for element in meta['mime'][3:]:
        # print element
        if re.search(filexpresion, element):
            file['name'] = re.search(filexpresion, element).group(1)
        elif (re.search(sizexpresion, element)):
            file['filesize'] = re.search(sizexpresion, element).group(1)
        elif (re.search(cfsexpresion, element)):
            file['CompressedFileSize'] = re.search(cfsexpresion, element).group(1)
        elif (re.search(crateexpresion, element)):
            file['CompressionRate'] = re.search(crateexpresion, element).group(1)
        elif (re.search(cdateexpresion, element)):
            file['CreationDate'] = re.search(cdateexpresion, element).group(1)
        elif (re.search(compexpresion, element)):
            file['Compression'] = re.search(compexpresion, element).group(1)
            files.append(file)
            file = {}
    rom['files'] = files
    pprint.pprint(rom, width=4)


print ("Reading data from: {0}".format(roms))
if args.hidden:
    HIDDEN=False
if args.hash:
    HASH=True
if args.mime:
    MIME=True
if args.list:
    hike()
elif args.filename and  os.path.exists(args.filename):
    dir_ = args.filename.split("/")
    file = dir_.pop()
    dir_.insert(0,os.getcwd())
    dir_ = "/".join(dir_)
    meta=fileinfo(dir_,file)
    data2dict(meta)





if WRITE:
    log.close()