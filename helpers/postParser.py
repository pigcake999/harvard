from markdown_it import MarkdownIt
from markdown_it.extensions.front_matter import front_matter_plugin
from markdown_it.extensions.footnote import footnote_plugin
import os

def parsePost(text):
    md = (
        MarkdownIt()
        .use(front_matter_plugin)
        .use(footnote_plugin)
        .disable('image')
        .enable('table')
    )
    tokens = md.parse(text)
    html_text = md.render(text)
    return html_text

def parse(post):
    with open(os.getcwd() + "/post_bodies/" + str(post['id']) + ".md", 'r') as f:
        return parsePost(f.read())

if __name__ == "__main__":
    post = {}#
    post['id'] = 1
    print(parse(post))