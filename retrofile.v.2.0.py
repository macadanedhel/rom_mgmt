#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os,glob,re, pprint, json, io
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

#-----------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description='Process some file.',
    epilog='comments > /dev/null'
)
parser.add_argument('--list',   "-l",   action='store_true',               help='files used')
parser.add_argument('--hash',   "-s",   action='store_true',               help='files used')
parser.add_argument('--hidden',   "-n",   action='store_true',               help='silent mode')
parser.add_argument('--filename',  "-f", type=str, help='a filename to parse')
parser.add_argument('--mime',  "-m", action='store_true',               help='files used')
parser.add_argument('--write',  "-w", action='store_true',               help='write results')
parser.add_argument('--listextension',  "-x", action='store_true',               help='list managed extensions ')
parser.add_argument('--test',  "-t", action='store_true',               help='check new functions')

args = parser.parse_args()

VERBOSE = False
HASH = False
MIME = False
HIDDEN = True
WRITE = False
EXT = False

ENVCONFIG = "config/env.ini"
EnvConfig = ConfigParser.ConfigParser()
Config = ConfigParser.ConfigParser()
EnvConfig.read(ENVCONFIG)
ROMS = EnvConfig.get('PATH', 'rom')

#-----------------------------------------------------------------------------------------------------------------------
percent = lambda x,y: (float(x)/float(y))*100 if y>0 else 0
#-----------------------------------------------------------------------------------------------------------------------
def hashfile (file,block_size=65536):
    hash = SHA256.new()
    with open(file, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hash.update(block)
    return hash.hexdigest()
#-----------------------------------------------------------------------------------------------------------------------
def fileinfo (path, file):
    meta={}
    meta['name']=file
    meta['bytes']=getsize(join(path, file))
    #if HIDDEN:
    #    print "\t{0}\t{1} bytes\t".format(file, getsize(join(path, file)))
    if HASH:
        hash = hashfile(join(path, file))
        #if HIDDEN :
        #    print "\t\t\t\t{0}".format(hash)
        meta ['hash'] = hash
    if MIME:
        pf = join(path, file)
        metadata = metadata_for(pf)
        charset = getTerminalCharset()
        #if HIDDEN:
        #    for line in metadata:
        #        print makePrintable(line, charset)
        meta ['mime'] = metadata
    return meta
#-----------------------------------------------------------------------------------------------------------------------
def hike (ROMS):
    for root, directories, filenames in os.walk(ROMS,topdown=False):
        dir_ = root.split("/")
        dir = dir_[len(dir_) - 1]
        print "DIRECTORY {0}".format(dir)
        #total = len(filenames)
        roms = EnvConfig.get('GAMES', 'file')
        extension = GenerateExtension(roms)
        for i in filenames:
            meta = fileinfo(root, i)
            data2dict(meta, extension)
#-----------------------------------------------------------------------------------------------------------------------
def metadata_for(filename):

    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
     print "Unable to parse file [{0}]".format(filename)
     #exit(1)
    try:
     metadata = extractMetadata(parser)
    except HachoirError, err:
     print "Metadata extraction error: %s" % unicode(err)
     metadata = None
    if not metadata:
     print "Unable to extract metadata"
     text = ["Unable to extract metadata"]
     #exit(1)
    else:
        text = metadata.exportPlaintext()
        #charset = getTerminalCharset()
        #for line in text:
         #print makePrintable(line, charset)
    return text
#-----------------------------------------------------------------------------------------------------------------------
def writeJson (datastore):
    USERCONFIG = "config/env.ini"
    Config = ConfigParser.ConfigParser()
    Config.read(USERCONFIG)
    filename = datetime.datetime.now().strftime("%Y%m%d")
    absfile = Config.get('LOG', 'path') + filename + ".json"
    with io.open(absfile, 'a', encoding='utf-8') as f:
        f.write(unicode(json.dumps(datastore)))
#-----------------------------------------------------------------------------------------------------------------------
def data2dict (meta, extension):
    filexpresion = 'File "(\w+[\s*\(\)\w*\[\]_-]*\.\w+)":'
    sizexpresion = '- File size: (\w+.\w+ \w+)'
    cfsexpresion = '- Compressed file size: (\w+.\w+ \w+)'
    crateexpresion = '- Compression rate: (\w+.\w+)'
    cdateexpresion = '- Creation date: (\d+ - \d+ - \d+ \d+:\d+:\d+)'
    compexpresion = '- Compression: (\w+)'
    mimexpresion = '- MIME type: (\w+[\s+\/]*\w+)'
    endianexpresion = '- Endianness: (\w+[\s*\w*]*)'
    filenamexp = '\w+[\s*\(\)\w*\[\]_-]*(.\w+)'
    files = []
    file = {}
    rom = {}
    rom['name'] = meta['name']
    rom['bytes'] = meta['bytes']
    rom['KB'] = meta['bytes']/1024
    if HASH:
        rom['hash'] = meta['hash']
    if MIME:
        for element in meta['mime'][:3]:
            if re.search(mimexpresion, element):
                rom['mime'] = re.search(mimexpresion, element).group(1)
            elif (re.search(endianexpresion, element)):
                rom['endian'] = re.search(endianexpresion, element).group(1)
        for element in meta['mime'][3:]:
            if re.search(filexpresion, element):
                file['name'] = re.search(filexpresion, element).group(1)
                extaux=re.search(filenamexp, file['name']).group(1)
                file ['potential_consoles'] = extension[extaux]
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
            else:
                file['no_mime'] = unicode(element)
                print '-----'+unicode(element)
        if len(files)>0 :
            rom['files'] = files
    if HIDDEN:
        pprint.pprint(rom, width=4)

    if WRITE:
        writeJson(rom)
#-----------------------------------------------------------------------------------------------------------------------
def consolesWithExtension (ext, gamestore):
    result = []
    for i in gamestore['roms']:
        if len(i['Extension'].split(" ")) > 1:
            if ext+" " in i['Extension']:
                result.append(i['name'])
        elif ext in i['Extension']:
            result.append(i['name'])
    return result
#-----------------------------------------------------------------------------------------------------------------------
def GenerateExtension (roms):
    extConsoles = {}
    if os.path.exists(roms):
        with open(roms, 'r') as f:
            gamestore = json.load(f)
        extension = []
        for i in gamestore['roms']:
            extension = list(set(extension + i['Extension'].split(" ")))
        for i in extension:
            extConsoles[i] = consolesWithExtension(i,gamestore)
            if EXT:
                print "{0}:{1}".format(i,extConsoles[i])
    return extConsoles
#-----------------------------------------------------------------------------------------------------------------------

print ("Reading data from: {0}".format(ROMS))
if args.hidden:
    HIDDEN=False
if args.hash:
    HASH=True
if args.mime:
    MIME=True
if args.write:
    WRITE=True
if args.list:
    hike(ROMS)
elif args.filename and  os.path.exists(args.filename):
    dir_ = args.filename.split("/")
    file = dir_.pop()
    dir_.insert(0,os.getcwd())
    dir_ = "/".join(dir_)
    roms = EnvConfig.get('GAMES', 'file')
    extension = GenerateExtension(roms)
    meta=fileinfo(dir_,file)
    data2dict(meta, extension)
elif args.listextension:
    EXT = True
    roms = EnvConfig.get('GAMES', 'file')
    GenerateExtension(roms)
elif args.test:
    print "test"
