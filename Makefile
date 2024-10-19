# Определение переменных
LOCAL_COMPOSE_FILE := docker/docker-compose.local.yml
DEV_COMPOSE_FILE := docker/docker-compose.development.yml
TEST_COMPOSE_FILE := docker/docker-compose.test.yml
PROD_COMPOSE_FILE := docker/docker-compose.production.yml
GIT_FLOW := git flow
VERSION := $(shell git describe --tags --abbrev=0)

# Функции
run_containers = docker compose -f $(1) up -d
stop_containers = docker compose -f $(1) down
restart_containers = $(stop_containers) $(run_containers)

# Цель для запуска всех сервисов
.PHONY: services
services: $(COMPOSE_FILE)
	$(call run_services)

# Цель для запуска конкретного сервиса
.PHONY: run-%
run-%:
	$(call run_containers,$(DIR)/$(COMPOSE_FILE))

# Цель для остановки всех сервисов
.PHONY: stop
stop:
	$(call stop_containers,$(DIR)/$(COMPOSE_FILE))

# Цель для перезапуска всех сервисов
.PHONY: restart
restart:
	$(call restart_containers,$(DIR)/$(COMPOSE_FILE))

# Цель для запуска API локально
.PHONY: local-api
local-api:
	$(call run_containers,$(DIR)/$(LOCAL_COMPOSE_FILE))

# Цель для запуска бота локально
.PHONY: local-bot
local-bot:
	$(call run_containers,$(DIR)/$(LOCAL_COMPOSE_FILE))

# Цель для запуска Celery worker локально
.PHONY: local-celery
local-celery:
	$(call run_containers,$(DIR)/$(LOCAL_COMPOSE_FILE))

# Цель для запуска API в dev окружении
.PHONY: dev-api
dev-api:
	$(call run_containers,$(DIR)/$(DEV_COMPOSE_FILE))

# Цель для запуска бота в dev окружении
.PHONY: dev-bot
dev-bot:
	$(call run_containers,$(DIR)/$(DEV_COMPOSE_FILE))

# Цель для запуска Celery worker в dev окружении
.PHONY: dev-celery
dev-celery:
	$(call run_containers,$(DIR)/$(DEV_COMPOSE_FILE))

# Цель для запуска API в test окружении
.PHONY: test-api
test-api:
	$(call run_containers,$(DIR)/$(TEST_COMPOSE_FILE))

# Цель для запуска бота в test окружении
.PHONY: test-bot
test-bot:
	$(call run_containers,$(DIR)/$(TEST_COMPOSE_FILE))

# Цель для запуска Celery worker в test окружении
.PHONY: test-celery
test-celery:
	$(call run_containers,$(DIR)/$(TEST_COMPOSE_FILE))

# Цель для запуска API в prod окружении
.PHONY: prod-api
prod-api:
	$(call run_containers,$(DIR)/$(PROD_COMPOSE_FILE))

# Цель для запуска бота в prod окружении
.PHONY: prod-bot
prod-bot:
	$(call run_containers,$(DIR)/$(PROD_COMPOSE_FILE))

# Цель для запуска Celery worker в prod окружении
.PHONY: prod-celery
prod-celery:
	$(call run_containers,$(DIR)/$(PROD_COMPOSE_FILE))

# Цель для генерации changelog
.PHONY: changelog
changelog:
	@echo "Создание changelog..."
	cz changelog

# Цель для увеличения версии
.PHONY: bump
bump:
	@echo "Увеличение версии..."
	cz bump --changelog --yes

# Цель для просмотра текущих веток
.PHONY: branches
branches:
	@echo "Просмотр текущих веток:"
	git branch -a

# Цель для инициализации Git Flow
.PHONY: init
init:
	@echo "Инициализация Git Flow..."
	$(GIT_FLOW) init -d
	@echo "Инициализация окружения..."
	pyenv install 3.12.0
	pyenv virtualenv 3.12.0 $$environment
	pyenv local $$environment
	poetry config virtualenvs.prefer-active-python true
	@echo "Установка зависимостей..."
	poetry install

