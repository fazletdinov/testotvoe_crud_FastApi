# Проект - тестовое CRUD

Проект реализован с помощью Fastapi, SQLAlchemy, PostgreSql, alembic, asyncio,
docker-compose,

### Чтобы запустить проект у себя локально, вам необходимо

Склонировать репозиторий

```
git clone git@github.com:fazletdinov/testotvoe_crud_FastApi.git
```

Далее Вам необходимо заполнить .env файл, как показано
на примере .env_example, можете полностью все скопировать,
однако нужно будет указать путь до проекта, то есть заполнить
переменную VOLUME_APP. Если у вас Linux, можете запустить команду

```commandline
pwd
```

из папки проекта, скопироввать результат и вставить в переменную VOLUME_APP
После заполнения можете запустить приложение командой:

```
make up
```

Приложение запущено, теперь можете прогнать тесты командой
в режиме verbose
```
make test
```
или другой командой, без режима verbose
```
docker compose exec app pytest
```

Отключить приложение можно командой

```commandline
make down
```

### Автор

[Idel Fazletdinov - fazletdinov](https://github.com/fazletdinov)
