from dishka import make_async_container

from DI.providers import *


def create_container():
    return make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        UnitOfWorkProvider(),
        ServiceProvider(),
    )