# Цель для создания новой ветки
.PHONY: feature-start
feature-start:
	@echo "2 последних изменения в репозитории:"
	git log --oneline -4
	@read -p "Введите имя ветки: " feature
	@echo "Создание новой ветки: $$feature"
	$(GIT_FLOW) feature start "$$feature"

# Цель для завершения ветки
.PHONY: feature-finish
feature-finish:
	@echo "Название текущей ветки:"
	git branch --show-current
	@read -p "Введите имя ветки: " feature
	@echo "Завершение ветки: $$feature"
	@echo "Текущий статус репозитория:"
	git status
	@read -p "Хотите добавить все изменения? (y/n): " add_all
	if [ "$$add_all" = "y" ]; then \
		git add .; \
	else \
		@read -p "Введите файлы для добавления (через пробел): " files; \
		git add $$files; \
	fi
	@echo "Создание коммита..."
	cz commit
	$(GIT_FLOW) feature finish $$feature
	git push --all

# Цель для начала и завершения нового релиза
.PHONY: release
release:
	@echo "Определение следующей версии..."
	next_version=$$(cz bump --dry-run | grep "version" | awk '{print $$3}')
	if [ -z "$$next_version" ]; then \
		echo "Ошибка: Не удалось определить следующую версию."; \
		exit 1; \
	fi
	@echo "Следующая версия: $$next_version"
	@read -p "Подтверждаете ли вы эту версию? (y/n): " confirm
	if [ "$$confirm" != "y" ]; then \
		@read -p "Введите номер релиза вручную: " version; \
	else \
		version=$$next_version; \
	fi
	@echo "Создание новой ветки релиза: $$version"
	if ! git flow release start $$version; then \
		echo "Ошибка: Не удалось создать ветку релиза."; \
		exit 1; \
	fi
	@echo "Завершение релиза: $$version"
	if ! cz changelog; then \
		echo "Ошибка: Не удалось сгенерировать changelog."; \
		exit 1; \
	fi
	if ! cz bump --yes; then \
		echo "Ошибка: Не удалось обновить версию."; \
		exit 1; \
	fi
	if ! git tag -d $$version 2> /dev/null; then \
		echo "Предупреждение: Тег $$version не найден для удаления."; \
	fi
	if ! git flow release finish $$version; then \
		echo "Ошибка: Не удалось завершить релиз."; \
		exit 1; \
	fi
	if ! git push origin master; then \
		echo "Ошибка: Не удалось отправить изменения в master."; \
		exit 1; \
	fi
	if ! git push origin develop; then \
		echo "Ошибка: Не удалось отправить изменения в develop."; \
		exit 1; \
	fi
	if ! git push --tag; then \
		echo "Ошибка: Не удалось отправить теги."; \
		exit 1; \
	fi

# Цель для начала нового хотфикса
.PHONY: start-hotfix
start-hotfix:
	@read -p "Введите номер хотфикса: " version
	@echo "Создание новой ветки хотфикса: $$version"
	$(GIT_FLOW) hotfix start $$version

# Цель для завершения хотфикса
.PHONY: finish-hotfix
finish-hotfix:
	@read -p "Введите номер хотфикса: " version
	@echo "Завершение хотфикса: $$version"
	@echo "Текущий статус репозитория:"
	git status
	@read -p "Хотите добавить все изменения? (y/n): " add_all
	if [ "$$add_all" = "y" ]; then \
		git add .; \
	else \
		@read -p "Введите файлы для добавления (через пробел): " files; \
		git add $$files; \
	fi
	@echo "Создание коммита..."
	cz commit
	$(GIT_FLOW) hotfix finish $$version

# Цель для просмотра логов контейнеров
.PHONY: logs
logs:
	@echo "Просмотр логов контейнеров..."
	docker compose -f $(COMPOSE_FILE) logs -f

