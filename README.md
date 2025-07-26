# ChatBot Service

Асинхронный чат-сервис на FastAPI с интеграцией OpenAI GPT-4, использующий PostgreSQL, Redis и Qdrant для хранения и обработки данных. Коммуникация с клиентом — через WebSocket.

---

## Технологии

- Python 3.12, FastAPI  
- PostgreSQL — основная БД  
- Redis — кэш и хранение истории сообщений  
- Qdrant — векторная база для поиска  
- OpenAI API (GPT-4)  
- Docker & Docker Compose  

---

## Быстрый старт

### Клонирование репозитория

```bash
git clone <ваш-репозиторий>
cd <папка-проекта>
```

## Запуск через Docker Compose

Для удобного запуска всех сервисов (PostgreSQL, Redis, Qdrant и приложения) используйте Docker Compose.

1. Убедитесь, что у вас установлен Docker и Docker Compose.

2. Запустите все сервисы командой:

```bash
docker-compose up --build
```
3. Приложение будет доступно по адресу: http://localhost:8000