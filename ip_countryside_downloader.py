import ftplib
import gzip
import ipaddress
import shutil
import os

from config import *
from md5hash import scan
from datetime import datetime


# @TODO is it possible to reduce number of ftp connections ?                -> Aufwand 5/8
# currently we're opening more than 10 ftp connections
# maybe we can reduce this number to only 6 ? (If this is more
# efficient)

# @TODO provide an force optional parameter which forces the download
# even if download is not neeeded!                                          -> Aufwand 5/8


# @TODO since that there aren't any md5 files for the inetnum databases
# we can use the date instead -> this COULD reduce number of downloads      -> Aufwand 5/8 
   

# @TODO when project is done:
# remove the comment where the zipped files are deleted after downloading 

def get_timestamp(host, cwd, delFileName, localfile):

    ftp = ftplib.FTP(host)
    ftp.login()
    print("Connected to " + host)
    ftp.cwd(cwd)

    if not os.path.exists(localfile):
        open(localfile,'w').close
    
    datetimeftp = ftp.sendcmd('MDTM ' + delFileName)
    modifiedTimeFtp = datetime.strptime(datetimeftp[4:], "%Y%m%d%H%M%S").strftime("%d %b %Y %H:%M:%S")
    
    with open(localfile, "r") as file:
        last = file.readline()
        try:
            last = datetime.strptime(last, "%d %b %Y %H:%M:%S")
            diff = datetime.strptime(datetimeftp[4:], "%Y%m%d%H%M%S") - last
        except:
            with open(localfile, "w") as file:
                file.writelines(modifiedTimeFtp)
            ftp.close()
            print("No timestamp yet\n")
            return True
        
    if (diff.days >= 7):
        with open(localfile, "w") as file:
            file.writelines(modifiedTimeFtp)
        ftp.close()
        print("1 week or older\n")
        return True
    else:
        ftp.close()
        print("younger than one week\n")
        return False

def download_del_files_needed(host, cwd, delFileName):
    
    ftp = ftplib.FTP(host)
    ftp.login()
    print("Connected to " + host)
    ftp.cwd(cwd)
    localfile = delFileName

    if not os.path.exists(delFileName):
        open(delFileName,'wb').close

    with open('temp', "wb") as file:
        print("Downloading file " + delFileName)
        ftp.retrbinary('RETR %s' % delFileName, file.write)
        print("Finished.")

    if (scan(delFileName) == scan('temp')):
        ftp.close()
        print("No changes in file\n")
        return False
    else:
        with open(localfile, "wb") as file:
            ftp.retrbinary('RETR %s' % delFileName, file.write)
        ftp.close()
        print("New changes in file\n")
        return True

 
