# Проект - тестовое CRUD

Проект реализован с помощью Fastapi, SQLAlchemy, PostgreSql, alembic, asyncio,
docker-compose,

### Чтобы запустить проект у себя локально, вам необходимо

Склонировать репозиторий

```
git clone git@github.com:fazletdinov/testotvoe_crud_FastApi.git
```

Далее Вам необходимо заполнить .env файл, как показано
на примере .env_example, можете полностью все скопировать.
Для запуска приложения и
для применения выполненных миграций необходимо выполнить следующие команды

```
make up
make migrate
```
Приложение запущено миграции применены, можете запускать тестовые сценарии
через Postman
Приложение можно остановить командой
```
make down
```
Следующей командой можете запустить приложения для прогона тестов,
написанных с помощью pytest
```
make up-test
```
Чтобы запустить тесты наберите команду

```
make test
```

Отключить приложение для тестов можно командой

```commandline
make down-test
```
* Вывод количества подменю и блюд для Меню через один (сложный) ORM запрос релизован в
директории src/crud/menu и не очень сложный в директории src/crud/submenu
* Тестовый сценарий из Postman реализовал в директории tests/api/api_v1/test_postman
* Реализовал в тестах аналог Django reverse() для FastAPI - tests/conftest в виде функции reverse_url
* Описать ручки API в соответствий c OpenAPI - [openapi.json](openapi.json)
* Конфигурция редис лежит в директории redis/redis.conf взято из документации
* bind 0.0.0.0 — замапил Redis на внутренний localhost Docker-контейнера.
* maxmemory 100mb — ограничил размер кэша.
* maxmemory-policy volatile-ttl — эта политика позволяет удалить наименее актуальные данные при достижении лимита памяти.
* Добавить в проект фоновую задачу с помощью Celery + RabbitMQ - посмотрите docker-compose.yml
* Добавить эндпоинт (GET) для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами - ENDPOINT - "full_menu_submenu_dish"
src/api/v1_handlers/menu/ - в самом конце
* Обновление меню из локального файла раз в 15 сек. - tasks
### Автор

[Idel Fazletdinov - fazletdinov](https://github.com/fazletdinov)
