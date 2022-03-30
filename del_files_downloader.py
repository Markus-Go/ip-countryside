import ftplib
import gzip
import shutil
import os

from config import *
from md5hash import scan

# @TODO check if download is needed ... 
# as the last update time of the files doesn't
# mean necessarily that the content has cahnged (was tested)
# it's better to compare the md5 values
# Therefore:
# download the md5 values for each delegation file
# implement the method download_del_file_needed() so that 
# it gets with ftp the corresponding md5 file from the server
# and compares it to the one in the subfolder del_files ... 

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

    

# @TODO after unzipping inetnum.gz delete the zipped files ...
# something like that os.remove(os.path.join(DEL_FILES_DIR, "{ALL_ZIPPED_FILESs}.gz"))
# is done after download finished

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

   # actual downloading is done in download_del_file function ... 
   if(download_del_files_needed(AFRINIC["host"], AFRINIC["del_cwd"], AFRINIC["del_md5"])):
       download_del_file(AFRINIC["host"], AFRINIC["del_cwd"], AFRINIC["del_fname"])
   if(download_del_files_needed(LACNIC["host"], LACNIC["del_cwd"], LACNIC["del_md5"])):
      download_del_file(LACNIC["host"],  LACNIC["del_cwd"],  LACNIC["del_fname"])
   if(download_del_files_needed(ARIN["host"],    ARIN["del_cwd"],    ARIN["del_md5"])):
      download_del_file(ARIN["host"],    ARIN["del_cwd"],    ARIN["del_fname"])
   if(download_del_files_needed(APNIC["host"],   APNIC["del_cwd"],   APNIC["del_md5"])):
      download_del_file(APNIC["host"],   APNIC["del_cwd"],   APNIC["del_fname"])
   #download_del_file(APNIC["host"],   APNIC["inet_cwd"],  APNIC["inet_fname_gz"], True)
   if(download_del_files_needed(RIPE["host"],    RIPE["del_cwd"],    RIPE["del_md5"])):
      download_del_file(RIPE["host"],    RIPE["del_cwd"],    RIPE["del_fname"])
   #download_del_file(RIPE["host"],    RIPE["inet_cwd"],   RIPE["inet_fname_gz"], True)
   
   os.remove(os.path.join(DEL_FILES_DIR, 'temp'))

   # return to project's root directory 
   os.chdir("../")

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