#!/usr/bin/env python3
import requests, os, bs4, pprint, logging, threading
from datetime import datetime, date, timedelta

logging.basicConfig(filename='MissingCalvinDataLog.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

download_threads = []
overall_start = date(1985,11,18) #first comic 1985,11,18
overall_end = date(1995,12,31) # last comic 1995,12,31. Next comic after last: 2007/01/01
overall_date_list = [(overall_start + timedelta(days=x)).strftime('%Y/%m/%d') for x in range((overall_end-overall_start).days + 1)]


# If transcripts module has already been saved, import it, else create it.
try:
    import transcripts_and_tags
except ModuleNotFoundError:
    with open('transcripts_and_tags.py', 'w') as file_object:
        file_object.write('transcripts = {} \n')
        file_object.write('tags = {} \n')
    import transcripts_and_tags
    logging.info('Created module.')

new_transcripts = transcripts_and_tags.transcripts
new_tags = transcripts_and_tags.tags

os.makedirs('calvin_and_hobbes_comics', exist_ok=True)

def download_calvin(start_date, end_date):
    start_datetime_object = datetime.strptime(start_date, '%Y/%m/%d')
    end_datetime_object = datetime.strptime(end_date, '%Y/%m/%d')
    thread_date_list = [(start_datetime_object + timedelta(days=x)).strftime('%Y/%m/%d') for x in range((end_datetime_object - start_datetime_object).days + 1)]

    for comic_date in (thread_date_list):
        comic_iso_date = datetime.strptime(comic_date, '%Y/%m/%d').strftime('%Y-%m-%d')
        #if comic hasn't been downloaded already
        if not os.path.isfile(f'calvin_and_hobbes_comics/{comic_iso_date}'):        
            try:
                res = requests.get(f'https://www.gocomics.com/calvinandhobbes/{comic_date}')
                res.raise_for_status()
                soup = bs4.BeautifulSoup(res.text, 'html.parser')       
                comic_picture_elem = soup.select('.item-comic-image > img:nth-child(1)')
                comic_trans_elem = soup.select('.comic__transcript-container > p:nth-child(2)')
                
                # Look for and try to save transcript to directory dictionary
                try:
                    comic_trans = comic_trans_elem[0].getText().lower()
                    new_transcripts[comic_iso_date] = comic_trans
                except:
                    logging.error(comic_iso_date + ' - Could not find transcript for comic')

                comic_url = comic_picture_elem[0].get('src')

                res = requests.get(comic_url)
                res.raise_for_status()

                comic_container = soup.select('.comic')
                comic_tags = comic_container[0].get('data-tags')

                # If tags exist, save in tags directory dictionary
                if len(comic_tags) > 0:
                    new_tags[comic_iso_date] = comic_tags.split(',')
                else:
                    logging.error(comic_iso_date + ' - Could not find tags for comic')

                # save comic image
                with open(os.path.join('calvin_and_hobbes_comics', comic_iso_date), 'wb') as image_file:
                    for chunk in res.iter_content(100000):
                        image_file.write(chunk)
                print(comic_iso_date) # for debug
            # On error, stop loop to save progress
            except:
                break

for i in range(0, len(overall_date_list), 60):
    thread_start = overall_date_list[i]
    thread_end = (datetime.strptime(overall_date_list[i], '%Y/%m/%d') + timedelta(days=59)).strftime('%Y/%m/%d') # End at 9 days past start date
    download_thread = threading.Thread(target=download_calvin, args=(thread_start, thread_end))
    download_threads.append(download_thread)
    download_thread.start()

for download_thread in download_threads:
    download_thread.join()
print('Done downloading comics.')

# Overwrite module with dictionaries with new entries added
with open('transcripts_and_tags.py', 'w') as file_object:
    file_object.write('transcripts = ' + pprint.pformat(new_transcripts) + '\n')
    file_object.write('tags = ' + pprint.pformat(new_tags) + '\n')

print('Done saving transcripts and tags.')

#TODO: check that transcript and tags exist for every instance of a comic image,
# because transcripts are only parsed when an image is being downloaded. It may 
# be possible to have missing existing transcripts caused by an oportune error?  