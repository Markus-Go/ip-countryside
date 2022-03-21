import ftplib
import gzip
import shutil
import os

from config import *


# @TODO check if download is needed ... 
def download_del_files():
   """
   Downloads all delegation files

   Arguments
   ----------
   none

   Returns
   ----------
   boolean value which indicates wether downloading was successful

   """

   # collect delegation files in one specific folder "del_files"
   # if the folder doesn't exist then try to create one first ... 
   del_files_dir = "del_files"

   try:
    
    if not os.path.exists(del_files_dir):
        os.makedirs(del_files_dir)

    # change to del_files directory
    os.chdir(del_files_dir)
   
   except OSError as e:
    
        print(e)

   # actual downloading is done in download_del_file function ... 
   download_del_file(AFRINIC["host"], AFRINIC["cwd"], AFRINIC["fname"])
   download_del_file(LACNIC["host"], LACNIC["cwd"], LACNIC["fname"])
   download_del_file(ARIN["host"], ARIN["cwd"], ARIN["fname"])
   download_del_file(APNIC["host"], APNIC["cwd"], APNIC["fname"])
   download_del_file(APNIC["host"], APNIC["splitcwd"], APNIC["splitfname"], True)
   download_del_file(RIPE["host"], RIPE["cwd"], RIPE["fname"])
   download_del_file(RIPE["host"], RIPE["splitcwd"], RIPE["splitfname"], True)

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

        with open(localfile, 'wb') as file:

            print("Downloading file " + delFileName)

            ftp.retrbinary('RETR %s' % delFileName, file.write)

            print("Download of " + delFileName + " finished.")

        ftp.close()

        # unzip of the .gz file
        if(zipped):

            localfile = os.path.splitext(delFileName)[0]

            with gzip.open(delFileName, 'rb') as f_in:

                with open(localfile, 'wb') as f_out:

                    shutil.copyfileobj(f_in, f_out)

    except IOError as e:

        print(e)


def download_del_file_needed():
    return False

    