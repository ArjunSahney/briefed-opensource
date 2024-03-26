# !pip install pygooglenews
# https://stackoverflow.com/questions/75565954/giving-error-while-installing-the-package-in-python

from pygooglenews import GoogleNews

def get_titles(search):
    stories = []
    gn = GoogleNews(country = 'US')
    search = gn.search(search)
    newsitem = search['entries']
    for item in newsitem:
        story = {
            'title': item.title,
            'link': item.link
        }
        stories.append(story)
    return stories

print(get_titles('football'))
