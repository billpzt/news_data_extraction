from robocorp.tasks import task
from NewsExtractor_ANTIGO import NewsExtractor as extractor

@task
def minimal_task():
    ex = extractor("Iran")
    ex.run()
