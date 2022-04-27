from celery.result import AsyncResult
res = AsyncResult("3d6dc0ba-7cbb-4799-a9ca-cf68078561c1")
print(res.ready())
