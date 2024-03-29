# ✨VKBot игра "СТО К ОДНОМУ"✨

### **Игровой бот в социальной сети "ВКонтакте"**
##### Стек технологий: 

##### Backend - **aiohttp alembic SQLAlchemy rabbitmq docker**
#
##### `Проект реализован c использованием CI/CD`
#

##### **Домашняя страница:** `https://vk.com/public215492605/`

###### В проекте реализовано

- простая регистрация по имени далее переход в закрытый чат
- игра работает используя кнопки(кроме ответов на вопросы)
- незарегистрированные пользователи играть не могут (даже если попадут в чат)
при старте запускается игра все состояния хранятся в БД(statemachine) и задается вопрос
- кто первый из участников нажмет ответить тот и начинает отвечать
- при неправильном(повторяющемся) ответе снова запускается возможность выбора отвечающего 
- игра продолжается до момента ответа на все вопросы или остановки одним из участников
- информация об игре выводиться по кнопке “инфо”
также выводиться статистика после завершения и отдельно при победе
счёт храниться для каждого участника в текущей игре, общий счёт конкретной игры и общий счет для каждого участника по всем сыгранным им играм


## **Запуск проекта локально**
##### 1. Клонировать репозиторий
#
```sh
git clone git@github.com:jamsi-max/hw-backend-summer-2022-final-VKBot-100-k-1.git
```
##### 2. Сооздать файл ".env" в папке infra с содержанием по примеру
DB_HOST=
DB_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
RABBITMQ_DEFAULT_USER=
RABBITMQ_DEFAULT_PASS=
AMQP_HOST=
SESSION_KEY=
ADMIN_EMAIL=
ADMIN_PASSWORD=
BOT_TOKEN=
BOT_GROUP_ID=
#
##### 3. Из директории "/infra", где находиться файл **"docker-compose.yaml"**  выполнить команду в консоле для запуска проекта в контейнерах:
`Внимание! Docker(Docke Compose) должен быть установлен и запущен`
```sh
docker-compose up -d
```
##### 4. Войти в контейнер "bot" и запустить миграции:
#
```sh
 sudo docker-compose exec bot sh
```
```sh
 python -m alembic revision --autogenerate 
```
```sh
python -m alembic upgrade head 
```
##### 5. Через админку добавмить вопросы/ответы 
#

### Документация проекта по адресу http://localhost/docs
#
##### Для остановки проекта используйте команду:
#
```sh
docker-compose down
```
## Лицензия

MIT

**Бесплатный софт**
##### Автор проекта: Макс
##### Связь с автором(телеграмм): https://t.me/jony2024 
##### © Copyright **[jamsi-max](https://github.com/jamsi-max)**
