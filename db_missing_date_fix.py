# Dropbox_MissingDateFix.py
import subprocess
import dropbox # download dropbox python sdk
import re
import shutil
import os
import webbrowser

EXIFTOOL = 'c:\\temp\\ExifTool\exiftool.exe' # path to ExifTool from http://www.sno.phy.queensu.ca/~phil/exiftool/ (download windows executable
dropbox_local_path_temp = 'c:\\temp\\dropbox\\' # local directory for temporary picture updating
dropbox_local_path_upload = 'C:\\Users\\xxxxxx\\Dropbox\\Missing_Date_Fix\\' # local directory which is configured as a dropbox upload location
client = dropbox.client.DropboxClient('xxxxxxxx') # create an app on dropbx and copy you token here
info = client.account_info()
print('Dropbox Account: ' + info['display_name'])
print('Loading pictures from Dropbox; please wait...')
print('Options:')
print('  - If you see a date at the promt like [MM/YYYY], hit Enter to update or type your own')
print('  - Enter new month and date as M/YY, MM/YY, M/YYYY, MM/YYYY')
print('  - Type "skip" or just hit Enter to go to the next file with no changes (assuming no\n    recommended date in brackets)')
print('  - Type "del" to delete the file from Dropbox (useful for duplicates)')
print('  - Type "exit" to quit the program')
# function which does all of the work; mostly based on an example from the dropbox python api example
def list_files(client, files=None, cursor=None):
    if files is None:
        files = {}
    has_more = True
    while has_more:
        result = client.delta(cursor,include_media_info=True)
        cursor = result['cursor']
        has_more = result['has_more']
        for lowercase_path, metadata in result['entries']:
            downloaded = False
            local = False
            # file name and location preparation
            file_path_remote = metadata['path']
            file_name = file_path_remote.split('/')[-1]
            file_path_local_no_date = dropbox_local_path_temp + file_name
            file_path_local_with_date = dropbox_local_path_upload + file_name
            if metadata is not None:
                files[lowercase_path] = metadata
            else:
                # no metadata indicates a deletion
                # remove if present
                files.pop(lowercase_path, None)
                # in case this was a directory, delete everything under it
                for other in files.keys():
                    if other.startswith(lowercase_path + '/'):
                        del files[other]
            if 'video_info' in metadata and str(metadata['video_info']['time_taken']) == 'None':
                 # skip avi and 3gp files (not supported by exiftool
                if re.search('.AVI$', metadata['path'], re.IGNORECASE) != None:
                    continue
                if re.search('.3GP$', metadata['path'], re.IGNORECASE) != None:
                    continue
                # If Video file but not local pc name, skip for now
                if re.search('xxxxxxx',os.environ['COMPUTERNAME'], re.IGNORECASE) == None: # update with local pc name
                    continue
                print('File:  ' + metadata['path'] +'; Date Taken:  '+ str(metadata['video_info']['time_taken']) + '; File Type:  Video; Size:  ' + str("{:,}".format(round(metadata['bytes']/1024),0)) + ' KB')
                # check for local pc presence
                if re.search('xxxxxxx', metadata['path']) != None: # Set local PC location
                    pathsplit = metadata['path'].split('/')
                    dbpath = 'c:\\users\\xxx\\dropbox\\xxxxxxx\\'  # update with local pc name
                    medpath = dbpath + '\\'.join(pathsplit[2:])
                    print(medpath)
                    if os.path.exists(medpath) != None:
                        print('Local Copy Found:  ' + medpath)
                        file_path_local_no_date = medpath
                        local = True
                if local == False:
                    print('Downloading file:  ' + metadata['path'])
                    out = open(file_path_local_no_date, 'wb')
                    with client.get_file(file_path_remote) as f:
                        out.write(f.read())
                downloaded = True
            if 'photo_info' in metadata and str(metadata['photo_info']['time_taken']) == 'None':
                print('Downloading file:  ' + metadata['path'] +':')
                #print('  Date Taken: '+ str(metadata['photo_info']['time_taken']) + '; File Type:  Photo; Size:  ' + str("{:,}".format(round(metadata['bytes']/1024),0)) + ' KB')
                #print('  Downloading file:  ' + metadata['path'])
                out = open(file_path_local_no_date, 'wb')
                with client.get_file(file_path_remote) as f:
                    out.write(f.read())
                downloaded = True
            if downloaded:
                # Check for usable date
                new_date_taken_orig_query = ''
                month_year = re.search('/([A-Za-z]+\s\d{4})/',file_path_remote)
                if month_year != None:
                    month,year = month_year.group(1).split(' ')
                    new_date_taken_orig_query = month_to_digit(month.upper()) + '/' + year
                # Preview the file
                webbrowser.open(file_path_local_no_date)
                # Enter the month and year; I didn't include date since it may be unlikely to remember it
                if new_date_taken_orig_query == '':
                    new_date_taken_orig = input('  Enter new date taken:  ')
                else:
                    new_date_taken_orig = input('  Enter new date taken: [' + new_date_taken_orig_query + ']:  ')
                if new_date_taken_orig_query != '' and new_date_taken_orig == '':
                    new_date_taken_orig = new_date_taken_orig_query
                if new_date_taken_orig_query == '' and new_date_taken_orig == '':
                    new_date_taken_orig = 'skip'
                # Skip the file
                if new_date_taken_orig == 'skip':
                    print('  Skipping Dropbox file')
                    continue
                # Delete the file
                if new_date_taken_orig == 'del':
                    print('  Deleting Dropbox file')
                    client.file_delete(file_path_remote)
                    continue
                # exit
                if new_date_taken_orig == 'exit':
                    print('  Exiting program')
                    exit()
                # Validate the date format
                new_date_taken = new_date_taken_orig.split('/')
                if len(new_date_taken) != 2:
                    print(new_date_taken + ' is malformed (should be [M]M/[YY]YY)')
                    exit()
                mo = new_date_taken[0]
                if len(mo) == 1 and re.match('[1-9]',mo) != None:
                    mo = '0' + mo
                yr = new_date_taken[1]
                if len(yr) == 2 and 0 <= int(yr) <= 14:
                    yr = '20' + yr
                if len(yr) == 2 and 20 <= int(yr) <= 99:
                    yr = '19' + yr
                new_date_taken = mo + '/' + yr
                print('  Updating date to: ' + new_date_taken)
                if re.match('\d{2}/\d{4}$',new_date_taken) == None:
                    print(new_date_taken + ' is malformed (should be [M]M/[YY]YY)')
                    exit()
                # Update Date Taken EXIF attribute
                month,year = new_date_taken.split('/')
                new_date_taken = '-DateTimeOriginal=' + year + ':' + month + ':01:00:00:00'
                cmd_args = [EXIFTOOL, new_date_taken, '-overwrite_original_in_place', file_path_local_no_date]
                p = subprocess.Popen(cmd_args, stdout=None).wait()
                if local == False:
                    #print('  Deleting original remote file: ' + file_path_remote)
                    # Delete the dropbox copy
                    client.file_delete(file_path_remote)
                    # Queue up the new version with correct date
                    #print('  Sending updated file back to Dropbox: ' + file_path_local_with_date)
                    shutil.copy2(file_path_local_no_date, file_path_local_with_date)
    return files, cursor

def month_to_digit(arg):
    if re.match('JAN',arg) != None: return '01'
    if re.match('FEB',arg) != None: return '02'
    if re.match('MAR',arg) != None: return '03'
    if re.match('APR',arg) != None: return '04'
    if re.match('MAY',arg) != None: return '05'
    if re.match('JUN',arg) != None: return '06'
    if re.match('JUL',arg) != None: return '07'
    if re.match('AUG',arg) != None: return '08'
    if re.match('SEP',arg) != None: return '09'
    if re.match('OCT',arg) != None: return '10'
    if re.match('NOV',arg) != None: return '11'
    if re.match('DEC',arg) != None: return '12'

files, cursor = list_files(client)
