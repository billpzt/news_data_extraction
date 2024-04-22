from robocorp.tasks import task
from NewsExtractor import NewsExtractor as extractor

@task
def minimal_task():
    ex = extractor(search_phrase="Iran", news_category="World & Nation")
    ex.run()
