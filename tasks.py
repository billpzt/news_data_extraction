from robocorp.tasks import task
from NewsExtractor import NewsExtractor as extractor

@task
def minimal_task():
    ex = extractor("Iran")
    ex.run()
