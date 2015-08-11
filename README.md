# Emotient Python SDK

This Python library wraps the Emotient Analytics API. For more information on the Emotient Analytics API and the Python code examples, see the [Emotient Analytics API documentation](https://analytics.emotient.com/apireference/?python#).

The Emotient Python SDK is hosted at [GitHub](https://github.com/emotient) and is free to use. We accept bug fixes and other enhancements through GitHub pull requests.

## Installation

You don't need this source code unless you want to modify the library. 

To install the library, run:

    pip install emotient

To install from source, run:

    git clone https://github.com/emotient/emotient-python.git
    cd emotient-python
    python setup.py install



## Quick Start

To use the Emotient Python SDK, you need an API key. If you don't have an Emotient Analytics account, [create one](https://analytics.emotient.com), and go to [Emotient Analytics API Access](https://analytics.emotient.com/apiKey) to get your key. 


The following example shows how to use your API key with the Emotient Python SDK:

```python
from emotient import EmotientAnalyticsAPI

api_key = "91se93z0-f73f-498a-b744-8d1e3a061fcf"
client = EmotientAnalyticsAPI(api_key)
``` 





## Examples

Group objects have similar functionality as media. You can create, retrieve, update (Isn't this --> UPLOAD???), delete, and download aggregated analytics for groups.


1. Retrieve all media:
 
        all_media = client.media.all()
 



1. Retrieve a list of media:
 
        media_list = client.media.list(page=1, per_page=500)
        for media in media_list:
	    print(media.id)




1. Retrieve a media object by ID, print the filename, and update the metadata: 

        media_id = 'c2128139-a984-b695-52a4-eae8021103bb'
        media = client.media.retrieve(media_id)
        print(media.data['filename'])
        media.update(meta_data={'tag': 'long video'})




1. Delete a media object (This is irreversible.): 
              
        media_id = 'c2128139-a984-b695-52a4-eae8021103bb'
        media = client.media.retrieve(media_id)
        media.delete()




1. Upload a new video, create a group, and add the new media to the group: 

        video_path = 'your/user/path/clip.mp4 
        with open(video_path, 'rb') as fp:
        	new_media = client.media.upload(fp)

        new_group = client.groups.create(name='My Group')
        new_group.media.add(new_media)




1. Download the Emotient Analytics CSV files for a media object:


        media_id = 'c2128139-a984-b695-52a4-eae8021103bb'
        media = client.media.retrieve(media_id)

        analytics_file = 'your/user/path/analytics.csv'
        with open(analytics_file, 'w') as fp:
        	media.analytics(fp)

        aggregated_analytics_file = 'your/user/path/aggregated_analytics.csv'
        with open(aggregated_analytics_file, 'w') as fp:
        	media.aggregated_analytics(fp, interval='summary', report='standard', gender='combined'`




1. List media in a group:

    
        group_id = 'c2128139-a984-b695-52a4-eae8021103bb'
        group = client.groups.retrieve(group_id)
        group_media_list = group.media.list(page=1, per_page=500)
        for media in group_media_list:
	    	print(media.id)



## Batch Tasks

Upload and download analytics for multiple videos with these scripts: <https://github.com/emotient/Samples>

## Contributing
1. [Fork it](https://github.com/emotient/emotient-python) and clone
2. Create your script branch with `git checkout -b my-new-script`
3. Commit your changes with `git commit -am 'Add some script'`
4. Push to the branch with `git push origin my-new-script`
5. Create a new Pull Request.

## Support

For more information, send us an email at <support@emotient.com>.
