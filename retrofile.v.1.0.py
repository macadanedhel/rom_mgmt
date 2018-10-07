#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os
from os.path import join, getsize
import ConfigParser, argparse
import xmltodict
import datetime

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


parser = argparse.ArgumentParser(
    description='Process some file.',
    epilog='comments > /dev/null'
)
parser.add_argument('--used',   "-u",   action='store_true',               help='files used')
parser.add_argument('--notused',   "-nu",   action='store_true',               help='files not used')
parser.add_argument('--write',   "-w",   action='store_true',               help='write logs to a file')
parser.add_argument('--list',   "-l",   action='store_true',               help='list file data')
parser.add_argument('--verbose',   "-v",   action='store_true',               help='LOL')
parser.add_argument('--generate',   "-g",   action='store_true',               help='Generates the gamelist.xml data')
parser.add_argument('--checkimage',   "-i",   action='store_true',               help='verify image path')

args = parser.parse_args()


VERBOSE = False
USED = False
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


#aux="/Users/e019553/Documents/09. mame/atari2600/gamelist.xml"
#aux1="/Users/e019553/Documents/09. mame/atari2600/"

print ("Reading data from: {0}".format(roms))

if args.used:
    USED=True
if args.notused:
    NOTUSED=True
if args.list:
    LIST=True
if args.generate:
    XML = True
if args.checkimage:
    IMAGE=True
if args.write:
    WRITE=True
    log = logcsv()
    log.write("dir"+DELIMITER+"name"+DELIMITER+"path"+DELIMITER+"issue"+DELIMITER+"size"+"\n")
if args.verbose:
    VERBOSE=True

for root, directories, filenames in os.walk(roms,topdown=False):
    #if VERBOSE:
    #    print ("{0}-{1}-{2}").format(root, directories, filenames)
    # Existe filelist en el directorio ?
    dir_ = root.split("/")
    dir = dir_[len(dir_) - 1]
    print "DIRECTORY {0}".format(dir)
    total = len(filenames)
    if filelist in filenames:
        #print root
        MGMTTLSIZE = 0
        NOMGMTTLSIZE = 0
        filenames.remove(filelist)
        #print root+"/"+file
        size=getsize(join(root, filelist))
        TOTALSIZE = TOTALSIZE + size
        # Tiene datos?
        if size>44:
            b=False
            data=ReadXML(root+"/"+filelist)
            # miramos el fichero de datos
            for i in  data['gameList']['game']:
                try:
                    mfile = i['path'].replace("./","",1)
                except:
                    if type(i) is unicode:
                        mfile = data['gameList']['game']['path'].replace("./","",1)
                        b=True
                if mfile in filenames:
                    # La rom existe en el fichero y el directorio
                    TOTALSIZE = TOTALSIZE + size
                    MGMTTLSIZE = MGMTTLSIZE +size
                    filenames.remove(mfile)
                    size = getsize(join(root, mfile))
                    if USED:
                        if WRITE:
                            log.write(dir + DELIMITER + mfile + DELIMITER + root + "/" + mfile + DELIMITER + MANAGED + DELIMITER + str(size) +"\n")
                        if LIST:
                            print ("\t\t{0}\t-\t{1}").format(mfile,MANAGED)
                        if IMAGE:
                            image=join(root, i['image'])
                            if not os.path.exists(image):
                                if not XML:
                                    print "BAD [{0}] {1}".format(mfile,image)
                                else:
                                    i['image']=""
                        if XML:
                            print "\t<game>"
                            for (k, v) in i.items() :
                                print ("\t\t<{0}>{1}</{0}>").format(k,v)
                            print "\t</game>"
                   # print ".",
                else:
                    # La rom existe en el fichero y NO en el directorio
                    print ("\t\t\t{0} - Not exits".format(mfile))
                    if WRITE:
                        log.write(dir + DELIMITER + mfile + DELIMITER +root+"/"+mfile + DELIMITER + NOTEXISTS +"\n")
                    if LIST:
                        print ("\t\t{0}\t-\t{1}").format(mfile,"not exists in directory")
                if b:
                    # fichero de 1 solo campo que tiene el diccionario así
                    total=1
                    break
            resto=len(filenames)
            prc = percent(resto,total)
            if resto>0:
                # No quedan ficheros en el directorio porque estaban todos en el fichero

                print ("\t{0:3.2f}% bad. This {1} of {2} files aren't managed:".format(prc, resto, total))
                for i in filenames:
                    size = getsize(join(root, i))
                    TOTALSIZE = TOTALSIZE + size
                    NOMGMTTLSIZE = NOMGMTTLSIZE + size
                    if NOTUSED:
                        print "\t\t{0}".format(i)
                        if WRITE:
                            log.write(dir + DELIMITER + i + DELIMITER +root+"/" + i + DELIMITER + UNMANAGED + DELIMITER + str(size) +"\n")
                        if LIST:
                            print ("\t\t{0}\t-\t{1}").format(i,UNMANAGED)
                        if XML:
                            tmp1 = mfile.split(".")
                            tmp1.pop()
                            name = ".".join(tmp1)
                            image = join(root, "images/"+name)
                            EXT="jpg"
                            print image+"."+EXT
                            if not os.path.exists(image+"."+EXT):
                                if not os.path.exists(image+"."+"png"):
                                    EXT=False
                                else:
                                    EXT="png"
                            print '\t<game source="mac">\n\
                                  <path>./{0}.zip</path>\n\
                                  <name>{0}</name>\n\
                                  <desc>Una prueba</desc>\n\
                                  <rating>0.0</rating>\n\
                                  <releasedate></releasedate>\n\
                                  <developer></developer>\n\
                                  <publisher></publisher>\n\
                                  <genre></genre>\n\
                                  <players>1</players>\n'.format(name)
                            if EXT in ['jpg','png']:
                                print '<image>./images/{0}-image.{1}</image>\n\
                                  <marquee>./images/{0}-marquee.{1}</marquee>\n\
                                </game>\n'.format(name,EXT)
                            else:
                                print '\t</game>\n'
            else:
                # TODOS gestionados
                print ("\t{0:3.2f}% managed".format(prc))
        # No tiene datos
        else:
            print "{0} files without resources file".format(total)
            if NOTUSED:
                print ("This files aren't managed:")

    #print "\n\n"
        TOTAL=NOMGMTTLSIZE+MGMTTLSIZE
        print "\ttotal size of not managed:\t{0}\t{1:3.2f}%".format(NOMGMTTLSIZE,percent(NOMGMTTLSIZE,TOTAL))
        print "\ttotal size of managed:\t\t{0}\t{1:3.2f}%".format(MGMTTLSIZE,percent(MGMTTLSIZE,TOTAL))
    else:
        if dir != 'images' :
            print "{0} files without resources file".format(total)
            if NOTUSED:
                print ("This files aren't managed:")
            for i in filenames:
                size = getsize(join(root, i))
                TOTALSIZE = TOTALSIZE + size
                NOMGMTTLSIZE = NOMGMTTLSIZE + size
                if NOTUSED:
                    print "\t\t{0}".format(i)
                    if WRITE:
                        log.write(
                            dir + DELIMITER + i + DELIMITER + root + "/" + i + DELIMITER + TOTALUNMANAGED + DELIMITER + str(
                                size) + "\n")
                    if LIST:
                        print ("\t\t{0}\t-\t{1}").format(i, TOTALUNMANAGED)
        print "\ttotal size of not managed:\t{0}".format(NOMGMTTLSIZE)


print "TOTAL SIZE:\t{0}".format(TOTALSIZE)
if WRITE:
    log.close()