def download_del_files(force):
   """
   Downloads all delegation files

   Arguments
   ----------
   none

   Returns
   ----------
   boolean value which indicates wether downloading was successful

   """


   # if downloading is not necessary and force is not set
   # skip downloading ...
   # @TODO logic not correct

   # if(not download_del_files_needed() and not force):     
   #    return

   # collect delegation files in one specific folder "del_files"
   # if the folder doesn't exist then try to create one first ... 
   del_files_dir = DEL_FILES_DIR

   try:
    
    if not os.path.exists(del_files_dir):
        os.makedirs(del_files_dir)

    # change to del_files directory
    os.chdir(del_files_dir)
   
   except OSError as e:
    
        print(e)
    
   # download if md5 changed

   # actual downloading is done in download_del_file function ... 
   #if(download_del_files_needed(AFRINIC["host"], AFRINIC["del_cwd"], AFRINIC["del_md5"])):
   #    download_del_file(AFRINIC["host"], AFRINIC["del_cwd"], AFRINIC["del_fname"])
   #if(download_del_files_needed(LACNIC["host"], LACNIC["del_cwd"], LACNIC["del_md5"])):
   #   download_del_file(LACNIC["host"],  LACNIC["del_cwd"],  LACNIC["del_fname"])
   #if(download_del_files_needed(ARIN["host"],    ARIN["del_cwd"],    ARIN["del_md5"])):
   #   download_del_file(ARIN["host"],    ARIN["del_cwd"],    ARIN["del_fname"])
   #if(download_del_files_needed(APNIC["host"],   APNIC["del_cwd"],   APNIC["del_md5"])):
   #   download_del_file(APNIC["host"],   APNIC["del_cwd"],   APNIC["del_fname"])
   #if(download_del_files_needed(RIPE["host"],    RIPE["del_cwd"],    RIPE["del_md5"])):
   #   download_del_file(RIPE["host"],    RIPE["del_cwd"],    RIPE["del_fname"])

   #download if older than one week

   if(get_timestamp(AFRINIC["host"], AFRINIC["del_cwd"], AFRINIC["del_fname"], AFRINIC["del_timestamp"])):
       download_del_file(AFRINIC["host"], AFRINIC["del_cwd"], AFRINIC["del_fname"])
   if(get_timestamp(LACNIC["host"], LACNIC["del_cwd"], LACNIC["del_fname"], LACNIC["del_timestamp"])):
      download_del_file(LACNIC["host"],  LACNIC["del_cwd"],  LACNIC["del_fname"])
   if(get_timestamp(ARIN["host"],    ARIN["del_cwd"],    ARIN["del_fname"],    ARIN["del_timestamp"])):
      download_del_file(ARIN["host"],    ARIN["del_cwd"],    ARIN["del_fname"])
   if(get_timestamp(APNIC["host"],   APNIC["del_cwd"],   APNIC["del_fname"],   APNIC["del_timestamp"])):
      download_del_file(APNIC["host"],   APNIC["del_cwd"],   APNIC["del_fname"])
   if(get_timestamp(RIPE["host"],    RIPE["del_cwd"],    RIPE["del_fname"],    RIPE["del_timestamp"])):
      download_del_file(RIPE["host"],    RIPE["del_cwd"],    RIPE["del_fname"])

    #irt files
   if(get_timestamp(APNIC["host"],   APNIC["inet_cwd"],  APNIC["irt_fname_gz"], APNIC["irt_timestamp"])):
      download_del_file(APNIC["host"],   APNIC["inet_cwd"],  APNIC["irt_fname_gz"], True)
   if(get_timestamp(RIPE["host"],    RIPE["inet_cwd"],   RIPE["irt_fname_gz"], RIPE["irt_timestamp"])):  
      download_del_file(RIPE["host"],    RIPE["inet_cwd"],   RIPE["irt_fname_gz"], True)

    #zip files
   if(get_timestamp(APNIC["host"],   APNIC["inet_cwd"],  APNIC["inet_fname_gz"], APNIC["inet_timestamp"])):
      download_del_file(APNIC["host"],   APNIC["inet_cwd"],  APNIC["inet_fname_gz"], True)
   if(get_timestamp(RIPE["host"],    RIPE["inet_cwd"],   RIPE["inet_fname_gz"], RIPE["inet_timestamp"])):  
      download_del_file(RIPE["host"],    RIPE["inet_cwd"],   RIPE["inet_fname_gz"], True)
   
   if os.path.exists('temp'):
       os.remove(os.path.join(DEL_FILES_DIR, 'temp'))

   # return to project's root directory 
   os.chdir(ROOT_DIR)

   return True


def download_del_file(host, cwd, delFileName, zipped=False):
    """
    Downloads a delegation file per ftp and unzipp it if needed

    Arguments
    ----------
    host: string
        Name of the host to connect with or IP address

    cwd: string
        Change working directory (e.g. to the directory where the file
        is located on host's machine)

    delFileName: string
        Name of the file to be downloaded

    zipped: bool
        If True the function will additionally unzip the downloaded file

    Returns
    ----------
    void

    """

    try:

        ftp = ftplib.FTP(host)
        ftp.login()

        print("Connected to " + host)

        ftp.cwd(cwd)

        localfile = delFileName

        with open(localfile, "wb") as file:

            print("Downloading file " + delFileName)

            ftp.retrbinary('RETR %s' % delFileName, file.write)

            print("Finished.\n")

        ftp.close()

        # unzip of the .gz file
        if(zipped):

            localfile = os.path.splitext(delFileName)[0]

            with gzip.open(delFileName, "rb") as f_in:

                with open(localfile, "wb") as f_out:

                    shutil.copyfileobj(f_in, f_out)

            #delete zipFile
            #os.remove(os.path.join(DEL_FILES_DIR, delFileName))

    except IOError as e:

        print(e)


def run_downloader(force=True):

    download_del_files(force)


run_downloader()