# db_missing_date_fix
Parse through dropbox media and update date info if missing metadata encountered

Windows-based python script to update data info on media files with missing date/time.  Script will parse through your dropbox account and when media with missing dates is encountered, it copies locally, prompts for new date/time, updates exif info, then re-uploads.

Wishlist
- handle video files (as well as picture files)
- possible re-work for linux/mac as well as windows
- refactor with config file
