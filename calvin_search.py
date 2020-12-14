#!/usr/bin/env python3
import transcripts_and_tags, pprint, shutil, os
from pathlib import Path

if os.path.isdir('tag_results'):
    shutil.rmtree('tag_results')
if os.path.isdir('keyword_results'):
    shutil.rmtree('keyword_results')

os.makedirs('tag_results')
os.makedirs('keyword_results')

search_str = input('Enter search string: ').lower()
where_to_search = input('Search by keyword, tag. (both by default) ').lower()

tag_results = []
trans_results = []

# Search for matching tags
if where_to_search != 'keyword':
    for k, v in transcripts_and_tags.tags.items():
        if search_str in v:
            tag_results.append(k)
            #copy results to directory
            shutil.copy('calvin_and_hobbes_comics/' + k, 'tag_results/')

    # Print tag search results        
    if len(tag_results) > 0:
        pprint.pprint(tag_results)        
    else:
        print('No comics with matching tags were found.')
    
# Search for matching keywords
if where_to_search != 'tag':
    for k, v in transcripts_and_tags.transcripts.items():
        if search_str in v:
            trans_results.append(k)
            shutil.copy('calvin_and_hobbes_comics/' + k, 'keyword_results/')

    # Print transcript search results
    if len(trans_results) > 0:
        pprint.pprint(trans_results)
    else: 
        print('No comics with matching keywords were found.')
