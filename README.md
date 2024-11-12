
# Проект SaberManager (версия с Docker)

## Описание

Это приложение использует Docker для изоляции окружения, а также предоставляет авторизацию через GitHub и Яндекс с помощью OAuth.

## Настройка окружения

### Шаг 1: Установка зависимостей

Создайте виртуальное окружение Python и установите зависимости из `requirements.txt`:

```bash
python3 -m venv venv
source venv/bin/activate  # активация виртуального окружения
pip install -r requirements.txt
```

### Шаг 2: Регистрация OAuth-приложений

#### GitHub

1. Перейдите по ссылке для регистрации приложения GitHub: [https://github.com/settings/applications/new](https://github.com/settings/applications/new).
2. Заполните поля:
   - **Application name**: любое название, например, `SaberManager`.
   - **Homepage URL**: `http://localhost:5000`.
   - **Authorization callback URL**: `http://localhost:5000/github/callback`.
3. После создания сохраните `Client ID` и `Client Secret`.

#### Яндекс

1. Перейдите по ссылке для регистрации приложения Яндекс: [https://oauth.yandex.ru/client/new](https://oauth.yandex.ru/client/new).
2. Заполните поля:
   - **Название приложения**: любое название, например, `SaberManager`.
   - **Redirect URI**: `http://localhost:5000/yandex/callback`.
3. Сохраните `Client ID` и `Client Secret`.

### Шаг 3: Настройка конфигурации

Создайте конфигурацию OAuth в файле `config.py` для использования в приложении:

```python
class Config:
    SECRET_KEY = 'your_secret_key'
    
    # GitHub OAuth
    GITHUB_CLIENT_ID = 'ваш_client_id_от_GitHub'
    GITHUB_CLIENT_SECRET = 'ваш_client_secret_от_GitHub'
    
    # Яндекс OAuth
    YANDEX_CLIENT_ID = 'ваш_client_id_от_Яндекс'
    YANDEX_CLIENT_SECRET = 'ваш_client_secret_от_Яндекс'
    
    # Database URL (для использования с Docker)
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:test@db:5432/TimeManager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки почты
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'elvenbe@yandex.ru'
    MAIL_PASSWORD = 'nfvevsdjnkgcqbbs'
    MAIL_DEFAULT_SENDER = 'elvenbe@yandex.ru'
```

### Шаг 4: Запуск проекта в Docker

1. Соберите и запустите контейнеры:

    ```bash
    docker-compose up --build
    ```

2. Приложение будет доступно по адресу: [http://localhost:5000](http://localhost:5000).

### Структура файлов Docker

- **Dockerfile**: инструкции для сборки контейнера приложения.
- **docker-compose.yml**: описание контейнеров приложения и базы данных.

### Возможные ошибки

Если вы получаете ошибки, связанные с доступом к GitHub или Яндексу, проверьте правильность `Client ID` и `Client Secret` в конфигурации `config.py`, а также настройки `Authorization callback URL` на платформах GitHub и Яндекс.