# Цель для сборки образов
.PHONY: build
build:
	@echo "Сборка образов..."
	docker compose -f $(DEV_COMPOSE_FILE) build

# Цель для запуска линтера
.PHONY: lint
lint:
	@echo "Запуск линтера..."
	poetry run flake8 .
	poetry run mypy .

# Цель для запуска тестов
.PHONY: test
test:
	@echo "Запуск тестов..."
	poetry run pytest

# Цель для очистки временных файлов и кэша
.PHONY: clean
clean:
	@echo "Очистка временных файлов и кэша..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name "*.db" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache

# Цель для обновления зависимостей проекта
.PHONY: update-deps
update-deps:
	@echo "Обновление зависимостей проекта..."
	poetry update

# Цель для создания новой миграции базы данных
.PHONY: revision
revision:
	@read -p "Введите сообщение для миграции: " msg
	@echo "Генерация миграции с сообщением: $$msg"
	poetry run alembic revision --autogenerate -m "$$msg"

# Цель для применения миграций базы данных
.PHONY: upgrade
upgrade:
	@echo "Применение миграций"
	poetry run alembic upgrade head

# Цель для изменения файла окружения
.PHONY: shake
shake:
	@echo "Изменение файла окружения"
	@read -p "Введите имя файла (.local.env или .dev.env): " file
	if [ "$$file" = ".local.env" ]; then \
		cp .local.env .env; \
	elif [ "$$file" = ".dev.env" ]; then \
		cp .dev.env .env; \
	else \
		echo "Неизвестное имя файла"; \
		exit 1; \
	fi

# Цель для вывода справки
.PHONY: help
help:
	@echo "Доступные команды:"
	@echo "  make init              - Инициализация Git Flow"
	@echo "  make feature-start     - Создание новой ветки"
	@echo "  make feature-finish    - Завершение ветки ветки"
	@echo "  make release           - Начало и завершение нового релиза"
	@echo "  make finish-release    - Завершение релиза с увеличением версии и созданием changelog"
	@echo "  make start-hotfix      - Начало нового хотфикса"
	@echo "  make finish-hotfix     - Завершение хотфикса"
	@echo "  make changelog         - Генерация changelog с Commitizen"
	@echo "  make bump              - Увеличение версии с Commitizen"
	@echo "  make branches          - Просмотр текущих веток"
	@echo "  make local-up          - Запуск локального окружения"
	@echo "  make local-down        - Остановка локального окружения"
	@echo "  make local-restart     - Перезапуск локального окружения"
	@echo "  make local-api         - Запуск API локально"
	@echo "  make local-bot         - Запуск бота локально"
	@echo "  make local-celery      - Запуск Celery worker локально"
	@echo "  make local-api-down    - Остановка локального API"
	@echo "  make local-bot-down    - Остановка локального бота"
	@echo "  make local-celery-down - Остановка локального Celery worker"
	@echo "  make dev-up            - Запуск dev окружения"
	@echo "  make dev-down          - Остановка dev окружения"
	@echo "  make dev-restart       - Перезапуск dev окружения"
	@echo "  make test-up           - Запуск test окружения"
	@echo "  make test-down         - Остановка test окружения"
	@echo "  make test-restart      - Перезапуск test окружения"
	@echo "  make prod-up           - Запуск production окружения"
	@echo "  make prod-down         - Остановка production окружения"
	@echo "  make prod-restart      - Перезапуск production окружения"
	@echo "  make logs              - Просмотр логов контейнеров"
	@echo "  make build             - Сборка образов"
	@echo "  make lint              - Запуск линтера"
	@echo "  make test              - Запуск тестов"
	@echo "  make clean             - Очистка временных файлов и кэша"
	@echo "  make update-deps       - Обновление зависимостей проекта"
	@echo "  make revision          - Создание новой миграции базы данных"
	@echo "  make upgrade           - Применение миграций базы данных"
	@echo "  make shake             - Изменение файла окружения"
	@echo "  make help              - Вывод справки по доступным командам"