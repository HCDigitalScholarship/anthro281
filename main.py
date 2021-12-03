import srsly 
import frontmatter
import markdown
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
templates = Jinja2Templates(directory="templates")
topics_path = Path.cwd() / 'data' / 'topics'
links_path = Path.cwd() / 'data' / 'links'

def load_topics(stem=None):
    if stem:
        try:
            topic_files = [(a.stem,frontmatter.load(a)) for a in topics_path.iterdir() if a.stem == stem]
        except IndexError:
            raise HTTPException(status_code=404, detail="Topic not found")
    else:    
        topic_files = [(a.stem,frontmatter.load(a)) for a in topics_path.iterdir()]
    topics = []
    for t in topic_files: 
        stem = t[0]
        md = t[1]
        md.stem = stem
        md.content = markdown.markdown(md.content)
        topics.append(md)
    return topics

def load_links(slug=None): #full title of topic
    if slug:
        try:
            topic_title = [frontmatter.load(a)['title'] for a in topics_path.iterdir() if a.stem == slug][0]
            links = [frontmatter.load(a).metadata for a in links_path.iterdir() if frontmatter.load(a).metadata['topic'] == topic_title]
        except IndexError:
            raise HTTPException(status_code=404, detail="Topic not found")
    else:    
        links = [frontmatter.load(a).metadata for a in links_path.iterdir()]

    return links

@app.get("/")
def index(request:Request):
    context = {"request": request}
    context['topics'] = load_topics()

    return templates.TemplateResponse("index.html", context)

    

@app.get("/topic/{slug}")
def topics(request:Request, slug:str):
    context = {"request": request}
    context['topics'] = load_topics()
    context['page'] = load_topics(stem=slug)[0]
    context['links'] = load_links(slug=slug)
    filters = []
    [filters.extend(a['filters']) for a in context['links']]
    context['filters'] =  filters
    return templates.TemplateResponse("topic.html", context)

