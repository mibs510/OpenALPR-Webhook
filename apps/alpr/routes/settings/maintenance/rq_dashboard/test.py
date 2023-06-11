from apps import default_q
from apps.alpr.routes.settings.maintenance.rq_dashboard.queue_functions import count_words_at_url

if __name__ == "__main__":
    for i in range(10):
        job = default_q.enqueue(count_words_at_url, 'http://nvie.com')
        print(job.result)


